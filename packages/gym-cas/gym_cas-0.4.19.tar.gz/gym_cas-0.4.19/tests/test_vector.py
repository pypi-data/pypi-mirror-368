from warnings import filterwarnings

from spb import MB
from spb.series import Arrow2DSeries, Arrow3DSeries, Parametric3DLineSeries, ParametricSurfaceSeries
from sympy.abc import t, u

from gym_cas import plot3d_line, plot3d_plane, plot3d_sphere, plot_vector, vector


def test_plot_vector_2d():
    p = plot_vector([1, 2], show=False)
    assert isinstance(p, MB)
    s = p.series
    assert len(s) == 1
    assert isinstance(s[0], Arrow2DSeries)
    assert s[0].get_data() == (0, 0, 1, 2)


def test_plot_vector_3d():
    p = plot_vector([1, 2, 3], show=False)
    assert isinstance(p, MB)
    s = p.series
    assert len(s) == 1
    assert isinstance(s[0], Arrow3DSeries)
    assert not s[0].is_streamlines
    assert s[0].get_data() == (0, 0, 0, 1, 2, 3)
    assert s[0].get_label(False) == "(0.0, 0.0, 0.0) -> (1.0, 2.0, 3.0)"


def test_plot3d_line():
    p = plot3d_line(vector(1 + t, 2 - t, 3 + t), (t, 0, 1), show=False)
    assert isinstance(p, MB)
    s = p.series
    assert len(s) == 1
    assert isinstance(s[0], Parametric3DLineSeries)
    assert s[0].get_data()[0][0] == 1
    assert s[0].get_label(False) == "(t + 1, 2 - t, t + 3)"


def test_plot3d_plane():
    filterwarnings("ignore", category=SyntaxWarning)
    p = plot3d_plane(vector(1 + t - u, 2 - t + u, 3 + t), (t, 0, 1), (u, 0, 1), show=False)
    assert isinstance(p, MB)
    s = p.series
    assert len(s) == 1
    assert isinstance(s[0], ParametricSurfaceSeries)
    assert s[0].get_data()[0][0][0] == 1
    assert s[0].get_label(False) == "(t - u + 1, -t + u + 2, t + 3)"


def test_plot3d_sphere():
    p = plot3d_sphere(3, show=False)
    assert isinstance(p, MB)
    s = p.series
    assert len(s) > 0
    assert isinstance(s[0], ParametricSurfaceSeries)
    assert s[0].get_label(False) == "$x^2 + y^2 + z^2 = 3^2$"

    p = plot3d_sphere(3, vector(1, 2, -3), show=False)
    assert isinstance(p, MB)
    s = p.series
    assert len(s) > 0
    assert isinstance(s[0], ParametricSurfaceSeries)
    assert s[0].get_label(False) == "$(x-1)^2 + (y-2)^2 + (z+3)^2 = 3^2$"


def test_vector():
    a = vector(3, 4)
    assert a.norm() == 5
    b = vector(1, 0)
    assert a + b == vector(4, 4)
    assert a.dot(b) == 3

    c = vector(1, 2, 3)
    assert c.norm() ** 2 == 1**2 + 2**2 + 3**2
    d = vector(0, 0, 1)
    assert c + d == vector(1, 2, 4)
    assert c.dot(d) == 3
    assert c.cross(d) == vector(2, -1, 0)
