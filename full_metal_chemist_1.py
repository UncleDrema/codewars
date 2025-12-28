import dataclasses
from collections import defaultdict
from typing import List, Tuple, Dict, Set


class MoleculeError(Exception):
    pass

class UnlockedMolecule(MoleculeError):
    pass

class InvalidBond(MoleculeError):
    pass

class LockedMolecule(MoleculeError):
    pass

class EmptyMolecule(MoleculeError):
    pass

Element = str
BounderTuple = Tuple[int, int, int, int]
MutateTuple = Tuple[int, int, Element]
AddTuple = Tuple[int, int, Element]

@dataclasses.dataclass(frozen=True)
class ElementDescriptor:
    symbol: Element
    valence: int
    atomic_weight: float
    order: int = 0

RAW_ELEMENTS: List[ElementDescriptor] = [
    ElementDescriptor('H', 1, 1.0, 2),
    ElementDescriptor('B', 3, 10.8, 4),
    ElementDescriptor('C', 4, 12.0, 1),
    ElementDescriptor('N', 3, 14.0, 9),
    ElementDescriptor('O', 2, 16.0, 3),
    ElementDescriptor('F', 1, 19.0, 7),
    ElementDescriptor('Mg', 2, 24.3, 8),
    ElementDescriptor('P', 3, 31.0, 10),
    ElementDescriptor('S', 2, 32.1, 11),
    ElementDescriptor('Cl', 1, 35.5, 6),
    ElementDescriptor('Br', 1, 80.0, 5)
]
ELEMENTS_CONFIG: Dict[Element, ElementDescriptor] = { elt.symbol: elt for elt in RAW_ELEMENTS }
def element_sort_key(elt: Element) -> int:
    return ELEMENTS_CONFIG[elt].order

class Atom(object):

    def __init__(self, elt, id_):
        self.element: Element = elt
        self.id: int = id_
        self.bounded: List[Atom] = []

    def __hash__(self):      return self.id

    def __eq__(self, other): return self.id == other.id

    @property
    def weight(self) -> float:
        return ELEMENTS_CONFIG[self.element].atomic_weight

    @property
    def valence(self) -> int:
        return ELEMENTS_CONFIG[self.element].valence

    @property
    def used_valence(self) -> int:
        return len(self.bounded)

    @property
    def remaining_valence(self) -> int:
        return self.valence - self.used_valence

    def __str__(self):
        if len(self.bounded) == 0:
            return f'Atom({self.element}.{self.id})'

        bounded_atoms: List[Atom] = []
        hydrogens: List[Atom] = []
        for bounded in self.bounded:
            if bounded.element == 'H':
                hydrogens.append(bounded)
            else:
                bounded_atoms.append(bounded)

        sorted_bounded_atoms = sorted(bounded_atoms, key=lambda a: element_sort_key(a.element))

        atoms_descriptions = []
        elements_and_ids: Dict[Element, List[int]] = defaultdict(list)
        for bounded in sorted_bounded_atoms:
            elements_and_ids[bounded.element].append(bounded.id)

        for el in sorted(elements_and_ids.keys(), key=element_sort_key):
            for atom_id in sorted(elements_and_ids[el]):
                atoms_descriptions.append(f'{el}{atom_id}')

        for _ in hydrogens:
            atoms_descriptions.append('H')

        return f'Atom({self.element}.{self.id}: {",".join(atoms_descriptions)})'

    def __repr__(self):
        return str(self)

    def bind(self, other):
        if self.id == other.id:
            raise InvalidBond
        if self.remaining_valence < 1 or other.remaining_valence < 1:
            raise InvalidBond
        self.bounded.append(other)
        other.bounded.append(self)
        return self

    def unbind(self, other):
        self.bounded.remove(other)
        other.bounded.remove(self)
        return self

    def unbind_all(self):
        for other in list(self.bounded):
            self.unbind(other)
        return self

class Molecule(object):
    def __init__(self, name: str = ''):
        self.name = name
        self.branches: List[List[Atom]] = []
        self.lonely_atoms = []
        self.id_counter = 1
        self.locked = False

    def get_all_atoms(self):
        atoms: List[Atom] = []
        visited: Set[int] = set()
        queue: List[Atom] = [*self.lonely_atoms]
        for branch in self.branches:
            for atom in branch:
                queue.append(atom)

        while queue:
            atom = queue.pop(0)
            if atom.id in visited:
                continue
            atoms.append(atom)
            visited.add(atom.id)
            for bound_atom in atom.bounded:
                if bound_atom.id not in visited:
                    queue.append(bound_atom)
        return atoms

    @property
    def formula(self):
        if not self.locked:
            raise UnlockedMolecule
        elements = defaultdict(lambda: 0)
        all_atoms = self.get_all_atoms()
        for atom in all_atoms:
            elements[atom.element] += 1
        sorted_elements = sorted(elements.items(), key=lambda x: element_sort_key(x[0]))

        res = ''
        for (elt, cnt) in sorted_elements:
            res += elt
            if cnt > 1:
                res += str(cnt)
        return res

    @property
    def molecular_weight(self):
        if not self.locked:
            raise UnlockedMolecule
        all_atoms = self.get_all_atoms()
        weight = 0
        for atom in all_atoms:
            weight += atom.weight
        return weight

    @property
    def atoms(self):
        return sorted(self.get_all_atoms(), key=lambda a: a.id)

    def create_atom(self, elt):
        res = Atom(elt, self.id_counter)
        self.id_counter += 1
        return res

    def cancel_atom(self):
        self.id_counter -= 1

    def get_branch(self, b):
        return self.branches[b - 1]

    def brancher(self, *branches: int):
        if self.locked:
            raise LockedMolecule

        for carbons_in_branch in branches:
            new_branch: List[Atom] = []
            for i in range(carbons_in_branch):
                new_branch.append(self.create_atom('C'))
                if i > 0:
                    new_branch[i - 1].bind(new_branch[i])
            self.branches.append(new_branch)
        return self

    def bounder(self, *bounders: BounderTuple):
        if self.locked:
            raise LockedMolecule

        for (c1, b1, c2, b2) in bounders:
            branch1 = self.get_branch(b1)
            carbon1 = branch1[c1 - 1]
            branch2 = self.get_branch(b2)
            carbon2 = branch2[c2 - 1]
            if (carbon1.remaining_valence < 1) or (carbon2.remaining_valence < 1) or (carbon1.id == carbon2.id):
                raise InvalidBond
            carbon1.bind(carbon2)
        return self

    def mutate(self, *mutations: MutateTuple):
        if self.locked:
            raise LockedMolecule

        for (nc, nb, elt) in mutations:
            branch = self.get_branch(nb)
            carbon = branch[nc - 1]
            if carbon.used_valence > ELEMENTS_CONFIG[elt].valence:
                raise InvalidBond
            carbon.element = elt
        return self

    def add(self, *additions: AddTuple):
        if self.locked:
            raise LockedMolecule

        for (nc, nb, elt) in additions:
            branch = self.get_branch(nb)
            carbon = branch[nc - 1]
            if carbon.remaining_valence < 1:
                raise InvalidBond(f'Insert {elt} on {carbon} at branch {nb}')
            new_atom = self.create_atom(elt)
            carbon.bind(new_atom)
        return self

    def add_chaining(self, nc: int, nb: int, *elements: Element):
        if self.locked:
            raise LockedMolecule

        for el in elements[:-1]:
            if ELEMENTS_CONFIG[el].valence <= 1:
                raise InvalidBond

        branch = self.get_branch(nb)
        carbon = branch[nc - 1]
        current_atom = carbon
        for elt in elements:
            if current_atom.remaining_valence < 1:
                raise InvalidBond
            new_atom = self.create_atom(elt)
            current_atom.bind(new_atom)
            current_atom = new_atom
        return self

    def closer(self):
        if self.locked:
            raise LockedMolecule

        for atom in self.atoms:
            for _ in range(atom.remaining_valence):
                closing_hydrogen = self.create_atom('H')
                atom.bind(closing_hydrogen)

        self.locked = True
        return self

    def find_branch(self, atom):
        for branch in self.branches:
            if atom in branch:
                return branch
        return None

    def remove_from_all_branches(self, atom):
        for branch in self.branches:
            if atom in branch:
                branch.remove(atom)

    def unlock(self):
        if not self.locked:
            raise UnlockedMolecule

        self.locked = False
        atoms: List[Atom] = self.atoms

        hydrogens = []
        for atom in atoms:
            if atom.element == 'H':
                hydrogens.append(atom)

        for hydrogen in hydrogens:
            branch = self.find_branch(hydrogen)
            if branch:
                if len(branch) == 1:
                    all_bounded = list(sorted(hydrogen.bounded, key=lambda a: element_sort_key(a.element)))
                    new_branch_head = all_bounded[0]
                    self.lonely_atoms.append(new_branch_head)
                branch.remove(hydrogen)
            hydrogen.unbind_all()

        empty_branches_indices = []
        for i, branch in enumerate(self.branches):
            if len(branch) == 0:
                empty_branches_indices.append(i)

        for empty_idx in sorted(empty_branches_indices, reverse=True):
            self.branches.pop(empty_idx)

        if len(self.branches) == 0:
            raise EmptyMolecule

        remaining_atoms = []
        for branch in self.branches:
            for atom in branch:
                remaining_atoms.append(atom)

        all_remaining_atoms = self.get_all_atoms()

        all_remaining_atoms.sort(key=lambda a: a.id)

        for idx, atom in enumerate(all_remaining_atoms):
            atom.id = idx + 1

        self.id_counter = len(all_remaining_atoms) + 1
        return self


def test_methane():
    methane = Molecule('methane').brancher(1).closer()

    print(methane.branches)
    print(methane.formula)
    print(methane.molecular_weight)

def test_octane():
    octane = Molecule('octane').brancher(8).closer()

    print(octane.branches)
    print(octane.formula)
    print(octane.molecular_weight)

def test_cyclohexane():
    cyclohexane = Molecule('cyclohexane').brancher(6).bounder((1, 1, 6, 1)).closer()

    print(cyclohexane.branches)
    print(cyclohexane.formula)
    print(cyclohexane.molecular_weight)

def test_furane():
    furane = Molecule('furane').brancher(5).bounder((5, 1, 1, 1), (5, 1, 4, 1), (2, 1, 3, 1)).mutate((1, 1, 'O')).closer()

    print(furane.branches)
    print(furane.formula)
    print(furane.molecular_weight)

def test_benzene():
    benzene = (Molecule('benzene')
               .brancher(2, 2, 2)
               .inspect('BRANCHES_CREATED')
               .bounder((1, 1, 2, 1), (1, 2, 2, 2), (1, 3, 2, 3))
               .inspect('double bonds created')
               .bounder((2, 1, 1, 2))
               .inspect('bond between branch 1 atom 2 and branch 2 atom 1')
               .bounder((2, 2, 1, 3))
               .inspect('bond between branch 2 atom 2 and branch 3 atom 1')
               .bounder((2, 3, 1, 1))
               .inspect('bond between branch 3 atom 2 and branch 1 atom 1')
               .closer()
               .inspect('closed with hydrogen'))

    print('\nBENZENE:')
    print(benzene.branches)
    print(benzene.formula)
    print(benzene.molecular_weight)

def test_isopropylmagnesium_bromide():
    isopropylmagnesium_bromide = (Molecule('isopropylmagnesium_bromide').brancher(4, 1)
                                  .inspect('BRANCHES CREATED')
                                  .bounder((2, 1, 1, 2))
                                  .inspect('bond between branch 1 atom 2 and branch 2 atom 1')
                                  .mutate((3, 1, 'Mg'), (4, 1, 'Br'))
                                  .inspect('Mutated with Mg and Br')
                                  .closer()
                                  .inspect('closed with hydrogen'))

    print('\nISOPROPYLMAGNESIUM:')
    print(isopropylmagnesium_bromide.branches)
    print(isopropylmagnesium_bromide.formula)
    print(isopropylmagnesium_bromide.molecular_weight)

def test_failed():
    failed = (Molecule('failed').brancher(1, 5)
              .inspect('BRANCHES CREATED')
    .bounder((2, 2, 5, 2), (4, 2, 1, 1))
    .inspect('bounded')
    .mutate((1, 1, 'H'))
    .inspect('mutated')
    .brancher(3)
    .inspect('added branch of 3')
    .bounder((2, 3, 1, 3), (2, 3, 3, 3))
    .inspect('bounder')
    .closer()
    .inspect('closed with hydrogen')
              .unlock()
              .inspect('unlocked')
              .add((2, 2, 'P'))
    .inspect('add P to 2 2')
              .add((2, 1, 'P'))
              .inspect('add P to 2 1')
              )

    print('\nFAILED:')
    print(failed.atoms)
    print('EXPECTED')
    print("['Atom(C.1: C2)', 'Atom(C.2: C1,C3,C5,P9)', 'Atom(C.3: C2,C4)', 'Atom(C.4: C3,C5)', 'Atom(C.5: C2,C4)', 'Atom(C.6: C7,C7)', 'Atom(C.7: C6,C6,C8,C8)', 'Atom(C.8: C7,C7)', 'Atom(P.9: C2)']".replace("'", ''))
