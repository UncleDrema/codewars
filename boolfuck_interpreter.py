from typing import Dict, List

def decypher_tape_index(i: int):
    num = i // 8
    ind = i % 8
    return num, ind

class Tape:
    def __init__(self):
        self.tape: Dict[int, int] = {}

    def __getitem__(self, i: int):
        num, ind = decypher_tape_index(i)
        if num not in self.tape:
            self.tape[num] = 0
        return (self.tape[num] >> ind) % 2

    def __setitem__(self, i: int, val: int):
        num, ind = decypher_tape_index(i)
        if num not in self.tape:
            self.tape[num] = 0
        if val == 1:
            self.tape[num] |= 1 << ind
        else:
            self.tape[num] &= ~(1 << ind)

def to_binary(s: str) -> List[int]:
    res = []
    for c in s:
        n = ord(c)
        for i in range(8):
            res.append((n >> i) % 2)

    return res

def read_input(data: List[int]):
    if len(data) == 0:
        return 0
    return data.pop(0)

# for i in range(-9, 10):
#     print(i, decypher_tape_index(i))

def convert_output(output_data: List[int]):
    res = []
    while len(output_data) > 0:
        while len(output_data) < 8:
            output_data.append(0)
        n = 0
        for i in range(8):
            n += output_data.pop() << (7 - i)
        res += chr(n)
    return ''.join(reversed(res))

def boolfuck(code, input=""):
    tape: Tape = Tape()
    input_data = to_binary(input)
    output_data = []
    p = 0
    pc = 0
    code_size = len(code)
    while pc < code_size:
        match code[pc]:
            case '+':
                tape[p] = 1 - tape[p]
                pc += 1
            case '<':
                p -= 1
                pc += 1
            case '>':
                p += 1
                pc += 1
            case ',':
                tape[p] = read_input(input_data)
                pc += 1
            case ';':
                output_data.append(tape[p])
                pc += 1
            case '[':
                if tape[p] == 0:
                    while pc < code_size and code[pc] != ']':
                        pc += 1
                else:
                    pc += 1
            case ']':
                if tape[p] == 1:
                    while pc >= 0 and code[pc] != '[':
                        pc -= 1
                else:
                    pc += 1
    output = convert_output(output_data)
    return output

print(boolfuck(';;;+;+;;+;+;+;+;+;+;;+;;+;;;+;;+;+;;+;;;+;;+;+;;+;+;;;;+;+;;+;;;+;;+;+;+;;;;;;;+;+;;+;;;+;+;;;+;+;;;;+;+;;+;;+;+;;+;;;+;;;+;;+;+;;+;;;+;+;;+;;+;+;+;;;;+;+;;;+;+;+;', ''))