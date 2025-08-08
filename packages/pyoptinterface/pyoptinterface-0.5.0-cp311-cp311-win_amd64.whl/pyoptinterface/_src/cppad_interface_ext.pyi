from collections.abc import Sequence
import enum


class graph_op(enum.Enum):
    abs = 0

    acos = 1

    acosh = 2

    add = 3

    asin = 4

    asinh = 5

    atan = 6

    atanh = 7

    atom4 = 8

    atom = 9

    azmul = 10

    cexp_eq = 11

    cexp_le = 12

    cexp_lt = 13

    comp_eq = 14

    comp_le = 15

    comp_lt = 16

    comp_ne = 17

    cos = 18

    cosh = 19

    discrete = 20

    div = 21

    erf = 22

    erfc = 23

    exp = 24

    expm1 = 25

    log1p = 26

    log = 27

    mul = 28

    neg = 29

    pow = 30

    print = 31

    sign = 32

    sin = 33

    sinh = 34

    sqrt = 35

    sub = 36

    sum = 37

    tan = 38

    tanh = 39

class cpp_graph_cursor:
    def __init__(self) -> None: ...

    @property
    def op_index(self) -> int: ...

    @property
    def arg_index(self) -> int: ...

class cpp_graph:
    def __init__(self) -> None: ...

    @property
    def n_dynamic_ind(self) -> int: ...

    @property
    def n_variable_ind(self) -> int: ...

    @property
    def n_constant(self) -> int: ...

    @property
    def n_dependent(self) -> int: ...

    @property
    def n_operator(self) -> int: ...

    @property
    def n_operator_arg(self) -> int: ...

    def constant_vec_get(self, arg: int, /) -> float: ...

    def dependent_vec_get(self, arg: int, /) -> int: ...

    def __str__(self) -> str: ...

    def get_cursor_op(self, arg: cpp_graph_cursor, /) -> graph_op: ...

    def get_cursor_n_arg(self, arg: cpp_graph_cursor, /) -> int: ...

    def get_cursor_args(self, arg: cpp_graph_cursor, /) -> list: ...

    def next_cursor(self, arg: cpp_graph_cursor, /) -> None: ...

class ADFunDouble:
    def __init__(self) -> None: ...

    @property
    def nx(self) -> int: ...

    @property
    def ny(self) -> int: ...

    @property
    def np(self) -> int: ...

    def to_graph(self, arg: cpp_graph, /) -> None: ...

class CppADAutodiffGraph:
    def __init__(self) -> None: ...

    @property
    def f(self) -> cpp_graph: ...

    @property
    def jacobian(self) -> cpp_graph: ...

    @property
    def hessian(self) -> cpp_graph: ...

def cppad_trace_graph_constraints(arg: "ExpressionGraph", /) -> ADFunDouble: ...

def cppad_trace_graph_objective(arg: "ExpressionGraph", /) -> ADFunDouble: ...

def cppad_autodiff(arg0: ADFunDouble, arg1: "AutodiffSymbolicStructure", arg2: CppADAutodiffGraph, arg3: Sequence[float], arg4: Sequence[float], /) -> None: ...
