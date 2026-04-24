def format_range(start, prev):
    if start == prev:
        return f'{start}'
    if prev == start + 1:
        return f'{start},{prev}'
    return f'{start}-{prev}'

def solution(args):
    result = ""
    start = args[0]
    prev = args[0]
    for n in args[1:]:
        if n != prev + 1:
            result += format_range(start, prev) + ','
            start = n
        prev = n
    result += format_range(start, prev)

    return result


print(solution([-6,-3,-2,-1,0,1,3,4,5,7,8,9,10,11,14,15,17,18,19,20]))