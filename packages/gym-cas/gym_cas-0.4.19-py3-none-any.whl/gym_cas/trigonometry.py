from typing import Union

from sympy import N, Symbol, acos, asin, atan, cos, pi, sin, tan


def Sin(v: Union[float, Symbol]):
    """Udregner sinus til vinklen i grader.

    Parametre
    ---
    - v : float or Symbol
        - Vinkel.

    Returnerer
    ---
    - o : float or Expression
        - Sinusværdien.

    Se også
    ---
    - `aSin`, `Cos`, `Tan`
    """
    return N(sin(v * pi / 180))


def Cos(v: Union[float, Symbol]):
    """Udregner cosinus til vinklen i grader.

    Parametre
    ---
    - v : float or Symbol
        - Vinkel.

    Returnerer
    ---
    - o : float or Expression
        - Cosinusværdien.

    Se også
    ---
    - `aCos`, `Sin`, `Tan`
    """
    return N(cos(v * pi / 180))


def Tan(v: Union[float, Symbol]):
    """Udregner tangens til vinklen i grader.

    Parametre
    ---
    - v : float or Symbol
        - Vinkel.

    Returnerer
    ---
    - o : float or Expression
        - Tangensværdien.

    Se også
    ---
    - `aTan`, `Sin`, `Cos`
    """
    return N(tan(v * pi / 180))


def aSin(val: Union[float, Symbol]):
    """Udregner vinklen i grader til en sinusværdi.

    Parametre
    ---
    - val : float or Symbol
        - Sinusværdien.

    Returnerer
    ---
    - v : float or Expression
        - Vinklen.

    Se også
    ---
    - `Sin`, `aCos`, `aTan`
    """
    return N(asin(val) / pi * 180)


def aCos(val: Union[float, Symbol]):
    """Udregner vinklen i grader til en cosinusværdi.

    Parametre
    ---
    - val : float or Symbol
        - Cosinusværdien.

    Returnerer
    ---
    - v : float or Expression
        - Vinklen.

    Se også
    ---
    - `Cos`, `aSin`, `aTan`
    """
    return N(acos(val) / pi * 180)


def aTan(val: Union[float, Symbol]):
    """Udregner vinklen i grader til en tangensværdi.

    Parametre
    ---
    - val : float or Symbol
        - Tangensværdien.

    Returnerer
    ---
    - v : float or Expression
        - Vinklen.

    Se også
    ---
    - `Tan`, `aSin`, `aCos`
    """
    return N(atan(val) / pi * 180)
