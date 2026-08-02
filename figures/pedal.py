"""Figures for the pedal-actuation robot, built from the repo's own bench data."""
import sys, numpy as np, pandas as pd
import matplotlib.pyplot as plt
sys.path.insert(0, ".")
import style
from style import S1, S2, INK, INK_2, MUTED, GRID

style.apply()
REPO = "../automotive-driving-robot"
OUT = "assets/fig"
import os; os.makedirs(OUT, exist_ok=True)

# ---------------------------------------------------------------- step response
d = pd.read_csv(f"{REPO}/Sys_Ident/Step/Step255_T3500_tT5000.csv")
t = d["Time (ms)"].to_numpy(float)
pos = d["Analogue Pedal Reading"].to_numpy(float)
pwm = d["Input PWM"].to_numpy(float)

step_i = int(np.argmax(pwm > 0))
t0 = t[step_i]
base = float(np.median(pos[:step_i])) if step_i > 5 else pos[0]
final = float(np.median(pos[-80:]))
span = final - base


def cross(frac):
    target = base + frac * span
    idx = np.where((t >= t0) & (pos >= target))[0]
    return t[idx[0]] - t0 if len(idx) else np.nan


t10, t90 = cross(0.10), cross(0.90)
rise = t90 - t10
overshoot = (pos[t >= t0].max() - final) / span * 100

fig, (a1, a2) = plt.subplots(
    2, 1, figsize=(7.4, 4.5), sharex=True,
    gridspec_kw={"height_ratios": [1, 2.1], "hspace": 0.08})

a1.plot(t / 1000, pwm, color=S2, lw=2)
a1.set_ylabel("Input\nPWM")
a1.set_ylim(-18, 285)
a1.set_yticks([0, 255])
a1.set_title("Commanded step", color=INK_2, fontsize=9)
style.tidy(a1, hide_x=True)

a2.plot(t / 1000, pos, color=S1, lw=2)
a2.set_ylabel("Pedal position  (ADC counts)")
a2.set_xlabel("Time  (s)")
a2.set_title("Measured pedal response", color=INK_2, fontsize=9)
a2.axhline(final, color=MUTED, lw=0.9, ls=(0, (4, 3)), zorder=1)
a2.axhline(base, color=MUTED, lw=0.9, ls=(0, (4, 3)), zorder=1)

# 10-90 rise band
a2.axvspan((t0 + t10) / 1000, (t0 + t90) / 1000, color=S1, alpha=0.09, lw=0, zorder=0)
mid = (t0 + (t10 + t90) / 2) / 1000
a2.annotate(f"10–90% rise\n{rise:.0f} ms", xy=(mid, base + 0.5 * span),
            xytext=(mid + 0.42, base + 0.42 * span), color=INK_2, fontsize=8.5,
            ha="left", va="center",
            arrowprops=dict(arrowstyle="-", color=MUTED, lw=0.9,
                            shrinkA=0, shrinkB=2))
a2.annotate(f"settles at {final:.0f}", xy=(t[-1] / 1000, final), xytext=(-4, 7),
            textcoords="offset points", ha="right", color=INK_2, fontsize=8.5)
a2.annotate(f"rest {base:.0f}", xy=(0.05, base), xytext=(0, 7),
            textcoords="offset points", color=INK_2, fontsize=8.5)
style.tidy(a2)

fig.suptitle("Open-loop step response of the pedal actuator",
             x=0.008, ha="left", color=INK, fontsize=11, fontweight="600")
fig.savefig(f"{OUT}/pedal-step-response.svg", format="svg")
plt.close(fig)

# ------------------------------------------------------------------------ PRBS
p = pd.read_csv(f"{REPO}/Sys_Ident/PRBS/T3000_sped100_seed69_Ts50_150.csv",
                header=None, names=["t", "pos", "pwm"])
fig, (a1, a2) = plt.subplots(
    2, 1, figsize=(7.4, 4.3), sharex=True,
    gridspec_kw={"height_ratios": [1, 1.7], "hspace": 0.08})

a1.step(p["t"] / 1000, p["pwm"], color=S2, lw=1.8, where="post")
a1.set_ylabel("PRBS drive\n(PWM)")
a1.set_yticks([-125, 0, 125])
a1.set_ylim(-175, 175)
a1.set_title("Pseudo-random binary excitation", color=INK_2, fontsize=9)
style.tidy(a1, hide_x=True)

a2.plot(p["t"] / 1000, p["pos"], color=S1, lw=1.8)
a2.set_ylabel("Pedal position  (ADC counts)")
a2.set_xlabel("Time  (s)")
a2.set_title("Plant response used to fit the actuator model", color=INK_2, fontsize=9)
style.tidy(a2)

fig.suptitle("System identification: PRBS excitation and response",
             x=0.008, ha="left", color=INK, fontsize=11, fontweight="600")
fig.savefig(f"{OUT}/pedal-prbs.svg", format="svg")
plt.close(fig)

# ------------------------------------------------------- sensor cross-validation
c = pd.read_csv(f"{REPO}/Pedal_and_Pot_Pos_Read/Crank Correlation.csv")
ped = c["Ped Normalised"].to_numpy(float)
pot = c["Pot Normalised"].to_numpy(float)
tt = c["Time"].to_numpy(float)
r = float(np.corrcoef(ped, pot)[0, 1])
err = np.abs(ped - pot)

fig, ax = plt.subplots(figsize=(7.4, 3.5))
ax.plot(tt, ped, color=S1, lw=2, label="Pedal sensor")
ax.plot(tt, pot, color=S2, lw=2, ls=(0, (5, 2.5)), label="Crank potentiometer")
ax.set_xlabel("Sample")
ax.set_ylabel("Normalised travel")
ax.set_ylim(-0.05, 1.16)
ax.set_yticks([0, 0.5, 1.0])
ax.legend(loc="upper left", ncol=2, columnspacing=1.4, handlelength=1.8)
ax.set_title(f"r = {r:.4f}     mean absolute error {err.mean()*100:.1f}% of travel",
             color=INK_2, fontsize=9)
style.tidy(ax)
fig.suptitle("Two independent sensors agree across the full pedal stroke",
             x=0.008, ha="left", color=INK, fontsize=11, fontweight="600")
fig.savefig(f"{OUT}/pedal-sensor-agreement.svg", format="svg")
plt.close(fig)

print(f"rise(10-90) = {rise:.0f} ms | base {base:.0f} -> final {final:.0f} "
      f"(span {span:.0f}) | overshoot {overshoot:.1f}%")
print(f"sensor r = {r:.4f} | mean abs err = {err.mean()*100:.2f}%")
print("wrote 3 svg")
