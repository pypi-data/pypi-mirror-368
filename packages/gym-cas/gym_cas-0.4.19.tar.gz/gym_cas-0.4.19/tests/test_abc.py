from sympy import Symbol, diff

from gym_cas import a, pi, u, x, y, z


def test_abc():
    assert isinstance(a, Symbol)
    assert a.is_real
    assert isinstance(x, Symbol)
    assert x.is_real
    assert isinstance(y, Symbol)
    assert y.is_real
    assert isinstance(z, Symbol)
    assert z.is_real


def fun(x):
    return x**2 + x


def test_abc_fun():
    assert fun(u)
    assert fun(1) == 2
    assert diff(fun(x), x)


def test_pi():
    assert isinstance(pi, float)
