from typing import Callable

from numpy import corrcoef
from numpy.polynomial import Polynomial
from spb import plot, plot_list
from spb.backends.base_renderer import Plot
from spb.defaults import TWO_D_B  # type: ignore
from sympy import Lambda, N, exp, latex, ln, simplify
from sympy.abc import t, x


def _reg_poly(x_points, y_points, deg):
    p = Polynomial.fit(x_points, y_points, deg)
    ps = simplify(p(x))

    yp = [float(N(p(x))) for x in x_points]
    r2 = float(corrcoef(yp, y_points)[0][1] ** 2)
    return Lambda(t, ps.subs(x, t)), r2


def _reg_pow(x_points, y_points, _):
    x_log = [float(N(ln(x))) for x in x_points]
    y_log = [float(N(ln(y))) for y in y_points]

    p = Polynomial.fit(x_log, y_log, 1)
    ps = exp(p.convert().coef[0]) * x ** p.convert().coef[1]

    f = Lambda(t, ps.subs(x, t))
    yp = [float(N(f(x))) for x in x_points]
    r2 = float(corrcoef(yp, y_points)[0][1] ** 2)
    return f, r2


def _reg_exp(x_points, y_points, _):
    y_log = [float(N(ln(y))) for y in y_points]

    p = Polynomial.fit(x_points, y_log, 1)
    ps = exp(p.convert().coef[0]) * exp(p.convert().coef[1]) ** x

    f = Lambda(t, ps.subs(x, t))
    yp = [float(N(f(x))) for x in x_points]
    r2 = float(corrcoef(yp, y_points)[0][1] ** 2)
    return f, r2


class RegressionFun:
    """
    Klasse til indkapsling af resultatet fra regression.

    Attributer
    ---
    f : Lambda
        Funktion.
    r2 : float
        Forklaringsgrad.
    plot : Plot
        Grafisk afbildning af funktion og datapunkter.
    """

    def __init__(self, f: Lambda, r2: float, plot: TWO_D_B):
        self.f = f
        self.r2 = r2
        self.plot = plot

    def __call__(self, *args):
        return self.f(*args)

    def __str__(self):
        return self.f.__str__()

    def _repr_latex_(self):
        return self.f._repr_latex_()


def _regression(
    x_points: list[float],
    y_points: list[float],
    deg: int,
    method: Callable[[list[float], list[float], int], tuple[Lambda, float]],
    *,
    show=True,
):
    fun, r2 = method(x_points, y_points, deg)

    p1 = plot_list(x_points, y_points, is_point=True, show=False, title=f"Forklaringsgrad $R^2 = {r2:.3}$")
    p2 = plot(fun(x), (x, min(x_points), max(x_points)), show=False, use_latex=True)
    if not (isinstance(p1, Plot) and isinstance(p2, Plot)):  # pragma: no cover
        msg = "Expected plots"
        raise TypeError(msg)
    plt = p1 + p2
    mul_symbol = None
    if method is _reg_exp:
        mul_symbol = "dot"
    plt.series[1]._latex_label = latex(plt.series[1].expr, mul_symbol=mul_symbol)
    if show:
        plt.show()

    return RegressionFun(fun, r2, plt)


def regression_poly(x_points: list[float], y_points: list[float], deg: int, *, show=True):
    """Polynomiel regression.

    - Lineær regression

    `regression_poly(x_points,y_points,1)`

    - Andre polynomier

    `regression_poly(x_points,y_points,deg)`

    Parametre
    ---
    - x_points, y_points : list
        - Datapunkter.

    - deg : int
        - Graden af polynomiet (ret linje er et førstegradspolynomium).

    - show : bool, default = True
        - Hvorvidt plot skal vises.

    Returnerer
    ---
    - RF : RegressionFun
       Objekt der indeholder funktion, forklaringsgrad og plotobjekt.
       De kan tilgås som hhv. `.f`, `.r2` og `.plot`.

    Se også
    ---
    - `regression_exp`, `regression_power`
    """
    return _regression(x_points, y_points, deg, _reg_poly, show=show)


def regression_power(x_points: list[float], y_points: list[float], *, show=True):
    """Potensregression.

    `regression_power(x_points,y_points)`

    Parametre
    ---
    - x_points, y_points : list
        - Datapunkter.

    - show : bool, default = True
        - Hvorvidt plot skal vises.

    Returnerer
    ---
    - RF : RegressionFun
       Objekt der indeholder funktion, forklaringsgrad og plotobjekt.
       De kan tilgås som hhv. `.f`, `.r2` og `.plot`.

    Se også
    ---
    - `regression_poly`, `regression_exp`
    """
    return _regression(x_points, y_points, 1, _reg_pow, show=show)


def regression_exp(x_points: list[float], y_points: list[float], *, show=True):
    """Eksponentiel regression.

    `regression_exp(x_points,y_points)`

    Parametre
    ---
    - x_points, y_points : list
        - Datapunkter.

    - show : bool, default = True
        - Hvorvidt plot skal vises.

    Returnerer
    ---
    - RF : RegressionFun
       Objekt der indeholder funktion, forklaringsgrad og plotobjekt.
       De kan tilgås som hhv. `.f`, `.r2` og `.plot`.

    Se også
    ---
    - `regression_poly`, `regression_power`
    """
    return _regression(x_points, y_points, 1, _reg_exp, show=show)
