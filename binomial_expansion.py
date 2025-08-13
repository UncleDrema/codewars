import re
import math


def parse_expression(expression):
    pattern = r"\(([-+]?\d*\.?\d*)?([a-z])([-+]?\d*\.?\d+|[-+]?\d+)?\)\^([-+]?\d+)"
    match = re.fullmatch(pattern, expression)

    if not match:
        raise ValueError("Invalid format. Expected format is (ax+b)^n")

    a, x, b, n = match.groups()

    a = int(a) if a and a != '+' and a != '-' else (1 if a != '-' else -1)
    b = int(b) if b else 0.0
    n = int(n)

    return a, b, n, x

def binomial_coefficient(n, k):
    if k == 0 or k == n:
        return 1
    return math.factorial(n) // (math.factorial(k) * math.factorial(n - k))

def optional_plus(coefficient, include_plus_sign):
    if coefficient < 0:
        return f'{coefficient}'
    return f'+{coefficient}' if include_plus_sign else f'{coefficient}'


def pretty_coefficient(coefficient, include_plus_sign=False, return_if_one=False):
    if coefficient == 1:
        return optional_plus(coefficient, include_plus_sign) if return_if_one else ''
    if coefficient == -1:
        return optional_plus(coefficient, include_plus_sign) if return_if_one else '-'
    return optional_plus(coefficient, include_plus_sign)

def term(coefficient, variable, power, include_plus_sign=False, return_coeff_if_one=False):
    pretty_coeff = pretty_coefficient(coefficient, include_plus_sign, return_coeff_if_one)
    if power == 0:
        return pretty_coeff
    if power == 1:
        return f'{pretty_coeff}{variable}'
    return f'{pretty_coeff}{variable}^{power}'

def expand(expr):
    a, b, n, x = parse_expression(expr)

    binomial_coefficients = [binomial_coefficient(n, k) for k in range(n + 1)]
    expression_coefficients = [a ** (n - k) * b ** k for k in range(n + 1)]
    resulting_coefficients = [binomial_coefficients[k] * expression_coefficients[k] for k in range(n + 1)]
    res = ''
    for i in range(n+1):
        if resulting_coefficients[i] != 0:
            res += term(resulting_coefficients[i], x, n - i, i != 0, i == n)

    return res

test_data = [
    '(4x+1)^5',
    '(x+1)^1',
    '(x+1)^2',
]

for d in test_data:
    print('Expression:', d)
    print(expand(d))