from math import acos, asin, atan, cos, pi, sin, tan

from sympy import zoo

from gym_cas import Cos, Sin, Tan, aCos, aSin, aTan

from .test_globals import _only_small_errors


def test_sin():
    assert _only_small_errors(Sin(90), 1)
    assert _only_small_errors(Sin(135), sin(135 * pi / 180))
    assert _only_small_errors(Sin(180), 0)
    assert _only_small_errors(Sin(45), sin(45 * pi / 180))
    assert _only_small_errors(Sin(0), 0)


def test_cos():
    assert _only_small_errors(Cos(90), 0)
    assert _only_small_errors(Cos(135), cos(135 * pi / 180))
    assert _only_small_errors(Cos(180), -1)
    assert _only_small_errors(Cos(45), cos(45 * pi / 180))
    assert _only_small_errors(Cos(0), 1)


def test_tan():
    assert _only_small_errors(Tan(45), 1)
    assert _only_small_errors(Tan(60), tan(60 * pi / 180))
    assert Tan(90) == zoo
    assert _only_small_errors(Tan(30), tan(30 * pi / 180))
    assert _only_small_errors(Tan(0), 0)


def test_asin():
    assert _only_small_errors(aSin(1), 90)
    assert _only_small_errors(aSin(0.5), asin(0.5) * 180 / pi)
    assert _only_small_errors(aSin(0), 0.0)
    assert _only_small_errors(aSin(0.75), asin(0.75) * 180 / pi)
    assert _only_small_errors(aSin(-1), -90)


def test_acos():
    assert _only_small_errors(aCos(1), 0)
    assert _only_small_errors(aCos(0.5), acos(0.5) * 180 / pi)
    assert _only_small_errors(aCos(0), 90)
    assert _only_small_errors(aCos(0.75), acos(0.75) * 180 / pi)
    assert _only_small_errors(aCos(-1), 180)


def test_atan():
    assert _only_small_errors(aTan(1), 45)
    assert _only_small_errors(aTan(0.5), atan(0.5) * 180 / pi)
    assert _only_small_errors(aTan(0), 0)
    assert _only_small_errors(aTan(0.75), atan(0.75) * 180 / pi)
    assert _only_small_errors(aTan(-1), -45)
