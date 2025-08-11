from spb import MB
from spb.series import Vector2DSeries
from sympy import Function, diff
from sympy.abc import t

from gym_cas import plot_ode


def test_plot_ode():
    f = Function("f")
    p = plot_ode(diff(f(t), t) - 5 * f(t) / t, (t, 1, 100), (f, 1, 100), show=False)  # type: ignore
    assert isinstance(p, MB)
    s = p.series
    assert len(s) == 1
    assert isinstance(s[0], Vector2DSeries)
    assert not s[0].is_streamlines
    assert s[0].get_data()[0][0][0] == 1.0
    assert s[0].get_label(False) == "(1, 5*y/t)"

    error = None
    try:
        p = plot_ode(diff(f(t), t, t) - 5 * f(t) / t, (t, 1, 100), (f, 1, 100), show=False)  # type: ignore
    except ValueError as e:
        error = e
    assert error is not None
