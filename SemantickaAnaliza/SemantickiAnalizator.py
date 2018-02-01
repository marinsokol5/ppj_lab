import fileinput
import sys

int_min_value = -2147483648
int_max_value = 2147483647


class Funkcija:
    def __init__(self, ime: str, tip: str, definirana: bool):
        self.ime = ime
        self.tip = tip
        self.definirana = definirana

    def __eq__(self, other):
        return self.ime == other.ime


class Identifikator:
    def __init__(self, ime: str, tip: str, l_izraz: bool, definiran: bool = True):
        self.ime = ime
        self.tip = tip
        self.l_izraz = l_izraz
        self.definiran = definiran

    def __eq__(self, other):
        return self.ime == other.ime


class Node:
    def __init__(self, tip: str, l_izraz: bool, tipovi=None, imena=None, br_elemenata: int = 0, ime: str = ""):
        self.ime = ime
        self.tip = tip
        self.l_izraz = l_izraz
        self.tipovi = tipovi
        self.imena = imena
        self.br_elemenata = br_elemenata


class Blok:
    def __init__(self, identifikatori, roditelj):
        self.identifikatori = identifikatori
        self.roditelj = roditelj


ulaz = list()
ulaz_indent = list()
funkcije = list()
index = 0
trenutna_funkcija = None
u_petlji = 0


def obidi_stablo():
    globalni_blok = Blok(list(), None)
    rek_obilazak(globalni_blok)
    if not provjeri_main_funkciju():
        print("main", end="")
    elif not provjeri_definiranost_funkcija():
        print("funkcija", end="")


def implicitno_pretvoriv(tip_iz: str, tip_u: str) -> bool:
    if tip_iz.startswith("funkcija") or tip_u.startswith("funkcija") or tip_iz == "void" or tip_u == "void":
        return False
    if tip_iz.startswith("niz") and not tip_u.startswith("niz"):
        return False
    if not tip_iz.startswith("niz") and tip_u.startswith("niz"):
        return False
    if not tip_iz.startswith("niz"):
        return not (tip_iz.endswith("int") and tip_u.endswith("char"))
    return tip_iz.endswith("int)") and tip_u.endswith("int)") or tip_iz.endswith("char)") and tip_u.endswith("char)")


def eksplicitno_pretvoriv(tip_iz: str, tip_u: str) -> bool:
    return implicitno_pretvoriv(tip_iz, tip_u) or tip_iz.endswith("int") and tip_u.endswith("char")


def usporedi_argumente(fun_argumenti, lista_argumenata) -> bool:
    if len(fun_argumenti) != len(lista_argumenata):
        return False
    for i in range(len(fun_argumenti)):
        if not implicitno_pretvoriv(lista_argumenata[i], fun_argumenti[i]):
            return False
    return True


def ispravan_prefiks(niz_znakova: str) -> bool:
    prefiksirano = False
    for znak in niz_znakova:
        if not prefiksirano and znak == "\\":
            prefiksirano = True
            continue
        if prefiksirano:
            if znak == "\\" or znak == "t" or znak == "n" or znak == "0" or znak == "'" or znak == "\"":
                prefiksirano = False
                continue
            else:
                return False
    return True


def nadi_identifikator(blok: Blok, idn_ime: str) -> Identifikator:
    identifikator = None
    while blok is not None and identifikator is None:
        for idn in blok.identifikatori:
            if idn.ime == idn_ime:
                identifikator = idn
                break
        blok = blok.roditelj
    return identifikator


def mul_izrazi(ime: str, start_index: int, blok: Blok) -> Node:
    global index
    if ulaz[index] != ime:
        return rek_obilazak(blok)
    prvi = rek_obilazak(blok)
    if not implicitno_pretvoriv(prvi.tip, "int"):
        print_error(start_index)
    index = index + 1
    drugi = rek_obilazak(blok)
    if not implicitno_pretvoriv(drugi.tip, "int"):
        print_error(start_index)
    return Node("int", False)


def proslijedi(ime: str, blok: Blok) -> Node:
    if ulaz[index] != ime:
        return rek_obilazak(blok)
    rek_obilazak(blok)
    return rek_obilazak(blok)


def tip_funkcije(tipovi, povratni_tip) -> str:
    result = "funkcija("
    for tip in tipovi:
        result += tip + ","
    if len(tipovi) == 0:
        result += "void,"
    return result[:-1] + "->" + povratni_tip + ")"


def rek_obilazak(blok: Blok, fun_blok: bool = False, ntip: str = "") -> Node:
    global index
    global u_petlji
    global trenutna_funkcija
    ime = ulaz[index]
    start_index = index
    index = index + 1
    if ime == "<unarni_operator>":
        index = index + 1
        return Node("", False, None, None, 0, ime)
    elif ime == "<primarni_izraz>":
        if ulaz[index].startswith("L_ZAGRADA"):
            index = index + 1
            izraz = rek_obilazak(blok)
            index = index + 1
            return izraz
        if ulaz[index].startswith("IDN"):
            idn_ime = ulaz[index].split()[2]
            index = index + 1
            identifikator = None
            temp_blok = blok
            while temp_blok is not None and identifikator is None:
                for idn in temp_blok.identifikatori:
                    if idn.ime == idn_ime:
                        identifikator = idn
                        break
                temp_blok = temp_blok.roditelj
            if identifikator is None:
                print_error(start_index)
            return Node(identifikator.tip, identifikator.l_izraz)
        if ulaz[index].startswith("BROJ"):
            vrijednost = int(ulaz[index].split()[2])
            index = index + 1
            if vrijednost < int_min_value or vrijednost > int_max_value:
                print_error(start_index)
            return Node("int", False)
        if not ispravan_prefiks(ulaz[index].split()[2][1:-1]):
            print_error(start_index)
        tip = "char" if ulaz[index].startswith("ZNAK") else "niz(const char)"
        index = index + 1
        return Node(tip, False)
    elif ime == "<postfiks_izraz>":
        if ulaz[index] == "<primarni_izraz>":
            return rek_obilazak(blok)
        postfiks_izraz = rek_obilazak(blok)
        if ulaz[index].startswith("L_UGL_ZAGRADA"):
            if not postfiks_izraz.tip.startswith("niz"):
                print_error(start_index)
            index = index + 1
            izraz = rek_obilazak(blok)
            if not implicitno_pretvoriv(izraz.tip, "int"):
                print_error(start_index)
            tip = postfiks_izraz.tip[4:-1]
            index = index + 1
            return Node(tip, not tip.startswith("const"))
        if ulaz[index].startswith("L_ZAGRADA"):
            if not postfiks_izraz.tip.startswith("funkcija"):
                print_error(start_index)
            index = index + 1
            temp = postfiks_izraz.tip.split("->")
            povratni_tip = temp[1][:-1]
            if ulaz[index] == "<lista_argumenata>":
                lista_argumenata = rek_obilazak(blok)
                tipovi = temp[0][9:].split(",")
                if not usporedi_argumente(tipovi, lista_argumenata.tipovi):
                    print_error(start_index)
            elif postfiks_izraz.tip != "funkcija(void->" + povratni_tip + ")":
                print_error(start_index)
            index = index + 1
            return Node(povratni_tip, False)
        index = index + 1
        if not postfiks_izraz.l_izraz or not implicitno_pretvoriv(postfiks_izraz.tip, "int"):
            print_error(start_index)
        return Node("int", False)
    elif ime == "<lista_argumenata>":
        if ulaz[index] == "<izraz_pridruzivanja>":
            return Node("", False, [rek_obilazak(blok).tip])
        lista_argumenata = rek_obilazak(blok)
        lista_argumenata.tipovi.append(rek_obilazak(blok).tip)
        return Node("", False, lista_argumenata.tipovi)
    elif ime == "<unarni_izraz>":
        if ulaz[index] == "<postfiks_izraz>":
            return rek_obilazak(blok)
        if ulaz[index] == "<unarni_operator>":
            rek_obilazak(blok)
            cast_izraz = rek_obilazak(blok)
            if not implicitno_pretvoriv(cast_izraz.tip, "int"):
                print_error(start_index)
            return Node("int", False)
        index = index + 1
        unarni_izraz = rek_obilazak(blok)
        if not unarni_izraz.l_izraz or not implicitno_pretvoriv(unarni_izraz.tip, "int"):
            print_error(start_index)
        return Node("int", False)
    elif ime == "<cast_izraz>":
        if ulaz[index] == "<unarni_izraz>":
            return rek_obilazak(blok)
        index = index + 1
        ime_tipa = rek_obilazak(blok)
        index = index + 1
        cast_izraz = rek_obilazak(blok)
        if not eksplicitno_pretvoriv(cast_izraz.tip, ime_tipa.tip):
            print_error(start_index)
        return Node(ime_tipa.tip, False)
    elif ime == "<ime_tipa>":
        if ulaz[index] == "<specifikator_tipa>":
            return rek_obilazak(blok)
        index = index + 1
        specifikator_tipa = rek_obilazak(blok)
        if specifikator_tipa.tip == "void":
            print_error(start_index)
        return Node("const " + specifikator_tipa.tip, False)
    elif ime == "<specifikator_tipa>":
        index = index + 1
        return Node(ulaz[index-1].split()[2], False)
    elif ime == "<izraz_pridruzivanja>":
        if ulaz[index] == "<log_ili_izraz>":
            return rek_obilazak(blok)
        postfiks_izraz = rek_obilazak(blok)
        if not postfiks_izraz.l_izraz:
            print_error(start_index)
        index = index + 1
        izraz_pridruzivanja = rek_obilazak(blok)
        if not implicitno_pretvoriv(izraz_pridruzivanja.tip, postfiks_izraz.tip):
            print_error(start_index)
        return Node(postfiks_izraz.tip, False)
    elif ime == "<izraz>":
        if ulaz[index] == "<izraz_pridruzivanja>":
            return rek_obilazak(blok)
        rek_obilazak(blok)
        index = index + 1
        izraz_pridruzivanja = rek_obilazak(blok)
        return Node(izraz_pridruzivanja.tip, False)
    elif ime == "<slozena_naredba>":
        index = index + 1
        if not fun_blok:
            blok = Blok(list(), blok)
        if ulaz[index] == "<lista_naredbi>":
            lista_naredbi = rek_obilazak(blok)
            index = index + 1
            return lista_naredbi
        rek_obilazak(blok)
        lista_naredbi = rek_obilazak(blok)
        index = index + 1
        return lista_naredbi
    elif ime == "<izraz_naredba>":
        if ulaz[index].startswith("TOCKAZAREZ"):
            index = index + 1
            return Node("int", False)
        izraz = rek_obilazak(blok)
        index = index + 1
        return Node(izraz.tip, False)
    elif ime == "<naredba_grananja>":
        index = index + 2
        izraz = rek_obilazak(blok)
        if not implicitno_pretvoriv(izraz.tip, "int"):
            print_error(start_index)
        index = index + 1
        naredba1 = rek_obilazak(blok)
        if not ulaz[index].startswith("KR_ELSE"):
            return naredba1
        index = index + 1
        return rek_obilazak(blok)
    elif ime == "<naredba_petlje>":
        if ulaz[index].startswith("KR_WHILE"):
            index = index + 2
            izraz = rek_obilazak(blok)
            if not implicitno_pretvoriv(izraz.tip, "int"):
                print_error(start_index)
            index = index + 1
            u_petlji = u_petlji + 1
            naredba = rek_obilazak(blok)
            u_petlji = u_petlji - 1
            return naredba
        index = index + 2
        rek_obilazak(blok)
        izraz_naredba2 = rek_obilazak(blok)
        if not implicitno_pretvoriv(izraz_naredba2.tip, "int"):
            print_error(start_index)
        if ulaz[index] == "<izraz>":
            rek_obilazak(blok)
        index = index + 1
        u_petlji = u_petlji + 1
        naredba = rek_obilazak(blok)
        u_petlji = u_petlji - 1
        return naredba
    elif ime == "<naredba_skoka>":
        if not ulaz[index].startswith("KR_RETURN"):
            if u_petlji == 0:
                print_error(start_index)
            index = index + 2
            return Node("", False)
        index = index + 1
        povratni_tip = trenutna_funkcija.tip.split("->")[1][:-1] if trenutna_funkcija is not None else ""
        if ulaz[index] == "<izraz>":
            izraz = rek_obilazak(blok)
            if trenutna_funkcija is None or not implicitno_pretvoriv(izraz.tip, povratni_tip):
                print_error(start_index)
        elif trenutna_funkcija is None or povratni_tip != "void":
            print_error(start_index)
        index = index + 1
        return Node("", False)
    elif ime == "<vanjska_deklaracija>":
        def_fun = rek_obilazak(blok)
        trenutna_funkcija = None
        return def_fun
    elif ime == "<definicija_funkcije>":
        ime_tipa = rek_obilazak(blok)
        if ime_tipa.tip.startswith("const"):
            print_error(start_index)
        novi_idn = ulaz[index].split()[2]
        identifikator = None
        for idn in blok.identifikatori:
            if idn.ime == novi_idn:
                identifikator = idn
                if not identifikator.ime.startswith("funkcija") or identifikator.definiran:
                    print_error(start_index)
                break
        index = index + 2
        tipovi = list()
        imena = list()
        if ulaz[index].startswith("KR_VOID"):
            index = index + 1
        else:
            lista_parametara = rek_obilazak(blok)
            tipovi = lista_parametara.tipovi
            imena = lista_parametara.imena
        index = index + 1
        tip = tip_funkcije(tipovi, ime_tipa.tip)
        if identifikator is None:
            blok.identifikatori.append(Identifikator(novi_idn, tip, False))
        else:
            if identifikator.tip != tip:
                print_error(start_index)
            identifikator.definiran = True
        postoji = False
        for fun in funkcije:
            if fun.ime == novi_idn and fun.tip == tip:
                fun.definirana = True
                postoji = True
        funkcija = Funkcija(novi_idn, tip, True)
        if not postoji:
            funkcije.append(funkcija)
        blok = Blok(list(), blok)
        for i in range(len(tipovi)):
            tip = tipovi[i]
            blok.identifikatori.append(Identifikator(imena[i], tip, tip == "int" or tip == "char"))
        trenutna_funkcija = funkcija
        return rek_obilazak(blok, True)
    elif ime == "<lista_parametara>":
        if ulaz[index] == "<deklaracija_parametra>":
            deklaracija_parametra = rek_obilazak(blok)
            return Node("", False, [deklaracija_parametra.tip], [deklaracija_parametra.ime])
        lista_parametara = rek_obilazak(blok)
        index = index + 1
        deklaracija_parametra = rek_obilazak(blok)
        if deklaracija_parametra.ime in lista_parametara.imena:
            print_error(start_index)
        lista_parametara.tipovi.append(deklaracija_parametra.tip)
        lista_parametara.imena.append(deklaracija_parametra.ime)
        return Node("", False, lista_parametara.tipovi, lista_parametara.imena)
    elif ime == "<deklaracija_parametra>":
        ime_tipa = rek_obilazak(blok)
        if ime_tipa.tip == "void":
            print_error(start_index)
        idn_ime = ulaz[index].split()[2]
        index = index + 1
        if not ulaz[index].startswith("L_UGL_ZAGRADA"):
            return Node(ime_tipa.tip, ime_tipa.tip == "int" or ime_tipa.tip == "char", None, None, 0, idn_ime)
        index = index + 2
        return Node("niz(" + ime_tipa.tip + ")", False, None, None, 0, idn_ime)
    elif ime == "<deklaracija>":
        ime_tipa = rek_obilazak(blok)
        rek_obilazak(blok, False, ime_tipa.tip)
        index = index + 1
        return Node("", False)
    elif ime == "<lista_init_deklaratora>":
        if ulaz[index] == "<init_deklarator>":
            return rek_obilazak(blok, False, ntip)
        rek_obilazak(blok, False, ntip)
        index = index + 1
        return rek_obilazak(blok, False, ntip)
    elif ime == "<init_deklarator>":
        izravni_deklarator = rek_obilazak(blok, False, ntip)
        if not ulaz[index].startswith("OP_PRIDRUZI"):
            if izravni_deklarator.tip.startswith("const") or izravni_deklarator.tip.startswith("niz(const"):
                print_error(start_index)
            return izravni_deklarator
        index = index + 1
        inicijalizator = rek_obilazak(blok)
        tip_t = izravni_deklarator.tip
        if tip_t.startswith("niz("):
            tip_t = tip_t[4:]
        if tip_t.startswith("const "):
            tip_t = tip_t[6:]
        if izravni_deklarator.tip.startswith("niz("):
            if inicijalizator.br_elemenata > izravni_deklarator.br_elemenata:
                print_error(start_index)
            for i in range(len(inicijalizator.tipovi)):
                if not implicitno_pretvoriv(inicijalizator.tipovi[i], tip_t):
                    print_error(start_index)
        elif tip_t == "int" or tip_t == "char":
            if not implicitno_pretvoriv(inicijalizator.tip, tip_t):
                print_error(start_index)
        else:
            print_error(start_index)
        return Node("", False)
    elif ime == "<izravni_deklarator>":
        idn_ime = ulaz[index].split()[2]
        index = index + 1
        if not ulaz[index].startswith("L_ZAGRADA"):
            if ntip == "void":
                print_error(start_index)
            for idn in blok.identifikatori:
                if idn.ime == idn_ime:
                    print_error(start_index)
            if not ulaz[index].startswith("L_UGL_ZAGRADA"):
                l_izraz = ntip == "int" or ntip == "char"
                blok.identifikatori.append(Identifikator(idn_ime, ntip, l_izraz))
                return Node(ntip, l_izraz)
            broj = int(ulaz[index+1].split()[2])
            if broj < 1 or broj > 1024:
                print_error(start_index)
            index = index + 3
            blok.identifikatori.append(Identifikator(idn_ime, "niz(" + ntip + ")", False))
            return Node("niz(" + ntip + ")", False, None, None, broj)
        index = index + 1
        tipovi = list()
        if ulaz[index] == "<lista_parametara>":
            tipovi = rek_obilazak(blok).tipovi
        else:
            index = index + 1
        index = index + 1
        tip = tip_funkcije(tipovi, ntip)
        identifikator = None
        for idn in blok.identifikatori:
            if idn.ime == idn_ime:
                identifikator = idn
                break
        if identifikator is not None:
            if identifikator.tip != tip:
                print_error(start_index)
        else:
            blok.identifikatori.append(Identifikator(idn_ime, tip, False, False))
            postoji = False
            for fun in funkcije:
                if fun.ime == idn_ime and fun.tip == tip:
                    postoji = True
                    break
            if not postoji:
                funkcije.append(Funkcija(idn_ime, tip, False))
        return Node(tip, False)
    elif ime == "<inicijalizator>":
        if ulaz[index] == "<izraz_pridruzivanja>":
            old_index = index
            izraz_pridruzivanja = rek_obilazak(blok)
            if old_index + 14 < len(ulaz) and ulaz[old_index+14].startswith("NIZ_ZNAKOVA"):
                niz = ulaz[old_index+14].split()[2][1:-1]
                br_elem = len(niz) + 1
                tipovi = list()
                for i in range(br_elem):
                    tipovi.append("const char")
                return Node("niz(const char)", False, tipovi, None, br_elem)
            return Node(izraz_pridruzivanja.tip, izraz_pridruzivanja.tip == "int" or izraz_pridruzivanja.tip == "char")
        index = index + 1
        lista_izraza_pridruzivanja = rek_obilazak(blok)
        index = index + 1
        return Node("", False, lista_izraza_pridruzivanja.tipovi, None, lista_izraza_pridruzivanja.br_elemenata)
    elif ime == "<lista_izraza_pridruzivanja>":
        if ulaz[index] == "<izraz_pridruzivanja>":
            izraz_pridruzivanja = rek_obilazak(blok)
            return Node("", False, [izraz_pridruzivanja.tip], None, 1)
        lista_izraza_pridruzivanja = rek_obilazak(blok)
        index = index + 1
        izraz_pridruzivanja = rek_obilazak(blok)
        lista_izraza_pridruzivanja.tipovi.append(izraz_pridruzivanja.tip)
        return Node("", False, lista_izraza_pridruzivanja.tipovi, None, lista_izraza_pridruzivanja.br_elemenata + 1)
    elif ime == "<prijevodna_jedinica>" or ime == "<lista_naredbi>" or ime == "<lista_deklaracija>":
        return proslijedi(ime, blok)
    elif ime == "<naredba>":
        return rek_obilazak(blok)
    else:
        return mul_izrazi(ime, start_index, blok)


def uredi_zavrsni_znak(ime: str) -> str:
    temp = ime.split()
    return temp[0] + "(" + temp[1] + "," + temp[2] + ")"


def provjeri_main_funkciju() -> bool:
    for fun in funkcije:
        if fun.ime == "main" and fun.tip == "funkcija(void->int)":
            return True
    return False


def provjeri_definiranost_funkcija() -> bool:
    for funkcija in funkcije:
        if not funkcija.definirana:
            return False
    return True


def print_error(start_index: int):
    i = start_index
    print(ulaz[i] + " ::=", end="")
    start_indent = ulaz_indent[i]
    i = i + 1
    while i < len(ulaz):
        if ulaz_indent[i] <= start_indent:
            break
        if ulaz_indent[i] == start_indent + 1:
            print(" " + (ulaz[i] if ulaz[i].startswith("<") else uredi_zavrsni_znak(ulaz[i])), end="")
        i = i + 1

    sys.exit(0)


def main():
    for line in fileinput.input():
        ulaz.append(line.strip())
        ulaz_indent.append(len(line) - len(line.lstrip(' ')))
    obidi_stablo()


if __name__ == '__main__':
    main()
