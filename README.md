# Лабораторна робота №8 — Алгебраїчні типи даних «по-Python'івськи»

**Варіант 3. Калькулятор зі змінними.** Іщенко Стефанія, ФеП-22.

## Модель (`model.py`)
```python
Expr: TypeAlias = Num | Var | Add | Mul     # sum type, вузли - @dataclass(frozen=True, slots=True)
Op:   TypeAlias = Literal["+", "*"]          # обмежений набір операторів
class Env(Protocol):                         # будь-що з методом get(name) -> int | None
    def get(self, key: str, /) -> int | None: ...
```
`UnboundVariableError(NameError)` — для відсутньої змінної. `binop(op: Op, l, r)` — фабрика вузла за літералом.

## Операції (чисті функції з `match/case`)
| Функція | Файл | Що робить |
|---|---|---|
| `eval_expr(e, env)` | `evaluator.py` | обчислення в середовищі; відсутня змінна → `UnboundVariableError` |
| `substitute(e, env)` | `evaluator.py` | підстановка відомих змінних як `Num` (часткова), нове дерево |
| `simplify(e)` | `evaluator.py` | constant folding + `x+0`, `x*1`, `x*0` |
| `free_vars(e)`, `count_nodes(e)` | `evaluator.py` | вільні змінні (`frozenset`), кількість вузлів |
| `render(e)` / `render_min(e)` | `pretty.py` | повністю дужковане / мінімальні дужки за пріоритетом |

Усі `match` закінчуються `case _: assert_never(e)` — якщо додати новий вузол і забути його
обробити, `mypy --strict` покаже помилку.

`Env` як `Protocol`: `eval_expr` приймає `dict`, `ChainMap` і власний клас `CountingEnv`
(у тестах) без жодного наслідування.

## Тести (`tests/test_calc.py`, 11 шт.)
Базові вузли, вкладене дерево `(x + 2) * y`, глибоке дерево на 401 вузол, відсутня змінна,
різні реалізації `Env`, рендер, чистота `substitute`, `simplify`, `free_vars`, `binop`,
незмінність і хешованість вузлів.

## Запуск
```bash
pip install -r requirements.txt
pytest -q
mypy --strict .
python main.py
```
