from collections.abc import Iterable

from spb import MB
from spb.backends.matplotlib.renderers import Line2DRenderer, Line3DRenderer
from spb.graphics import graphics
from spb.series import List2DSeries, List3DSeries


def _check_len_annotations(x, labels):
    if len(labels) != len(x):
        msg = "Number of annotations should be equal to the number of points."
        raise ValueError(msg)


class Point2DSeries(List2DSeries):
    """List of points (scatter plot)."""

    def __init__(self, list_x, list_y, label="", annotations=None, **kwargs):
        kwargs.setdefault("is_point", True)

        if annotations is not None:
            _check_len_annotations(list_x, annotations)
        self.annotations = annotations

        super().__init__(list_x, list_y, label=label, **kwargs)


class Point3DSeries(List3DSeries):
    """List of points (scatter plot) in 3D."""

    def __init__(self, list_x, list_y, list_z, label="", annotations=None, **kwargs):
        kwargs.setdefault("is_point", True)

        if annotations is not None:
            _check_len_annotations(list_x, annotations)
        self.annotations = annotations

        super().__init__(list_x, list_y, list_z, label=label, **kwargs)


class Point2DRenderer(Line2DRenderer):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

    def draw(self):  # pragma: no cover
        s = self.series
        p = self.plot
        data = s.get_data()
        if s.annotations is not None and isinstance(p, MB):
            for x, y, annotation in zip(*data, s.annotations):
                p._ax.annotate(annotation, (x, y))
        super().draw()


class Point3DRenderer(Line3DRenderer):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

    def draw(self):  # pragma: no cover
        s = self.series
        p = self.plot
        data = s.get_data()
        if s.annotations is not None and isinstance(p, MB):
            for x, y, z, annotation in zip(*data, s.annotations):
                p._ax.text(x, y, z, annotation)
        super().draw()


MB.renderers_map.update({Point2DSeries: Point2DRenderer})  # type: ignore
MB.renderers_map.update({Point3DSeries: Point3DRenderer})  # type: ignore


def plot_points(x: Iterable, y: Iterable, label="", annotations=None, **kwargs):
    """Afbild punkter i et koordinatsystem

    `plot_points(x,y)`

    - Afbild punkter med angivelse af label

    `plot_points(x,y,label)`

    Parametre
    ---------
    - x : Iterable
        - Punkternes x-værdier

    - y : Iterable
        - Punkternes y-værdier

    - label : String, optional
        - Label for alle punkter

    - annotations : Iterable, optional
        - Annotering for alle punkter. Vises som tekst ved hvert punkt.

    - rendering_kw : se `list_2d`, `list_3d`
    - kwargs : se `list_2d`, `list_3d`

    Returnerer
    ---------
    - plt : Plot
        - Plotobjektet.

    Se også
    ---------
    - [SPB: list_2d](https://sympy-plot-backends.readthedocs.io/en/latest/modules/graphics/functions_2d.html#spb.graphics.functions_2d.list_2d)
    - [SPB: list_3d](https://sympy-plot-backends.readthedocs.io/en/latest/modules/graphics/functions_3d.html#spb.graphics.functions_3d.list_3d)
    """
    return graphics(Point2DSeries(x, y, label, annotations, **kwargs), **kwargs)


def plot3d_points(x: Iterable, y: Iterable, z: Iterable, label="", annotations=None, **kwargs):
    """Afbild punkter i et tredimensionelt koordinatsystem

    `plot3d_points(x,y,z)`

    - Afbild punkter med angivelse af label

    `plot3d_points(x,y,z,label)`

    Parametre
    ---------
    - x : Iterable
        - Punkternes x-værdier

    - y : Iterable
        - Punkternes y-værdier

    - z : Iterable
        - Punkternes y-værdier

    - label : String, optional
        - Label for alle punkter

    - annotations : Iterable, optional
        - Annotering for alle punkter. Vises som tekst ved hvert punkt.

    - camera : dict, optional
        - Indstillinger der videregives til [`view_init`](https://matplotlib.org/stable/api/_as_gen/mpl_toolkits.mplot3d.axes3d.Axes3D.view_init.html)

    - rendering_kw : se `list_3d`
    - kwargs : se `list_3d`

    Returnerer
    ---------
    - plt : Plot
        - Plotobjektet.

    Se også
    ---------
    - [SPB: list_3d](https://sympy-plot-backends.readthedocs.io/en/latest/modules/graphics/functions_3d.html#spb.graphics.functions_3d.list_3d)
    """
    return graphics(Point3DSeries(x, y, z, label, annotations, **kwargs), **kwargs)
