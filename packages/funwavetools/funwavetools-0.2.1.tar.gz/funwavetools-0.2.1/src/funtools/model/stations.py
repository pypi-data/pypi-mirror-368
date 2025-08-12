# import typing
from collections.abc import Callable
from pathlib import Path
from re import A

import holoviews as hv
import numpy as np
import scipy.signal as sig
from scipy.signal import find_peaks

from ..io.field import Parser
from ..io.input import InputFile
from ..math import waves

hv.extension("bokeh")  # pyright: ignore


def _read_station_file(dpath):

    input = InputFile.from_file(dpath)
    fpath = dpath / input.get_str("STATIONS_FILE")
    out_dpath = dpath / input.get_str("RESULT_FOLDER")
    dt = input.get_flt("PLOT_INTV_STATION")
    idxs = np.loadtxt(fpath).astype(int) - 1

    dx, dy = [input.get_flt(s) for s in ["DX", "DY"]]
    nx, ny = [input.get_int(s) for s in ["Mglob", "Nglob"]]

    min_depth = input.get_flt("MinDepth")
    i = idxs[:, 0]
    j = idxs[:, 1]

    bathy = Parser(dpath, input).read_bathy()

    x = (0.5 + i) * dx
    y = (0.5 + j) * dy

    filt_i = (0 <= i) & (i < nx)
    filt_j = (0 <= j) & (j < ny)
    filt = filt_i & filt_j

    n = len(i)
    h = np.zeros(n)
    h[filt] = -bathy[j[filt], i[filt]]
    h[~filt] = np.nan

    is_valid = np.zeros(n).astype(bool)
    is_valid[filt] = True

    k = np.arange(n) + 1

    return i, j, x, y, h, k, is_valid, dt, min_depth, out_dpath


class Station:
    """Class for handling a station"""

    # pylint: disable=too-many-instance-attributes
    def __init__(
        self,
        k: int,
        i: int,
        j: int,
        x: float,
        y: float,
        h: float,
        is_valid: bool,
        dt: float,
        min_depth: float,
        dpath: Path | str,
    ) -> None:

        if isinstance(dpath, str):
            dpath = Path(dpath)

        self._fpath = dpath / f"sta_{k:04d}"
        self._k = int(k)
        self._i = int(i)
        self._j = int(j)
        self._x = float(x)
        self._y = float(y)
        self._h = float(h)
        self._dt = float(dt)
        self._is_valid = is_valid

        self._min_depth = min_depth

    def _load_data(self) -> np.ndarray:
        """Returns data from station file"""
        data = np.loadtxt(self._fpath)
        t = data[:, 0]

        return data
        # Filtering repeated data
        dt = np.diff(t)
        i = np.argmin(dt)

        if dt[i] == 0:
            return data[:i, :]

        else:
            return data

    def eta_timeseries(self) -> tuple[np.ndarray, np.ndarray]:
        """Returns timestamp and eta timeseries data for station"""
        data = self._load_data()
        t = data[:, 0]
        eta = data[:, 1]
        return t, eta

    def compute_spectra(
        self, tlim: None | tuple[None | float, None | float] = None, **kwargs
    ) -> tuple[np.ndarray, np.ndarray, float, float]:
        t, eta = self.eta_timeseries()
        return waves.compute_spectral_density(eta, self._dt, t=t, tlim=tlim, **kwargs)

    def compute_overtopping(
        self, direction: float | tuple[float, float] = (1, 0), method: str = "vector"
    ):

        match method:
            case "vector":
                if not isinstance(direction, tuple):
                    raise ValueError(
                        f"Expected a tuple of two numbers for method {method}"
                    )
                nx, ny = direction

            case "point":
                if not isinstance(direction, tuple):
                    raise ValueError(
                        f"Expected a tuple of two numbers for method {method}"
                    )

                x1, y1 = direction
                nx = x1 - self.x
                ny = y1 - self.y

            case "cartesian":
                if not isinstance(direction, float):
                    raise ValueError(f"Expected a number for method {method}")

                angle = np.deg2rad(direction)
                nx = np.cos(angle)
                ny = np.sin(angle)

            case "true_north":
                raise NotImplementedError
            case _:
                raise TypeError(f"Unknown method {method}")

        # Normalizing
        d = np.sqrt(nx**2 + ny**2)
        nx /= d
        ny /= d

        data = self._load_data()
        t = data[:, 0]
        eta = data[:, 1]
        u = data[:, 2]
        v = data[:, 3]

        s = u * nx * v * ny

        wl = eta - self._h
        wl[wl < self._min_depth] = self._min_depth

        flux = wl * u

        return t, flux, s

    @property
    def k(self) -> int:
        """Station indices with starting index 1"""
        return self._k

    @property
    def i(self) -> int:
        """Station x location indices with starting index 0"""
        return self._i

    @property
    def j(self) -> int:
        """Station y locaation indices with starting index 0"""
        return self._j

    @property
    def x(self) -> float:
        """Station x locations"""
        return self._x

    @property
    def y(self) -> float:
        """Station y locations"""
        return self._y

    @property
    def h(self) -> float:
        """Station depths"""
        return self._h


class Runup:

    def __init__(self, x, h, eta, min_depth=0):

        self._x = x
        self._h = h

        data = eta.copy()
        nt, _ = eta.shape

        for i in range(nt):
            data[i, :] = data[i, :] + h + min_depth

        self._water_height = data
        self._idxs = [np.where(a[:-1] * a[1:] < 0)[0] for a in data]

    def simple_filter(self, n_range):
        """Returns zeros"""
        # Seperating zeros data based on initial zero
        lines = []
        for i0 in self._idxs[0]:
            line = [np.array([i0])]

            for next_idxs in self._idxs[1:]:

                idxs = [k for k in next_idxs if abs(k - i0) <= n_range]

                if len(idxs) == 0:
                    break

                line.append(np.array(idxs))

            lines.append(line)

        # Refining zero point
        # NOTE: indices can be float with non-integer part used for linear interpolation
        def get_point(i, j):

            jp = j + 1
            wh = self._water_height[i, j]
            whp = self._water_height[i, jp]

            # NOTE: Interpolation causes osscilations
            return j

            if wh < whp:
                return np.interp(0, [wh, whp], [j, jp])
            else:
                return np.interp(0, [whp, wh], [jp, j])

        raw_lines = lines
        lines = []
        for raw_line in raw_lines:

            line = []
            for i, idxs in enumerate(raw_line):

                line.append(np.array([get_point(i, j) for j in idxs]))

            lines.append(line)

        # Computing min and max index for each given rangge
        raw_lines = lines
        lines = []
        for raw_line in raw_lines:

            lines.append(
                {
                    #'raw': raw_line,
                    "max": np.array([s.max() for s in raw_line]),
                    "min": np.array([s.min() for s in raw_line]),
                }
            )

        raw_lines = lines
        lines = []

        def convolve(data, window_size=31):
            n = window_size // 2
            data = np.concatenate([[data[0]] * n, data, [data[-1]] * n])
            return np.convolve(data, np.ones(window_size), "valid") / window_size

        # Smoothingg data
        for raw_line in raw_lines:

            max_i = raw_line["max"]
            min_i = raw_line["min"]

            for _ in range(0):
                max_i = convolve(max_i, window_size=31)
                min_i = convolve(min_i, window_size=31)

            lines.append(
                {
                    #'raw': raw_line,
                    "max": max_i,
                    "min": min_i,
                }
            )

        # Interpolating distance and height using 'float' indices
        def get_values(idxs, vals):
            i = np.floor(idxs).astype(int)
            s = idxs - i
            return (1 - s) * vals[i] + s * vals[i + 1]

        raw_lines = lines
        lines = []
        for raw_line in raw_lines:

            max_i = raw_line["max"]
            min_i = raw_line["min"]

            lines.append(
                {
                    "i": raw_line,
                    "x": {
                        "max": get_values(max_i, self._x),
                        "min": get_values(min_i, self._x),
                    },
                    "h": {
                        "max": get_values(max_i, -self._h),
                        "min": get_values(min_i, -self._h),
                    },
                }
            )
        return lines


class Transect:

    def __init__(self, stations: list[Station]) -> None:
        self._items = stations  # [:200]

        self._i = np.array([s.i for s in self._items]).astype(int)
        self._j = np.array([s.j for s in self._items]).astype(int)
        self._h = np.array([s.h for s in self._items]).astype(float)
        self._x = np.array([s.x for s in self._items]).astype(float)

    def load_data(self):

        ns = len(self._items)

        t, eta = self._items[0].eta_timeseries()
        nt = len(t)

        data = np.zeros([ns, nt])

        data[0, :] = eta

        for i, s in enumerate(self._items[1:], start=1):

            _, eta = s.eta_timeseries()
            data[i, :] = eta

        data = data.T

        # for i in range(nt):
        #   data[i, :] = data[i, :] + self._h

        return t, data

    def compute_runup(self, n_range, distance):

        t, data = self.load_data()

        runup = Runup(self._x, self._h, data)
        data = runup.simple_filter(n_range)[0]

        def process(data):

            idxs, _ = find_peaks(data, distance=distance)
            peaks = data[idxs]
            n = len(peaks)
            i = int(0.98 * n)
            return {"data": data, "peaks": peaks, "r2": np.mean(np.sort(peaks)[i:])}

        data = {
            "t": t,
            "x": process(data["x"]["min"] - data["x"]["min"][0]),
            "h": process(data["h"]["min"]),
        }

        filt = data["h"]["data"] < 0
        data["h"]["data"][filt] = 0

        return data

    def plot_runup(self, n_range, distance):

        scale = 1 / 3600
        t_label = "Time (hr)"
        fontsize = {
            "labels": 18,
            "xticks": 16,
            "yticks": 16,
            "legend": 16,
        }

        def _plot_runup(data, var_label):

            plt = hv.Curve(zip(t * scale, data["data"]))

            plt.opts(
                width=1000,
                xlabel=t_label,
                show_grid=True,
                ylabel=var_label,
                fontsize=fontsize,
            )

        data = self.compute_runup(n_range, distance)

        t = data["t"]


class Stations:
    """Class for handling stations file"""

    # pylint: disable=too-many-instance-attributes
    def __init__(
        self,
        dpath: Path | str,
    ):
        """Parse FUNWAVE simulations by folder containing input.txt file"""

        if isinstance(dpath, str):
            dpath = Path(dpath)

        i, j, x, y, h, k, is_valid, dt, min_depth, out_dpath = _read_station_file(dpath)

        self._k = k
        self._i = i
        self._j = j
        self._x = x
        self._y = y
        self._h = h
        self.is_valid = is_valid
        self._dt = dt
        # self.out_dpath = out_dpath

        args = zip(k, i, j, x, y, h, is_valid)
        self._items = [Station(*a, dt, min_depth, out_dpath) for a in args]

    def __getitem__(self, key: int) -> Station:
        return self._items[key - 1]

    def compute_transmission(
        self,
        indices: list[int],
        tlim: None | tuple[None | float, None | float] = None,
        **kwargs,
    ):

        stas = [self[i] for i in indices]
        x = np.array([s.x for s in stas])
        y = np.array([s.y for s in stas])

        strip = lambda a, b, c, d: d

        hm0 = np.array([strip(*s.compute_spectra(tlim=tlim, **kwargs)) for s in stas])
        hm0 /= hm0[0]
        return x, y, hm0

    @property
    def k(self) -> np.ndarray:
        """Station indices with starting index 1"""
        return self._k

    @property
    def i(self) -> np.ndarray:
        """Station x location indices with starting index 0"""
        return self._i

    @property
    def j(self) -> np.ndarray:
        """Station y locaation indices with starting index 0"""
        return self._j

    @property
    def x(self) -> np.ndarray:
        """Station x locations"""
        return self._x

    @property
    def y(self) -> np.ndarray:
        """Station y locations"""
        return self._y

    @property
    def h(self) -> np.ndarray:
        """Station depths"""
        return self._h

    def to_simple_transects(self, n_transects: int) -> list[Transect]:

        n = len(self._items)
        m = n // n_transects

        return [Transect(self._items[i : (i + m)]) for i in range(0, n, m)]
