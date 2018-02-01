import sys

def parse_text(start_state, rules_for_state, fileinput_gen, file=None):
    if file:
        f = open(file, 'w+')
        sys.stdout = f

    line_number = 1
    state = start_state
    text = ''.join(fileinput_gen)
    start_index = 0
    end_index = len(text)
    while start_index < end_index:
        best_len = 0
        best_rule = None
        rules = rules_for_state[state]
        regex = text[start_index:end_index]
        for rule in rules:
            length = rule.automate.satisfies(regex)
            if length > best_len:
                best_len = length
                best_rule = rule
        if best_rule:
            accepted_text = regex[:best_len]
            if best_rule.vrati_se is not None:
                accepted_text = accepted_text[:best_rule.vrati_se]
                start_index += best_rule.vrati_se
            else:
                start_index += len(accepted_text)
            if best_rule.uniform_sign != '-':
                print(best_rule.uniform_sign, line_number, accepted_text, sep=' ') #regex or accepted_text
            if best_rule.udji_u_stanje:
                state = best_rule.udji_u_stanje
            if best_rule.novi_redak:
                line_number += 1
        else:
            start_index += 1
    f.close()
