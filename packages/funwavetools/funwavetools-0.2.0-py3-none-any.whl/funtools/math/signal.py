from collections.abc import Callable
from functools import partial

import numpy as np
import scipy.signal as sig
from scipy import interpolate


def newton_iterative(
    f: Callable,
    df: Callable,
    x0: float,
    tolerance: float = 10**-8,
    max_iterations: int = 100,
) -> float:

    x = x0
    for i in range(max_iterations):

        dx = -f(x) / df(x)
        x += dx
        if np.abs(dx) < tolerance:
            break

    return x


g = 9.81


def _f(k: float, w: float, h: float) -> float:
    return g * k * np.tanh(k * h) - w**2


def _dfdk(k: float, w: float, h: float) -> float:
    return g * np.tanh(k * h) + g * k * np.cosh(k * h) ** -2


def solve_dispersion(w=None, h=None, k=None, tolerance=10**-8, max_iterations=100):

    is_w, is_h, is_k = chks = tuple((x is not None for x in [w, h, k]))

    n = int(np.sum(chks))
    if not n == 2:
        raise Exception("Must specify only two of w, h, and k")

    if not is_k:
        # Linear approximation
        k0 = np.sqrt(w**2 / (g * h))
        f = partial(_f, w=w, h=h)
        df = partial(_dfdk, w=w, h=h)
        return newton_iterative(
            f, df, k0, tolerance=tolerance, max_iterations=max_iterations
        )

    elif not is_w:
        raise NotImplementedError()
    elif not is_h:
        raise NotImplementedError()

    # Sanity check
    raise Exception("Unexpected State")



def compute_spectral_density(
        eta: np.ndarray,
        dt: float,
        t: None | np.ndarray,
        tlim: None | tuple[float|None, float|None],
        **kwargs 
    ) -> tuple[np.ndarray, np.ndarray, float, float]:


    if t is None:
        if tlim is not None:
            raise NotImplementedError()
    else:
        if tlim is not None:
            t0, t1 = tlim
            if t0 is None: t0 = t.min()
            if t1 is None: t1 = t.max()
        else:
            t0, t1 = t.min(), t.max()

        # Interpolating onto equispaced grid
        n = int(np.round((t1 - t0) / dt))
        ti = np.arange(n + 1) * dt + t0
        eta = np.interp(ti, t, eta)
    
    if len(kwargs) == 0:
        kwargs["nfft"] = len(eta)

    freq, density = sig.welch(eta, 1/dt, scaling="density", **kwargs)

    energy = np.trapezoid(density, freq)
    hm0 = 4*np.sqrt(energy)

    return freq, density, energy, hm0





