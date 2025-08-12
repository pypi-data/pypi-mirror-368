from gym_cas import exp, ln, log, log10

from .test_globals import _only_small_errors


def test_log():
    assert log(exp(2)) == 2
    assert log(1) == 0


def test_ln():
    assert ln(exp(2)) == 2
    assert ln(1) == 0


def test_log10():
    assert _only_small_errors(log10(10), 1)
    assert log10(1) == 0
