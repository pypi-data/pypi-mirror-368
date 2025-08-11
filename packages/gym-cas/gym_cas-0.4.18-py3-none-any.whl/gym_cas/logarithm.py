from sympy import N, log


def log10(x: float):
    """Beregner 10-talslogaritmen.

    Parametre
    ---------
    - x : float
        - Værdien der skal udregnes logaritmen til.

    Returnerer
    ---------
    - y : float
        - Den beregnede værdi af logaritmen.

    Se også
    ---------
    - [SymPy: Exponentials and logarithms](https://docs.sympy.org/latest/tutorials/intro-tutorial/simplification.html#exponentials-and-logarithms)
    """
    return N(log(x, 10.0))
