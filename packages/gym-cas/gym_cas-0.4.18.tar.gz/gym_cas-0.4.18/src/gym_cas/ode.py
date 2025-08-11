from spb import plot_vector
from sympy import classify_ode, diff, solve
from sympy.abc import y


def plot_ode(ode, x_range, f_range, n=15, **kwargs):
    """Afbild et linjefelt

    Parametre
    ---------
    - ode : Expression
        - 1. ordens differentialligning.

    - x_range : tuple
        - Interval for den uafhængige variabel (x, start, stop)

    - f_range : tuple
        - Interval for den afhængige variabel (f, start, stop)

    - n : int, optional
        - Antallet af punkter (i begge retninger). Standardværdi: 15

    - kwargs : se `vector_field_2d`

    Returnerer
    ---------
    - plt : Plot
        - Plotobjektet.

    Se også
    ---------
    - [SPB: vector_field_2d](https://sympy-plot-backends.readthedocs.io/en/latest/modules/graphics/vectors.html#spb.graphics.vectors.vector_field_2d)
    """

    if "1st_linear" not in classify_ode(ode):
        e = "plot_ode virker kun med differentialligninger af første grad."
        raise ValueError(e)

    kwargs.setdefault("use_cm", False)
    kwargs.setdefault("scalar", False)
    kwargs.setdefault("quiver_kw", {"color": "black", "headwidth": 5})

    x, f = x_range[0], f_range[0]
    df = solve(ode, diff(f(x), x))[0].replace(f(x), y)

    f_range = (y, f_range[1], f_range[2])

    return plot_vector([1, df], x_range, f_range, n=n, **kwargs)
