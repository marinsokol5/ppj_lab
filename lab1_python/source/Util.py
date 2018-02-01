class Automate:
    def __init__(self):
        self.number_of_states = 0
        self.start_state = None
        self.acceptable_state = None
        self.epsilon_transitions = []
        self.transitions = []
        self.current_states = set()

    def new_state(self):
        self.number_of_states += 1
        return self.number_of_states - 1

    def add_epsilon_transition(self, left_state, right_state):
        self.epsilon_transitions.append(Transition(
            left_state=left_state,
            right_state=right_state,
            transition_sign='$'
        ))

    def add_transition(self, left_state, right_state, transition_char):
        self.transitions.append(Transition(
            left_state=left_state,
            right_state=right_state,
            transition_sign=transition_char
        ))

    def satisfies(self, regex):
        self.initialize()
        length = 0
        for i, char in enumerate(regex):
            temp_states = set()
            for trans in self.transitions:
                if trans.transition_sign == char and trans.left_state in self.current_states:
                    temp_states.add(trans.right_state)
            if len(temp_states) == 0:
                return length
            self.find_epsilon_surroundings(temp_states)
            self.current_states = temp_states
            if self.acceptable_state in self.current_states:
                length = i + 1
        return length

    def initialize(self):
        self.current_states = {self.start_state}
        self.find_epsilon_surroundings(self.current_states)

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


class Rule:
    def __init__(self, regex, uniform_sign, udji_u_stanje, novi_redak, vrati_se):
        self.automate = Automate()
        left_state, right_state = turn_exp_to_automate(regex, self.automate)
        self.automate.start_state = left_state
        self.automate.acceptable_state = right_state
        self.uniform_sign = uniform_sign
        self.udji_u_stanje = udji_u_stanje
        self.novi_redak = novi_redak
        self.vrati_se = vrati_se


def turn_exp_to_automate(reg_exp: str, automat: Automate):
    reg_choices = []
    bracket_counter = 0
    size_of_grouped_signs = 0
    for i in range(len(reg_exp)):
        if reg_exp[i] == '(' and is_operator(reg_exp, i):
            bracket_counter += 1
        elif reg_exp[i] == ')' and is_operator(reg_exp, i):
            bracket_counter -= 1
        elif bracket_counter == 0 and reg_exp[i] == '|' and is_operator(reg_exp, i):
            reg_choices.append(reg_exp[size_of_grouped_signs:i])
            size_of_grouped_signs = i + 1

    if reg_choices:
        reg_choices.append(reg_exp[size_of_grouped_signs:])
    left_state = automat.new_state()
    right_state = automat.new_state()
    if reg_choices:
        for choice in reg_choices:
            temp_start_state, temp_acceptable_state = turn_exp_to_automate(choice, automat)
            automat.add_epsilon_transition(left_state, temp_start_state)
            automat.add_epsilon_transition(temp_acceptable_state, right_state)
    else:
        prefixed = False
        last_state = left_state
        i = 0
        while i < len(reg_exp):
            if prefixed:
                prefixed = False
                if reg_exp[i] == 't':
                    transition_char = '\t'
                elif reg_exp[i] == 'n':
                    transition_char = '\n'
                elif reg_exp[i] == '_':
                    transition_char = ' '
                else:
                    transition_char = reg_exp[i]

                a = automat.new_state()
                b = automat.new_state()
                automat.add_transition(a, b, transition_char)
            else:
                if reg_exp[i] == '\\':
                    prefixed = True
                    i += 1
                    continue
                if reg_exp[i] != '(':
                    a = automat.new_state()
                    b = automat.new_state()
                    if reg_exp[i] == '$':
                        automat.add_epsilon_transition(a, b)
                    else:
                        automat.add_transition(a, b, reg_exp[i])
                else:
                    j = i + find__index_of_closing_bracket(reg_exp[i:])
                    temp_start_state, temp_acceptable_state = turn_exp_to_automate(reg_exp[i + 1:j], automat)
                    a = temp_start_state
                    b = temp_acceptable_state
                    i = j

            if i + 1 < len(reg_exp) and reg_exp[i + 1] == '*':
                x, y = a, b
                a = automat.new_state()
                b = automat.new_state()
                automat.add_epsilon_transition(a, x)
                automat.add_epsilon_transition(y, b)
                automat.add_epsilon_transition(a, b)
                automat.add_epsilon_transition(y, x)
                i += 1

            automat.add_epsilon_transition(last_state, a)
            last_state = b
            i += 1
        automat.add_epsilon_transition(last_state, right_state)
    return left_state, right_state


def is_operator(reg_exp: str, i: int):
    counter = 0
    while i - 1 >= 0 and reg_exp[i - 1] == '\\':
        counter += 1
        i -= 1
    return counter % 2 == 0


def find__index_of_closing_bracket(expression: str):
    number_of_brackets = 0
    for i in range(len(expression)):
        if expression[i] == '(' and is_operator(expression, i):
            number_of_brackets += 1
        elif expression[i] == ')' and is_operator(expression, i):
            number_of_brackets -= 1
        if number_of_brackets == 0:
            return i
