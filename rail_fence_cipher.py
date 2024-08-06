def get_steps(n):
    steps = []
    fst = (n - 1) * 2
    snd = 0
    for i in range(1, n + 1):
        steps.append((fst, snd))
        fst -= 2
        snd += 2
    return steps


def run_index_cycle(steps, ln, callback):
    for fst, snd in steps:
        ind = snd // 2
        first_flag = True
        while ind < ln:
            if first_flag:
                if fst > 0:
                    callback(ind)
                    ind += fst
                first_flag = not first_flag
            else:
                if snd > 0:
                    callback(ind)
                    ind += snd
                first_flag = not first_flag


def encode_rail_fence_cipher(string, n):
    res = ''
    ln = len(string)
    steps = get_steps(n)

    def callback(ind):
        nonlocal res
        res += string[ind]

    run_index_cycle(steps, ln, callback)

    return res


def decode_rail_fence_cipher(string, n):
    ln = len(string)
    res = ['' for _ in range(ln)]
    steps = get_steps(n)
    str_ind = 0

    def callback(ind):
        nonlocal str_ind, res
        res[ind] = string[str_ind]
        str_ind += 1

    run_index_cycle(steps, ln, callback)

    return ''.join(res)


r1 = encode_rail_fence_cipher('АБВГДЕЁЖЗИЙКЛ', 1)
print(r1)
print(decode_rail_fence_cipher(r1, 1))
print(encode_rail_fence_cipher("WEAREDISCOVEREDFLEEATONCE", 3))
print(decode_rail_fence_cipher(encode_rail_fence_cipher("WEAREDISCOVEREDFLEEATONCE", 3), 3))
