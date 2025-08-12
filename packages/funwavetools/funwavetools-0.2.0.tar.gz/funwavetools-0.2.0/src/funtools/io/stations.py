from __future__ import annotations, division

import math
from abc import ABC, abstractmethod
from os import stat
from pathlib import Path
from re import A

import numpy as np
from bokeh.embed.util import is_tex_string
from pyparsing import traceParseAction

from ..math import grid
from .field import Parser


class InterpolationPoints:

    def __init__(self, point, offsets) -> None:

        self._reference = i, j = point
        self._interpolation = [(int(i + di), int(j + dj)) for di, dj in offsets]

    @property
    def reference(self) -> tuple[int, int]:
        return self._reference

    @property
    def interpolation(self) -> list[tuple[int, int]]:
        return self._interpolation


class BoxInterpolator:

    _MODES_ = ["nearest", "linear", "cubic"]

    def __init__(self, mode: str = "nearest") -> None:

        self._mode = mode

        if mode not in self._MODES_:
            raise ValueError(f"Invalid interpolation mode: {mode}")

        self._mode = mode

    @property
    def is_nearest(self) -> bool:
        return self._mode == "nearest"

    def get_interpolation_offsets(self) -> list[tuple[int, int]]:
        """Returns relative offsets for interpolation points"""
        match self._mode:
            case "nearest":
                offsets = [(0, 0)]

            case "linear":
                offsets = [(0, 1), (1, 1), (0, 0), (1, 0)]

            case "cubic":
                offsets = [
                    (-1, 2),
                    (0, 2),
                    (1, 2),
                    (2, 2),
                    (-1, 1),
                    (0, 1),
                    (1, 1),
                    (2, 1),
                    (-1, 0),
                    (0, 0),
                    (1, 0),
                    (2, 0),
                    (-1, -1),
                    (0, -1),
                    (1, -1),
                    (2, -1),
                ]

            case _:
                assert False, f"Fatal Error: Invalid mode {self._mode}"

        return offsets

    def compute_reference_indices(
        self, pts, dx: float, dy: float
    ) -> list[tuple[int, int]]:

        def convert(x: float, y: float) -> tuple[int, int]:

            x = x - dx / 2
            y = y - dy / 2

            if self._mode == "nearest":
                i = round(x / dx)
                j = round(y / dy)
                return i, j

            i = int(x // dx)
            j = int(y // dy)
            return i, j

        return [convert(*p) for p in pts]

    def get_interpolation_indices(
        self, indices: list[tuple[int, int]]
    ) -> list[InterpolationPoints]:

        offsets = self.get_interpolation_offsets()
        return [InterpolationPoints(i, offsets) for i in indices]

    def get_interpolation_points(
        self,
        indices: list[tuple[int, int]],
    ) -> list[tuple[float, float]]:

        return [((i + 0.5) * dx, (j + 0.5) * dy) for i, j in idxs]


class BathyGrid:

    def __init__(self, parser: Parser):

        self._parser = parser
        self._data = None

    @property
    def dx(self) -> float:
        return self._parser.dx

    @property
    def dy(self) -> float:
        return self._parser.dy

    @property
    def ds(self) -> tuple[float, float]:
        return self.dx, self.dy

    @property
    def data(self) -> np.ndarray:

        if self._data is None:
            self._data = self._parser.read_bathy()

        return self._data


class Mapper:

    def __init__(self):

        self._items = {}
        self._n = 0

    def update(self, new_pts: list) -> list:

        def get_station_index(pt):

            if pt in self._items:
                return self._items[pt]
            else:
                self._n += 1
                self._items[pt] = self._n

                return self._n

        test = [get_station_index(pt) for pt in new_pts]
        return test


class Item(ABC):
    """DUMMY"""

    def __init__(self, interp: str) -> None:
        super().__init__()
        self._interp = BoxInterpolator(mode=interp)
        self._bathy = None

    def _link_bathy(self, bathy: BathyGrid) -> None:
        self._bathy = bathy

    @abstractmethod
    def compute_reference_indices(self) -> list[tuple[int, int]]:
        pass

    def get_reference_points(self):
        assert not self._bathy is None
        dx, dy = self._bathy.ds
        idxs = self.compute_reference_indices()
        return [((i + 0.5) * dx, (j + 0.5) * dy) for i, j in idxs]

    def get_interpolation_indices(self) -> list[tuple[int, int]]:
        ref_points = self.compute_reference_indices()

        interp_pts = self._interp.get_interpolation_indices(ref_points)

        test = [x for i in interp_pts for x in i.interpolation]
        return test

    def get_interpolation_points(
        self,
    ) -> list[tuple[float, float]]:

        assert not self._bathy is None
        dx, dy = self._bathy.ds
        idxs = self.get_interpolation_indices()
        return [((i + 0.5) * dx, (j + 0.5) * dy) for i, j in idxs]

    def show(self, detail_level: int = 0):
        pass

    @abstractmethod
    def to_dict(self) -> dict:
        pass

    def get_config(self, mapper: Mapper) -> dict:
        config = self.to_dict()
        pts = self.get_interpolation_indices()

        config["map"] = mapper.update(pts)
        return config

    @classmethod
    def from_config(cls, config: dict) -> Item:
        print(cls)
        assert False
        return Item(interp="nearest")


class SubCollection:

    __ITEM_CLASS__ = Item

    def __init__(self, items: list, **kwargs) -> None:
        self._items = items
        self._bathy = None
        self._kwargs = kwargs

    def __getitem__(self, index: int) -> Item:
        return self._items[index]

    def _link_bathy(self, bathy: BathyGrid) -> None:
        self._bathy = bathy

        for i in self._items:
            i._link_bathy(self._bathy)

    def append(self, item: Item) -> None:
        self._items.append(item)

    def extend(self, items: list) -> None:
        self._items.extend(items)

    def get_interpolation_indices(self) -> list[tuple[int, int]]:

        return list(
            set([x for i in self._items for x in i.get_interpolation_indices()])
        )

    def get_interpolation_points(
        self,
    ) -> list[tuple[float, float]]:

        assert not self._bathy is None
        dx, dy = self._bathy.ds
        idxs = self.get_interpolation_indices()
        return [((i + 0.5) * dx, (j + 0.5) * dy) for i, j in idxs]

    def get_config(self, mapper: Mapper) -> list[dict] | dict:

        items = [it.get_config(mapper) for it in self._items]

        if len(self._kwargs) == 0:
            return items

        else:
            config = self._kwargs
            config["items"] = items
            return config

    @classmethod
    def from_config(cls, data: list) -> SubCollection:
        subcls = cls.__ITEM_CLASS__
        return cls([subcls.from_config(d) for d in data])


class Collection(ABC):
    """DUMMMY"""

    __ITEM_CLASS__ = Item
    __ITEMS_CLASS__ = SubCollection

    def __init__(self, default_name: str) -> None:
        """DUMMY"""
        cls = self.__ITEMS_CLASS__
        assert issubclass(cls, SubCollection)
        assert not cls == SubCollection
        self._items: dict = {}
        self._default_name = default_name
        self._bathy = None

    def _link_bathy(self, bathy: BathyGrid) -> None:
        """Link common bathymetry grid info"""
        self._bathy = bathy

        for i in self._items.values():
            i._link_bathy(bathy)

    def __getitem__(self, key: str | int):
        """Returns objecct by index for simple list, object by name, or list of objec by group name."""
        keys = list(self._items.keys())
        n = len(keys)

        if isinstance(key, int):
            if n == 0:
                raise ValueError("No stations added, can not access by index")
            if n > 1:
                raise ValueError(
                    "Subgroups of stations detected, can not access by index."
                )

            grp_key = keys[0]

            item = self._items[grp_key]

            if issubclass(item.__class__, Item):
                return item
            else:
                return item[key]

        elif isinstance(key, str):
            return self._items[key]

        else:
            assert False

    def add(self, *args, **kwargs) -> None:
        """DUMMY"""
        pass

    def _add(
        self,
        new_item: Item,
        name: str | None = None,
    ) -> None:
        """Add an item to collection with optional name"""

        assert isinstance(self._bathy, BathyGrid)
        if name is None:
            name = self._default_name

        new_item._link_bathy(self._bathy)
        assert isinstance(new_item, self.__ITEM_CLASS__)

        if name not in self._items:
            # If new key, add single item
            self._items[name] = new_item
        else:
            item = self._items[name]

            if isinstance(item, self.__ITEMS_CLASS__):
                # add to group
                self._items[name].append(new_item)
            else:
                # if single named items, convert SubCollection
                old_item = item
                cls = self.__ITEMS_CLASS__
                assert issubclass(cls, SubCollection)
                subitems = cls([old_item, new_item])
                subitems._link_bathy(self._bathy)
                self._items[name] = subitems

    def _add_group(
        self, new_items: list, group_name: str | None = None, **kwargs
    ) -> None:
        """Add items to collections with opitonal group name"""

        assert isinstance(self._bathy, BathyGrid)
        assert all([isinstance(it, self.__ITEM_CLASS__) for it in new_items])

        for it in new_items:
            it._link_bathy(self._bathy)

        if group_name not in self._items:

            cls = self.__ITEMS_CLASS__

            subitems = cls(new_items, **kwargs)
            subitems._link_bathy(self._bathy)
            self._items[group_name] = subitems
        else:

            item = self._items[group_name]

            if issubclass(item.__class__, SubCollection):

                item.extend(new_items)
            else:
                items = [item]
                items.extend(new_items)

                cls = self.__ITEMS_CLASS__
                item = cls(items)

                new_items.insert(0, item)
                subitems = cls(new_items)
                subitems._link_bathy(self._bathy)
                self._items[group_name] = subitems

    def get_interpolation_indices(self) -> list[tuple[int, int]]:
        """DUMMMY"""

        # ref_points = [x for ]

        ref_points = self.compute_reference_indices()
        interp_pts = self._interp.get_interpolation_indices(ref_points)
        return [x for i in interp_pts for x in i.interpolation]

    def get_interpolation_points(
        self, dx: float, dy: float
    ) -> list[tuple[float, float]]:
        """DUMMMY"""
        idxs = self.get_interpolation_indices()
        return [((i + 0.5) * dx, (j + 0.5) * dy) for i, j in idxs]

    def show(self, detail_level: int = 0):
        """DUMMMY"""

        n = len(self._items)

        if n < 1:
            raise RuntimeError("Nothing to show")

        if n == 1:

            key = list(self._items.keys())[0]

            return self._items[key].show(detail_level)

        plts = []
        for key, item in self._items.items():
            plt = item.show(detail_level).relabel(key)
            plts.append(plt)

        plt = plts[0]
        for p in plts[1:]:
            plt = plt * p

        return plt

    def get_config(self, mapper: Mapper) -> dict:
        """DUMMMY"""

        # NOTE: One-line version doesn't update mapper
        config = {}
        for k, d in self._items.items():
            config[k] = d.get_config(mapper)

        return config

    @classmethod
    def from_config(cls, config: dict):
        """DUMMMY"""

        obj = cls()
        for k, d in config.items():

            if isinstance(d, list):
                subcls = cls.__ITEMS_CLASS__
            elif isinstance(d, dict):
                if "_method_" in d:
                    subcls = cls.__ITEMS_CLASS__
                else:
                    subcls = cls.__ITEM_CLASS__
            else:
                assert False

            print(subcls)
            obj._items[k] = subcls.from_config(d)

        return obj


import holoviews as hv


class Station(Item):

    def __init__(self, point: tuple[float, float], interp: str = "nearest"):

        super().__init__(interp)

        self._target_pt = point

    def compute_reference_indices(self) -> list[tuple[int, int]]:
        assert not self._bathy is None
        dx, dy = self._bathy.ds
        return self._interp.compute_reference_indices([self._target_pt], dx, dy)

    def show(self, detail_level: int = 1):

        trg_pts = [self._target_pt]

        if detail_level == 0:

            if self._interp.is_nearest:
                pts = self.get_interpolation_points()
            else:
                pts = trg_pts

            return hv.Scatter(pts)

        else:
            plt = hv.Scatter(trg_pts)

            plt = plt.relabel("Target")

            pts = self.get_interpolation_points()

            grid_plt = hv.Scatter(pts, label="Grid")
            grid_plt.opts(marker="plus")

            plt = grid_plt * plt

        return plt

    def to_dict(self):
        return {
            "target_point": self._target_pt,
            "reference_index": self.compute_reference_indices()[0],
            "interpolation_mode": self._interp._mode,
        }

    @classmethod
    def from_config(cls, config: dict):
        return Station(config["target_point"], interp=config["interpolation_mode"])


class Substations(SubCollection):

    __ITEM_CLASS__ = Station

    def show(self, detail_level: int = 1):

        if detail_level == 0:

            pts = []

            for i in self._items:
                if i._interp.is_nearest:
                    pts.append(i.get_interpolation_points())
                else:
                    pts.append([i._target_pt])

            pts = [x for n in pts for x in n]
            plt = hv.Scatter(pts)
        else:

            trg_pts = [s._target_pt for s in self._items]
            plt = hv.Scatter(trg_pts)

            plt = plt.relabel("Target")

            pts = self.get_interpolation_points()
            grid_plt = hv.Scatter(pts, label="Grid")
            grid_plt.opts(marker="plus", size=10)

            plt = grid_plt * plt

        return plt


class Stations(Collection):

    __ITEM_CLASS__ = Station
    __ITEMS_CLASS__ = Substations

    def __init__(self) -> None:
        super().__init__(default_name="Station")

    def add(
        self,
        point: tuple[float, float],
        name: str = "Station",
        interp: str = "nearest",
    ) -> None:

        self._add(Station(point, interp=interp), name=name)

        # self._add(x, y, name=name, interp=interp)

    def add_group(
        self,
        points: list[tuple[float, float]],
        group_name: str = "Station",
        interp: str = "nearest",
    ) -> None:

        items = [Station(pt, interp=interp) for pt in points]
        self._add_group(items, group_name=group_name)


class Transect(Item):

    def __init__(
        self,
        point_0: tuple[float, float],
        point_1: tuple[float, float],
        interp: str = "linear",
        is_2d: bool = True,
    ):
        """TEST"""
        super().__init__(interp)

        if is_2d:
            if self._interp.is_nearest:
                raise ValueError("Interpolation must be used for a 2D transect")

        self._is_2d = is_2d
        self._line = [point_0, point_1]

        x0, y0 = point_0
        x1, y1 = point_1

        self._xl = xl = x1 - x0
        self._yl = yl = y1 - y0
        self._x0 = x0
        self._y0 = y0

        self._sl = sl = math.sqrt(xl**2 + yl**2)
        self._normal = (-yl / sl, xl / sl)

        self._x_min, self._x_max = min(x0, x1), max(x0, x1)
        self._y_min, self._y_max = min(y0, y1), max(y0, y1)

        self._kwargs = {
            "point_0": point_0,
            "point_1": point_1,
            "interp": interp,
        }

    def get_linear_points(
        self,
        divisions: int | list[float],
    ):
        """TEST"""
        if isinstance(divisions, int):
            if divisions < 1:
                raise ValueError("divisions must be greater than 0")

            n = divisions
            i = grid.rectilinear(n, 1 / n)

        else:
            for i, s0 in enumerate(divisions):

                if s0 < 0:
                    msg = f"Values in divisions must between 0 and 1, value at index {i:d} is less than 0."
                    raise ValueError(msg)

                if s0 > 1:
                    msg = f"Values in divisions must between 0 and 1, value at index {i:d} is greater than 0."
                    raise ValueError(msg)

            i = np.array(divisions)

        x = i * self._xl + self._x0
        y = i * self._yl + self._y0

        pts = [(float(x0), float(y0)) for x0 in x for y0 in y]

        return pts

    @classmethod
    def create_1d_x(
        cls, x_range: tuple[float, float], y: float, interp: str = "nearest"
    ) -> Transect:
        """TEST"""

        x0, x1 = x_range
        point_0 = (x0, y)
        point_1 = (x1, y)
        obj = cls(point_0, point_1, interp, is_2d=False)

        obj._kwargs = {
            "x_range": x_range,
            "y": y,
            "interp": interp,
        }
        return obj

    @classmethod
    def create_1d_y(
        cls, y_range: tuple[float, float], x: float, interp: str = "nearest"
    ) -> Transect:
        """TEST"""

        y0, y1 = y_range
        point_0 = (x, y0)
        point_1 = (x, y1)

        obj = cls(point_0, point_1, interp, is_2d=False)

        obj._kwargs = {
            "y_range": y_range,
            "x": x,
            "interp": interp,
        }
        return obj

    def compute_reference_indices(self) -> list[tuple[int, int]]:
        """TEST"""

        assert not self._bathy is None
        dx, dy = self._bathy.ds
        """Return list of InterpolationPoints for"""
        x_min, y_min = self._x_min, self._y_min
        x_max, y_max = self._x_max, self._y_max

        args = zip([x_min, y_min], [dx, dy])
        i0, j0 = (math.floor(s / ds - 0.5) for s, ds in args)
        args = zip([x_max, y_max], [dx, dy])
        i1, j1 = (math.ceil(s / ds - 0.5) for s, ds in args)

        is_x_1d = i1 - i0 <= 1
        is_y_1d = j1 - j0 <= 1

        assert not (is_x_1d and is_y_1d)

        if self._interp.is_nearest:

            assert is_x_1d or is_y_1d

            if is_y_1d:
                j = round(y_max / dy - 0.5)
                idxs = [(i, j) for i in range(i0, i1 + 1)]

            else:
                i = round(x_max / dx - 0.5)
                idxs = [(i, j) for j in range(j0, j1 + 1)]

        else:

            if is_y_1d:
                j1 = j0 + 1

            if is_x_1d:
                i1 = i1 + 1

            x = [(i, (i + 0.5) * dx) for i in range(i0, i1)]
            y = [(j, (j + 0.5) * dy) for j in range(j0, j1)]

            gen_box = lambda x0, y0: [(x0, y0), (x0 + dx, y0 + dy)]
            boxes = [((i, j), gen_box(x0, y0)) for i, x0 in x for j, y0 in y]

            idxs = [idx for idx, b in boxes if self.intersects_box(b, self._line)]

        return idxs
        return self._interp.get_interpolation_indices(idxs)

    @staticmethod
    def intersects(
        s0: list[tuple[float, float]], s1: list[tuple[float, float]]
    ) -> bool:
        """TEST"""

        dx0 = s0[1][0] - s0[0][0]
        dx1 = s1[1][0] - s1[0][0]
        dy0 = s0[1][1] - s0[0][1]
        dy1 = s1[1][1] - s1[0][1]
        p0 = dy1 * (s1[1][0] - s0[0][0]) - dx1 * (s1[1][1] - s0[0][1])
        p1 = dy1 * (s1[1][0] - s0[1][0]) - dx1 * (s1[1][1] - s0[1][1])
        p2 = dy0 * (s0[1][0] - s1[0][0]) - dx0 * (s0[1][1] - s1[0][1])
        p3 = dy0 * (s0[1][0] - s1[1][0]) - dx0 * (s0[1][1] - s1[1][1])
        return (p0 * p1 <= 0) & (p2 * p3 <= 0)

    @staticmethod
    def intersects_box(
        box: list[tuple[float, float]], line: list[tuple[float, float]]
    ) -> bool:
        """TEST"""
        (x0, y0), (x1, y1) = box

        low_lef = (x0, y0)
        low_rig = (x1, y0)
        upp_lef = (x0, y1)
        upp_rig = (x1, y1)

        boundaries = [
            [low_lef, low_rig],
            [low_rig, upp_rig],
            [upp_rig, upp_lef],
            [upp_lef, low_lef],
        ]

        are_inter = [Transect.intersects(b, line) for b in boundaries]

        return any(are_inter)

    def show(self, detail_level: int = 0):
        """TEST"""

        if self._interp.is_nearest:
            x, y = zip(*self.get_reference_points())
            x0, x1 = min(x), max(x)
            y0, y1 = min(y), max(y)
            line = [(x0, y0), (x1, y1)]

        else:
            line = self._line

        if detail_level == 0:
            return hv.Path(line)

        pt0, pt1 = line
        plt = hv.Path(line, label="Target").opts(show_legend=True)

        plt = plt * hv.Scatter(pt0, label="Point 1")
        plt = plt * hv.Scatter(pt1, label="Point 2")

        plt = plt * _plot_arrow(pt0, pt1, self._normal, self._sl, "Normal")

        if detail_level < 2:
            return plt

        pts = self.get_interpolation_points()

        plt = plt * hv.Scatter(pts, label="Grid")

        return plt.opts(show_legend=True)

    def to_dict(self) -> dict:
        return self._kwargs


def _plot_arrow(pt0, pt1, normal, length, label, ratio=0.2):

    x0, y0 = pt0
    x1, y1 = pt1
    xc = (x0 + x1) / 2
    yc = (y0 + y1) / 2

    nx, ny = normal

    la = ratio * length

    x0 = xc - nx * la
    x1 = xc + nx * la
    y0 = yc - ny * la
    y1 = yc + ny * la

    pt0 = (x0, y0)
    pt1 = (x1, y1)

    plt = hv.Path([pt0, pt1], label=label).opts(show_legend=True)

    plt *= hv.Scatter(pt1, label=label)

    return plt


class AlignedTransects(Transect):

    def __init__(
        self,
        point_0: tuple[float, float],
        point_1: tuple[float, float],
        interp: str = "linear",
        is_2d: bool = True,
    ):
        super().__init__(point_0, point_1, interp, is_2d)

        self._transects = []
        self._is_1d_x = True
        self._kwargs = {}

    def get_normal_transect(self, x, y):
        """Returns end points of normal transects using specified origin point"""
        nx, ny = self._normal
        x0 = float(x - nx * self._dist_back)
        y0 = float(y - ny * self._dist_back)

        x1 = float(x + nx * self._dist_forw)
        y1 = float(y + ny * self._dist_forw)
        return [(x0, y0), (x1, y1)]

    def create_normals(
        self,
        divisions: int | list[float],
        distance_forward: float,
        distance_backward: float,
    ):

        self._kwargs.update(
            {
                "divisions": divisions,
                "distance_backward": distance_backward,
                "distance_forward": distance_forward,
            }
        )
        self._dist_forw = distance_forward
        self._dist_back = distance_backward

        pts = self.get_linear_points(divisions)

        transects = [self.get_normal_transect(*s) for s in pts]

        if self._interp.is_nearest:
            assert not self._is_2d

            if self._is_1d_x:
                args = [((y0, y1), x) for (x, y0), (_, y1) in transects]
                transects = [
                    Transect.create_1d_y(y, x, interp="nearest") for y, x in args
                ]

            else:
                args = [((x0, x1), y) for (x0, y), (x1, y) in transects]

                transects = [
                    Transect.create_1d_x(x, y, interp="nearest") for x, y in args
                ]
        else:

            iterp = self._interp._mode
            transects = [Transect(*l, interp=iterp) for l in transects]

        for t in transects:
            t._link_bathy(self._bathy)

        self._transects = transects

    @classmethod
    def create_1d_x(
        cls,
        x_range: tuple[float, float],
        y: float,
        interp: str = "nearest",
    ) -> AlignedTransects:

        self = super().create_1d_x(x_range, y, interp=interp)
        assert isinstance(self, AlignedTransects)
        self._is_1d_x = True
        return self

    @classmethod
    def create_1d_y(
        cls,
        y_range: tuple[float, float],
        x: float,
        interp: str = "nearest",
    ) -> AlignedTransects:

        self = super().create_1d_y(y_range, x, interp=interp)
        assert isinstance(self, AlignedTransects)
        self._is_1d_x = False
        return self

    def show(self, detail_level: int = 0):

        if len(self._transects) == 0:
            return super().show(detail_level)

        plt = super().show(detail_level=1)

        plts = [t.show(detail_level=0) for t in self._transects]

        for p in plts:
            plt = p * plt

        return plt

    def to_dict(self) -> dict:
        return self._kwargs


class LinkedAlignedTransects:

    def __init__(self, bathy: BathyGrid) -> None:
        self._bathy = bathy

    def create(self, point_0, point_1, interp="linear"):

        obj = AlignedTransects(point_0, point_1, interp=interp)
        obj._link_bathy(self._bathy)

        obj._kwargs = {
            "point_0": point_0,
            "point_1": point_1,
            "interp": interp,
            "_method_": "array_2d",
        }
        return obj

    def create_1d_x(
        self, x_range: tuple[float, float], y: float, interp: str = "nearest"
    ):

        obj = AlignedTransects.create_1d_x(x_range, y, interp=interp)
        obj._link_bathy(self._bathy)
        obj._kwargs = {
            "x_range": x_range,
            "y": y,
            "interp": interp,
            "_method_": "array_1d_x",
        }
        return obj

    def create_1d_y(
        self, y_range: tuple[float, float], x: float, interp: str = "nearest"
    ):

        obj = AlignedTransects.create_1d_y(y_range, x, interp=interp)
        obj._link_bathy(self._bathy)
        obj._kwargs = {
            "y_range": y_range,
            "x": x,
            "interp": interp,
            "_method_": "array_1d_y",
        }
        return obj


class Runup(Transect):

    @classmethod
    def from_config(self, config: dict) -> Runup:
        return {}


class Subrunups(SubCollection):

    __ITEM_CLASS__ = Runup

    @classmethod
    def from_config(cls, data: list | dict) -> Subrunups:

        if isinstance(data, list):
            return [Runup.from_config(d) for d in data]

        else:

            method = data.pop("_method_")
            interp = data["interp"]

            match method:
                case "array_1d_y":
                    keys = ["y_range", "x"]
                    method = AlignedTransects.create_1d_y
                case "array_1d_x":
                    keys = ["x_range", "y"]
                    method = AlignedTransects.create_1d_x
                case "array_2d":
                    keys = ["point_0", "point_1"]
                    method = AlignedTransects

            args = [data[k] for k in keys]

            obj = method(*args, interp=interp)

            keys = ["divisions", "distance_backward", "distance_forward"]
            args = (data[k] for k in keys)

            obj.create_normals(*args)

            runups = [t for t in obj._transects]

            for r in runups:
                r.__class__ = Runup

            data.pop("items")
            return Subrunups(runups, **data)


class Runups(Collection):

    __ITEM_CLASS__ = Runup
    __ITEMS_CLASS__ = Subrunups

    def __init__(self) -> None:
        super().__init__(default_name="Runup")

    def add_1d(
        self,
        x_range: tuple[float, float],
        y: float,
        name: str = "Runup",
        interp: str = "nearest",
    ) -> None:
        item = Runup.create_1d_x(x_range, y, interp=interp)
        self._add(item, name=name)

    def add(
        self,
        point_0: tuple[float, float],
        point_1: tuple[float, float],
        name: str = "Runup",
        interp: str = "linear",
    ) -> None:

        item = Runup(point_0, point_1, interp=interp)
        self._add(item, name=name)

    def add_array(
        self,
        transects: AlignedTransects,
    ):

        kwargs = transects._kwargs
        runups = transects._transects

        for r in runups:
            r.__class__ = Runup

        for i in range(10):

            key = f"Runup Array {i+1:d}"

            if not key in self._items:

                self._add_group(runups, group_name=key, **kwargs)
                return

        raise RuntimeError("Max runup arrays reached")

    def get_array_constructor(self) -> LinkedAlignedTransects:

        assert not self._bathy is None
        return LinkedAlignedTransects(self._bathy)


class TimeseriesFile:

    def __init__(self, parser: Parser) -> None:

        self._bathy = BathyGrid(parser)

        self._stations = Stations()
        self._runups = Runups()

        self._items = {
            "Stations": self._stations,
            "Runups": self._runups,
        }

        for c in self._items.values():
            c._link_bathy(self._bathy)

    @property
    def stations(self) -> Stations:
        return self._items["Stations"]

    @property
    def runups(self) -> Runups:
        return self._items["Runups"]

    def to_file(self):

        mapper = Mapper()
        config = {}
        for k, c in self._items.items():
            config[k] = c.get_config(mapper)

        empty = [k for k, d in config.items() if len(d) == 0]

        for k in empty:
            del config[k]

        return config

    def _link_bathy(self):

        for d in self._items.values():
            d._link_bathy(self._bathy)

    @classmethod
    def from_file(cls, parser: Parser, config: dict):

        obj = TimeseriesFile(parser)

        for k, d in config.items():
            cls = obj._items[k].__class__
            obj._items[k] = cls.from_config(d)

        obj._link_bathy()
        return obj
