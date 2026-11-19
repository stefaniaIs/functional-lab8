from evaluator import count_nodes, eval_expr, free_vars, simplify, substitute
from model import Add, Mul, Num, UnboundVariableError, Var, binop
from pretty import render, render_min


def main() -> None:
    # (x + 2) * (y + 0) + 3 * 4
    e = Add(Mul(Add(Var("x"), Num(2)), Add(Var("y"), Num(0))), Mul(Num(3), Num(4)))
    env = {"x": 5, "y": 10}
    print("Вираз:      ", render(e))
    print("Мін. дужки: ", render_min(e))
    print("Змінні:     ", sorted(free_vars(e)), "вузлів:", count_nodes(e))
    print("eval з", env, "=", eval_expr(e, env))
    partial_e = substitute(e, {"x": 5})
    print("Підстановка x=5:", render_min(partial_e))
    print("Спрощення:      ", render_min(simplify(partial_e)))
    print("binop('*', ...):", render(binop("*", Num(2), Var("z"))))
    try:
        eval_expr(e, {"x": 1})
    except UnboundVariableError as err:
        print("Помилка:", err)


if __name__ == "__main__":
    main()
