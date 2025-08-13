import re

def tokenize(expression):
    if expression == "":
        return []

    regex = re.compile("\s*(=>|[-+*\/\%=\(\)]|[A-Za-z_][A-Za-z0-9_]*|[0-9]*\.?[0-9]+)\s*")
    tokens = regex.findall(expression)
    return [s for s in tokens if not s.isspace()]

def is_identifier(token):
    return re.fullmatch(r'[A-Za-z_][A-Za-z0-9_]*', token) is not None

class Interpreter:
    ops = ['+', '-', '*', '/', '%']
    op_prior = {
        '+': 1,
        '-': 1,
        '*': 2,
        '/': 2,
        '%': 2,
        '(': 3,
        ')': 3
    }

    def make_op(self, op, n1, n2):
        match op:
            case '+':
                return n1 + n2
            case '-':
                return n1 - n2
            case '*':
                return n1 * n2
            case '/':
                return n1 // n2
            case '%':
                return n1 % n2

    def __init__(self):
        self.vars = {}
        self.functions = {}

    def get_value(self, token):
        if is_identifier(token):
            if token in self.vars:
                return self.vars[token]
            else:
                raise Exception(f"Invalid identifier. No variable with name '{token}' was found.")
        try:
            return int(token)
        except ValueError:
            raise Exception(f"Invalid token '{token}'. Expected an integer or a variable name.")

    def eval(self, tokens):
        if len(tokens) == 1:
            return self.get_value(tokens[0])
        stack = []
        res = []
        for tok in tokens:
            if tok in Interpreter.ops:
                while len(stack) > 0 and stack[-1] in Interpreter.ops and Interpreter.op_prior[stack[-1]] >= \
                        Interpreter.op_prior[tok]:
                    res.append(stack.pop())
                stack.append(tok)
            elif tok == '(':
                stack.append(tok)
            elif tok == ')':
                while stack[-1] != '(':
                    res.append(stack.pop())
                stack.pop()
            else:
                res.append(self.get_value(tok))
        while len(stack) > 0:
            res.append(stack.pop())
        for tok in res:
            if tok not in Interpreter.ops:
                stack.append(tok)
            else:
                op2 = stack.pop()
                op1 = stack.pop()
                stack.append(self.make_op(tok, op1, op2))
        assert len(stack) == 1
        return stack[0]

    def input(self, expression):
        tokens = tokenize(expression)
        if len(tokens) == 0:
            return ''
        if len(tokens) == 1:
            try:
                return self.get_value(tokens[0])
            except ValueError:
                raise Exception(f'Invalid identifier. No variable with name \'{var}\' was found.')
        elif tokens[1] == '=':
            var = tokens[0]
            if not is_identifier(var):
                raise Exception(f"Invalid identifier '{var}'. Expected a valid variable name.")
            self.vars[var] = self.eval(tokens[2:])
            return self.vars[var]
        else:
            return self.eval(tokens)

def main():
    interpreter = Interpreter()
    while True:
        try:
            expression = input(">>> ")
            if expression.strip().lower() == 'exit':
                break
            result = interpreter.input(expression)
            print(result)
        except Exception as e:
            print(f"ERROR: {e}")

if __name__ == "__main__":
    main()