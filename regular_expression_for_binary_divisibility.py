import random

def build_finite_state_machine(n):
    # build finite state machine
    # q(i) from Q ~ remainder when dividing current number by n
    # starting from remainder 0, Q = {0, 1, ..., n - 1}
    # delta(q,sigma) = (2*q + sigma) mod n
    # accept all in q(0) (F={0})
    transitions = {}
    for i in range(n):
        transitions[i] = {}
        for bit in [0, 1]:
            transitions[i][bit] = (2 * i + bit) % n
    return transitions

def run_state_machine(machine, number):
    state = 0
    for bit in number:
        state = machine[state][int(bit)]
    return state == 0

def random_test_state_machines(n):
    state_machine = build_finite_state_machine(n)
    for i in range(1000):
        num = random.randint(1, 1000)
        binary_num = '{0:b}'.format(num)
        is_divisible = (num % n) == 0
        assert is_divisible == run_state_machine(state_machine, binary_num)

def print_graphviz_state_machine(n):
    res = f'''digraph DFA_n{n} {{
    rankdir=LR;
    node [shape = circle];  
'''
    state_machine = build_finite_state_machine(n)
    res += f'    0 [label = "0", shape = doublecircle];\n'
    for i in range(1, n):
        res += f'    {i} [label = "{i}"];\n'
    for i in range(n):
        for bit in [0, 1]:
            res += f'    {i} -> {state_machine[i][bit]} [label = "{bit}"];\n'
    res += '}'
    print(res)

def regex_divisible_by(n):
    state_machine = build_finite_state_machine(n)

print_graphviz_state_machine(3)