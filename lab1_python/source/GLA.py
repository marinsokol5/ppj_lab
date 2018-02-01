import fileinput
from collections import defaultdict
from lab1_python.source.Util import Automate, Transition, Rule
import lab1_python.source.analizator.AnalizatorBackBone as abb
import os
import sys

def main():
    regular_definitions = {}
    rules_for_state = defaultdict(list)
    code_rules_for_state = []
    dir_path = os.path.dirname(os.path.realpath(__file__))
    file = sys.argv[2]
    sys.argv.remove(file)
    for line in fileinput.input():
        line = line.strip()
        if len(line) > 1 and line.startswith("{"):
            #  regular definitions
            reg_name, reg_exp = line.split(' ')
            for name, exp in regular_definitions.items():
                reg_exp = reg_exp.replace(name, '({exp})'.format(**locals()))
            regular_definitions[reg_name] = reg_exp
        elif line.startswith('%X'):
            #  states for lexical analyzer
            states = line[3:].split(' ')
        elif line.startswith('%L'):
            #  uniform signs
            uniform_signs = set(line[3:].split(' '))
        elif line.startswith('<'):
            #  rules for lexical analysis
            state = line[1:line.index('>')]
            regex = line[line.index('>') + 1:]
            udji_u_stanje = None
            novi_redak = False
            vrati_se = None
            uniform_sign = None
            for name, exp in regular_definitions.items():
                regex = regex.replace(name, '({exp})'.format(**locals()))
        elif line.startswith('{') and len(line) == 1:
            continue
        elif line.startswith('UDJI_U_STANJE'):
            udji_u_stanje = line[len('UDJI_U_STANJE '):]
        elif line.startswith('NOVI_REDAK'):
            novi_redak = True
        elif line.startswith('VRATI_SE'):
            vrati_se = int(line[len('VRATI_SE ')])
        elif line.startswith('}') and len(line) == 1:
            regex2 = "\\t|\\_"
            rule = Rule(
                regex=regex,
                uniform_sign=uniform_sign,
                udji_u_stanje=udji_u_stanje,
                novi_redak=novi_redak,
                vrati_se=vrati_se,
            )
            rules_for_state[state].append(rule)
            regex = regex.replace('\\', '\\\\')
            regex = regex.replace("'", "\\'")
            code_udji_u_stanje = None if udji_u_stanje is None else "'{udji_u_stanje}'".format(**locals())
            code_rules_for_state.append(
                "rules_for_state['{state}'].append(Rule(regex='{regex}',"
                "uniform_sign='{uniform_sign}',udji_u_stanje={code_udji_u_stanje},"
                "novi_redak={novi_redak},vrati_se={vrati_se},))".format(**locals())
            )

        else:
            uniform_sign = line
            if uniform_sign != '-':
                uniform_signs.add(uniform_sign)

    pom = '\n'.join(code_rules_for_state)
    code = '\n'.join([
        'import fileinput',
        'import lab1_python.source.analizator.AnalizatorBackBone as abb',
        'from collections import defaultdict',
        'from lab1_python.source.Util import Automate, Transition, Rule',
        'fileinput_gen = fileinput.input()',
        'rules_for_state = defaultdict(list)',
        '{pom}'.format(**locals()),
        "abb.parse_text(start_state='{states[0]}',"
        "rules_for_state=rules_for_state,fileinput_gen=fileinput_gen,file='{file}')".format(**locals()),
    ])

    folder_path = os.path.join(dir_path, 'analizator')
    file_path = os.path.join(folder_path, 'LA.py')
    if not os.path.exists(folder_path):
        os.makedirs(folder_path)

    file = open(file_path, 'w+')
    file.write(code)


if __name__ == '__main__':
    main()
