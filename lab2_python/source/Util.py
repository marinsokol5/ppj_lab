from collections import defaultdict, OrderedDict
from operator import or_
from functools import reduce
import sys


class LRStavka:
    def __init__(self, left_side: str, right_side: list, index: int):
        self.left_side = left_side
        self.right_side = right_side
        self.transitions = set()
        self.index = index

    def the_same(self):
        return LRStavka(self.left_side, self.right_side.copy(), self.index)

    def get_next(self):
        return LRStavka(self.left_side, self.right_side.copy(), self.index + 1)

    def potpuna(self):
        if len(self.right_side) == 1 and (self.right_side[0] == ' ' or self.right_side[0] == '$'):
            return True
        return self.index == len(self.right_side)

    def get_next_sign(self):
        return self.right_side[self.index]

    def tocka_na_pocetku(self):
        return self.index == 0

    def get_next_next_sign(self):
        return self.right_side[self.index + 1]

    def __eq__(self, other):
        """Overrides the default implementation"""
        if isinstance(self, other.__class__):
            return self.__dict__ == other.__dict__
        return False

    def __hash__(self) -> int:
        return hash((self.left_side, self.index))

    def __repr__(self):
        pom = " ".join(self.right_side)
        pom2 = ",".join(self.transitions)
        return "{self.left_side} -> {pom},index: {self.index},  [{self.transitions}]".format(**locals())
        # return "{self.left_side}".format(**locals())


class Automate:
    def __init__(self, start_state, states=[], transitions=[], extra=[]):
        self.number_of_states = len(states)
        self.start_state = start_state
        self.acceptable_state = states
        self.states = states
        self.epsilon_transitions = []
        self.transitions = transitions
        self.extra = extra
        self.epsilon_states = dict()

    def add_epsilon_transition(self, left_state, right_state):
        # print('epsilon', left_state, ' prema ', right_state)
        self.epsilon_transitions.append(Transition(
            left_state=left_state,
            right_state=right_state,
            transition_sign='$'
        ))

    def fill_extra_info(self):
        self.extra_info = defaultdict(list)
        for trans in self.transitions:
            self.extra_info[trans.left_state].append("{trans.transition_sign}, {trans.right_state}".format(**locals()))
        for trans in self.epsilon_transitions:
            self.extra_info[trans.left_state].append("{trans.transition_sign}, {trans.right_state}".format(**locals()))

    def add_transition(self, left_state, right_state, transition_char):
        # print('neepsilon', transition_char, '   ', left_state, ' prema ', right_state)
        self.transitions.append(Transition(
            left_state=left_state,
            right_state=right_state,
            transition_sign=transition_char
        ))

    def find_epsilon_surrounding_v3(self, state):
        if state in self.epsilon_states:
            return self.epsilon_states[state]

        pom = {state}
        self.find_epsilon_surroundings(pom)
        self.epsilon_states[state] = pom
        return pom

    def find_epsilon_surroundings_v3(self, states):
        pom = set()
        for state in states:
            pom.update(self.find_epsilon_surrounding_v3(state))
        return pom

    def set_epsilon_states(self):
        self.epsilon_states = defaultdict(list)
        l = len(self.states)
        for i, state in enumerate(self.states):
            print("{i}/{l}".format(**locals()))
            pom = {state}
            self.find_epsilon_surroundings(pom)
            self.epsilon_states[state] = pom

    def find_epsilon_surroundings_v2(self, states):
        if not self.epsilon_states:
            self.set_epsilon_states()
        pom = set()
        for state in states:
            pom.update(self.epsilon_states[state])
        return pom

    def find_epsilon_surroundings(self, states):
        while True:
            length = len(states)
            for eps in self.epsilon_transitions:
                if eps.left_state in states:
                    states.add(eps.right_state)
            if length == len(states):
                break

class Transition:
    def __init__(self, left_state, right_state, transition_sign):
        self.left_state = left_state
        self.right_state = right_state
        self.transition_sign = transition_sign

    def __repr__(self):
        return "{self.left_state} prelazi s {self.transition_sign} u {self.right_state}".format(**locals())


def get_empty_non_ending_signs(productions_for_sign: dict):
    empty = set()
    while True:
        pom_empty = set()
        for sign, productions in productions_for_sign.items():
            for production in productions:
                if production == '$' or all([sign in empty for sign in production.split(' ')]):
                    if sign not in empty:
                        pom_empty.add(sign)
                    break
        if len(pom_empty) == 0:
            return empty
        empty.update(pom_empty)


def get_direct_signs(productions_for_sign: dict, empty: set):
    direct = defaultdict(set)
    for sign, productions in productions_for_sign.items():
        for production in productions:
            if production == '$':
                continue

            array = production.split(' ')
            for s in array:
                direct[sign].add(s)
                if s not in empty:
                    break
    return direct


def get_starting_signs(dict_of_direct_signs: defaultdict):
    size = 0
    pom_dict = dict_of_direct_signs.copy()
    while True:
        pom = {
            sign: reduce(or_, [direct_signs] + [pom_dict[pom] for pom in direct_signs if
                                                pom in pom_dict])
            for sign, direct_signs in pom_dict.items()
        }
        pom_size = sum([len(values) for values in pom.values()])
        if pom_size == size:
            break
        size = pom_size
        pom_dict = pom
    return pom


def get_lr_productions(productions_dict: defaultdict):
    result = defaultdict(list)
    for left_side, productions in productions_dict.items():
        for production in productions:
            if production == '$':
                result[left_side].append(LRStavka(
                    left_side=left_side,
                    right_side=[],
                    index=0,
                ))
            else:
                list_of_production_signs = production.split(" ")
                for i in range(len(list_of_production_signs) + 1):
                    result[left_side].append(LRStavka(
                        left_side=left_side,
                        right_side=production.split(" "),
                        index=i,
                    ))
    return result


def create_epsilon_automate(lr_productions_dict: dict, fake_start_state, zapocinje, empty_signs):
    start, end = lr_productions_dict[fake_start_state]
    start = start.the_same()
    start.transitions.add('#')
    automate = Automate(
        start_state=start
    )
    automate.states.append(start)
    not_processed_productions = [automate.start_state]
    processed = []

    while len(not_processed_productions):
        lr_stavka = not_processed_productions.pop(0)
        processed.append(lr_stavka)
        if not lr_stavka.potpuna():
            # find the sign after a *
            sign = lr_stavka.get_next_sign()

            # when that sign from above comes production, next production in list
            lr_stavka_next = lr_stavka.get_next()
            lr_stavka_next.transitions.update(lr_stavka.transitions)

            # tbd
            if lr_stavka_next not in automate.states:
                automate.states.append(lr_stavka_next)
            automate.add_transition(lr_stavka, lr_stavka_next, sign)

            if lr_stavka_next not in processed and lr_stavka_next not in not_processed_productions:
                not_processed_productions.append(lr_stavka_next)

            # epsilon productions
            for lr_stavka_pom in lr_productions_dict[sign]:
                if lr_stavka_pom.tocka_na_pocetku():
                    lr_stavka_pom = lr_stavka_pom.the_same()
                    # generates empty niz
                    if lr_stavka.index + 1 >= len(lr_stavka.right_side):
                        lr_stavka_pom.transitions.update(lr_stavka.transitions)

                    # there is a sign and it has something in zapocinje skup
                    else:
                        sign_after = lr_stavka.get_next_next_sign()
                        lr_stavka_pom.transitions.update(zapocinje[sign_after])
                        if sign_after in empty_signs:
                            lr_stavka_pom.transitions.update(lr_stavka.transitions)
                    if lr_stavka_pom not in automate.states:
                        automate.states.append(lr_stavka_pom)
                    automate.add_epsilon_transition(lr_stavka, lr_stavka_pom)

                    if lr_stavka_pom not in processed and lr_stavka_pom not in not_processed_productions:
                        not_processed_productions.append(lr_stavka_pom)
    return automate


def put_arrow_in_between(begin, end):
    return begin + ' -> ' + end


def lr_productions_from_dict(dict_of_lr_productions):
    result = []
    for sign, lr_stavke in dict_of_lr_productions.items():
        for stavka in lr_stavke:
            result.append(stavka)
    return result


def list_of_sets_contains_object(state: str, dka_states: list):
    for setOfObjects in dka_states:
        if state in setOfObjects:
            return True
    return False


def find_where_given_states_lead_to(this_states: set, epsilon_nka: Automate):
    result = defaultdict(set)
    for transition in epsilon_nka.transitions:
        if transition.left_state in this_states:
            state = transition.right_state
            result[transition.transition_sign].add(state)
    return result


def find_dka_states(epsilon_nka: Automate):
    dka_states = []
    dka_transitions = []

    start = {epsilon_nka.start_state}
    start = epsilon_nka.find_epsilon_surroundings_v3(start)
    e_nka_states = [start]
    dka_states.append(start)
    while len(e_nka_states):
        this_states = e_nka_states[0]
        pom = find_where_given_states_lead_to(this_states, epsilon_nka)
        for key, values in pom.items():
            values = epsilon_nka.find_epsilon_surroundings_v3(values)
            if values not in dka_states:
                dka_states.append(values)
                e_nka_states.append(values)
            trans = Transition(dka_states.index(this_states), dka_states.index(values), key)
            dka_transitions.append(trans)
        e_nka_states.pop(0)

    return dka_states, dka_transitions


def find_index_in_list_of_sets(state: str, dka_states: list):
    result = []
    for i, e_states in enumerate(dka_states):
        if state in e_states:
            result.append(i)
    return result


def find_dka_transitions(epsilon_nka: Automate, dka_states: list):
    transitions = []
    for transition in epsilon_nka.transitions:
        left_indexes = find_index_in_list_of_sets(transition.left_state, dka_states)
        right_indexes = find_index_in_list_of_sets(transition.right_state, dka_states)
        for left in left_indexes:
            for right in right_indexes:
                transitions.append(Transition(left, right, transition.transition_sign))
    return transitions


def get_indexes_of_list(dka_states: list):
    result = set()
    for i, value in enumerate(dka_states):
        result.add(i)
    return result


def epsilon_nka_to_dka(epsilon_nka: Automate):
    dka_states, dka_transitions = find_dka_states(epsilon_nka)
    # dka_transitions = find_dka_transitions(epsilon_nka, dka_states)
    return Automate(
        states=[i for i, _ in enumerate(dka_states)],
        start_state='0',
        transitions=dka_transitions,
        extra=dka_states,
    )


def find_action_for_ending(dka_state: int, ending_sign: str, dka: Automate, artifical_start_sign="<%>", stack_sign="#"):
    # if pomakni
    for transition in dka.transitions:
        if transition.left_state == dka_state and transition.transition_sign == ending_sign:
            state = transition.right_state
            return "Pomakni {state}".format(**locals())

    # if reduciraj
    stavke = dka.extra[dka_state]
    # mislim da se ovo radi samo kada je jedna stavka u dka stanjima , might be utter bull though
    for stavka in stavke:
        if stavka.potpuna() and not stavka.left_side == artifical_start_sign:
            if ending_sign in stavka.transitions:
                if len(stavka.right_side) == 0:
                    stavka.right_side.append('$')
                stavka_with_arrow = put_arrow_in_between(stavka.left_side, " ".join(stavka.right_side))
                return "Reduciraj {stavka_with_arrow}".format(**locals())

    if ending_sign == stack_sign:
        for stavka in stavke:
            if stavka.left_side.startswith(artifical_start_sign):
                return "Prihvati"

    return "-"


def find_action_for_non_ending(dka_state, non_ending_sign, dka):
    for transition in dka.transitions:
        if transition.left_state == dka_state and transition.transition_sign == non_ending_sign:
            state = transition.right_state
            return "Stavi {state}".format(**locals())
    return "-"


def create_lr_table(dka: Automate, ending_signs: set, non_ending_signs: list):
    result = OrderedDict()
    for state in dka.states:
        result[state] = OrderedDict()
        for ending_sign in ending_signs:
            result[state][ending_sign] = find_action_for_ending(
                dka_state=state,
                ending_sign=ending_sign,
                dka=dka
            )
        for non_ending_sign in non_ending_signs:
            result[state][non_ending_sign] = find_action_for_non_ending(
                dka_state=state,
                non_ending_sign=non_ending_sign,
                dka=dka
            )
    return result


class Node:
    def __init__(self, value: str, non_ending_sign=True):
        self.value = value
        self.sign = value.split(" ")[0]
        self.children = []
        self.is_non_ending_sign = non_ending_sign

    def add_node(self, node):
        self.children.append(node)

    def __str__(self, level=0):
        ret = " " * level + self.value + "\n"
        children_reversed = self.children.copy()
        children_reversed.reverse()

        # check if epsilon needs to be added becouse non ending parent doesnt have any children :(
        if self.is_non_ending_sign and len(children_reversed) == 0:
            children_reversed.append(Node("$", False))

        for child in children_reversed:
            ret += child.__str__(level + 1)

        return ret


def lr_parse(lr_table, fileinput_gen, start_state=0, end_of_file_sign='#', synchornizing_sings=[], file=None):
    if file:
        f = open(file, 'w+')
        sys.stdout = f

    stack_nodes = []
    stack_states = [start_state]
    inputs = [line.strip() for line in fileinput_gen] + [end_of_file_sign]

    while True:
        current_state = stack_states[-1]
        current_input = inputs[0]

        action = lr_table[current_state][current_input.split(" ")[0]]

        if action.startswith("Pomakni"):
            # add a node
            node = Node(current_input, non_ending_sign=False)
            stack_nodes.append(node)

            # add a dka state
            stack_states.append(int(action.split(" ")[1]))

            # remove the read sign from input
            inputs.pop(0)
        elif action.startswith("Reduciraj"):
            left_side, rigth_side = action[len("Reduciraj "):].split(" -> ")

            # assumes that they exist and are in right order
            node = Node(left_side)
            for sign in rigth_side.strip().split(" "):
                if sign != '$':
                    node.add_node(stack_nodes.pop(-1))
                    stack_states.pop(-1)
            stack_nodes.append(node)
            # assumes that exists
            new_state = lr_table[stack_states[-1]][left_side]
            stack_states.append(int(new_state[len("Stavi "):]))
        elif action.startswith("Prihvati"):
            break
        elif action.startswith("-"):
            while current_input.split(" ")[0] not in synchornizing_sings:
                inputs.pop(0)
                current_input = inputs[0]

            current_state = stack_states[-1]
            current_input = inputs[0]
            action = lr_table[current_state][current_input.split(" ")[0]]
            while action.startswith("-"):
                stack_states.pop(-1)
                stack_nodes.pop(-1)

                current_state = stack_states[-1]
                current_input = inputs[0]
                action = lr_table[current_state][current_input.split(" ")[0]]
            continue
    print(stack_nodes[0].__str__().strip())
