class DuplicateFromError(Exception):
    pass

class DuplicateSelectError(Exception):
    pass

class DuplicateGroupByError(Exception):
    pass

class DuplicateOrderByError(Exception):
    pass


from pprint import pprint
from typing import Iterable, List, Any, Generator
from functools import cmp_to_key

def any_of(predicates):
    def any_predicate(values):
        for predicate in predicates:
            if predicate(values):
                return True
        return False
    return any_predicate

def nodes_at_depth(groups: Iterable, depth: int) -> Generator[List[Any], None, None]:
    """
    Итерирует все узлы (списки вида [key, items]) на заданной глубине.
    depth == 1  -> возвращает элементы верхнего уровня (т.е. сам список групп)
    depth == 2  -> возвращает все узлы, расположенные внутри node[1] верхнего уровня и т.д.
    """
    if depth <= 0:
        return
    if depth == 1:
        for g in groups:
            # ожидаем, что узел — список/кортеж вида [key, items]
            if isinstance(g, (list, tuple)) and len(g) >= 2:
                yield g  # возвращаем сам объект-узел (список), чтобы можно было менять g[1]
        return

    # depth > 1: спускаемся на уровень ниже
    for g in groups:
        if not (isinstance(g, (list, tuple)) and len(g) >= 2):
            continue
        child = g[1]
        # если child — последовательность (список групп/элементов), рекурсивно ищем в ней
        if isinstance(child, list):
            yield from nodes_at_depth(child, depth - 1)
        # если child — не список, ничего нет на таком пути (пропускаем)

def make_grouping(grouping_fn, values, existing_groups):
    res = []
    groups = {}
    for k in existing_groups:
        grouped_values = []
        groups[k] = grouped_values
        res.append([k, groups[k]])

    for val in values:
        group_key = grouping_fn(val)
        groups[group_key].append(val)
    return res

class QueryExecutor:
    def __init__(self):
        self.from_exprs = None
        self.select_expr = None
        self.group_by_exprs = None
        self.order_by_expr = None
        self.where_exprs = []
        self.having_exprs = []

    def select(self, expr=lambda x: x):
        if self.select_expr is not None:
            raise DuplicateSelectError()
        self.select_expr = expr
        return self

    def from_(self, *values):
        if self.from_exprs is not None:
            raise DuplicateFromError()
        self.from_exprs = values
        return self

    def where(self, *or_exprs):
        self.where_exprs.append(or_exprs)
        return self

    def order_by(self, expr):
        if self.order_by_expr is not None:
            raise DuplicateOrderByError()
        self.order_by_expr = expr
        return self

    def group_by(self, *exprs):
        if self.group_by_exprs is not None:
            raise DuplicateGroupByError()
        self.group_by_exprs = exprs
        return self

    def having(self, *or_exprs):
        self.having_exprs.append(or_exprs)
        return self

    def execute(self):
        res = []
        # from
        if self.from_exprs is not None and len(self.from_exprs) > 0:
            res = self.from_exprs[0]
            first_join = True
            for grouping_fn in self.from_exprs[1:]:
                new_res = []
                for val in res:
                    for expr_val in grouping_fn:
                        if first_join:
                            new_res.append([val, expr_val])
                        else:
                            new_res.append([*val, expr_val])
                res = new_res
                first_join = False
        # where
        for or_exprs in self.where_exprs:
            res = list(filter(any_of(or_exprs), res))
        # group by
        if self.group_by_exprs is not None:
            existing_groups = []
            for grouping_fn in self.group_by_exprs:
                distinct_group_keys = []
                for val in res:
                    group_key = grouping_fn(val)
                    if group_key not in distinct_group_keys:
                        distinct_group_keys.append(group_key)
                existing_groups.append(list(distinct_group_keys))
            res = make_grouping(self.group_by_exprs[0], res, existing_groups[0])

            for depth, (grouping_fn, existing_group) in enumerate(zip(self.group_by_exprs[1:], existing_groups[1:]), start=1):
                for node in nodes_at_depth(res, depth):
                    groups_in_node = []
                    for val in node[1]:
                        group_key = grouping_fn(val)
                        if group_key not in groups_in_node:
                            groups_in_node.append(group_key)
                    node[1] = make_grouping(grouping_fn, node[1], groups_in_node)

        # having
        for or_exprs in self.having_exprs:
            res = list(filter(any_of(or_exprs), res))
        # select
        if self.select_expr is not None:
            res = list(map(lambda val: self.select_expr(val), res))
        # order by
        if self.order_by_expr is not None:
            res.sort(key=cmp_to_key(self.order_by_expr))
        return res

def query():
    return QueryExecutor()

persons = [
            {"name": "Peter", "profession": "teacher", "age": 20, "marital_status": "married", "isReal": True},
            {"name": "Michael", "profession": "teacher", "age": 50, "marital_status": "single", "isReal": True},
            {"name": "Peter", "profession": "teacher", "age": 20, "marital_status": "married", "isReal": False},
            {"name": "Anna", "profession": "scientific", "age": 20, "marital_status": "married", "isReal": True},
            {"name": "Rose", "profession": "scientific", "age": 50, "marital_status": "married", "isReal": False},
            {"name": "Anna", "profession": "scientific", "age": 20, "marital_status": "single", "isReal": True},
            {"name": "Anna", "profession": "politician", "age": 50, "marital_status": "married", "isReal": False}
        ]

def profession(person): return person["profession"]
def is_teacher(person): return person["profession"] == "teacher"
def name(person): return person["name"]
def name(person): return person["name"]
def age(person): return person["age"]
def marital_status(person):
    print(f'getting marital status for {person}')
    return person["marital_status"]
def profession_count(group): return [group[0], len(group[1])]
def natural_compare(value1, value2): return -1 if (value1 < value2) else 1 if (value1 > value2) else 0
def reality(person): return "real" if person["isReal"] else "simulated"

#q = query().select().from_(persons[:]).group_by(profession, name, age, marital_status, reality)
#q = query().select().from_(persons[:]).group_by(profession, name, age, marital_status)
#q = query().from_([1, 2, 4, 5, 6, 7, 8, 9]).group_by(ternarity, size).select()



numbers =  [1, 2, 3, 4, 5, 6, 7, 8, 9]


def is_prime(number):
    if number < 2:
        return False

    divisor = 2

    while number % divisor != 0:
        divisor += 1

    return divisor == number

def prime(number): return "prime" if is_prime(number) else "divisible"


def is_even(number): return number % 2 == 0


def parity(number): return "even" if is_even(number) else "odd"


def descendent_compare(number1, number2): return number2 - number1


def odd(group): return group[0] == "odd"


def less_than_3(number): return number < 3


def greater_than_4(number): return number > 4

#q = query().select().from_(numbers[:]).group_by(parity, prime)
q = query().select().from_(numbers[:]).order_by(descendent_compare)

pprint(q.execute())
