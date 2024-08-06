priority = {
    '~': 3,
    '*': 2,
    '/': 2,
    '+': 1,
    '-': 1
}

ops = {'~', '*', '/', '+', '-'}


def rpn(expression):
    res = []
    stack = []
    prev = ''
    for i in range(len(expression)):
        c = expression[i]
        if c == ' ':
            continue
        if c == '(':
            stack.append(c)
        elif c == ')':
            while stack[-1] != '(':
                res.append(stack.pop())
            stack.pop()
        elif c in ops:
            if c == '-' and not prev.isdigit() and not (prev == ')'):
                stack.append('~')
            else:
                while len(stack) > 0 and stack[-1] in ops and priority[stack[-1]] >= priority[c]:
                    res.append(stack.pop())
                stack.append(c)

        else:
            if len(res) > 0 and prev.isdigit():
                res[-1] += c
            else:
                res.append(c)
        prev = c
    while len(stack) > 0:
        res += stack.pop()
    for i in range(len(res)):
        if res[i].isdigit():
            res[i] = int(res[i])
    return res


def calc(expression):
    expr = rpn(expression)
    s = []
    for e in expr:
        if e == '~':
            o1 = s.pop()
            s.append(-o1)
        elif e == '+':
            o2 = s.pop()
            o1 = s.pop()
            s.append(o1 + o2)
        elif e == '-':
            o2 = s.pop()
            o1 = s.pop()
            s.append(o1 - o2)
        elif e == '*':
            o2 = s.pop()
            o1 = s.pop()
            s.append(o1 * o2)
        elif e == '/':
            o2 = s.pop()
            o1 = s.pop()
            s.append(o1 / o2)
        else:
            s.append(e)
    return s[0]

print(calc('1 + 2 * (3 + - 2)'))