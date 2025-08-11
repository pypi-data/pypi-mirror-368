from typing import Union
from warnings import warn

from sympy import nsolve, real_roots, solve


def solve_interval(eq, start: Union[float, int], end: Union[float, int], n=100, **kwargs):
    """Løs ligning numerisk i et interval.

    `solve_interval( ligning, start, slut )`

    Parametre
    ---
    - eq : ligning
        - En ligning med en ubekendt.

    - start : int, float
        - Start på intervallet hvor løsninger skal findes.

    - end : int, float
        - Slutningen på intervallet hvor løsninger skal findes.

    - n : int, default = 100
        - Antal gange der skal forsøges. `nsolve` kaldes n gange.

    - kwargs : Se `nsolve`

    Returnerer
    ---
    - solutions : list
        - Liste med fundne løsninger. Er tom hvis ingen løsninger blev fundet.

    Se også
    ---
    - [SymPy: Solve One or a System of Equations Numerically](https://docs.sympy.org/latest/guides/solving/solve-numerically.html)
    """

    solutions = []
    value_error = None
    n_warn, max_warn = 0, 10
    step = (end - start) / n
    for i in range(0, n):
        x0 = start + i * step
        try:
            solution = nsolve(eq, x0, **kwargs)
            if start <= solution <= end:
                solutions.append(solution)
        except ValueError as e:
            value_error = e
        except Exception as e:  # pragma: no cover
            if n_warn < max_warn:
                warn(str(e), stacklevel=2)
                n_warn += 1
    solutions = list(set(solutions))
    if len(solutions) == 0 and value_error is not None:
        warn(str(value_error), stacklevel=2)

    solutions.sort()
    return solutions


sympy_solve = solve


def solve(f, *args, **kwargs):
    """Løs ligning eller ligningssystem. Bygger ovenpå SymPy.solve, men benytter real_roots hvis relevant.

    `solve(ligning)`

    Parametre
    ---
    - f : Equation, list
        - Ligning eller liste med ligninger.

    Returnerer
    ---
    - solutions: list
        - Liste med løsninger.

    Se også
    ---
    - [SymPy: solve](https://docs.sympy.org/latest/modules/solvers/solvers.html#sympy.solvers.solvers.solve)
    - [SymPy: real_roots](https://docs.sympy.org/latest/modules/polys/reference.html#sympy.polys.polytools.real_roots)
    """
    try:
        if (f).is_polynomial():
            return [sol.evalf(5) for sol in real_roots(f, *args, **kwargs)]
    except Exception:
        return sympy_solve(f, *args, **kwargs)
    return sympy_solve(f, *args, **kwargs)
