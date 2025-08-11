from spb import MB
from spb.series import List2DSeries, List3DSeries

from gym_cas import plot3d_points, plot_points
from gym_cas.plot_helpers import _check_len_annotations


def test_check_len_annotations():
    error = None
    try:
        _check_len_annotations([1], [1, 2])
    except ValueError as e:
        error = e
    assert error is not None


def test_plot_points():
    p = plot_points([1, 2, 3, 3], [1, 3, 5, 7], show=False)
    assert isinstance(p, MB)
    s = p.series
    assert len(s) == 1
    assert isinstance(s[0], List2DSeries)
    assert (s[0].get_data()[0] == [1, 2, 3, 3]).all()
    assert (s[0].get_data()[1] == [1, 3, 5, 7]).all()

    p = plot_points([-4, 0], [-2, 5], rendering_kw={"marker": "*"}, show=False)
    assert isinstance(p, MB)
    s = p.series
    assert len(s) == 1
    assert isinstance(s[0], List2DSeries)
    assert (s[0].get_data()[0] == [-4, 0]).all()
    assert (s[0].get_data()[1] == [-2, 5]).all()

    p = plot_points([-4, 0], [-2, 5], rendering_kw={"marker": "*"}, aspect="equal", show=False)
    assert isinstance(p, MB)
    s = p.series
    assert len(s) == 1
    assert isinstance(s[0], List2DSeries)
    assert (s[0].get_data()[0] == [-4, 0]).all()
    assert (s[0].get_data()[1] == [-2, 5]).all()

    a = plot_points(
        [-40, 0, 0],
        [-20, 50, 100],
        "hej",
        annotations=["A", "B", "C"],
        rendering_kw={"marker": "*"},
        aspect="equal",
        show=False,
    )
    b = plot_points(
        [-4, 0], [-2, 5], "hej", rendering_kw={"marker": "*"}, aspect="equal", annotations=["A", "B"], show=False
    )
    assert isinstance(a, MB)
    assert isinstance(b, MB)
    p = a + b
    s = p.series
    assert len(s) == 2
    assert isinstance(s[0], List2DSeries)
    assert s[0].annotations == ["A", "B", "C"]


def test_plot3d_points():
    p = plot3d_points([1, 2, 3, 3], [1, 3, 5, 7], [0, 0, 0, 0], show=False)
    assert isinstance(p, MB)
    s = p.series
    assert len(s) == 1
    assert isinstance(s[0], List3DSeries)
    assert (s[0].get_data()[0] == [1, 2, 3, 3]).all()
    assert (s[0].get_data()[1] == [1, 3, 5, 7]).all()
    assert (s[0].get_data()[2] == [0, 0, 0, 0]).all()

    p = plot3d_points([-4, 0], [-2, 5], [0, 0], rendering_kw={"marker": "*"}, show=False)
    assert isinstance(p, MB)
    s = p.series
    assert len(s) == 1
    assert isinstance(s[0], List3DSeries)
    assert (s[0].get_data()[0] == [-4, 0]).all()
    assert (s[0].get_data()[1] == [-2, 5]).all()
    assert (s[0].get_data()[2] == [0, 0]).all()

    p = plot3d_points([-4, 0], [-2, 5], [0, 0], rendering_kw={"marker": "*"}, aspect="equal", show=False)
    assert isinstance(p, MB)
    s = p.series
    assert len(s) == 1
    assert isinstance(s[0], List3DSeries)
    assert (s[0].get_data()[0] == [-4, 0]).all()
    assert (s[0].get_data()[1] == [-2, 5]).all()
    assert (s[0].get_data()[2] == [0, 0]).all()

    a = plot3d_points(
        [-40, 0, 0],
        [-20, 50, 100],
        [0, 0, 0],
        "hej",
        annotations=["A", "B", "C"],
        rendering_kw={"marker": "*"},
        aspect="equal",
        show=False,
    )
    b = plot3d_points(
        [-4, 0],
        [-2, 5],
        [0, 0],
        "hej",
        rendering_kw={"marker": "*"},
        aspect="equal",
        annotations=["A", "B"],
        show=False,
    )
    assert isinstance(a, MB)
    assert isinstance(b, MB)
    p = a + b
    s = p.series
    assert len(s) == 2
    assert isinstance(s[0], List3DSeries)
    assert s[0].annotations == ["A", "B", "C"]
