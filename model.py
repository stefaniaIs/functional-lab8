"""Варіант 3. Калькулятор зі змінними: ADT Expr = Num | Var | Add | Mul."""

from __future__ import annotations

from dataclasses import dataclass
from typing import Literal, Protocol, TypeAlias


@dataclass(frozen=True, slots=True)
class Num:
    value: int


@dataclass(frozen=True, slots=True)
class Var:
    name: str


@dataclass(frozen=True, slots=True)
class Add:
    left: Expr
    right: Expr


@dataclass(frozen=True, slots=True)
class Mul:
    left: Expr
    right: Expr


Expr: TypeAlias = Num | Var | Add | Mul

# Обмежений набір операторів (Literal): використовується в рендері та фабриці вузлів
Op: TypeAlias = Literal["+", "*"]


class Env(Protocol):
    """Структурний контракт середовища: підходить dict, ChainMap, власні класи."""

    def get(self, key: str, /) -> int | None: ...


class UnboundVariableError(NameError):
    def __init__(self, name: str) -> None:
        super().__init__(f"variable '{name}' is not defined")
        self.name = name


def binop(op: Op, left: Expr, right: Expr) -> Expr:
    """Фабрика бінарного вузла за літералом оператора."""
    match op:
        case "+":
            return Add(left, right)
        case "*":
            return Mul(left, right)
