from gym_cas import (
    N,
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


def test_degroup():
    x1 = degroup([1, 2, 3, 8], [0, 1, 2, 3, 10])
    x2 = degroup([1, 2, 3, 8], [[0, 1], [1, 2], [2, 3], [3, 10]])
    assert x1 == x2
    assert x1[0] == 0.5
    assert x1[-1] == 10 - (10 - 3) / 9

    x1 = degroup([[1, 2, 3, 8], [1, 2, 3, 10]], [0, 1, 2, 3, 10])
    x2 = degroup([[1, 2, 3, 8], [1, 2, 3, 10]], [[0, 1], [1, 2], [2, 3], [3, 10]])
    assert x1 == x2
    assert x1[0][0] == 0.5
    assert x1[0][-1] == 10 - (10 - 3) / 9
    assert x1[1][0] == 0.5
    assert x1[1][-1] == 10 - (10 - 3) / 11

    x1 = degroup([[1, 2, 3, 8], [1, 2, 3, 10]], [[0, 1, 2, 3, 10], [-5, 5, 10, 20, 100]])
    x2 = degroup(
        [[1, 2, 3, 8], [1, 2, 3, 10]], [[[0, 1], [1, 2], [2, 3], [3, 10]], [[-5, 5], [5, 10], [10, 20], [20, 100]]]
    )
    assert x1 == x2
    assert x1[0][0] == 0.5
    assert x1[0][-1] == 10 - (10 - 3) / 9
    assert x1[1][0] == 0
    assert abs(x1[1][-1] - (100 - (100 - 20) / 11)) < 1e-13


def test_group():
    x1 = group([1, 2, 3, 8, 10], [0, 1, 2, 3, 10])
    x2 = group([1, 2, 3, 8, 10], [[0, 1], [1, 2], [2, 3], [3, 10]])
    assert x1 == x2
    assert x1[0] == 1
    assert x1[-1] == 2


def test_frekvenstabel():
    table = frekvenstabel([8, 3, 2, 1, 1, 2, 3, 4], show=False)
    assert table.frekvens == [25.0, 25.0, 25.0, 12.5, 12.5]
    assert table.hyppighed == [2, 2, 2, 1, 1]
    assert table.observation == [1, 2, 3, 4, 8]
    assert table.kumuleret_frekvens == [25.0, 50.0, 75.0, 87.5, 100.0]

    table1 = frekvenstabel([8, 3, 2, 1], [[1, 2], [2, 3], [3, 4], [4, 5]], show=False)
    table2 = frekvenstabel([8, 3, 2, 1], [1, 2, 3, 4, 5], show=False)
    assert table1.frekvens == [57.14285714285714, 21.428571428571427, 14.285714285714285, 7.142857142857142]
    assert table1.frekvens == table2.frekvens
    assert table1.hyppighed == table2.hyppighed
    assert table1.observation == table2.observation
    assert table1.kumuleret_frekvens == table2.kumuleret_frekvens


def test_kvartiler():
    assert kvartiler([1, 1, 1, 3, 7, 8]) == [1, 1.0, 2.0, 7.0, 8]
    assert kvartiler([1, 1, 3, 7, 8], [1, 2, 3]) == [1.0, 3.0, 7.5]


def test_percentiles():
    assert (
        percentile([1, 1, 1, 3, 7, 8], [20, 50, 80], method="inverted_cdf")
        == percentile([1, 1, 1, 3, 7, 8], [20, 50, 80])
    ).all()
    assert (
        percentile([1, 1, 1, 3, 7, 8], [20, 50, 80]) != percentile([1, 1, 1, 3, 7, 8], [20, 50, 80], method="linear")
    ).any()


def test_groups():
    assert group_mean([1, 2, 3, 1], [1, 2, 3, 4, 5]) == 3.0714285714285716
    assert group_var([1, 2, 3, 1], [1, 2, 3, 4, 5], ddof=1) > group_var([1, 2, 3, 1], [1, 2, 3, 4, 5])
    assert N(group_std([1, 2, 3, 1], [1, 2, 3, 4, 5], ddof=1)) > N(group_std([1, 2, 3, 1], [1, 2, 3, 4, 5]))
    assert N(group_std([1, 2, 2, 1], [1, 2, 3, 4, 5])) == ((2 * 1.5**2 + 4 * 0.5**2) / 6) ** 0.5
    assert group_percentile([1, 2, 3, 1], [1, 2, 3, 4, 5], [25, 50, 75]) == [2.375, 3.166666666666667, 3.75]
