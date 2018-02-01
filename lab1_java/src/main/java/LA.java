import java.io.BufferedReader;
import java.io.IOException;
import java.io.InputStreamReader;
import java.util.*;

public class LA {
    private static String stanje = "S_pocetno";
    private static int duljinaPodniza;
    private static int redak = 1;
    private static String tip = "";
    private static Map<String, List<Pravilo>> stanja = new HashMap<>();

    public static void main(String[] args) throws IOException {
        BufferedReader reader = new BufferedReader(new InputStreamReader(System.in));

        // inicijaliziranje automata.
        stanje = "S_pocetno";
        List<Pravilo> pravila = null;
        int i;	pravila = new ArrayList<>();
        i = 0;
        pravila.add(new Pravilo("\t|\\_"));
        pravila.get(i).dodajArgument("-");
        i++;
        pravila.add(new Pravilo("\n"));
        pravila.get(i).dodajArgument("-");
        pravila.get(i).dodajArgument("NOVI_REDAK");
        i++;
        pravila.add(new Pravilo("#\\|"));
        pravila.get(i).dodajArgument("-");
        pravila.get(i).dodajArgument("UDJI_U_STANJE S_komentar");
        i++;
        pravila.add(new Pravilo("((0|1|2|3|4|5|6|7|8|9)(0|1|2|3|4|5|6|7|8|9)*|0x((0|1|2|3|4|5|6|7|8|9)|a|b|c|d|e|f|A|B|C|D|E|F)((0|1|2|3|4|5|6|7|8|9)|a|b|c|d|e|f|A|B|C|D|E|F)*)"));
        pravila.get(i).dodajArgument("OPERAND");
        i++;
        pravila.add(new Pravilo("\\("));
        pravila.get(i).dodajArgument("LIJEVA_ZAGRADA");
        i++;
        pravila.add(new Pravilo("\\)"));
        pravila.get(i).dodajArgument("DESNA_ZAGRADA");
        i++;
        pravila.add(new Pravilo("-"));
        pravila.get(i).dodajArgument("OP_MINUS");
        i++;
        pravila.add(new Pravilo("-(\t|\n|\\_)*-"));
        pravila.get(i).dodajArgument("OP_MINUS");
        pravila.get(i).dodajArgument("UDJI_U_STANJE S_unarni");
        pravila.get(i).dodajArgument("VRATI_SE 1");
        i++;
        pravila.add(new Pravilo("\\((\t|\n|\\_)*-"));
        pravila.get(i).dodajArgument("LIJEVA_ZAGRADA");
        pravila.get(i).dodajArgument("UDJI_U_STANJE S_unarni");
        pravila.get(i).dodajArgument("VRATI_SE 1");
        i++;
        stanja.put("S_pocetno", pravila);
        pravila = new ArrayList<>();
        i = 0;
        pravila.add(new Pravilo("\\|#"));
        pravila.get(i).dodajArgument("-");
        pravila.get(i).dodajArgument("UDJI_U_STANJE S_pocetno");
        i++;
        pravila.add(new Pravilo("\\n"));
        pravila.get(i).dodajArgument("-");
        pravila.get(i).dodajArgument("NOVI_REDAK");
        i++;
        pravila.add(new Pravilo("(\\(|\\)|\\|\\|\\||\\*|\\\\|\\$|\\t|\\n|\\_|!|\"|#|%|&|\'|+|,|-|.|/|0|1|2|3|4|5|6|7|8|9|:|;|<|=|>|?|@|A|B|C|D|E|F|G|H|I|J|K|L|M|N|O|P|Q|R|S|T|U|V|W|X|Y|Z|[|]|^|_|`|a|b|c|d|e|f|g|h|i|j|k|l|m|n|o|p|q|r|s|t|u|v|w|x|y|z|~)"));
        pravila.get(i).dodajArgument("-");
        i++;
        stanja.put("S_komentar", pravila);
        pravila = new ArrayList<>();
        i = 0;
        pravila.add(new Pravilo("\\t|\\_"));
        pravila.get(i).dodajArgument("-");
        i++;
        pravila.add(new Pravilo("\\n"));
        pravila.get(i).dodajArgument("-");
        pravila.get(i).dodajArgument("NOVI_REDAK");
        i++;
        pravila.add(new Pravilo("-"));
        pravila.get(i).dodajArgument("UMINUS");
        pravila.get(i).dodajArgument("UDJI_U_STANJE S_pocetno");
        i++;
        pravila.add(new Pravilo("-(\\t|\\n|\\_)*-"));
        pravila.get(i).dodajArgument("UMINUS");
        pravila.get(i).dodajArgument("VRATI_SE 1");
        i++;
        stanja.put("S_unarni", pravila);

        System.err.println("Init gotov");

        StringBuilder source = new StringBuilder();
        String line = reader.readLine();
        while (line != null) {
            source.append(line + "\n");
            line = reader.readLine();
        }

        for (Token token : analiziraj(source.toString().toCharArray())) {
            System.out.println(token);
        }
    }

    private static List<Token> analiziraj(char[] source) {
        List<Token> tokeni = new ArrayList<Token>();
        int trenutniZnak = 0;
        while (trenutniZnak < source.length) {
            duljinaPodniza = 0;
            int indexPravila = 0;
            int i = 0;
            for (Pravilo pravilo : stanja.get(stanje)) {
                int pomDuljina = 0;
                int duljinaPodudaranja = 0;
                Automat automat = pravilo.getAutomat();
                automat.reset();
                for (; trenutniZnak + pomDuljina < source.length; pomDuljina++) {
                    automat.prijediUNovoStanje(source[trenutniZnak+pomDuljina]);
                    if (automat.getSkupStanja().size() == 0) {
                        break;
                    }

                    if (automat.getSkupStanja().contains(automat.brStanja - 1)) {
                        duljinaPodudaranja = pomDuljina + 1;
                    }
                }

                if (duljinaPodudaranja > duljinaPodniza) {
                    duljinaPodniza = duljinaPodudaranja;
                    indexPravila = i;
                }

                i++;
            }

            if (duljinaPodniza == 0) {
                System.err.println("Greška na liniji: " + redak);
                trenutniZnak++;
                continue;
            }

            for (String akcija : stanja.get(stanje).get(indexPravila).getArgumenti()) {
                odradiAkciju(akcija);
            }

            StringBuilder tokenValue = new StringBuilder();
            for (int j = 0; j < duljinaPodniza; j++) {
                tokenValue.append(source[j+trenutniZnak]);
            }

            if (!tip.equals("-")) {
                tokeni.add(new Token(tip, tokenValue.toString(), redak));
            }

            trenutniZnak += duljinaPodniza;
        }

        return tokeni;
    }

    private static void odradiAkciju(String s) {
        if (s.equals("-")) {
            tip = "-";
        } else if (s.toUpperCase().equals("NOVI_REDAK")) {
            redak++;
        } else if (s.toUpperCase().startsWith("UDJI_U_STANJE ")) {
            stanje = s.split("\\s")[1];
        } else if (s.toUpperCase().startsWith("VRATI_SE ")) {
            duljinaPodniza = Integer.parseInt(s.split("\\s")[1]);
        } else {
            tip = s;
        }
    }

    public static class Pravilo {
        private List<String> argumenti = new ArrayList<String>();
        private Automat automat = new Automat();

        public Pravilo(String regex) {
            automat = pretvori(regex.toCharArray());
        }

        public Pravilo(String regex, List<String> argumenti) {
            automat = pretvori(regex.toCharArray());
            this.argumenti = argumenti;
        }

        public Automat getAutomat() {
            return automat;
        }

        private static Automat pretvori(char[] izraz) {
            List<Automat> izbori = new ArrayList<>();
            int brZagrada = 0;
            int negrupirani = 0;
            for (int i = 0, len = izraz.length; i < len; i++) {
                if (izraz[i] == '(' && jeOperator(izraz, i)) {
                    brZagrada++;
                } else if (izraz[i] == ')' && jeOperator(izraz, i)) {
                    brZagrada--;
                } else if (brZagrada == 0 && izraz[i] == '|' && jeOperator(izraz, i)) {
                    izbori.add(pretvori(new String(izraz).substring(negrupirani, i).toCharArray()));
                    negrupirani = i + 1;
                }
            }

            if (!izbori.isEmpty()) {
                izbori.add(pretvori(new String(izraz).substring(negrupirani).toCharArray()));
                return iliOperator(izbori);
            } else {
                Automat rez = new Automat();
                StringBuilder zaKonkatenirati = new StringBuilder();
                boolean prefiksirano = false;
                for (int i = 0; i < izraz.length; i++) {
                    if (prefiksirano) {
                        prefiksirano = false;
                        char prijelazniZnak = izraz[i];
                        if (izraz[i] == 't') {
                            prijelazniZnak = '\t';
                        } else if (izraz[i] == 'n') {
                            prijelazniZnak = '\n';
                        } else if (izraz[i] == '_') {
                            prijelazniZnak = ' ';
                        }
                        zaKonkatenirati.append(prijelazniZnak);

                    } else {
                        if (izraz[i] == '\\') {
                            prefiksirano = true;
                            continue;
                        }

                        if (izraz[i] == '(') {
                            int j = pronadiZatvorenuZagradu(izraz, i) + 1;
                            Automat temp = pretvori(new String(izraz).substring(i + 1, j - 1).toCharArray());
                            rez = nadovezivanje(rez, obican(zaKonkatenirati.toString().toCharArray()));
                            if (j < izraz.length && izraz[j] == '*') {
                                rez = nadovezivanje(rez, kleeneovOperator(temp));
                                i = j;
                            } else {
                                rez = nadovezivanje(rez, temp);
                                i = j - 1;
                            }

                            zaKonkatenirati.setLength(0);
                            continue;

                        } else if (izraz[i] == '$') {
                            rez = nadovezivanje(rez, obican(zaKonkatenirati.toString().toCharArray()));
                            if (i + 1 < izraz.length && izraz[i+1] == '*') {
                                rez = nadovezivanje(rez, kleeneovOperator(epsilon()));
                                i++;
                            } else {
                                rez = nadovezivanje(rez, epsilon());
                            }

                            zaKonkatenirati.setLength(0);
                            continue;
                        }

                        if (i + 1 < izraz.length && izraz[i+1] == '*') {
                            rez = nadovezivanje(rez, obican(zaKonkatenirati.toString().toCharArray()));
                            rez = nadovezivanje(rez, kleeneovOperator(obican(new char[]{izraz[i]})));
                            i++;
                            zaKonkatenirati.setLength(0);
                            continue;
                        }

                        if (izraz[i] == ')') continue;

                        zaKonkatenirati.append(izraz[i]);
                    }
                }
                rez = nadovezivanje(rez, obican(zaKonkatenirati.toString().toCharArray()));

                return rez;
            }

        }

        private static Automat epsilon() {
            Automat a = new Automat();
            a.brStanja = 2;
            a.dodajEpsilonPrijelaz(0, 1);
            a.prihvatljivoStanje = 1;

            return a;
        }

        private static Automat obican(char[] niz) {
            if (niz.length == 0) return new Automat();
            Automat a = new Automat();
            a.brStanja = niz.length + 1;
            for (int i = 0; i < niz.length; i++) {
                a.dodajPrijelaz(i, i + 1, niz[i]);
            }

            a.prihvatljivoStanje = a.brStanja - 1;
            return a;
        }

        private static Automat nadovezivanje(Automat a1, Automat a2) {
            if (a1.brStanja == 0) {
                return  a2;
            }
            if (a2.brStanja == 0) {
                return a1;
            }
            for (Automat.Prijelaz prijelaz : a2.prijelazi) {
                a1.dodajPrijelaz(prijelaz.iz + a1.brStanja - 1, prijelaz.u + a1.brStanja - 1, prijelaz.znak);
            }

            for (Map.Entry<Integer, Set<Integer>> epsilon : a2.epsilonPrijelazi.entrySet()) {
                int iz = epsilon.getKey();
                for (Integer u : epsilon.getValue()) {
                    a1.dodajEpsilonPrijelaz(iz + a1.brStanja - 1, u + a1.brStanja - 1);
                }
            }
            a1.brStanja += a2.brStanja - 1;

            a1.prihvatljivoStanje = a1.brStanja - 1;
            return a1;
        }

        private static Automat iliOperator(List<Automat> automati) {
            Automat novi = new Automat();
            novi.brStanja = 2;
            for (Automat automat : automati) {
                novi.brStanja += automat.brStanja;
            }

            int pom = 1;
            for (Automat automat : automati) {
                novi.dodajEpsilonPrijelaz(0, pom);
                for (Automat.Prijelaz prijelaz : automat.prijelazi) {
                    novi.dodajPrijelaz(prijelaz.iz + pom, prijelaz.u + pom, prijelaz.znak);
                }
                for (Map.Entry<Integer, Set<Integer>> epsilon : automat.epsilonPrijelazi.entrySet()) {
                    for (Integer u : epsilon.getValue()) {
                        novi.dodajEpsilonPrijelaz(epsilon.getKey() + pom, u + pom);
                    }
                }

                pom += automat.brStanja;
                novi.dodajEpsilonPrijelaz(pom - 1, novi.brStanja - 1);
            }

            novi.prihvatljivoStanje = novi.brStanja - 1;
            return novi;
        }

        private static Automat kleeneovOperator(Automat automat) {
            Automat novi = new Automat();
            novi.brStanja = automat.brStanja + 2;
            novi.dodajEpsilonPrijelaz(0, novi.brStanja - 1);
            novi.dodajEpsilonPrijelaz(0, 1);
            novi.dodajEpsilonPrijelaz(novi.brStanja - 2, 1);
            novi.dodajEpsilonPrijelaz(novi.brStanja - 2, novi.brStanja - 1);

            for (Automat.Prijelaz prijelaz : automat.prijelazi) {
                novi.dodajPrijelaz(prijelaz.iz + 1, prijelaz.u + 1, prijelaz.znak);
            }

            for (Map.Entry<Integer, Set<Integer>> epsilon : automat.epsilonPrijelazi.entrySet()) {
                for (Integer u : epsilon.getValue()) {
                    novi.dodajEpsilonPrijelaz(epsilon.getKey() + 1, u + 1);
                }
            }

            novi.prihvatljivoStanje = novi.brStanja - 1;
            return novi;
        }

        private static int pronadiZatvorenuZagradu(char[] izraz, int i) {
            int brZagrada = 1;
            i++;
            while (i < izraz.length) {
                if (i + 1 < izraz.length && izraz[i] == '(' && jeOperator(izraz, i)) {
                    brZagrada++;
                } else if (i + 1 < izraz.length && izraz[i] == ')' && jeOperator(izraz, i)) {
                    brZagrada--;
                    if (brZagrada == 0) {
                        return i;
                    }
                }

                i++;
            }

            return i;
        }

        private static boolean jeOperator(char[] izraz, int i) {
            int br = 0;
            while (i - 1 >= 0 && izraz[i - 1] == '\\') {
                br++;
                i--;
            }

            return br % 2 == 0;
        }

        public void dodajArgument(String argument) {
            argumenti.add(argument);
        }

        public List<String> getArgumenti() {
            return argumenti;
        }
    }

    public static class Token {
        private String tip;
        private String vrijednost;
        private int redak;

        public Token(String tip, String vrijednost, int redak) {
            this.tip = tip;
            this.vrijednost = vrijednost;
            this.redak = redak;
        }

        @Override
        public String toString() {
            return String.format("%s %d %s", tip, redak, vrijednost);
        }
    }

    public static class Automat {
        private int brStanja;
        private int prihvatljivoStanje;
        private List<Prijelaz> prijelazi = new ArrayList<Prijelaz>();
        private Map<Integer, Set<Integer>> epsilonPrijelazi = new HashMap<>();
        private Set<Integer> skupStanja = new TreeSet<>();

        public Set<Integer> getSkupStanja() {
            return skupStanja;
        }

        public Automat() {
            skupStanja.add(0);
        }

        public void prijediUNovoStanje(char znak) {
            generirajEpsilonOkruzenje();

            Set<Integer> novaStanja = new TreeSet<>();
            for (Prijelaz prijelaz : prijelazi) {
                if (skupStanja.contains(prijelaz.getIz()) && prijelaz.getZnak() == znak) {
                    novaStanja.add(prijelaz.getU());
                }
            }

            skupStanja = novaStanja;
            generirajEpsilonOkruzenje();
        }

        public void reset() {
            skupStanja.clear();
            skupStanja.add(0);
        }

        private void generirajEpsilonOkruzenje() {
            boolean imaPromjene = true;
            while (imaPromjene) {
                imaPromjene = false;
                Set<Integer> pom = new TreeSet<>(skupStanja);
                for (Integer stanje : pom) {
                    if (epsilonPrijelazi.containsKey(stanje)) {
                        for (Integer novoStanje : epsilonPrijelazi.get(stanje)) {
                            if (!skupStanja.contains(novoStanje)) {
                                skupStanja.add(novoStanje);
                                imaPromjene = true;
                            }
                        }
                    }
                }
            }
        }

        public void dodajPrijelaz(int iz, int u, char znak) {
            prijelazi.add(new Prijelaz(iz, u, znak));
        }

        public void dodajEpsilonPrijelaz(int iz, int u) {
            if (epsilonPrijelazi.containsKey(iz)) {
                epsilonPrijelazi.get(iz).add(u);
            } else {
                Set<Integer> noviSet = new TreeSet<>();
                noviSet.add(u);
                epsilonPrijelazi.put(iz, noviSet);
            }
        }

        public static class Prijelaz {
            private int iz;
            private int u;
            private char znak;

            public Prijelaz(int iz, int u, char znak) {
                this.iz = iz;
                this.u = u;
                this.znak = znak;
            }

            public char getZnak() {
                return znak;
            }

            public int getIz() {
                return iz;
            }

            public int getU() {
                return u;
            }

            @Override
            public String toString() {
                return String.format("%d, %c -> %d", iz, znak, u);
            }
        }
    }

}
