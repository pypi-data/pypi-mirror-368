# SPDX-FileCopyrightText: 2023-present JACS <jacs@zbc.dk>
#
# SPDX-License-Identifier: MIT
from math import pi
from warnings import filterwarnings

from numpy import mean, median, std, var
from spb import plot, plot3d_implicit, plot3d_list, plot3d_revolution, plot_geometry, plot_implicit, plot_list
from sympy import (
    Function,
    Matrix,
    N,
    Piecewise,
    Symbol,
    acos,
    asin,
    atan,
    cos,
    diff,
    dsolve,
    exp,
    expand,
    factor,
    integrate,
    limit,
    ln,
    log,
    nsolve,
    oo,
    simplify,
    sin,
    sqrt,
    symbols,
    tan,
)

from .__about__ import __version__
from .algebra import solve, solve_interval
from .config import _configure_spb
from .excel import excel_read
from .logarithm import log10
from .ode import plot_ode
from .plot_helpers import plot3d_points, plot_points
from .regression import regression_exp, regression_poly, regression_power
from .stat_plot import boxplot, plot_bars, plot_hist, plot_sum
from .stats import (
    degroup,
    frekvenstabel,
    group,
    group_mean,
    group_percentile,
    group_std,
    group_var,
    kvartiler,
    percentile,
)
from .trigonometry import Cos, Sin, Tan, aCos, aSin, aTan
from .vector import plot3d_line, plot3d_plane, plot3d_sphere, plot_vector, vector

filterwarnings("ignore", category=UserWarning, module="spb.series", lineno=1128)

a, b, c, d, e, f, g, h, i, j, k, l, m, n, o, p, q, r, s, t, u, v, w, x, y, z = symbols(
    "a b c d e f g h i j k l m n o p q r s t u v w x y z", real=True
)

_configure_spb()

__all__ = [
    "Cos",
    "Function",
    "Matrix",
    "N",
    "Piecewise",
    "Sin",
    "Symbol",
    "Tan",
    "__version__",
    "a",
    "aCos",
    "aSin",
    "aTan",
    "acos",
    "asin",
    "atan",
    "b",
    "boxplot",
    "c",
    "cos",
    "d",
    "degroup",
    "diff",
    "dsolve",
    "e",
    "excel_read",
    "exp",
    "expand",
    "f",
    "factor",
    "frekvenstabel",
    "g",
    "group",
    "group_mean",
    "group_percentile",
    "group_std",
    "group_var",
    "i",
    "integrate",
    "j",
    "k",
    "kvartiler",
    "l",
    "limit",
    "ln",
    "log",
    "log10",
    "m",
    "mean",
    "median",
    "n",
    "nsolve",
    "o",
    "oo",
    "p",
    "percentile",
    "pi",
    "plot",
    "plot3d_implicit",
    "plot3d_line",
    "plot3d_list",
    "plot3d_plane",
    "plot3d_points",
    "plot3d_revolution",
    "plot3d_sphere",
    "plot_bars",
    "plot_geometry",
    "plot_hist",
    "plot_implicit",
    "plot_list",
    "plot_ode",
    "plot_points",
    "plot_sum",
    "plot_vector",
    "q",
    "r",
    "regression_exp",
    "regression_poly",
    "regression_power",
    "s",
    "simplify",
    "sin",
    "solve",
    "solve_interval",
    "sqrt",
    "std",
    "symbols",
    "t",
    "tan",
    "u",
    "v",
    "var",
    "vector",
    "w",
    "x",
    "y",
    "z",
]
