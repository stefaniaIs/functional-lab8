from collections import ChainMap
from dataclasses import FrozenInstanceError

import pytest

from evaluator import count_nodes, eval_expr, free_vars, simplify, substitute
from model import Add, Expr, Mul, Num, UnboundVariableError, Var, binop
from pretty import render, render_min

# (x + 2) * y
NESTED: Expr = Mul(Add(Var("x"), Num(2)), Var("y"))


class CountingEnv:
    """Власне середовище, сумісне з Protocol Env без наслідування."""

    def __init__(self, data: dict[str, int]) -> None:
        self.data, self.lookups = data, 0

    def get(self, key: str, /) -> int | None:
        self.lookups += 1
        return self.data.get(key)


def test_eval_basic() -> None:
    assert eval_expr(Num(5), {}) == 5
    assert eval_expr(Add(Num(2), Num(3)), {}) == 5
    assert eval_expr(Mul(Num(2), Num(3)), {}) == 6
    assert eval_expr(Var("a"), {"a": -7}) == -7


def test_eval_nested_with_env() -> None:
    assert eval_expr(NESTED, {"x": 3, "y": 4}) == 20


def test_eval_deep_tree() -> None:
    e: Expr = Num(0)
    for i in range(1, 101):
        e = Add(e, Mul(Var("k"), Num(i)))
    assert eval_expr(e, {"k": 2}) == 2 * 5050
    assert count_nodes(e) == 1 + 100 * 4


def test_missing_variable() -> None:
    with pytest.raises(UnboundVariableError) as ei:
        eval_expr(NESTED, {"x": 1})
    assert ei.value.name == "y"
    assert isinstance(ei.value, NameError)


def test_env_protocol_variants() -> None:
    env = CountingEnv({"x": 1, "y": 2})
    assert eval_expr(NESTED, env) == 6
    assert env.lookups == 2
    assert eval_expr(NESTED, ChainMap({"x": 1}, {"y": 2})) == 6


def test_render() -> None:
    assert render(NESTED) == "((x + 2) * y)"
    assert render_min(NESTED) == "(x + 2) * y"
    assert render_min(Add(Num(1), Mul(Num(2), Num(3)))) == "1 + 2 * 3"
    assert render_min(Mul(Num(-1), Var("x"))) == "(-1) * x"


def test_substitute_is_pure_and_partial() -> None:
    s = substitute(NESTED, {"x": 3})
    assert s == Mul(Add(Num(3), Num(2)), Var("y"))
    assert NESTED == Mul(Add(Var("x"), Num(2)), Var("y"))  # оригінал не змінився
    assert free_vars(s) == frozenset({"y"})
    assert eval_expr(s, {"y": 4}) == eval_expr(NESTED, {"x": 3, "y": 4})


def test_simplify() -> None:
    assert simplify(Add(Num(2), Num(3))) == Num(5)
    assert simplify(Add(Var("x"), Num(0))) == Var("x")
    assert simplify(Mul(Num(1), Var("x"))) == Var("x")
    assert simplify(Mul(Var("x"), Add(Num(0), Num(0)))) == Num(0)
    assert simplify(substitute(NESTED, {"x": 3})) == Mul(Num(5), Var("y"))
    assert simplify(NESTED) == NESTED


def test_free_vars_and_nodes() -> None:
    assert free_vars(NESTED) == frozenset({"x", "y"})
    assert free_vars(Num(1)) == frozenset()
    assert count_nodes(NESTED) == 5


def test_binop_literal_factory() -> None:
    assert binop("+", Num(1), Num(2)) == Add(Num(1), Num(2))
    assert binop("*", Var("a"), Num(2)) == Mul(Var("a"), Num(2))


def test_nodes_are_immutable_and_hashable() -> None:
    with pytest.raises(FrozenInstanceError):
        NESTED.left = Num(0)  # type: ignore[union-attr,misc]
    assert len({NESTED, Mul(Add(Var("x"), Num(2)), Var("y"))}) == 1
