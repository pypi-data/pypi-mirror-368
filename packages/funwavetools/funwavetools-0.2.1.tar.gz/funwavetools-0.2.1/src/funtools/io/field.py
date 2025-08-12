from pathlib import Path

import numpy as np

from ..math import grid
from ..math.geometry import Polygon
from ..math.projection import LinkedProjections
from .input import InputFile


class Parser:
    def __init__(self, dpath: Path, input: InputFile | None = None) -> None:
        if input is None:
            input = InputFile.from_file(dpath)

        self._dpath = dpath / input.get_str("RESULT_FOLDER")

        self._is_2d = input.get_int("Nglob") > 3



        self._waterlevel = input.get_flt('WaterLevel')



        self._bathy_type = input.get_str('DEPTH_TYPE')


        match self._bathy_type:
            case 'DATA':
                self._bathy_fpath = dpath/ input.get_str('DEPTH_FILE')

            case 'SLOPE':
                self._depth_flat = input.get_flt('DEPTH_FLAT')
                self._slp = input.get_flt('SLP')
                self._xslp = input.get_flt('Xslp')
            case 'FLAT':
                self._depth_flat = input.get_flt('DEPTH_FLAT')
            case _:
                raise ValueError(f"Invalid DEPTH_TYPE '{self._bathy_type}' detected in input file.")

        self._m, self._n = m, n = [input.get_int(s) for s in ["Mglob", "Nglob"]]
        self._dx, self._dy = dx, dy = [input.get_flt(s) for s in ["DX", "DY"]]
        self._x, self._y = grid.rectilinear2d(m, dx, n, dy)

        self._xb, self._yb = grid.rectilinear2d(m, dx, n, dy, mode='border')
        self._si = self._sj = 1
        self._sx = slice(0, m)
        self._sy = slice(0, n)

        self._i_west = self._get_i(input.get_flt("Sponge_west_width"))
        self._i_east = self._get_i(dx * m - input.get_flt("Sponge_east_width"))

        self._j_south = self._get_j(input.get_flt("Sponge_south_width"))
        self._j_north = self._get_j(dy * n - input.get_flt("Sponge_north_width"))

        self._i_wave = self._get_i(input.get_flt("Wc_WK"))

        is_binary = input.get_str("FIELD_IO_TYPE") == "BINARY"
        self.__read = self._read_binary if is_binary else self._read_ascii

        self._view_bounds = self.bounds

        self._view_args = {}

    def get_type(self, name: str) -> tuple[bool, bool]:
        """Returns two bools indicating if variable is mean data or velocity data, respectively"""

        _normal_ = [
            "eta",
        ]

        _velocites_ = ["u", "v"]

        _mean_ = [
            "etamean",
            "Hsig",
            "Havg",
            "Hrms",
        ]

        _velocites_mean_ = [
            "umean",
            "vmean",
            "ulagm",
            "vlagm",
        ]

        if name in _normal_:
            return False, False

        if name in _velocites_:
            return False, True

        if name in _mean_:
            return True, False

        if name in _velocites_mean_:
            return True, True

        raise NotImplementedError(f"Type for variable {name} not implemented")

    def _get_i(self, x: float) -> int:
        """Get index of nearest x point in grid"""
        return round(x / self._dx)

    def _get_j(self, y: float) -> int:
        """Get index of nearest y point in grid"""
        return round(y / self._dy)

    def get_view_kwargs(self) -> dict:
        """Returns non-None set_view kwargs"""
        return {k: d for k, d in self._view_args.items() if not d is None}

    def get_time_steps(self, name: str) -> list[int]:
        """Return list of file indices by variable name"""

        def parse(fpath: Path) -> int:
            *_, i = fpath.name.split("_")
            return int(i)

        return sorted([parse(f) for f in self._dpath.glob(f"{name}_*")])

    def set_view(
        self,
        bounds: tuple[float, float, float, float] | None = None,
        stride: tuple[int, int] | int | None = None,
        crop_sponges: bool = False,
        crop_wavemaker: bool = False,
        remove_waterlevel: bool = False,
    ) -> None:
        """Set view of data"""

        self._view_args = {
            "bounds": bounds,
            "stride": stride,
            "crop_sponges": crop_sponges,
            "crop_wavemaker": crop_wavemaker,
        }

        # TODO: 1D support?
        i0 = self._i_west if crop_sponges else 0
        i1 = self._i_east if crop_sponges else self._m
        j0 = self._j_south if crop_sponges else 0
        j1 = self._j_north if crop_sponges else self._n

        if crop_wavemaker:
            i0 = self._i_wave

        # TODO: Add None support?
        if not bounds is None:
            x0, y0, x1, y1 = bounds
            # bounds do not override above cropping
            i0 = max(self._get_i(x0), i0)
            i1 = min(self._get_i(x1), i1)
            j0 = max(self._get_j(y0), j0)
            j1 = min(self._get_j(y1), j1)

        if stride is None:
            si = sj = 1
        elif isinstance(stride, int):
            si = sj = stride
        else:
            si, sj = stride

        if si == 1:
            self._sx = slice(i0, 10)
        else:
            self._sx = slice(i0, i1, si)

        if sj == 1:
            self._sy = slice(j0, j1)
        else:
            self._sy = slice(j0, j1, sj)

        x = self._x[self._sx]
        y = self._y[self._sy]

        dx = self._dx * si / 2
        dy = self._dy * sj / 2

        self.remove_waterlevel =remove_waterlevel
        self._view_bounds = x[0] - dx, y[0] - dy, x[-1] + dx, y[-1] + dy

    @property
    def x(self) -> np.ndarray:
        """Returns x grid points with set view"""
        return self._x[self._sx]

    @property
    def dx(self) -> float:
        """Return x grid spacing with stride"""
        return self._dx * self._si

    @property
    def y(self) -> np.ndarray:
        """Returns y grid points with set view"""
        return self._y[self._sy]

    @property
    def dy(self) -> float:
        """Return y grid spacing with stride"""
        return self._dy * self._sj

    @property
    def bounds(self) -> tuple[float, float, float, float]:
        return 0, 0, self._dx * self._m, self._dy * self._n

    @property
    def view_bounds(self) -> tuple[float, float, float, float]:
        return self._view_bounds

    def force_2d(self):
        if self._m > 3:
            raise Exception("Forcing 2D mode with 2D data")
        self._sy = slice(0, self._n, 1)

    def _read_binary(self, fpath: Path) -> np.ndarray:
        return np.fromfile(fpath, dtype="<f8").reshape([self._n, self._m])[
            self._sy, self._sx
        ]

    def _read_ascii(self, fpath: Path) -> np.ndarray:
        return np.loadtxt(fpath)[self._sy, self._sx]

    def _read(self, fpath: Path) -> np.ndarray:
        return self.__read(fpath)

    def read(self, fname: str) -> np.ndarray:
        return self._read(self._dpath / fname)

    def read_bathy(self) -> np.ndarray:

        fpath = self._dpath / 'dep.out'
        if fpath.exists():
            return -self._read(self._dpath / "dep.out")

        match self._bathy_type:

            case 'DATA':
                return -self._read_ascii(self._bathy_fpath)
            case 'FLAT':
                return -self._depth_flat*np.ones([self._n, self._m])
            case 'SLOPE':

                h = np.ones(self._m)*self._depth_flat
                filt = self._x > self._xslp
                x = self._x[filt]
                h[filt]= self._depth_flat - (x-self._xslp)*self._slp
                return np.vstack([-h]*self._n)



    def read_mask_step(self, index: int):
        return ~self.read_step("mask", index).astype(bool)

    def read_step(self, name: str, index: int, mask_data: bool = False) -> np.ndarray:
        fname = "%s_%05d" % (name, index)
        return self._read(self._dpath / fname)

    def _read_shape(self, fpath: str) -> Polygon:
        """Overrideable method for transforming polygon in child classes"""
        return Polygon.from_file(fpath)

    def read_shape(self, fpath: str) -> Polygon:
        """Returns Polygon and applies view"""
        poly = self._read_shape(fpath)
        return poly.apply_crop(self.view_bounds)  # , buffer_ratio=0.1)


class ProjectionParser(Parser):
    def __init__(
        self,
        dpath: Path,
        espg_code: int,
        transform_fpath: Path,
        input: InputFile | None = None,
    ) -> None:
        super().__init__(dpath, input)
        """"""
        self._proj = LinkedProjections.create_funwave(espg_code, transform_fpath)

        self._ui = np.array([])
        self._vi = np.array([])

        self._xi = np.array([])
        self._yi = np.array([])

        self._view_bounds = self._proj.bounds_to_source(*self.view_bounds)

    def set_view(
        self,
        bounds: tuple[float, float, float, float] | None = None,
        stride: tuple[int, int] | int | None = None,
        crop_sponges: bool = False,
        crop_wavemaker: bool = False,
        source: str | None = None,
        target: str | None = None,
        resolution: float | None = None,
    ) -> None:
        self._view_args = {
            "bounds": bounds,
            "stride": stride,
            "crop_sponges": crop_sponges,
            "crop_wavemaker": crop_wavemaker,
            "source": source,
            "target": target,
            "resolution": resolution,
        }

        # Computing bounding box in target coordinates
        if bounds is None:
            bounds = self._proj.bounds_to_source(*super().bounds, source=target)
        else:
            # TODO: Add support for reverse direction
            bounds = self._proj.bounds_to_source(*bounds, source=target, target=source)

        # Computing bounding box in FUNWAVE coordinates
        # if target is None:
        # fun_bounds = bounds
        # else

        fun_bounds = self._proj.bounds_to_target(
            *bounds, source=source
        )  # , source=target)

        super().set_view(fun_bounds, stride, crop_sponges, crop_wavemaker)

        # Restricting projected view to max data size
        # bounds = self._proj.bounds_to_source(*self.view_bounds, source=target)

        u0, v0, u1, v1 = bounds

        if resolution is None:
            du = dv = min(self._dx, self._dy)
        else:
            du = dv = resolution

        self._ui, self._vi = u, v = grid.nearest_linspace2d(u0, u1, du, v0, v1, dv)

        xi, yi = self._proj.to_target(*np.meshgrid(u, v), source=target)

        self._pts = self.y, self.x
        self._pts_interp = yi, xi

        self._view_bounds = (u[0] - du, v[0] - dv, u[-1] + du, v[-1] + dv)

        return
        shp = xi.shape
        # xi, yi = self._proj.to_target(u, v, source=target)
        # self._xi, self._yi = xi, yi = np.meshgrid(xi, yi)

        x0, y0, x1, y1 = self.view_bounds

        i = np.floor((xi - x0 + self.dx / 2) / self.dx).astype(int)
        j = np.floor((yi - y0 + self.dy / 2) / self.dy).astype(int)

        n, m = len(self.y), len(self.x)

        filt_x = (0 <= i) & (i < m - 1)
        filt_y = (0 <= j) & (j < n - 1)
        filt = filt_x & filt_y

        i, j, xi, yi = [s[filt] for s in [i, j, xi, yi]]
        ip, jp = i + 1, j + 1

        self._i, self._j, self._ip, self._jp = i, j, ip, jp
        x1, x2 = self.x[i], self.x[ip]
        y1, y2 = self.y[j], self.y[jp]

        self._empty_data = np.ones(shp) * np.nan

        factor = 1 / (self.dx * self.dy)

        self._w11 = (x2 - xi) * (y2 - yi) * factor
        self._w12 = (x2 - xi) * (yi - y1) * factor
        self._w21 = (xi - x1) * (y2 - yi) * factor
        self._w22 = (xi - x1) * (yi - y1) * factor
        self._filt = filt

        du, dv = du / 2, dv / 2
        self._view_bounds = (u[0] - du, v[0] - dv, u[-1] + du, v[-1] + dv)

    def _read_shape(self, fpath: str) -> Polygon:
        poly = super()._read_shape(fpath)
        return poly.apply_transform(self._proj.to_source)

    def _read(self, fpath: Path) -> np.ndarray:
        args = self._pts, super()._read(fpath)
        kwargs = {"bounds_error": False}

        from scipy.interpolate import RegularGridInterpolator

        return RegularGridInterpolator(*args, **kwargs)(self._pts_interp)
