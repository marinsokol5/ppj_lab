import java.io.BufferedReader;
import java.io.File;
import java.io.IOException;
import java.io.InputStreamReader;
import java.nio.charset.StandardCharsets;
import java.nio.file.Files;
import java.nio.file.StandardOpenOption;
import java.util.*;

public class GLA {
    private static Map<String, String> regDef = new HashMap<String, String>();
    private static Map<String, List<PravilaString>> stanja = new LinkedHashMap<>();
    private static Set<String> tipovi = new HashSet<String>();
    private static String pocetnoStanje;

    public static void main(String[] args) throws IOException {
        BufferedReader reader = new BufferedReader(new InputStreamReader(System.in));

        // regularne definicije
        String line = reader.readLine();
        while (line != null && line.startsWith("{")) {
            dodajRegDef(line);
            line = reader.readLine();
        }

        // stanja leksickog analizatora
        pocetnoStanje = line.split("\\s")[1];
        while (line != null && line.startsWith("%X")) {
            dodajStanje(line);
            line = reader.readLine();
        }

        // tipovi tokena
        while (line != null && line.startsWith("%L")) {
            dodajTip(line);
            line = reader.readLine();
        }

        // pravila leksickog analizatora
        while (line != null) {
            List<String> lines = new ArrayList<String>();
            while (!line.trim().equals("}")) {
                if (!line.trim().equals("{")) {
                    lines.add(line);
                }

                line = reader.readLine();
            }
            dodajPravilo(lines);

            line = reader.readLine();
        }

        File file = new File("./analizator/LA.java");
        file.createNewFile();
        Files.write(file.toPath(), generirajAnalizator().getBytes(StandardCharsets.UTF_8), StandardOpenOption.WRITE);
    }

    private static void dodajRegDef(String line) {
        String[] pom = line.split("\\s+");
        String ime = pom[0].split("\\{|\\}")[1];

        StringBuilder sb = new StringBuilder();
        char[] chars = pom[1].toCharArray();
        for (int i = 0; i < chars.length; i++) {
            if (chars[i] == '{' && jeOperator(chars, i)) {
                i++;
                StringBuilder temp = new StringBuilder();
                while (i < chars.length) {
                    if (chars[i] == '}' && jeOperator(chars, i)) {
                        break;
                    }

                    temp.append(chars[i++]);
                }

                sb.append("(" + regDef.get(temp.toString()) + ")");
            } else {
                sb.append(chars[i]);
            }
        }

        regDef.put(ime, sb.toString());
    }

    private static void dodajStanje(String line) {
        // izbacuje %X_
        line = line.substring(3);
        for (String stanje : line.split("\\s")) {
            stanja.put(stanje, new ArrayList<PravilaString>());
        }
    }

    private static void dodajTip(String line) {
        // izbacuje %L_
        line = line.substring(3);
        for (String tip : line.split("\\s")) {
            tipovi.add(tip);
        }
    }

    private static void dodajPravilo(List<String> lines) {
        String prviRed = lines.get(0);
        int indeks = prviRed.indexOf(">");
        List<PravilaString> pravila = stanja.get(prviRed.substring(1, indeks));

        char[] pom = prviRed.substring(indeks + 1).toCharArray();
        StringBuilder sb = new StringBuilder();
        for (int i = 0; i < pom.length; i++) {
            if (pom[i] == '{' && jeOperator(pom, i)) {
                i++;
                StringBuilder temp = new StringBuilder();
                while (i < pom.length) {
                    if (pom[i] == '}' && jeOperator(pom, i)) {
                        break;
                    }

                    temp.append(pom[i++]);
                }

                sb.append("(" + regDef.get(temp.toString()) + ")");
            } else {
                sb.append(pom[i]);
            }
        }

        String regex = sb.toString();
        PravilaString novo = new PravilaString(regex);
        for (int i = 1, len = lines.size(); i < len; i++) {
            novo.getArgumentiAkcija().add(lines.get(i));
        }

        pravila.add(novo);
    }

    private static boolean jeOperator(char[] izraz, int i) {
        int br = 0;
        while (i - 1 >= 0 && izraz[i - 1] == '\\') {
            br++;
            i--;
        }

        return br % 2 == 0;
    }

    private static String generirajAnalizator() {
        // Prvi dio LA
        StringBuilder sb = new StringBuilder("import java.io.BufferedReader;\n" +
                "import java.io.IOException;\n" +
                "import java.io.InputStreamReader;\n" +
                "import java.util.*;\n" +
                "\n" +
                "public class LA {\n" +
                "    private static String stanje = \"S_pocetno\";\n" +
                "    private static int duljinaPodniza;\n" +
                "    private static int redak = 1;\n" +
                "    private static String tip = \"\";\n" +
                "    private static Map<String, List<Pravilo>> stanja = new HashMap<>();\n" +
                "\n" +
                "    public static void main(String[] args) throws IOException {\n" +
                "        BufferedReader reader = new BufferedReader(new InputStreamReader(System.in));");

        // Generirani kod LA
        sb.append("\n" + "\tstanje = \"" + dodajEscape(pocetnoStanje) + "\";\n");
        sb.append("\tList<Pravilo> pravila = null;\n");
        sb.append("\tint i;");
        for (Map.Entry<String, List<PravilaString>> entry : stanja.entrySet()) {
            sb.append("\tpravila = new ArrayList<>();\n");
            sb.append("\ti = 0;\n");
            for (PravilaString pravilaString : entry.getValue()) {
                sb.append("\tpravila.add(new Pravilo(\"" + dodajEscape(pravilaString.getRegex()) + "\"));\n");
                for (String akcija : pravilaString.getArgumentiAkcija()) {
                    sb.append("\tpravila.get(i).dodajArgument(\"" + dodajEscape(akcija) + "\");\n");
                }
                sb.append("\ti++;\n");
            }

            sb.append("\tstanja.put(\"" + dodajEscape(entry.getKey()) + "\", pravila);\n");
        }

        // Drugi dio LA
        return sb.append("StringBuilder source = new StringBuilder();\n" +
                "        String line = reader.readLine();\n" +
                "        while (line != null) {\n" +
                "            source.append(line + \"\\n\");\n" +
                "            line = reader.readLine();\n" +
                "        }\n" +
                "\n" +
                "        for (Token token : analiziraj(source.toString().toCharArray())) {\n" +
                "            System.out.println(token);\n" +
                "        }\n" +
                "    }\n" +
                "\n" +
                "    private static List<Token> analiziraj(char[] source) {\n" +
                "        List<Token> tokeni = new ArrayList<Token>();\n" +
                "        int trenutniZnak = 0;\n" +
                "        while (trenutniZnak < source.length) {\n" +
                "            duljinaPodniza = 0;\n" +
                "            int indexPravila = 0;\n" +
                "            int i = 0;\n" +
                "            for (Pravilo pravilo : stanja.get(stanje)) {\n" +
                "                int pomDuljina = 0;\n" +
                "                int duljinaPodudaranja = 0;\n" +
                "                Automat automat = pravilo.getAutomat();\n" +
                "                automat.reset();\n" +
                "                for (; trenutniZnak + pomDuljina < source.length; pomDuljina++) {\n" +
                "                    automat.prijediUNovoStanje(source[trenutniZnak+pomDuljina]);\n" +
                "                    if (automat.getSkupStanja().size() == 0) {\n" +
                "                        break;\n" +
                "                    }\n" +
                "\n" +
                "                    if (automat.getSkupStanja().contains(automat.brStanja - 1)) {\n" +
                "                        duljinaPodudaranja = pomDuljina + 1;\n" +
                "                    }\n" +
                "                }\n" +
                "\n" +
                "                if (duljinaPodudaranja > duljinaPodniza) {\n" +
                "                    duljinaPodniza = duljinaPodudaranja;\n" +
                "                    indexPravila = i;\n" +
                "                }\n" +
                "\n" +
                "                i++;\n" +
                "            }\n" +
                "\n" +
                "            if (duljinaPodniza == 0) {\n" +
                "                System.err.println(\"Greska na liniji: \" + redak);\n" +
                "                trenutniZnak++;\n" +
                "                continue;\n" +
                "            }\n" +
                "\n" +
                "            for (String akcija : stanja.get(stanje).get(indexPravila).getArgumenti()) {\n" +
                "                odradiAkciju(akcija);\n" +
                "            }\n" +
                "\n" +
                "            StringBuilder tokenValue = new StringBuilder();\n" +
                "            for (int j = 0; j < duljinaPodniza; j++) {\n" +
                "                tokenValue.append(source[j+trenutniZnak]);\n" +
                "            }\n" +
                "\n" +
                "            if (!tip.equals(\"-\")) {\n" +
                "                tokeni.add(new Token(tip, tokenValue.toString(), redak));\n" +
                "            }\n" +
                "\n" +
                "            trenutniZnak += duljinaPodniza;\n" +
                "        }\n" +
                "\n" +
                "        return tokeni;\n" +
                "    }\n" +
                "\n" +
                "    private static void odradiAkciju(String s) {\n" +
                "        if (s.equals(\"-\")) {\n" +
                "            tip = \"-\";\n" +
                "        } else if (s.toUpperCase().equals(\"NOVI_REDAK\")) {\n" +
                "            redak++;\n" +
                "        } else if (s.toUpperCase().startsWith(\"UDJI_U_STANJE \")) {\n" +
                "            stanje = s.split(\"\\\\s\")[1];\n" +
                "        } else if (s.toUpperCase().startsWith(\"VRATI_SE \")) {\n" +
                "            duljinaPodniza = Integer.parseInt(s.split(\"\\\\s\")[1]);\n" +
                "        } else {\n" +
                "            tip = s;\n" +
                "        }\n" +
                "    }\n" +
                "\n" +
                "    public static class Pravilo {\n" +
                "        private List<String> argumenti = new ArrayList<String>();\n" +
                "        private Automat automat = new Automat();\n" +
                "\n" +
                "        public Pravilo(String regex) {\n" +
                "            automat = pretvori(regex.toCharArray());\n" +
                "        }\n" +
                "\n" +
                "        public Pravilo(String regex, List<String> argumenti) {\n" +
                "            automat = pretvori(regex.toCharArray());\n" +
                "            this.argumenti = argumenti;\n" +
                "        }\n" +
                "\n" +
                "        public Automat getAutomat() {\n" +
                "            return automat;\n" +
                "        }\n" +
                "\n" +
                "        private static Automat pretvori(char[] izraz) {\n" +
                "            List<Automat> izbori = new ArrayList<>();\n" +
                "            int brZagrada = 0;\n" +
                "            int negrupirani = 0;\n" +
                "            for (int i = 0, len = izraz.length; i < len; i++) {\n" +
                "                if (izraz[i] == '(' && jeOperator(izraz, i)) {\n" +
                "                    brZagrada++;\n" +
                "                } else if (izraz[i] == ')' && jeOperator(izraz, i)) {\n" +
                "                    brZagrada--;\n" +
                "                } else if (brZagrada == 0 && izraz[i] == '|' && jeOperator(izraz, i)) {\n" +
                "                    izbori.add(pretvori(new String(izraz).substring(negrupirani, i).toCharArray()));\n" +
                "                    negrupirani = i + 1;\n" +
                "                }\n" +
                "            }\n" +
                "\n" +
                "            if (!izbori.isEmpty()) {\n" +
                "                izbori.add(pretvori(new String(izraz).substring(negrupirani).toCharArray()));\n" +
                "                return iliOperator(izbori);\n" +
                "            } else {\n" +
                "                Automat rez = new Automat();\n" +
                "                StringBuilder zaKonkatenirati = new StringBuilder();\n" +
                "                boolean prefiksirano = false;\n" +
                "                for (int i = 0; i < izraz.length; i++) {\n" +
                "                    if (prefiksirano) {\n" +
                "                        prefiksirano = false;\n" +
                "                        char prijelazniZnak = izraz[i];\n" +
                "                        if (izraz[i] == 't') {\n" +
                "                            prijelazniZnak = '\\t';\n" +
                "                        } else if (izraz[i] == 'n') {\n" +
                "                            prijelazniZnak = '\\n';\n" +
                "                        } else if (izraz[i] == '_') {\n" +
                "                            prijelazniZnak = ' ';\n" +
                "                        }\n" +
                "                        zaKonkatenirati.append(prijelazniZnak);\n" +
                "\n" +
                "                    } else {\n" +
                "                        if (izraz[i] == '\\\\') {\n" +
                "                            prefiksirano = true;\n" +
                "                            continue;\n" +
                "                        }\n" +
                "\n" +
                "                        if (izraz[i] == '(') {\n" +
                "                            int j = pronadiZatvorenuZagradu(izraz, i) + 1;\n" +
                "                            Automat temp = pretvori(new String(izraz).substring(i + 1, j - 1).toCharArray());\n" +
                "                            rez = nadovezivanje(rez, obican(zaKonkatenirati.toString().toCharArray()));\n" +
                "                            if (j < izraz.length && izraz[j] == '*') {\n" +
                "                                rez = nadovezivanje(rez, kleeneovOperator(temp));\n" +
                "                                i = j;\n" +
                "                            } else {\n" +
                "                                rez = nadovezivanje(rez, temp);\n" +
                "                                i = j - 1;\n" +
                "                            }\n" +
                "\n" +
                "                            zaKonkatenirati.setLength(0);\n" +
                "                            continue;\n" +
                "\n" +
                "                        } else if (izraz[i] == '$') {\n" +
                "                            rez = nadovezivanje(rez, obican(zaKonkatenirati.toString().toCharArray()));\n" +
                "                            if (i + 1 < izraz.length && izraz[i+1] == '*') {\n" +
                "                                rez = nadovezivanje(rez, kleeneovOperator(epsilon()));\n" +
                "                                i++;\n" +
                "                            } else {\n" +
                "                                rez = nadovezivanje(rez, epsilon());\n" +
                "                            }\n" +
                "\n" +
                "                            zaKonkatenirati.setLength(0);\n" +
                "                            continue;\n" +
                "                        }\n" +
                "\n" +
                "                        if (i + 1 < izraz.length && izraz[i+1] == '*') {\n" +
                "                            rez = nadovezivanje(rez, obican(zaKonkatenirati.toString().toCharArray()));\n" +
                "                            rez = nadovezivanje(rez, kleeneovOperator(obican(new char[]{izraz[i]})));\n" +
                "                            i++;\n" +
                "                            zaKonkatenirati.setLength(0);\n" +
                "                            continue;\n" +
                "                        }\n" +
                "\n" +
                "                        if (izraz[i] == ')') continue;\n" +
                "\n" +
                "                        zaKonkatenirati.append(izraz[i]);\n" +
                "                    }\n" +
                "                }\n" +
                "                rez = nadovezivanje(rez, obican(zaKonkatenirati.toString().toCharArray()));\n" +
                "\n" +
                "                return rez;\n" +
                "            }\n" +
                "\n" +
                "        }\n" +
                "\n" +
                "        private static Automat epsilon() {\n" +
                "            Automat a = new Automat();\n" +
                "            a.brStanja = 2;\n" +
                "            a.dodajEpsilonPrijelaz(0, 1);\n" +
                "            a.prihvatljivoStanje = 1;\n" +
                "\n" +
                "            return a;\n" +
                "        }\n" +
                "\n" +
                "        private static Automat obican(char[] niz) {\n" +
                "            if (niz.length == 0) return new Automat();\n" +
                "            Automat a = new Automat();\n" +
                "            a.brStanja = niz.length + 1;\n" +
                "            for (int i = 0; i < niz.length; i++) {\n" +
                "                a.dodajPrijelaz(i, i + 1, niz[i]);\n" +
                "            }\n" +
                "\n" +
                "            a.prihvatljivoStanje = a.brStanja - 1;\n" +
                "            return a;\n" +
                "        }\n" +
                "\n" +
                "        private static Automat nadovezivanje(Automat a1, Automat a2) {\n" +
                "            if (a1.brStanja == 0) {\n" +
                "                return  a2;\n" +
                "            }\n" +
                "            if (a2.brStanja == 0) {\n" +
                "                return a1;\n" +
                "            }\n" +
                "            for (Automat.Prijelaz prijelaz : a2.prijelazi) {\n" +
                "                a1.dodajPrijelaz(prijelaz.iz + a1.brStanja - 1, prijelaz.u + a1.brStanja - 1, prijelaz.znak);\n" +
                "            }\n" +
                "\n" +
                "            for (Map.Entry<Integer, Set<Integer>> epsilon : a2.epsilonPrijelazi.entrySet()) {\n" +
                "                int iz = epsilon.getKey();\n" +
                "                for (Integer u : epsilon.getValue()) {\n" +
                "                    a1.dodajEpsilonPrijelaz(iz + a1.brStanja - 1, u + a1.brStanja - 1);\n" +
                "                }\n" +
                "            }\n" +
                "            a1.brStanja += a2.brStanja - 1;\n" +
                "\n" +
                "            a1.prihvatljivoStanje = a1.brStanja - 1;\n" +
                "            return a1;\n" +
                "        }\n" +
                "\n" +
                "        private static Automat iliOperator(List<Automat> automati) {\n" +
                "            Automat novi = new Automat();\n" +
                "            novi.brStanja = 2;\n" +
                "            for (Automat automat : automati) {\n" +
                "                novi.brStanja += automat.brStanja;\n" +
                "            }\n" +
                "\n" +
                "            int pom = 1;\n" +
                "            for (Automat automat : automati) {\n" +
                "                novi.dodajEpsilonPrijelaz(0, pom);\n" +
                "                for (Automat.Prijelaz prijelaz : automat.prijelazi) {\n" +
                "                    novi.dodajPrijelaz(prijelaz.iz + pom, prijelaz.u + pom, prijelaz.znak);\n" +
                "                }\n" +
                "                for (Map.Entry<Integer, Set<Integer>> epsilon : automat.epsilonPrijelazi.entrySet()) {\n" +
                "                    for (Integer u : epsilon.getValue()) {\n" +
                "                        novi.dodajEpsilonPrijelaz(epsilon.getKey() + pom, u + pom);\n" +
                "                    }\n" +
                "                }\n" +
                "\n" +
                "                pom += automat.brStanja;\n" +
                "                novi.dodajEpsilonPrijelaz(pom - 1, novi.brStanja - 1);\n" +
                "            }\n" +
                "\n" +
                "            novi.prihvatljivoStanje = novi.brStanja - 1;\n" +
                "            return novi;\n" +
                "        }\n" +
                "\n" +
                "        private static Automat kleeneovOperator(Automat automat) {\n" +
                "            Automat novi = new Automat();\n" +
                "            novi.brStanja = automat.brStanja + 2;\n" +
                "            novi.dodajEpsilonPrijelaz(0, novi.brStanja - 1);\n" +
                "            novi.dodajEpsilonPrijelaz(0, 1);\n" +
                "            novi.dodajEpsilonPrijelaz(novi.brStanja - 2, 1);\n" +
                "            novi.dodajEpsilonPrijelaz(novi.brStanja - 2, novi.brStanja - 1);\n" +
                "\n" +
                "            for (Automat.Prijelaz prijelaz : automat.prijelazi) {\n" +
                "                novi.dodajPrijelaz(prijelaz.iz + 1, prijelaz.u + 1, prijelaz.znak);\n" +
                "            }\n" +
                "\n" +
                "            for (Map.Entry<Integer, Set<Integer>> epsilon : automat.epsilonPrijelazi.entrySet()) {\n" +
                "                for (Integer u : epsilon.getValue()) {\n" +
                "                    novi.dodajEpsilonPrijelaz(epsilon.getKey() + 1, u + 1);\n" +
                "                }\n" +
                "            }\n" +
                "\n" +
                "            novi.prihvatljivoStanje = novi.brStanja - 1;\n" +
                "            return novi;\n" +
                "        }\n" +
                "\n" +
                "        private static int pronadiZatvorenuZagradu(char[] izraz, int i) {\n" +
                "            int brZagrada = 1;\n" +
                "            i++;\n" +
                "            while (i < izraz.length) {\n" +
                "                if (i + 1 < izraz.length && izraz[i] == '(' && jeOperator(izraz, i)) {\n" +
                "                    brZagrada++;\n" +
                "                } else if (i + 1 < izraz.length && izraz[i] == ')' && jeOperator(izraz, i)) {\n" +
                "                    brZagrada--;\n" +
                "                    if (brZagrada == 0) {\n" +
                "                        return i;\n" +
                "                    }\n" +
                "                }\n" +
                "\n" +
                "                i++;\n" +
                "            }\n" +
                "\n" +
                "            return i;\n" +
                "        }\n" +
                "\n" +
                "        private static boolean jeOperator(char[] izraz, int i) {\n" +
                "            int br = 0;\n" +
                "            while (i - 1 >= 0 && izraz[i - 1] == '\\\\') {\n" +
                "                br++;\n" +
                "                i--;\n" +
                "            }\n" +
                "\n" +
                "            return br % 2 == 0;\n" +
                "        }\n" +
                "\n" +
                "        public void dodajArgument(String argument) {\n" +
                "            argumenti.add(argument);\n" +
                "        }\n" +
                "\n" +
                "        public List<String> getArgumenti() {\n" +
                "            return argumenti;\n" +
                "        }\n" +
                "    }\n" +
                "\n" +
                "    public static class Token {\n" +
                "        private String tip;\n" +
                "        private String vrijednost;\n" +
                "        private int redak;\n" +
                "\n" +
                "        public Token(String tip, String vrijednost, int redak) {\n" +
                "            this.tip = tip;\n" +
                "            this.vrijednost = vrijednost;\n" +
                "            this.redak = redak;\n" +
                "        }\n" +
                "\n" +
                "        @Override\n" +
                "        public String toString() {\n" +
                "            return String.format(\"%s %d %s\", tip, redak, vrijednost);\n" +
                "        }\n" +
                "    }\n" +
                "\n" +
                "    public static class Automat {\n" +
                "        private int brStanja;\n" +
                "        private int prihvatljivoStanje;\n" +
                "        private List<Prijelaz> prijelazi = new ArrayList<Prijelaz>();\n" +
                "        private Map<Integer, Set<Integer>> epsilonPrijelazi = new HashMap<>();\n" +
                "        private Set<Integer> skupStanja = new TreeSet<>();\n" +
                "\n" +
                "        public Set<Integer> getSkupStanja() {\n" +
                "            return skupStanja;\n" +
                "        }\n" +
                "\n" +
                "        public Automat() {\n" +
                "            skupStanja.add(0);\n" +
                "        }\n" +
                "\n" +
                "        public void prijediUNovoStanje(char znak) {\n" +
                "            generirajEpsilonOkruzenje();\n" +
                "\n" +
                "            Set<Integer> novaStanja = new TreeSet<>();\n" +
                "            for (Prijelaz prijelaz : prijelazi) {\n" +
                "                if (skupStanja.contains(prijelaz.getIz()) && prijelaz.getZnak() == znak) {\n" +
                "                    novaStanja.add(prijelaz.getU());\n" +
                "                }\n" +
                "            }\n" +
                "\n" +
                "            skupStanja = novaStanja;\n" +
                "            generirajEpsilonOkruzenje();\n" +
                "        }\n" +
                "\n" +
                "        public void reset() {\n" +
                "            skupStanja.clear();\n" +
                "            skupStanja.add(0);\n" +
                "        }\n" +
                "\n" +
                "        private void generirajEpsilonOkruzenje() {\n" +
                "            boolean imaPromjene = true;\n" +
                "            while (imaPromjene) {\n" +
                "                imaPromjene = false;\n" +
                "                Set<Integer> pom = new TreeSet<>(skupStanja);\n" +
                "                for (Integer stanje : pom) {\n" +
                "                    if (epsilonPrijelazi.containsKey(stanje)) {\n" +
                "                        for (Integer novoStanje : epsilonPrijelazi.get(stanje)) {\n" +
                "                            if (!skupStanja.contains(novoStanje)) {\n" +
                "                                skupStanja.add(novoStanje);\n" +
                "                                imaPromjene = true;\n" +
                "                            }\n" +
                "                        }\n" +
                "                    }\n" +
                "                }\n" +
                "            }\n" +
                "        }\n" +
                "\n" +
                "        public void dodajPrijelaz(int iz, int u, char znak) {\n" +
                "            prijelazi.add(new Prijelaz(iz, u, znak));\n" +
                "        }\n" +
                "\n" +
                "        public void dodajEpsilonPrijelaz(int iz, int u) {\n" +
                "            if (epsilonPrijelazi.containsKey(iz)) {\n" +
                "                epsilonPrijelazi.get(iz).add(u);\n" +
                "            } else {\n" +
                "                Set<Integer> noviSet = new TreeSet<>();\n" +
                "                noviSet.add(u);\n" +
                "                epsilonPrijelazi.put(iz, noviSet);\n" +
                "            }\n" +
                "        }\n" +
                "\n" +
                "        public static class Prijelaz {\n" +
                "            private int iz;\n" +
                "            private int u;\n" +
                "            private char znak;\n" +
                "\n" +
                "            public Prijelaz(int iz, int u, char znak) {\n" +
                "                this.iz = iz;\n" +
                "                this.u = u;\n" +
                "                this.znak = znak;\n" +
                "            }\n" +
                "\n" +
                "            public char getZnak() {\n" +
                "                return znak;\n" +
                "            }\n" +
                "\n" +
                "            public int getIz() {\n" +
                "                return iz;\n" +
                "            }\n" +
                "\n" +
                "            public int getU() {\n" +
                "                return u;\n" +
                "            }\n" +
                "\n" +
                "            @Override\n" +
                "            public String toString() {\n" +
                "                return String.format(\"%d, %c -> %d\", iz, znak, u);\n" +
                "            }\n" +
                "        }\n" +
                "    }\n" +
                "\n" +
                "}").toString();
    }

    private static String dodajEscape(String s) {
        StringBuilder sb = new StringBuilder();

        for (char c : s.toCharArray()) {
            if (c == '\\' || c == '\"' || c == '\'') {
                sb.append('\\');
            }

            sb.append(c);
        }

        return sb.toString();
    }

    public static class PravilaString {
        private String regex;
        private List<String> argumentiAkcija = new ArrayList<>();

        public PravilaString(String regex) {
            this.regex = regex;
        }

        public String getRegex() {
            return regex;
        }

        public List<String> getArgumentiAkcija() {
            return argumentiAkcija;
        }
    }

}
