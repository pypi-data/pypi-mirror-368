from collections.abc import Callable
from functools import partial

import numpy as np
import scipy
import scipy.signal as sig
from scipy import constants, interpolate


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


def _f(k: float, w: float, h: float) -> float:
    g = constants.G
    return g * k * np.tanh(k * h) - w**2


def _dfdk(k: float, w: float, h: float) -> float:
    g = constants.G
    return g * (np.tanh(k * h) + k * h * np.cosh(k * h) ** -2)


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


def compute_reflection(array, h, dt, dl):

    _N_EQNS_ = 3
    grav = constants.G

    _, n = array.shape
    # Round down nearest even number
    n -= n % 2
    array = array[:, :n]
    nhalf = n // 2
    shp = (_N_EQNS_, nhalf)

    # Precomputing coefficents
    a_n = np.zeros(shp)
    b_n = np.zeros(shp)
    s_n = np.zeros(shp)

    for i, x in enumerate(data):
        fn = scipy.fft.fft(x, n)

        a_n[i, :] = 2 * np.real(fn[1:nhalf]) / n  # Real component
        b_n[i, :] = -2 * np.imag(fn[1:nhalf]) / n  # Imaginary component

        fn_squared = np.abs(fn) ** 2
        fn_fold = fn_squared[1:nhalf] * 2
        s_n[i, :] = dt * fn_fold / n  # Spectral/energy density

    df = 1 / (n * dt)
    f = df * np.arange(nhalf)  # Frequencies

    # Computing wave numbers using dispersion relationship
    k = np.array([solve_dispersion(h=h, w=2 * np.pi * f0) for f0 in f])

    a_inc = np.zeros(shp)
    b_inc = np.zeros(shp)
    a_ref = np.zeros(shp)
    b_ref = np.zeros(shp)
    nmin = np.zeros(_N_EQNS_)
    nmax = np.zeros(_N_EQNS_)
    g1 = [0, 0, 1]
    g2 = [1, 2, 2]
    gpos = np.append(0, dl)
    # gpos = [0, 0.30, 0.90]  # Distance from first gauge in the array

    for i in range(3):
        a_1 = a_n[g1[i], :]
        a_2 = a_n[g2[i], :]
        b_1 = b_n[g1[i], :]
        b_2 = b_n[g2[i], :]
        pos1 = gpos[g1[j]]
        pos2 = gpos[g2[j]]

        term1 = (
            -a_2 * np.sin(k * pos1)
            + a_1 * np.sin(k * pos2)
            + b_2 * np.cos(k * pos1)
            - b_1 * np.cos(k * pos2)
        )
        term2 = (
            a_2 * np.cos(k * pos1)
            - a_1 * np.cos(k * pos2)
            + b_2 * np.sin(k * pos1)
            - b_1 * np.sin(k * pos2)
        )
        term3 = (
            -a_2 * np.sin(k * pos1)
            + a_1 * np.sin(k * pos2)
            - b_2 * np.cos(k * pos1)
            + b_1 * np.cos(k * pos2)
        )
        term4 = (
            a_2 * np.cos(k * pos1)
            - a_1 * np.cos(k * pos2)
            - b_2 * np.sin(k * pos1)
            + b_1 * np.sin(k * pos2)
        )

        a_inc[i, :] = term1 / (2 * np.sin(k * (pos2 - pos1)))
        b_inc[i, :] = term2 / (2 * np.sin(k * (pos2 - pos1)))

        a_ref[i, :] = term3 / (2 * np.sin(k * (pos2 - pos1)))
        b_ref[i, :] = term4 / (2 * np.sin(k * (pos2 - pos1)))

        # Upper and lower limits of significant spectra
        l_min = abs(pos2 - pos1) / 0.45  # Ranges suggested by Goda and Suzuki (1976)
        l_max = abs(pos2 - pos1) / 0.05

        kmin = 2 * np.pi / l_min
        kmax = 2 * np.pi / l_max

        wmin = np.sqrt(g * kmin * np.tanh(kmin * h))
        wmax = np.sqrt(g * kmax * np.tanh(kmax * h))

        fmin = wmin / (2 * np.pi)
        fmax = wmax / (2 * np.pi)

        nmin[j] = round(fmax / df)
        nmax[j] = round(fmin / df)

    range_idx = np.arange(int(np.min(nmin)), int(np.max(nmax)) + 1)

    for j in range(3):
        for i in range(len(a_inc)):
            if i < nmin[j] or i > nmax[j]:
                a_inc[i, j] = np.nan
                b_inc[i, j] = np.nan
                a_ref[i, j] = np.nan
                b_ref[i, j] = np.nan

    a_incav = np.nanmean(a_inc[range_idx, :], axis=1)
    b_incav = np.nanmean(b_inc[range_idx, :], axis=1)
    a_refav = np.nanmean(a_ref[range_idx, :], axis=1)
    b_refav = np.nanmean(b_ref[range_idx, :], axis=1)

    # Backing out spectra
    s_i = (a_incav**2 + b_incav**2) / (2 * df)
    s_r = (a_refav**2 + b_refav**2) / (2 * df)
    Sfcheck = (An**2 + Bn**2) / (2 * df)

    # Evaluate energies of resolved incident and reflected waves
    e_i = np.sum(s_i) * df
    e_r = np.sum(s_r) * df

    # Reflection coefficient
    refco = np.sqrt(e_r / e_i)

    # Calculate incident, reflected, and total Hmo wave height
    mo = np.sum(Sn, axis=0) * df
    h_tot = 4.004 * np.sqrt(mo)
    h_i = 4.004 * np.sqrt(e_i)
    h_r = 4.004 * np.sqrt(e_r)
    h_icheck = np.mean(h_tot) / np.sqrt(1 + refco**2)
    h_rcheck = refco * np.mean(h_tot) / np.sqrt(1 + refco**2)


def compute_spectral_density(
    eta: np.ndarray,
    dt: float,
    t: None | np.ndarray,
    tlim: None | tuple[float | None, float | None],
    **kwargs
) -> tuple[np.ndarray, np.ndarray, float, float]:

    if t is None:
        if tlim is not None:
            raise NotImplementedError()
    else:
        if tlim is not None:
            t0, t1 = tlim
            if t0 is None:
                t0 = t.min()
            if t1 is None:
                t1 = t.max()
        else:
            t0, t1 = t.min(), t.max()

        # Interpolating onto equispaced grid
        n = int(np.round((t1 - t0) / dt))
        ti = np.arange(n + 1) * dt + t0
        eta = np.interp(ti, t, eta)

    if len(kwargs) == 0:
        kwargs["nfft"] = len(eta)

    freq, density = sig.welch(eta, 1 / dt, scaling="density", **kwargs)

    energy = float(np.trapezoid(density, freq))
    hm0 = 4 * np.sqrt(energy)

    return freq, density, energy, hm0
