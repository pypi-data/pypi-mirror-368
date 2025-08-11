from math import floor
from typing import Union

from numpy import linspace, mean, median, percentile, unique
from sympy import sqrt

from .globals import ELEMENTS_IN_INTERVAL

ROUNDING_ERROR_ALLOWED = 10e-6


def _check_len_groups(x, groups):
    if hasattr(groups[0], "__iter__"):
        if len(groups[0]) != ELEMENTS_IN_INTERVAL:
            msg = "Each list in groups must be of size 2 (start and end of interval)."
            raise ValueError(msg)

    if hasattr(x[0], "__iter__"):
        x = x[0]

    if hasattr(groups[0], "__iter__"):
        if len(groups) != len(x):
            msg = f"The length of groups ({len(groups)}) as a 2d list must match the length of observations ({len(x)})."
            raise ValueError(msg)
    elif len(groups) != len(x) + 1:
        msg = f"The length of groups ({len(groups)}) as a 1d list must match the length of observations ({len(x)}+1)."
        raise ValueError(msg)


def _group_1d_to_2d(edges):
    result = []
    prev = edges[0]
    for i in range(1, len(edges)):
        result.append([prev, edges[i]])
        prev = edges[i]
    return result


def _group_2d_to_1d(edges):
    result = [edges[0][0]]
    for e in edges:
        result.append(e[1])
    return result


def _degroup_2d(x, edges):
    """
    Transform list of observations between edges.
    Each element in edges must contain start end end.
    The length of edges must be equal to the length of x
    """
    _check_len_groups(x, edges)
    data = []
    for i, xx in enumerate(x):
        data += linspace(edges[i][0], edges[i][1], xx + 2).tolist()[1:-1]
    return data


def degroup(x, groups):
    """Transformer grupperet data til enkelte observationer indenfor hvert interval.
    Det antages at observationer er uniformt fordelt i hvert interval.

    Parametre
    ---
    - x : list
        - Et eller flere datasæt med observationer.

    - groups : list, optional
        - Liste med start og slut for hver interval. Hvert element kan bestå af en eller to værdier.
        Hvis hvert element består af 1 værdi skal listen indeholde n+1 elementer hvor n er antallet er observationer.
        Ellers skal den indeholde n elementer.
        Der kan angives en liste med grupperinger for alle datasæt eller lister med grupperinger for hvert datasæt som
        hver især overholder ovenstående betingelser.

    Returnerer
    ---
    - data : list
        - Liste eller indlejret lister med transformerede datasæt.

    Se også
    ---
    - `group`
    """
    data = []
    if hasattr(groups[0], "__iter__"):
        if hasattr(groups[0][0], "__iter__"):
            for i, xx in enumerate(x):
                _check_len_groups(xx, groups[i])
                data.append(_degroup_2d(xx, groups[i]))
            return data

        if len(groups[0]) == ELEMENTS_IN_INTERVAL:
            _check_len_groups(x, groups)
            if hasattr(x[0], "__iter__"):
                for xx in x:
                    data.append(_degroup_2d(xx, groups))
                return data
            else:
                return _degroup_2d(x, groups)
        else:
            for i, xx in enumerate(x):
                _check_len_groups(xx, groups[i])
                data.append(_degroup_2d(xx, _group_1d_to_2d(groups[i])))
            return data

    _check_len_groups(x, groups)
    if hasattr(x[0], "__iter__"):
        for xx in x:
            data.append(_degroup_2d(xx, _group_1d_to_2d(groups)))
        return data
    else:
        return _degroup_2d(x, _group_1d_to_2d(groups))


def group(x: list, groups):
    """Grupper observationer i halvåbne intervaller ]a,b] hvor a < b.

    Parametre
    ---
    - x : list
        - Et datasæt med observationer.

    - groups : list, optional
        - Liste med start og slut for hver interval. Hvert element kan bestå af en eller to værdier.

    Returnerer
    ---
    - data : list
        - Liste eller indlejret lister med transformerede datasæt.

    Se også
    ---
    - `degroup`
    """
    if not hasattr(groups[0], "__iter__"):
        groups = _group_1d_to_2d(groups)

    x.sort()
    idx = 0
    outliers = 0
    while idx < len(x) and x[idx] <= groups[0][0]:
        outliers += 1
        idx += 1

    result = [0] * len(groups)
    for i, g in enumerate(groups):
        while idx < len(x) and x[idx] <= g[1]:
            result[i] += 1
            idx += 1

    outliers += len(x) - idx - 1
    if outliers > 0:
        warn = f"{outliers} observations were outside the given group intervals."
        raise Warning(warn)
    return result


class FrequencyTable:
    observation: list
    total: int
    hyppighed: list
    frekvens: list
    kumuleret_frekvens: list

    def __init__(self, x: list):
        self.total = len(x)
        hyp = unique(x, return_counts=True)
        self.observation = hyp[0].tolist()
        self.hyppighed = hyp[1].tolist()
        self.init_freq()

    def init_freq(self):
        self.frekvens = []
        self.kumuleret_frekvens = []
        kf = 0
        for i in range(len(self.observation)):
            f = self.hyppighed[i] / self.total * 100
            self.frekvens.append(f)
            kf += f
            self.kumuleret_frekvens.append(kf)

    def __str__(self):
        names = ["Observation", "Hyppighed", "Frekvens %", "Kumuleret frekvens %"]
        if isinstance(self, FrequencyTableGrouped):
            names[0] = "Observationsinterval"
        s = "| "
        lens = []
        for n in names:
            s += f"{n} | "
            lens.append(len(n))
        s = s[:-1]
        s += "\n| "
        for n in range(len(names)):
            s += "-" * (lens[n] - 1) + ": | "
        s += "\n| "
        for i in range(len(self.observation)):
            for k, n in enumerate([self.observation, self.hyppighed, self.frekvens, self.kumuleret_frekvens]):
                if hasattr(n[i], "__iter__") and len(n[i]) == ELEMENTS_IN_INTERVAL:
                    if isinstance(n[i][0], float):
                        stub = f"] {n[i][0]:.5} ;"
                    else:
                        stub = f"] {n[i][0]} ;"
                    s += " " * (floor(lens[k] / 2) - len(stub)) + stub
                    if isinstance(n[i][1], float):
                        stub = f" {n[i][1]:.5} ]"
                    else:
                        stub = f" {n[i][1]} ]"
                    s += stub + " " * (floor(lens[k] / 2) - len(stub)) + " | "
                elif isinstance(n[i], float):
                    s += f"{n[i]:>{lens[k]}.5} | "
                else:
                    s += f"{n[i]:>{lens[k]}} | "
            if i < len(self.observation) - 1:
                s += "\n| "
        return s


class FrequencyTableGrouped(FrequencyTable):
    def __init__(self, x: list, groups: list):
        self.total = sum(x)
        self.observation = []
        self.hyppighed = x

        _check_len_groups(x, groups)
        if hasattr(groups[0], "__iter__"):
            for g in groups:
                self.observation.append(g)
        else:
            for i in range(len(groups) - 1):
                self.observation.append([groups[i], groups[i + 1]])

        self.init_freq()


def frekvenstabel(x, groups: Union[None, list] = None, *, show=True):
    """Beregn hyppighed, frekvenser og kumulerede frekvenser af et datasæt.

    Parametre
    ---
    - x : list
        - Et datasæt med ugrupperede eller grupperede observationer.

    - groups : list, optional
        - Liste med start og slut for hver interval. Hvert element kan bestå af en eller to værdier.
        Hvis hvert element består af 1 værdi skal listen indeholde n+1 elementer hvor n er antallet er observationer.
        Ellers skal den indeholde n elementer.

    - show : boolean, default = True
        - Skal resultaterne printes?

    Returnerer
    ---
    - table : FrequencyTable or FrequencyTableGrouped
        - Objekt indeholdende hyppighed, frekvenser og kumulerede frekvenser.

    Se også
    ---
    - `kvartiler`
    """
    if hasattr(x[0], "__iter__"):
        msg = "x must be list of elements."
        raise ValueError(msg)

    if groups is None:
        table = FrequencyTable(x)
    else:
        table = FrequencyTableGrouped(x, groups)
    if show:
        print(table)
    return table


def kvartiler(data: list, n=(0, 1, 2, 3, 4)):
    """Beregn kvartiler med medianmetoden for et ugrupperet datasæt.
    Q2 er medianen for hele datasættet. Q1 og Q3 er medianer for hhv. nedre og øvre halvdele af datasættet.
    Hvis datasættet indeholder et ulige antal observationer så medtages den midterste observation ikke i beregning af Q1
    og Q3.

    Parametre
    ---
    - data : list
        - Et ugrupperet datasæt.

    - n : Iterable, default = (0,1,2,3,4)
        - Liste med heltal der markerer hvilke kvartiler og i hvilken rækkefølge de returneres.
        Standard er alle 5 dvs. fra Q0 til Q4.

    Returnerer
    ---
    - kvartiler : list
        - Liste med kvartiler.

    Se også
    ---
    - `frekvenstabel`
    """
    data.sort()

    l2 = len(data) // 2
    lower = data[0:l2]
    higher = data[-l2:]
    results = [min(data), median(lower), median(data), median(higher), max(data)]
    return [results[i] for i in n]


# Sørg for at numpy's percentile der eksporteres herfra bruger samme "sumkurve" antagelse for percentiler som systime.
percentile._implementation.__defaults__ = (None, None, False, "inverted_cdf", False)  # pyright: ignore[reportFunctionMemberAccess]


def group_percentile(data, groups, q):
    """Beregn percentiler for et grupperet datasæt hvor der antages uniform fordeling i intervallerne.

    Parametre
    ---
    - data : list
        - Et datasæt med grupperede observationer.

    - groups : list, optional
        - Liste med start og slut for hver interval. Hvert element kan bestå af en eller to værdier.
        Hvis hvert element består af 1 værdi skal listen indeholde n+1 elementer hvor n er antallet er observationer.
        Ellers skal den indeholde n elementer.

    - q : float or list
        - Percentiler der skal beregnes angivet som kommatal eller liste med kommatal.

    Returnerer
    ---
    - percentiles : list
        - Liste med beregnede percentiler.

    Se også
    ---
    - `group_mean`, `group_var`, `group_std`
    """
    f = frekvenstabel(data, groups, show=False)
    if not hasattr(q, "__iter__"):
        q = [q]
    results = []
    for qq in q:
        i = next(i for i, v in enumerate(f.kumuleret_frekvens) if (v >= qq or abs(qq - v) < ROUNDING_ERROR_ALLOWED))
        if i == 0:
            x1 = 0
        else:
            x1 = f.kumuleret_frekvens[i - 1]
        results.append(
            ((f.observation[i][1] - f.observation[i][0]) / (f.kumuleret_frekvens[i] - x1)) * (qq - x1)
            + f.observation[i][0]
        )
    if len(results) == 1:
        return results[0]
    return results


def group_mean(data, groups):
    """Beregn gennemsnit for et grupperet datasæt hvor der antages uniform fordeling i intervallerne.

    Parametre
    ---
    - data : list
        - Et datasæt med grupperede observationer.

    - groups : list, optional
        - Liste med start og slut for hver interval. Hvert element kan bestå af en eller to værdier.
        Hvis hvert element består af 1 værdi skal listen indeholde n+1 elementer hvor n er antallet er observationer.
        Ellers skal den indeholde n elementer.

    Returnerer
    ---
    - mean : float
        - Gennemsnit.

    Se også
    ---
    - `group_precentiles`, `group_var`, `group_std`
    """
    return mean(degroup(data, groups))


def group_var(data, groups, ddof=0):
    """Beregn variansen for et grupperet datasæt hvor der antages uniform fordeling i intervallerne.

    Parametre
    ---
    - data : list
        - Et datasæt med grupperede observationer.

    - groups : list, optional
        - Liste med start og slut for hver interval. Hvert element kan bestå af en eller to værdier.
        Hvis hvert element består af 1 værdi skal listen indeholde n+1 elementer hvor n er antallet er observationer.
        Ellers skal den indeholde n elementer.

    - ddof: int, default = 0
        - Delta Degrees Of Freedom (på dansk frihedsgrader). Brug 0 til populationer og 1 til stikprøver.

    Returnerer
    ---
    - var : float
        - Varians.

    Se også
    ---
    - `group_precentiles`, `group_mean`, `group_std`
    """
    f = frekvenstabel(data, groups, show=False)
    m = group_mean(data, groups)
    summation = 0
    for i, o in enumerate(f.observation):
        summation += ((o[0] + o[1]) / 2 - m) ** 2 * f.hyppighed[i]
    return summation / (f.total - ddof)


def group_std(data, groups, ddof=0):
    """Beregn standardafvigelsen for et grupperet datasæt hvor der antages uniform fordeling i intervallerne.

    Parametre
    ---
    - data : list
        - Et datasæt med grupperede observationer.

    - groups : list, optional
        - Liste med start og slut for hver interval. Hvert element kan bestå af en eller to værdier.
        Hvis hvert element består af 1 værdi skal listen indeholde n+1 elementer hvor n er antallet er observationer.
        Ellers skal den indeholde n elementer.

    - ddof: int, default = 0
        - Delta Degrees Of Freedom (på dansk frihedsgrader). Brug 0 til populationer og 1 til stikprøver.

    Returnerer
    ---
    - std : float
        - Standardafvigelsen.

    Se også
    ---
    - `group_precentiles`, `group_var`, `group_mean`
    """
    return sqrt(group_var(data, groups, ddof))
