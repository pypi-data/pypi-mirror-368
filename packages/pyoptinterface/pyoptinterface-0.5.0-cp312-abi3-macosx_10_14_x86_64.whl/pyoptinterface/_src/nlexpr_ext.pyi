from collections.abc import Sequence
import enum

import pyoptinterface._src.core_ext


class ArrayType(enum.Enum):
    Constant = 0

    Variable = 1

    Parameter = 2

    Unary = 3

    Binary = 4

    Ternary = 5

    Nary = 6

class UnaryOperator(enum.Enum):
    Neg = 0

    Sin = 1

    Cos = 2

    Tan = 3

    Asin = 4

    Acos = 5

    Atan = 6

    Abs = 7

    Sqrt = 8

    Exp = 9

    Log = 10

    Log10 = 11

class BinaryOperator(enum.Enum):
    Sub = 0

    Div = 1

    Pow = 2

    LessThan = 3

    LessEqual = 4

    Equal = 5

    NotEqual = 6

    GreaterEqual = 7

    GreaterThan = 8

class TernaryOperator(enum.Enum):
    IfThenElse = 0

class NaryOperator(enum.Enum):
    Add = 0

    Mul = 1

class ExpressionHandle:
    def __init__(self, arg0: ArrayType, arg1: int, /) -> None: ...

    @property
    def array(self) -> ArrayType: ...

    @property
    def id(self) -> int: ...

class UnaryNode:
    def __init__(self, arg0: UnaryOperator, arg1: ExpressionHandle, /) -> None: ...

    @property
    def op(self) -> UnaryOperator: ...

    @property
    def operand(self) -> ExpressionHandle: ...

class BinaryNode:
    def __init__(self, arg0: BinaryOperator, arg1: ExpressionHandle, arg2: ExpressionHandle, /) -> None: ...

    @property
    def op(self) -> BinaryOperator: ...

    @property
    def left(self) -> ExpressionHandle: ...

    @property
    def right(self) -> ExpressionHandle: ...

class NaryNode:
    def __init__(self, arg0: NaryOperator, arg1: Sequence[ExpressionHandle], /) -> None: ...

    @property
    def op(self) -> NaryOperator: ...

    @property
    def operands(self) -> list[ExpressionHandle]: ...

class ExpressionGraph:
    def __init__(self) -> None: ...

    def __str__(self) -> str: ...

    def n_variables(self) -> int: ...

    def n_parameters(self) -> int: ...

    def add_variable(self, id: int = 0) -> ExpressionHandle: ...

    def add_constant(self, value: float) -> ExpressionHandle: ...

    def add_parameter(self, id: int = 0) -> ExpressionHandle: ...

    def add_unary(self, arg0: UnaryOperator, arg1: ExpressionHandle, /) -> ExpressionHandle: ...

    def add_binary(self, arg0: BinaryOperator, arg1: ExpressionHandle, arg2: ExpressionHandle, /) -> ExpressionHandle: ...

    def add_ternary(self, arg0: TernaryOperator, arg1: ExpressionHandle, arg2: ExpressionHandle, arg3: ExpressionHandle, /) -> ExpressionHandle: ...

    def add_nary(self, arg0: NaryOperator, arg1: Sequence[ExpressionHandle], /) -> ExpressionHandle: ...

    def add_repeat_nary(self, arg0: NaryOperator, arg1: ExpressionHandle, arg2: int, /) -> ExpressionHandle: ...

    def append_nary(self, arg0: ExpressionHandle, arg1: ExpressionHandle, /) -> None: ...

    def get_nary_operator(self, arg: ExpressionHandle, /) -> NaryOperator: ...

    def add_constraint_output(self, arg: ExpressionHandle, /) -> None: ...

    def add_objective_output(self, arg: ExpressionHandle, /) -> None: ...

    def merge_variableindex(self, arg: pyoptinterface._src.core_ext.VariableIndex, /) -> ExpressionHandle: ...

    def merge_scalaraffinefunction(self, arg: pyoptinterface._src.core_ext.ScalarAffineFunction, /) -> ExpressionHandle: ...

    def merge_scalarquadraticfunction(self, arg: pyoptinterface._src.core_ext.ScalarQuadraticFunction, /) -> ExpressionHandle: ...

    def merge_exprbuilder(self, arg: pyoptinterface._src.core_ext.ExprBuilder, /) -> ExpressionHandle: ...

    def is_compare_expression(self, arg: ExpressionHandle, /) -> bool: ...

def unpack_comparison_expression(arg0: ExpressionGraph, arg1: ExpressionHandle, arg2: float, /) -> tuple[ExpressionHandle, float, float]: ...
