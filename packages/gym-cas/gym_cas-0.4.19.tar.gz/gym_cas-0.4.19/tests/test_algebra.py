from pytest import warns

from gym_cas import c, cos, pi, solve, solve_interval, x

from .test_globals import _only_small_errors


def test_solve_interval():
    sol = solve_interval(x**2 + x * cos(x) ** 2 - 1, -10, 10)
    assert len(sol) == 2
    assert _only_small_errors(-1.10564834684030, sol[0])
    assert _only_small_errors(0.777969224724682, sol[1])

    sol = solve_interval(x**2 + x * cos(x) ** 2 - 1, -10, 0)
    assert len(sol) == 1
    assert _only_small_errors(-1.10564834684030, sol[0])

    with warns(UserWarning, match="Could not find root"):
        sol = solve_interval(x**2 + 1, -10, 10)
        assert len(sol) == 0


def test_solve():
    sol = solve(x**4 - 4.0 * x**2 - x + x * c + c)
    assert len(sol) == 1
    assert sol[0][c] is not None
    # [{c: x*(-x**3 + 4.0*x + 1.0)/(x + 1.0)}]

    sol = solve([c - x, 2.0 * c - x**2 + 10])
    assert len(sol) == 2
    assert any(_only_small_errors(s[c], -2.31662479035540) for s in sol)
    # [{c: -2.31662479035540, x: -2.31662479035540}, {c: 4.31662479035540, x: 4.31662479035540}]

    sol = solve(x**4 - 4.0 * x**2 - x + 1)
    assert len(sol) == 4
    # [-1.76, -0.694, 0.396, 2.06]

    # sol = solve([x**4 - 4.0 * x**2 - x + 1, 2 * c**2 - x**2], x, c)
    # assert len(sol) == 8

    sol = solve(x**2)
    assert sol == [0, 0]

    sol = solve(cos(x))
    assert len(sol) == 2
    assert any(_only_small_errors(s, pi / 2) for s in sol)
