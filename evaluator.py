"""Чисті функції над Expr через match/case."""

from __future__ import annotations

from typing import assert_never

from model import Add, Env, Expr, Mul, Num, UnboundVariableError, Var


def eval_expr(e: Expr, env: Env) -> int:
    """Обчислює вираз у середовищі env; відсутня змінна -> UnboundVariableError."""
    match e:
        case Num(value=v):
            return v
        case Var(name=n):
            value = env.get(n)
            if value is None:
                raise UnboundVariableError(n)
            return value
        case Add(left=a, right=b):
            return eval_expr(a, env) + eval_expr(b, env)
        case Mul(left=a, right=b):
            return eval_expr(a, env) * eval_expr(b, env)
        case _:
            assert_never(e)


def substitute(e: Expr, env: Env) -> Expr:
    """Підставляє відомі змінні як Num; невідомі лишає. Повертає НОВЕ дерево."""
    match e:
        case Num():
            return e
        case Var(name=n):
            value = env.get(n)
            return e if value is None else Num(value)
        case Add(left=a, right=b):
            return Add(substitute(a, env), substitute(b, env))
        case Mul(left=a, right=b):
            return Mul(substitute(a, env), substitute(b, env))
        case _:
            assert_never(e)


def simplify(e: Expr) -> Expr:
    """Constant folding + алгебраїчні тотожності: x+0, x*1, x*0."""
    match e:
        case Num() | Var():
            return e
        case Add(left=a, right=b):
            match (simplify(a), simplify(b)):
                case (Num(value=x), Num(value=y)):
                    return Num(x + y)
                case (Num(value=0), other) | (other, Num(value=0)):
                    return other
                case (l, r):
                    return Add(l, r)
        case Mul(left=a, right=b):
            match (simplify(a), simplify(b)):
                case (Num(value=x), Num(value=y)):
                    return Num(x * y)
                case (Num(value=0), _) | (_, Num(value=0)):
                    return Num(0)
                case (Num(value=1), other) | (other, Num(value=1)):
                    return other
                case (l, r):
                    return Mul(l, r)
        case _:
            assert_never(e)
    raise AssertionError("unreachable")  # pragma: no cover


def free_vars(e: Expr) -> frozenset[str]:
    match e:
        case Num():
            return frozenset()
        case Var(name=n):
            return frozenset({n})
        case Add(left=a, right=b) | Mul(left=a, right=b):
            return free_vars(a) | free_vars(b)
        case _:
            assert_never(e)


def count_nodes(e: Expr) -> int:
    match e:
        case Num() | Var():
            return 1
        case Add(left=a, right=b) | Mul(left=a, right=b):
            return 1 + count_nodes(a) + count_nodes(b)
        case _:
            assert_never(e)
