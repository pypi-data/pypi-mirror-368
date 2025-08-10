"""Bit Vectors With Xes"""

from ._arithmetic import adc, add, div, lsh, matmul, mod, mul, neg, ngc, rsh, sbc, srsh, sub
from ._bits import (
    Array,
    ArrayLike,
    Bits,
    BitsLike,
    Composite,
    Empty,
    Key,
    Scalar,
    ScalarLike,
    UintLike,
    Vector,
    VectorLike,
    bits,
    i2bv,
    lit2bv,
    stack,
    u2bv,
)
from ._bitwise import and_, impl, ite, mux, not_, or_, xor
from ._code import decode, encode_onehot, encode_priority
from ._count import clz, cpop, ctz
from ._enum import Enum
from ._logical import land, lor, lxor
from ._predicate import eq, ge, gt, le, lt, match, ne, sge, sgt, sle, slt
from ._struct import Struct
from ._unary import uand, uor, uxor
from ._union import Union
from ._util import clog2
from ._word import cat, lrot, pack, rep, rrot, sxt, xt

# Alias Vector to Vec for brevity
Vec = Vector

__all__ = [
    # bits
    "Bits",
    "BitsLike",
    "Array",
    "ArrayLike",
    "Vector",
    "Vec",
    "Enum",
    "VectorLike",
    "Scalar",
    "ScalarLike",
    "Empty",
    "Composite",
    "Struct",
    "Union",
    "UintLike",
    "Key",
    # bitwise
    "not_",
    "or_",
    "and_",
    "xor",
    "impl",
    "ite",
    "mux",
    # count
    "cpop",
    "clz",
    "ctz",
    # logical
    "lor",
    "land",
    "lxor",
    # unary
    "uor",
    "uand",
    "uxor",
    # encode/decode
    "encode_onehot",
    "encode_priority",
    "decode",
    # arithmetic
    "add",
    "adc",
    "sub",
    "sbc",
    "neg",
    "ngc",
    "mul",
    "div",
    "mod",
    "matmul",
    "lsh",
    "rsh",
    "srsh",
    # word
    "xt",
    "sxt",
    "lrot",
    "rrot",
    "cat",
    "rep",
    "pack",
    # predicate
    "match",
    "eq",
    "ne",
    "lt",
    "le",
    "gt",
    "ge",
    "slt",
    "sle",
    "sgt",
    "sge",
    # factory
    "bits",
    "stack",
    "lit2bv",
    "u2bv",
    "i2bv",
    # util
    "clog2",
]
