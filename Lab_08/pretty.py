"""Текстове представлення виразу."""

from __future__ import annotations

from typing import assert_never

from model import Add, Expr, Mul, Num, Op, Var

# Пріоритет операторів для мінімальної кількості дужок
PRECEDENCE: dict[Op, int] = {"+": 1, "*": 2}


def render(e: Expr) -> str:
    """Повністю дужковане представлення: ((x + 2) * y)."""
    match e:
        case Num(value=v):
            return str(v)
        case Var(name=n):
            return n
        case Add(left=a, right=b):
            return f"({render(a)} + {render(b)})"
        case Mul(left=a, right=b):
            return f"({render(a)} * {render(b)})"
        case _:
            assert_never(e)


def render_min(e: Expr, parent: int = 0) -> str:
    """Дужки лише там, де їх вимагає пріоритет: (x + 2) * y."""
    match e:
        case Num(value=v):
            return str(v) if v >= 0 or parent == 0 else f"({v})"
        case Var(name=n):
            return n
        case Add(left=a, right=b):
            return _wrap("+", render_min(a, 1), render_min(b, 1), parent)
        case Mul(left=a, right=b):
            return _wrap("*", render_min(a, 2), render_min(b, 2), parent)
        case _:
            assert_never(e)


def _wrap(op: Op, left: str, right: str, parent: int) -> str:
    s = f"{left} {op} {right}"
    return f"({s})" if PRECEDENCE[op] < parent else s
