import fileinput
import os
import sys
from collections import defaultdict
import pickle
import time

import lab2_python.source.Util as util


def main():
    start_time = time.time()
    productions = defaultdict(list)
    dir_path = os.path.dirname(os.path.realpath(__file__))
    file = sys.argv[2]
    sys.argv.remove(file)

    # parsing the .san file
    for line in fileinput.input():
        line = line.rstrip()
        if line.startswith('%V'):
            #  non_ending_signs
            non_ending_signs = line[3:].split(' ')
        elif line.startswith('%T'):
            #  ending signs
            ending_signs = line[3:].split(' ')
        elif line.startswith('%Syn'):
            synchronizing_signs = set(line[len('%Syn '):].split(' '))
        elif line.startswith('<'):
            state = line
        elif line.startswith(" "):
            line = line.strip()
            productions[state].append(line)

    # adding the totally useless starting state
    state = '<%>'
    productions[state].append(non_ending_signs[0])
    non_ending_signs.append(state)

    # famous venture for 'ZAPOCINJE' table
    # prazni nezavrsni znakovi
    empty_non_ending_signs = util.get_empty_non_ending_signs(productions)
    # zapocinjeIzravnoZnakom
    direct_signs = util.get_direct_signs(productions, empty_non_ending_signs)
    # zapocinjeZnakom
    start_signs = util.get_starting_signs(direct_signs)

    # adding ending signs
    # connecting them to themselves (again useless)
    for sign in ending_signs:
        start_signs[sign] = {sign}

    # start for ending sings - samo s kojim nezavrsnim znakovim je zapocinje skup
    start_signs_ending = {k: {ending for ending in v if ending in ending_signs} for k, v in start_signs.items()}

    # stavke
    lr_productions = util.get_lr_productions(productions)

    epsilon_nka = util.create_epsilon_automate(lr_productions, '<%>', start_signs_ending, empty_non_ending_signs)
    print(len(epsilon_nka.states), len(epsilon_nka.transitions), len(epsilon_nka.epsilon_transitions))
    dka = util.epsilon_nka_to_dka(epsilon_nka)

    # sign for end of input
    ending_signs.insert(0, "#")

    lr_table = util.create_lr_table(
        dka=dka,
        ending_signs=ending_signs,
        non_ending_signs=non_ending_signs,
    )
    #epsilon_nka.fill_extra_info()
    #dka.fill_extra_info()

    lr_table_krastavac_file = os.path.join(dir_path, "lr_table.pkl")
    with open(lr_table_krastavac_file, 'wb') as handle:
        pickle.dump(lr_table, handle, protocol=pickle.HIGHEST_PROTOCOL)

    code = '\n'.join([
        'import fileinput',
        'import lab2_python.source.Util as util',
        'import pickle',
        'fileinput_gen = fileinput.input()',
        "with open('{lr_table_krastavac_file}', 'rb') as handle:".format(**locals()),
        '    lr_table = pickle.load(handle)',
        "util.lr_parse(lr_table=lr_table, fileinput_gen=fileinput_gen, file='{file}', synchornizing_sings={synchronizing_signs})".format(**locals())
    ])

    folder_path = os.path.join(dir_path, 'analizator')
    file_path = os.path.join(folder_path, 'SA.py')
    if not os.path.exists(folder_path):
        os.makedirs(folder_path)

    file = open(file_path, 'w+')
    file.write(code)

    end_time = time.time()
    print(end_time-start_time)

if __name__ == '__main__':
    main()
