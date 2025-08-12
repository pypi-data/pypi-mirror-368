import matplotlib.pyplot as plt
import numpy as np

SCALES = ["G", "M", "k", "", "m", "u", "n", "p"]


def format_num(x: float):
    scale = 1e9
    for s in SCALES:
        if x / scale >= 1:
            return f"{x / scale:.3g} {s}"
        scale /= 1e3


def plot_coupled_RLC_sol(Uin_func, sol):
    Uin = np.array([Uin_func(t, sol.y[:, i]) for i, t in enumerate(sol.t)])
    labels = ["V_primary", "I_primary", "V_secondary", "I_secondary"]
    units = ["V", "A", "V", "A"]
    R, C = 1 + len(sol.y), 1
    plt.figure(figsize=(9 * C, R * 3))
    i = 1
    plt.subplot(R, C, i)
    plt.title(f"Uin ({Uin_func.__name__}). max = {format_num(Uin.max())}V")
    plt.plot(sol.t, Uin)
    for k, y in enumerate(sol.y):
        i += 1
        plt.subplot(R, C, i)
        plt.title(f"{labels[k]}. max = {format_num(y.max())}{units[k]}")
        plt.plot(sol.t, y)
    plt.tight_layout()
    plt.savefig(Uin_func.__name__)
    plt.close()
