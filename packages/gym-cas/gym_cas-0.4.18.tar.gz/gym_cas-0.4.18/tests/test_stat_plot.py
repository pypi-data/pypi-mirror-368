from spb import MB
from spb.series import Line2DBaseSeries

from gym_cas import boxplot, plot_bars, plot_hist, plot_sum
from gym_cas.stat_plot import BarplotSeries, BoxplotSeries, _check_len_labels

from .test_globals import _only_small_errors


def test_check_len_labels():
    error = None
    try:
        _check_len_labels([1], [1, 2])
    except ValueError as e:
        error = e
    assert error is not None


def test_boxplot():
    p = boxplot([[1, 2, 3, 8], [1, 2, 3, 10]], label=["test1", "test2"], show=False)
    s = p.series
    assert isinstance(p, MB)
    assert len(s) == 1
    assert isinstance(s[0], BoxplotSeries)
    assert s[0].get_data()[0]["whislo"] == 1
    assert str(s[0]) is not None

    p = boxplot([[1, 2, 3, 8], [1, 2, 3, 10]], show=False)
    s = p.series
    assert isinstance(p, MB)
    assert len(s) == 1
    assert isinstance(s[0], BoxplotSeries)
    assert s[0].get_data()[0]["whislo"] == 1

    p = boxplot([[1, 2, 3, 8], [1, 2, 3, 10]], [1, 2, 3, 4, 5], label=["test1", "test2"], show=False)
    s = p.series
    assert isinstance(p, MB)
    assert len(s) == 1
    assert isinstance(s[0], BoxplotSeries)
    assert s[0].get_data()[0]["whislo"] == 1

    p = boxplot([[1, 2, 3, 8], [1, 2, 3, 10]], [[1, 2, 3, 4, 5], [1, 3, 5, 7, 9]], show=False)
    s = p.series
    assert isinstance(p, MB)
    assert len(s) == 1
    assert isinstance(s[0], BoxplotSeries)
    assert s[0].get_data()[0]["whislo"] == 1

    p = boxplot([1, 2, 3, 8], [1, 2, 3, 4, 5], label="test", show=False)
    s = p.series
    assert isinstance(p, MB)
    assert len(s) == 1
    assert isinstance(s[0], BoxplotSeries)
    assert s[0].get_data()[0]["whislo"] == 1


def test_plot_bars():
    p = plot_bars([1, 2, 3, 3], label="hejsa", show=False)
    s = p.series
    assert isinstance(p, MB)
    assert len(s) == 1
    assert isinstance(s[0], BarplotSeries)
    assert s[0].get_data() == ([1, 2, 3], [25, 25, 50], [1, 2, 3])
    assert str(s[0]) is not None

    p = plot_bars([[1, 2, 3, 10, 10], [1, 2, 2, 3, 6, 8]], label=["hejsa", "davs der"], show=False)
    s = p.series
    assert isinstance(p, MB)
    assert len(s) == 2
    assert isinstance(s[0], BarplotSeries)
    assert s[0].get_data()[1] == [100 / 5, 100 / 5, 100 / 5, 200 / 5]

    p = plot_bars([[1, 2, 3, 10, 10], [1, 2, 2, 3, 6, 8]], show=False)
    s = p.series
    assert isinstance(p, MB)
    assert len(s) == 2
    assert isinstance(s[0], BarplotSeries)
    assert s[0].get_data()[1] == [100 / 5, 100 / 5, 100 / 5, 200 / 5]


def test_plot_sum():
    p = plot_sum([1, 2, 3, 3], label="hejsa", show=False)
    assert isinstance(p, MB)
    s = p.series
    assert len(s) == 1 + 3  # 3 series to show kvartiler
    assert isinstance(s[0], Line2DBaseSeries)

    p = plot_sum([[1, 2, 3, 10, 10], [1, 2, 2, 3, 6]], [0, 10, 20, 30, 40, 50], label=["hejsa", "davs der"], show=False)
    assert isinstance(p, MB)
    s = p.series
    assert len(s) == 2
    assert isinstance(s[0], Line2DBaseSeries)

    p = plot_sum([[1, 2, 3, 10, 10], [1, 2, 2, 3, 6]], [[0, 10, 20, 30, 40, 50], [0, 10, 20, 30, 40, 60]], show=False)
    assert isinstance(p, MB)
    s = p.series
    assert len(s) == 2
    assert isinstance(s[0], Line2DBaseSeries)

    p = plot_sum([1, 2, 3, 3], [0, 10, 20, 30, 40], label="hejsa", show=False)
    assert isinstance(p, MB)
    s = p.series
    assert len(s) == 1 + 3  # 3 series to show kvartiler
    assert isinstance(s[0], Line2DBaseSeries)


def test_plot_hist():
    p = plot_hist([1, 2, 3, 3], [1, 3, 5, 7, 9], show=False)
    assert isinstance(p, MB)
    s = p.series
    assert len(s) == 1
    assert isinstance(s[0], BarplotSeries)
    assert s[0].get_data()[0] == [2, 4, 6, 8]
    assert _only_small_errors(s[0].get_data()[1], [100 / 9 / 2, 200 / 9 / 2, 300 / 9 / 2, 300 / 9 / 2])
