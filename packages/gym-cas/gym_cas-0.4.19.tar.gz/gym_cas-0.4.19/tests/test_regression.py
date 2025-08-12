from spb import MB
from sympy.core.numbers import Float

from gym_cas import regression_exp, regression_poly, regression_power


def test_linear():
    f = regression_poly([1, 2, 3, 4], [3, 6, 12, 4], 1, show=False)
    assert callable(f)
    assert isinstance(f(2.0),Float)
    assert isinstance(f.r2, float)
    assert isinstance(f.plot, MB)
    assert str(f) is not None
    assert f._repr_latex_() is not None


def test_poly():
    f = regression_poly([1, 2, 3, 4], [3, 6, 12, 4], 3, show=False)
    assert callable(f)
    assert isinstance(f(2.0),Float)
    assert isinstance(f.r2, float)
    assert isinstance(f.plot, MB)


def test_power():
    f = regression_power([1, 2, 3], [3, 6, 12], show=False)
    assert callable(f)
    assert isinstance(f(2.0),Float)
    assert isinstance(f.r2, float)
    assert isinstance(f.plot, MB)


def test_exp():
    f = regression_exp([1, 2, 3], [3, 6, 12], show=False)
    assert callable(f)
    assert isinstance(f(2.0),Float)
    assert isinstance(f.r2, float)
    assert isinstance(f.plot, MB)
