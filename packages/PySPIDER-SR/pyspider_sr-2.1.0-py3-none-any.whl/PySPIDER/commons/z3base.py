from __future__ import annotations

#from functools import lru_cache
from typing import Any, Tuple, List, assert_type # Protocol, Union
from abc import abstractmethod, ABC
from collections import defaultdict, Counter
from collections.abc import Callable, Iterable
from dataclasses import dataclass, KW_ONLY # field, replace
from itertools import count, permutations
import z3

lowercase_greek_letters = "αβγδεζηθικλμνξοπρστυφχψω"

@dataclass(frozen=True)
class SymmetryRep:
    _: KW_ONLY
    rank: int

    def __add__(self, other):
        print("Warning, SymmetryReps have been added")
        return FullRank(rank=self.rank + other.rank)

@dataclass(frozen=True)
class Antisymmetric(SymmetryRep):
    def __repr__(self):
        return f"Antisymmetric rank {self.rank}"

@dataclass(frozen=True)
class SymmetricTraceFree(SymmetryRep):
    def __repr__(self):
        return f"Symmetric trace-free rank {self.rank}"

@dataclass(frozen=True)
class FullRank(SymmetryRep):
    def __repr__(self):
        return f"Rank {self.rank}"

Irrep = Antisymmetric | SymmetricTraceFree | FullRank

@dataclass(frozen=True)
class IndexHole:
    def __lt__(self, other):
        if isinstance(other, IndexHole):
            return False
        elif isinstance(other, VarIndex):
            return True
        else:
            raise TypeError(
                f"Operation not supported between instances of "
                f"'{type(self)}' and '{type(other)}'"
            )

    def __gt__(self, other):
        if isinstance(other, (IndexHole, VarIndex)):
            return False
        else:
            raise TypeError(
                f"Operation not supported between instances of "
                f"'{type(self)}' and '{type(other)}'"
            )

    def __eq__(self, other):
        if not isinstance(other, IndexHole):
            return False
        else:
            return True

    def __repr__(self):
        return "{ }"

@dataclass(frozen=True)
class SMTIndex:
    var: z3.ArithRef
    src: Any = None

    def __lt__(self, other):
        return str(self.var) < str(other.var)

    def __eq__(self, other):
        if not isinstance(other, SMTIndex):
            raise TypeError(
                f"Operation not supported between instances of "
                f"'{type(self)}' and '{type(other)}'"
            )
        else:
            return self.var == other.var

    def __repr__(self):
        return f"{repr(self.var)}"

    def __hash__(self):
        return hash(self.var)

@dataclass(frozen=True)
class VarIndex:
    value: int
    src: Any = None

    def __lt__(self, other):
        if isinstance(other, str):
            return True # 't' always goes after spatial indices
        elif not isinstance(other, VarIndex):
            return NotImplemented
        else:
            return self.value < other.value

    def __eq__(self, other):
        if isinstance(other, str):
            return False # 't' is different from spatial indices
        elif not isinstance(other, VarIndex):
            return NotImplemented
        else:
            return self.value == other.value

    def __repr__(self):
        return lowercase_greek_letters[self.value]

    def __hash__(self):
        return hash(self.value)

@dataclass(frozen=True)
class LiteralIndex:
    value: int

    def __lt__(self, other):
        if isinstance(other, str):
            return True # 't' always goes after spatial indices
        elif not isinstance(other, LiteralIndex):
            raise TypeError(
                f"Operation not supported between instances of "
                f"'{type(self)}' and '{type(other)}'"
            )
        else:
            return self.value < other.value

    def __eq__(self, other):
        if isinstance(other, str):
            return True # 't' always goes after spatial indices
        elif not isinstance(other, LiteralIndex):
            raise TypeError(
                f"Operation not supported between instances of "
                f"'{type(self)}' and '{type(other)}'"
            )
        else:
            return self.value == other.value

    def __repr__(self):
        return "xyzt"[self.value]  # if your problem has 5 dimensions you messed up

Index = IndexHole | SMTIndex | VarIndex | LiteralIndex

# get rank of an Einstein expression by looking at its VarIndices/IndexHoles
# (for LiteralIndex, return 0)
def index_rank(indices: Iterable[VarIndex | IndexHole]):
    index_counter = Counter(indices)
    num_singles = len([
        count for index, count in index_counter.items() 
        if count == 1 and isinstance(index, VarIndex)
    ])
    num_holes = index_counter[IndexHole()]
    return num_singles+num_holes

# get highest index in list of indices
def highest_index(indices: Iterable[VarIndex]):
    # IndexHoles always count as the default of -1
    return max(
        (-1 if isinstance(index, IndexHole) else index.value) 
        for index in indices
    ) if indices else -1

@dataclass(frozen=True)
class EinSumExpr[T](ABC):
    _: KW_ONLY
    can_commute_indices: bool = False
    can_commute_exprs: bool = True

    @abstractmethod
    def __lt__(self, other):
        ...

    @abstractmethod
    def __eq__(self, other):
        ...

    # may need separate struct_eq if we need to manually check for terms 
    # commuting across *

    @abstractmethod
    def __repr__(self):
        ...

    def get_rank(self):
        match self.rank:
            case SymmetryRep(rank=rank):
                return rank
            case _ as rank:
                return rank

    @abstractmethod
    def sub_exprs(self) -> Iterable[EinSumExpr[T]]:
        """ Implementation returns list of sub_exprs 
        (whatever this attribute may be called) """
        ...

    @abstractmethod
    def own_indices(self) -> Iterable[T]:
        """ Implementation returns list of own indices """
        ...

    #@lru_cache(maxsize=10000)
    def all_indices(self) -> list[T]:
        # make sure these are in depth-first/left-to-right order
        """ List all indices """
        return (list(self.own_indices()) + 
                [idx for expr in self.sub_exprs() for idx in expr.all_indices()])

    @abstractmethod
    def eq_canon(self) -> Tuple[EinSumExpr[T], int]:
        """ Returns the canonical form of the term modulo equality rewrites 
        & the sign after rewrites. """
        ...

    @abstractmethod
    def map[T2](self, *,
                expr_map: Callable[[EinSumExpr[T]], EinSumExpr[T2]] = lambda x: x,
                index_map: Callable[[T], T2] = lambda x: x) -> EinSumExpr[T2]:
        """ Constructs a copy of self replacing (direct) child expressions 
        according to expr_map and (direct) child indices according to index_map"""
        ...

    def map_all_indices[T2](self, index_map: Callable[[T], T2]) -> EinSumExpr[T2]:
        def mapper(expr):
            nonlocal index_map
            return expr.map(expr_map=mapper, index_map=index_map)
        ms = mapper(self)
        #src_check = lambda x: x.src if hasattr(x, 'src') else None
        return ms

    def purge_indices(self): # return a copy with only IndexHoles
        return self.map_all_indices(index_map=lambda idx: IndexHole())

    def canonical_indexing_problem(
        self, idx_cache: defaultdict | None = None
    ) -> tuple[EinSumExpr[SMTIndex], list[z3.ExprRef]]:
        base_id = f"i{id(self)}"
        def next_z3_var():
            return free_z3_var(base_id)
        
        idx_cache = (defaultdict(next_z3_var) 
                     if idx_cache is None else idx_cache)
        
        constraints = []
        def emap(expr):
            nonlocal constraints
            updated, cxs = expr.canonical_indexing_problem(idx_cache)
            constraints += cxs
            return updated

        def imap(idx):
            if isinstance(idx, IndexHole):
                return SMTIndex(next_z3_var())
            #print(id(idx_cache), idx, len(idx_cache), idx_cache[idx])
            return SMTIndex(idx_cache[idx], src=idx)

        updated = self.map(expr_map=emap, index_map=imap)
        #print(id(idx_cache), list(idx_cache.items()))

        new_constraints = []
        if self.can_commute_indices:
            # constraint on own_indices
            #own_indices = sorted(list(updated.own_indices()))
            own_indices = list(updated.own_indices())
            for i, i_next in zip(own_indices, own_indices[1:]):
                # for reassignment, only add constraint if the first index 
                # in the pair isn't already constrained
                if i.src is None:
                    new_constraints.append(i.var <= i_next.var)
        if self.can_commute_exprs:
            duplicates = defaultdict(list)
            for e, e_new in zip(self.sub_exprs(), updated.sub_exprs()):
                #print(id(e), hash(e), [(se, hash(se)) for se in e.sub_exprs()], e)
                duplicates[e].append(e_new)
            for dup_list in duplicates.values():
                for e, e_next in zip(dup_list, dup_list[1:]):
                    new_constraints.append(
                        lexico_le(e.all_indices(), e_next.all_indices())
                    )
            #print(duplicates)

        #print(">>", updated, list(updated.own_indices()), new_constraints)
        constraints += new_constraints
        return updated, constraints

def generate_indexings(
    expr: EinSumExpr[IndexHole | VarIndex], autocorrect: bool = False
) -> Iterable[EinSumExpr[VarIndex]]:
    # includes lexicographic constraints
    indexed_expr, constraints = expr.canonical_indexing_problem()
    assert_type(indexed_expr, EinSumExpr[SMTIndex])
    #print(indexed_expr)
    #print(constraints)
    # add global constraints
    indices = indexed_expr.all_indices()
    n_single_inds = expr.rank
    n_total_inds = (len(indices)+n_single_inds)//2
    # use-next-variable constraints
    single_idx_max = 0
    paired_idx_max = n_single_inds
    for j, idx in enumerate(indices):
        s_idx_max_next = z3.Int(f's_idxmax_{j}')
        p_idx_max_next = z3.Int(f'p_idxmax_{j}')
        constraints += [z3.Or(
            z3.And(idx.var == single_idx_max,
                   s_idx_max_next == single_idx_max + 1, 
                   p_idx_max_next == paired_idx_max),
            z3.And(idx.var >= n_single_inds, idx.var <= paired_idx_max,
                   s_idx_max_next == single_idx_max,
                   p_idx_max_next == (paired_idx_max + 
                                       z3.If(idx.var == paired_idx_max, 1, 0))
                  )
        )]
        single_idx_max = s_idx_max_next
        paired_idx_max = p_idx_max_next
    constraints += [
        single_idx_max == n_single_inds, 
        paired_idx_max == n_total_inds
    ]
    # constrain number of appearances in pair
    for paired_idx in range(n_single_inds, n_total_inds):
       constraints.append(
           z3.AtMost(*[idx.var == paired_idx for idx in indices], 2)
       )
    # give problem to smt solver
    solver = z3.Solver()
    solver.add(*constraints)
    # smt solver finds a new solution
    while (result := solver.check()) == z3.sat:
        m = solver.model()
        indexing = {index: m[index.var] for index in indices}
        mapped_expr = indexed_expr.map_all_indices(
            index_map=lambda index: VarIndex(
                indexing[index].as_long(), src=index.src
            )
        )
        subexpr_commut_valid, first_perm = check_subexpr_cv(mapped_expr)
        if (subexpr_commut_valid and 
            check_commutative_validity(mapped_expr, list(mapped_expr.all_indices()))): 
            # check expression is actually valid
            yield mapped_expr
        else:
            if autocorrect:
                # print(first_perm, check_commutative_validity(
                #     mapped_expr, list(mapped_expr.all_indices())
                # )) 
                #print(f"{mapped_expr} failed the test")
                mapped_expr = secv_canon(mapped_expr, start=first_perm)
                yield mapped_expr
        # prevent smt solver from repeating solution
        solver.add(
            z3.Or(*[idx.var != val for idx, val in indexing.items()])
        )
    if result == z3.unknown:
        raise RuntimeError("Could not solve SMT problem :(")
    #print(solver.to_smt2())

def lexico_le(idsA: list[SMTIndex], idsB: list[SMTIndex]) -> z3.ExprRef:
    lt = True
    for a, b in zip(reversed(idsA), reversed(idsB)):
        lt = z3.Or(a.var < b.var, z3.And(a.var == b.var, lt))
    return lt

# check whether this term is canonical with respect to the own_indices 
# of commutative expressions
def check_commutative_validity(
    mapped_expr: EinSumExpr[VarIndex], 
    all_indices: List[VarIndex], 
    inds_to_left: int = 0
) -> bool: 
    if mapped_expr.can_commute_indices: # check commutative indices
        commuting_inds = list(mapped_expr.own_indices())
        in_com_inds = lambda idx: idx in commuting_inds
        must_be_sorted = (
            list(filter(in_com_inds, all_indices[:inds_to_left]))
            + [commuting_inds[i] for i in range(1, len(commuting_inds)) 
               if commuting_inds[i-1] == commuting_inds[i]]
            + list(filter(in_com_inds, 
                         all_indices[inds_to_left + len(commuting_inds):]))
        )
        #print(must_be_sorted)
        if any(must_be_sorted[i] < must_be_sorted[i-1] 
               for i in range(1, len(must_be_sorted))):
            return False
        
    for subexpr in mapped_expr.sub_exprs():
        if not check_commutative_validity(subexpr, all_indices, inds_to_left):
            return False
        inds_to_left += len(list(subexpr.all_indices()))
    return True   

# check if canonicity violated by relabel+sort (only a little messy)
def check_subexpr_cv(mapped_expr: EinSumExpr[VarIndex]):
    first_bound_ind = mapped_expr.rank
    last_bound_ind = highest_index(mapped_expr.all_indices())
    bound_inds = list(range(first_bound_ind, last_bound_ind+1))
    for i, perm in enumerate(permutations(bound_inds)):
        if perm != bound_inds:
            imap = lambda i: (VarIndex(perm[i.value-first_bound_ind]) 
                              if i.value in bound_inds else i)
            relabeled_expr = mapped_expr.map_all_indices(imap)
            if (relabeled_expr.eq_canon()[0].all_indices() < 
                mapped_expr.all_indices()):
                #print(mapped_expr, mapped_expr.all_indices(), perm, bound_inds, i)
                return False, i
    return True, -1

# canonicalize wrt relabel+sort if necessary
def secv_canon(expr: EinSumExpr[VarIndex], start: int = 0):
    # check commutative expressions at base by relabel+sort 
    # (only a little messy)
    first_bound_ind = expr.rank
    last_bound_ind = highest_index(expr.all_indices())
    bound_inds = list(range(first_bound_ind, last_bound_ind+1))
    best_expr = expr
    for perm in list(permutations(bound_inds))[start:]:
        #print(bound_inds, perm)
        # imap = lambda i: VarIndex(perm[i.value-first_bound_ind]) 
        #         if (isinstance(i, VarIndex) and i.value in bound_inds) else i
        imap = lambda i: (VarIndex(perm[i.value-first_bound_ind]) 
                          if i.value in bound_inds else i)
        relabeled_expr = expr.map_all_indices(imap)
        relabeled_ec = relabeled_expr.eq_canon()[0]
        if relabeled_ec.all_indices() < best_expr.all_indices():
            best_expr = relabeled_ec
    #print(expr, '->', best_expr)
    return best_expr

def free_z3_var(prefix: str, *, ctr=count()):
    return z3.Int(f"{prefix}_{next(ctr)}")
