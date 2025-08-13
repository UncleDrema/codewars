from dataclasses import dataclass
import re
from typing import Optional


def tokenize(expression):
    if expression == "":
        return []

    regex = re.compile("\s*(=>|[-+*\/\%=\(\)]|[A-Za-z_][A-Za-z0-9_]*|[0-9]*\.?[0-9]+)\s*")
    tokens = regex.findall(expression)
    return [s for s in tokens if not s.isspace()]

def is_identifier(token):
    return re.fullmatch(r'[A-Za-z_][A-Za-z0-9_]*', token) is not None

@dataclass
class Function:
    name: str
    args: list[str]
    body: list[str]

    def __str__(self):
        return f"Function(name={self.name}, args={self.args}, body={self.body})"

class Interpreter:
    ops = ['+', '-', '*', '/', '%']
    op_prior = {
        '+': 1,
        '-': 1,
        '*': 2,
        '/': 2,
        '%': 2,
        '=': 0,
        '(': 3,
        ')': 3
    }

    def make_op(self, op, n1, n2):
        n1 = int(n1) if isinstance(n1, str) and n1.isdigit() else n1
        n2 = int(n2) if isinstance(n2, str) and n2.isdigit() else n2
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
        self.history = []

    def get_value(self, token, vars_context):
        if is_identifier(token):
            if token in vars_context:
                return vars_context[token]
            else:
                raise Exception(f"Invalid identifier. No variable with name '{token}' was found. history: {self.history}")
        try:
            return int(token)
        except ValueError:
            raise Exception(f"Invalid token '{token}'. Expected an integer or a variable name. history: {self.history}")

    def extract_args(self, tokens, start, arg_count):
        args = []
        i = start
        for _ in range(arg_count):
            if i >= len(tokens):
                raise Exception(f"Not enough arguments for function history: {self.history}")
            # Если следующий токен — функция, рекурсивно собираем её вызов
            if tokens[i] in self.functions:
                func = self.functions[tokens[i]]
                sub_args, next_i = self.extract_args(tokens, i + 1, len(func.args))
                args.append([tokens[i]] + sum(sub_args, []))
                i = next_i
            else:
                args.append([tokens[i]])
                i += 1
        return args, i

    def resolve_functions(self, tokens, vars_context):
        i = 0
        result = []
        while i < len(tokens):
            tok = tokens[i]
            if tok in self.functions:
                func = self.functions[tok]
                arg_count = len(func.args)
                args_tokens, next_i = self.extract_args(tokens, i + 1, arg_count)
                args_values = [self.eval(arg, vars_context) for arg in args_tokens]
                func_vars = vars_context.copy()
                for name, value in zip(func.args, args_values):
                    func_vars[name] = value
                func_result = self.eval(func.body, func_vars)
                result.append(str(func_result))
                i = next_i
            else:
                result.append(tok)
                i += 1
        return result

    def eval(self, tokens, vars_context):
        tokens = self.resolve_functions(tokens, vars_context)
        if len(tokens) == 1:
            return self.get_value(tokens[0], vars_context)
        stack = []
        res = []
        n = len(tokens)
        for idx, tok in enumerate(tokens):
            if tok in Interpreter.ops or tok == '=':
                while (len(stack) > 0 and (stack[-1] in Interpreter.ops or stack[-1] == '=') and Interpreter.op_prior[stack[-1]] >= \
                        Interpreter.op_prior[tok]):
                    res.append(stack.pop())
                stack.append(tok)
            elif tok == '(':
                stack.append(tok)
            elif tok == ')':
                while stack[-1] != '(':
                    res.append(stack.pop())
                stack.pop()
            else:
                if is_identifier(tok) and idx + 1 < n and tokens[idx + 1] == '=':
                    res.append(tok)
                else:
                    res.append(self.get_value(tok, vars_context) if is_identifier(tok) else tok)
        while len(stack) > 0:
            res.append(stack.pop())

        stack2 = []
        assign_vars = []
        for tok in res:
            if tok not in Interpreter.ops and tok != '=':
                stack2.append(tok)
            elif tok == '=':
                value = stack2.pop()
                var = stack2.pop()
                assign_vars.append(var)
                stack2.append(value)
            else:
                # Перед операцией, если есть цепочка присваиваний, обработать их
                if assign_vars:
                    value = stack2[-1]
                    for var in assign_vars:
                        if not is_identifier(var):
                            raise Exception(f"Invalid assignment target '{var}' history: {self.history}")
                        if var in self.functions:
                            raise Exception(
                                f"Cannot assign to '{var}', function with this name exists. history: {self.history}")
                        self.vars[var] = value
                    assign_vars.clear()
                op2 = stack2.pop()
                op1 = stack2.pop()
                stack2.append(self.make_op(tok, op1, op2))
        if assign_vars:
            value = stack2[-1]
            for var in assign_vars:
                if not is_identifier(var):
                    raise Exception(f"Invalid assignment target '{var}' history: {self.history}")
                if var in self.functions:
                    raise Exception(
                        f"Cannot assign to '{var}', function with this name exists. history: {self.history}")
                self.vars[var] = value
            assign_vars.clear()
        assert len(stack2) == 1
        return stack2[0]

    def is_assignment(self, tokens):
        if len(tokens) < 3 or tokens[1] != '=':
            return False
        if not is_identifier(tokens[0]):
            return False
        for tok in tokens[2:]:
            if not (tok.isdigit() or is_identifier(tok) or tok in Interpreter.ops):
                return False
        return True

    def parse_function_declaration(self, tokens: list[str]) -> Optional[Function]:
        if tokens[0] != 'fn':
            return None
        if not is_identifier(tokens[1]):
            return None
        func_operator_pos = tokens.index('=>')
        if func_operator_pos == -1:
            return None
        func_args = tokens[2:func_operator_pos]
        func_body = tokens[func_operator_pos + 1:]
        if len(func_body) == 0:
            return None
        for tok in func_body:
            if is_identifier(tok) and tok not in func_args:
                raise Exception(f"Function body cannot use variables that are not declared as arguments. history: {self.history}")
        if len(set(func_args)) != len(func_args):
            raise Exception(f"Function arguments must be unique. history: {self.history}")
        for arg in func_args:
            if not is_identifier(arg):
                raise Exception(f"Invalid function argument '{arg}'. Expected a valid variable name. history: {self.history}")
        return Function(tokens[1], func_args, func_body)

    def input(self, expression):
        self.history.append(expression)
        tokens = tokenize(expression)
        if len(tokens) == 0:
            return ''
        elif self.is_assignment(tokens):
            var = tokens[0]
            if not is_identifier(var):
                raise Exception(f"Invalid identifier '{var}'. Expected a valid variable name. history: {self.history}")
            if var in self.functions:
                raise Exception(f"Cannot declare var '{var}' because a function with than name exists. history: {self.history}")
            self.vars[var] = self.eval(tokens[2:], self.vars)
            return int(self.vars[var])
        else:
            func = self.parse_function_declaration(tokens)
            if func is not None:
                if func.name in self.vars:
                    raise Exception(f"Already defined var with name '{func.name}'. history: {self.history}")
                self.functions[func.name] = func
                return ''
            else:
                return int(self.eval(tokens, self.vars))

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