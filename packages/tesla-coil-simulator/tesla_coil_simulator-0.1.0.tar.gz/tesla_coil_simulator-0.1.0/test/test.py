from typing import Dict

import matplotlib.pyplot as plt
import numpy as np

from tesla_coil_simulator.DRSSTC import RLC, find_resonant_poles, simulate_coupled_RLC
from tesla_coil_simulator.utils import format_num


def fixed_freq_square_Uin(f, amp):
    def fixed_freq_square_Uin(t, sol_t):
        return amp * np.sign(np.sin(2 * np.pi * f * t))

    return fixed_freq_square_Uin


def primary_current_feedback_square_Uin(amp):
    def primary_current_feedback_square_Uin(t, sol_t):
        Vx, Ix, Vy, Iy = sol_t
        if t == 0:
            return amp  # kickstart!
        return amp * np.sign(Ix)  # following primary current Ix

    return primary_current_feedback_square_Uin


def max_voltage_vs_driving_freq(x: RLC, y: RLC, k, time, f_list_dic: Dict, amp):
    for key, f_list in f_list_dic.items():
        Vy_max, Vy_idx = [], 2
        for f in f_list:
            Uin = fixed_freq_square_Uin(f, amp)
            sol = simulate_coupled_RLC(x, y, k, time, Uin, plot=False)
            Vy_max.append(np.max(sol.y[Vy_idx]))
        if len(f_list) < 10:
            plt.scatter(f_list, Vy_max, s=20, label=key)
        else:
            plt.plot(f_list, Vy_max, label=key)
    plt.legend()
    plt.title("max secondary voltage VS driving freq")
    plt.savefig("max_voltage_vs_driving_freq")
    plt.close()


def max_voltage_vs_coupling(x: RLC, y: RLC, k_list, time, amp):
    Vy_max, Vy_idx = [], 2
    for k in k_list:
        Uin = primary_current_feedback_square_Uin(amp)
        sol = simulate_coupled_RLC(x, y, k, time, Uin, plot=False)
        Vy_max.append(np.max(sol.y[Vy_idx]))
    plt.plot(k_list, Vy_max)
    plt.title("max secondary voltage VS coupling coefficient")
    plt.savefig("max_voltage_vs_coupling")
    plt.close()


x = RLC(R=0.1, L=6e-6, C=50e-9)
y = RLC(R=500, L=50e-3, C=6e-12)
k = 0.1  # coupling coefficient
amp = 300  # amplitude of driving voltage Uin (V)
f_poles = find_resonant_poles(x, y, k)
info = f"""
primary: {x}
secondary: {y}
coupling (k): {k}
resonant poles: {[f"{format_num(f)}Hz" for f in f_poles]}
"""
print(info)

time = np.linspace(0, 200e-6, 1000)

Uin = fixed_freq_square_Uin(250e3, amp)
simulate_coupled_RLC(x, y, k, time, Uin, plot=True)

Uin = primary_current_feedback_square_Uin(amp)
simulate_coupled_RLC(x, y, k, time, Uin, plot=True)

f_list_dic = dict(freq=np.linspace(200e3, 400e3, 100).tolist(), f_poles=f_poles)
max_voltage_vs_driving_freq(x, y, k, time, f_list_dic, amp)

k_list = np.logspace(np.log10(0.005), np.log10(0.2), 100)
max_voltage_vs_coupling(x, y, k_list, time, amp)
