class RegExp:
    def __init__(self, *args):
        self.args = args
    def __repr__(self):
        args = ", ".join(map(repr, self.args))
        return f"{self.__class__.__name__}({args})"
    def __eq__(self, other):
        return type(self) is type(other) and self.args == other.args
class Any(RegExp): pass
class Normal(RegExp): pass
class Or(RegExp): pass
class Str(RegExp): pass
class ZeroOrMore(RegExp): pass

from dataclasses import dataclass


# ---------------------------------------------------------------------------
# Узлы AST
# ---------------------------------------------------------------------------

@dataclass
class ASTNode:
    """Базовый класс узла AST."""


@dataclass
class CharNode(ASTNode):
    """Одиночный символ."""
    char: str

    def __repr__(self) -> str:
        return f"Char({self.char!r})"


@dataclass
class ConcatNode(ASTNode):
    """Конкатенация двух подвыражений."""
    left: ASTNode
    right: ASTNode

    def __repr__(self) -> str:
        return f"Concat({self.left}, {self.right})"


@dataclass
class AltNode(ASTNode):
    """Альтернатива (|)."""
    left: ASTNode
    right: ASTNode

    def __repr__(self) -> str:
        return f"Alt({self.left}, {self.right})"


@dataclass
class StarNode(ASTNode):
    """Операция Клини (*)."""
    child: ASTNode

    def __repr__(self) -> str:
        return f"Star({self.child})"


@dataclass
class GroupNode(ASTNode):
    """Группа в скобках."""
    child: ASTNode

    def __repr__(self) -> str:
        return f"Group({self.child})"

# Символы с особым синтаксическим смыслом (нельзя использовать как литерал без \\)
_SPECIAL = frozenset("()|*\\")


# ---------------------------------------------------------------------------
# Внутренний парсер (рекурсивный спуск)
# ---------------------------------------------------------------------------

class _Parser:
    """Реализует рекурсивный спуск по грамматике выражений."""

    def __init__(self, text: str) -> None:
        self._text = text
        self._pos = 0

    # ------------------------------------------------------------------
    # Вспомогательные методы
    # ------------------------------------------------------------------

    def _peek(self) -> str | None:
        """Вернуть текущий символ без сдвига (или None в конце строки)."""
        if self._pos < len(self._text):
            return self._text[self._pos]
        return None

    def _consume(self) -> str:
        """Считать и вернуть текущий символ, сдвинуть позицию."""
        ch = self._text[self._pos]
        self._pos += 1
        return ch

    def _expect(self, expected: str) -> None:
        """Считать символ и проверить, что он равен *expected*."""
        ch = self._peek()
        if ch != expected:
            got = repr(ch) if ch is not None else "конец строки"
            raise ValueError(
                f"Ожидался {expected!r}, получен {got} "
                f"(позиция {self._pos})"
            )
        self._consume()

    # ------------------------------------------------------------------
    # Грамматические правила
    # ------------------------------------------------------------------

    def parse_expr(self) -> ASTNode:
        """expr ::= term ('|' term)?"""
        node = self._parse_term()
        if self._peek() == "|":
            self._consume()  # съесть '|'
            right = self._parse_term()
            node = AltNode(node, right)
        # Убрали цикл while - теперь только один '|' разрешен
        return node

    def _parse_term(self) -> ASTNode:
        """term ::= factor factor*  (конкатенация, леворекурсивная)"""
        factors: list[ASTNode] = []
        while self._peek() is not None and self._peek() not in ("|", ")"):
            factors.append(self._parse_factor())

        if not factors:
            raise ValueError(
                f"Пустой терм недопустим (позиция {self._pos}): "
                "используйте непустые операнды альтернативы и группы"
            )

        node = factors[0]
        for f in factors[1:]:
            node = ConcatNode(node, f)
        return node

    def _parse_factor(self) -> ASTNode:
        """factor ::= atom ('*')?"""
        node = self._parse_atom()
        ch = self._peek()
        if ch == "*":
            self._consume()
            node = StarNode(node)
        return node

    def _parse_atom(self) -> ASTNode:
        """atom ::= CHAR | 'ε' | '(' expr ')'"""
        ch = self._peek()

        if ch is None:
            raise ValueError(
                f"Неожиданный конец выражения (позиция {self._pos})"
            )

        # Скобочная группа
        if ch == "(":
            self._consume()          # съесть '('
            node = self.parse_expr()
            self._expect(")")
            return GroupNode(node)

        # Лишняя закрывающая скобка
        if ch == ")":
            raise ValueError(
                f"Неожиданная ')' (позиция {self._pos})"
            )

        # Квантификатор/альтернатива без левого операнда
        if ch in ("*"):
            raise ValueError(
                f"Квантификатор {ch!r} без операнда (позиция {self._pos})"
            )

        # Обычный символ
        self._consume()
        return CharNode(ch)


# ---------------------------------------------------------------------------
# Публичный API
# ---------------------------------------------------------------------------

def parse(regex: str) -> ASTNode:
    """Разобрать строку регулярного выражения и вернуть корень AST.

    Поддерживаются:
    - Литеральные символы (любой не-спецсимвол)
    - Конкатенация  ``ab``
    - Альтернатива  ``a|b``
    - Квантификаторы ``*``, ``+``, ``?``
    - Группировка ``(...)``
    - Экранирование ``\\*``, ``\\(``, ``\\\\`` и т.д.

    Args:
        regex: Строка с регулярным выражением.

    Returns:
        Корень дерева разбора.

    Raises:
        ValueError: Если выражение пустое или содержит синтаксическую ошибку.

    Examples:
        >>> parse('a')
        Char('a')
        >>> parse('a|b')
        Alt(Char('a'), Char('b'))
        >>> parse('(a|b)*')
        Star(Alt(Char('a'), Char('b')))
    """
    if not regex:
        raise ValueError("Пустое регулярное выражение")

    p = _Parser(regex)
    ast = p.parse_expr()

    if p._peek() is not None:
        raise ValueError(
            f"Неожиданный символ {p._peek()!r} (позиция {p._pos})"
        )

    return ast

# Маппим результат парсера в типы по задаче

def map_to_task(node: ASTNode) -> RegExp:
    if isinstance(node, CharNode):
        if node.char == '.':
            return Any()
        return Normal(node.char)
    if isinstance(node, AltNode):
        return Or(map_to_task(node.left), map_to_task(node.right))
    if isinstance(node, StarNode):
        return ZeroOrMore(map_to_task(node.child))
    if isinstance(node, GroupNode):
        return map_to_task(node.child)

    if isinstance(node, ConcatNode):
        nodes = []

        def collect(n):
            if isinstance(n, ConcatNode):
                collect(n.left)
                collect(n.right)
            else:
                nodes.append(map_to_task(n))

        collect(node)
        return Str(nodes)
    return node

def parse_regexp(indata: str):
    try:
        res = parse(indata)
        return map_to_task(res)
    except:
        return None


if __name__ == "__main__":
    #print(parse_regexp('(abc)def'))
    print(parse_regexp('(ln;807\'2dhA/@ZHkq)3uX~5:ia\x0bNe[{1&OR9zpJ6\\f<=LT!YWK+}U\n"jmy'))
    #print(parse_regexp("."), "===", Any())
    #print(parse_regexp("a"), "===", Normal("a"))
    #print(parse_regexp("a|b"), "===", Or(Normal("a"), Normal("b")))
    #print(parse_regexp("a*"), "===", ZeroOrMore(Normal("a")))
    #print(parse_regexp("(a)"), "===", Normal("a"))
    #print(parse_regexp("(a)*"), "===", ZeroOrMore(Normal("a")))
    #print(parse_regexp("(a|b)*"), "===", ZeroOrMore(Or(Normal("a"), Normal("b"))))
    #print(parse_regexp("a|b*"), "===", Or(Normal("a"), ZeroOrMore(Normal("b"))))
    #print(parse_regexp("abcd"), "===", Str([Normal("a"), Normal("b"), Normal("c"), Normal("d")]))
    #print(parse_regexp("ab|cd"), "===", Or(Str([Normal("a"), Normal("b")]), Str([Normal("c"), Normal("d")])))