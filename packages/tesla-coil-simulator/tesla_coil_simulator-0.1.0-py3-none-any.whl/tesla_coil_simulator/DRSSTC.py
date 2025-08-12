from typing import Callable

import numpy as np
from numpy import sqrt
from scipy.integrate import solve_ivp

from .utils import format_num as fm
from .utils import plot_coupled_RLC_sol

PI2 = 2 * np.pi


class RLC:
    def __init__(s, R, L, C, type="series"):
        s.R, s.L, s.C, s.type = R, L, C, type
        s.f0 = 1 / (PI2 * sqrt(L * C))
        if type == "series":
            s.Q = sqrt(L / C) / R
        elif type == "parallel":
            s.Q = sqrt(C / L) * R

    def __repr__(s):
        return f"R: {fm(s.R)}Ω, L: {fm(s.L)}H, C: {fm(s.C)}F, f0: {fm(s.f0)}Hz, Q: {fm(s.Q)}"

    def find_L_by_f(s, f):
        return (1 / f / PI2) ** 2 / s.C


def find_resonant_poles(x: RLC, y: RLC, k):
    M = k * sqrt(x.L * y.L)
    # need to verify below
    a4 = (x.L * y.L - M**2) * x.C * y.C
    a3 = 0
    a2 = -(x.L * x.C + y.L * y.C)
    a1 = 0
    a0 = 1
    fs = np.roots([a4, a3, a2, a1, a0]) / PI2
    return sorted([f for f in fs if f > 0])


def simulate_coupled_RLC(
    x: RLC,
    y: RLC,
    k: float,
    time: np.ndarray,
    Uin: Callable,
    plot=True,
):
    assert x.type == y.type == "series", "DRSSTC uses series RLC!"
    M = k * sqrt(x.L * y.L)

    def func(t, sol_t):
        Vx, Ix, Vy, Iy = sol_t
        dVx_dt = Ix / x.C
        dVy_dt = Iy / y.C
        """
        x.L * dIx_dt + M   * dIy_dt = Uin(t) - Vx - x.R * Ix
        M   * dIx_dt + y.L * dIy_dt = 0      - Vy - y.R * Iy
        A x = B
        """
        A = [[x.L, M], [M, y.L]]
        B = [Uin(t, sol_t) - Vx - x.R * Ix, 0 - Vy - y.R * Iy]
        dIx_dt, dIy_dt = np.linalg.solve(A, B)
        return [dVx_dt, dIx_dt, dVy_dt, dIy_dt]

    t_span = [time[0], time[-1]]
    vars0 = [0, 0, 0, 0]
    sol = solve_ivp(func, t_span, vars0, t_eval=time)
    if plot:
        plot_coupled_RLC_sol(Uin, sol)
    return sol
