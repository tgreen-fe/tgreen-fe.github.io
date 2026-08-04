"""3Pi+ straight-line control: figures built from the run logs and the
end-of-run tape measurements. Run from the site root:  python figures/threepi.py
"""
import sys, os, glob
import numpy as np
import pandas as pd
import matplotlib.pyplot as plt

sys.path.insert(0, "figures")
sys.path.insert(0, ".")
import style
from style import S1, S2, INK, INK_2, MUTED, GRID

style.apply()

DATA = os.environ.get("THREEPI_DATA", "../3pi-imitation-control/data")
OUT = "assets/fig"
os.makedirs(OUT, exist_ok=True)

# Greys for the two uncorrected baselines, blue for the classical corrector,
# orange for the learned one. Encoding: colour = family, not just series index.
C_PWM, C_PID, C_IMU, C_RL = "#a9a7a0", INK_2, S1, S2

RUNS = {
    "PWM":    ("pwm/test_*_pwm.csv",            C_PWM),
    "PID":    ("pid/test_*_pid.csv",            C_PID),
    "IMU":    ("imu/test_[012]_no_mass.csv",    C_IMU),
    "IMU-IL": ("imu-il/test_*_no_mass.csv",     C_RL),
}


def load(pattern):
    out = []
    for f in sorted(glob.glob(os.path.join(DATA, pattern))):
        d = pd.read_csv(f)
        out.append((d["x"].to_numpy(float) / 1000.0, d["y"].to_numpy(float) / 1000.0))
    return out


# --------------------------------------------------------------- 1. trajectories
fig, ax = plt.subplots(figsize=(7.4, 4.2))
ax.axhline(0, color=MUTED, lw=1, ls=(0, (4, 3)), zorder=1)

ends = []
for name, (pattern, colour) in RUNS.items():
    runs = load(pattern)
    if not runs:
        raise SystemExit(f"no data for {name} at {os.path.join(DATA, pattern)}")
    for x, y in runs:
        ax.plot(x, y, color=colour, lw=1.5, alpha=0.75, solid_capstyle="round")
    x_end = max(x[-1] for x, _ in runs)
    y_end = np.median([y[np.argmax(x)] for x, y in runs])
    ends.append((name, colour, x_end, y_end, len(runs)))

NUDGE = {"PWM": (7, 0), "PID": (7, 0), "IMU": (8, -9), "IMU-IL": (8, 11)}
for name, colour, x_end, y_end, n in ends:
    ax.annotate(f"{name}  ({n} runs)", xy=(x_end, y_end), xytext=NUDGE[name],
                textcoords="offset points", color=colour, fontsize=8.5,
                va="center", ha="left", fontweight="600")

ax.set_xlabel("Distance travelled  (m)")
ax.set_ylabel("Lateral deviation  (m)")
ax.set_xlim(0, 3.95)
ax.set_ylim(-0.18, 0.78)
ax.set_title("All runs, unweighted robot. The two uncorrected controllers were not run as far.",
             color=INK_2, fontsize=9)
style.tidy(ax)
fig.suptitle("Lateral deviation over a straight-line run",
             x=0.008, ha="left", color=INK, fontsize=11, fontweight="600")
fig.savefig(f"{OUT}/threepi-trajectories.svg", format="svg")
plt.close(fig)

for name, colour, x_end, y_end, n in ends:
    print(f"traj  {name:7s} n={n}  x_max={x_end:.2f} m  median y at end={y_end:+.3f} m")

# ----------------------------------------------- 2. measured end-of-run deviation
# Tape measurement against the graph-paper track: (lowest run, mean, highest run).
MEASURED = {
    "PWM":    {"no mass": (0.57, 0.60, 0.78)},
    "PID":    {"no mass": (0.18, 0.32, 0.41)},
    "IMU":    {"no mass": (-0.02, -0.01, 0.00),
               "150 g left": (0.14, 0.15, 0.16),
               "150 g right": (-0.08, -0.07, -0.05)},
    "IMU-IL": {"no mass": (-0.09, -0.03, 0.08),
               "150 g left": (-0.01, 0.04, 0.11),
               "150 g right": (-0.14, -0.05, 0.10)},
}
CONDS = ["no mass", "150 g left", "150 g right"]
COLOUR = {"PWM": C_PWM, "PID": C_PID, "IMU": C_IMU, "IMU-IL": C_RL}

fig, ax = plt.subplots(figsize=(7.4, 4.0))
ax.axhline(0, color=MUTED, lw=1, ls=(0, (4, 3)), zorder=1)

order = ["PWM", "PID", "IMU", "IMU-IL"]
width, gap = 0.17, 0.02
for i, ctrl in enumerate(order):
    off = (i - (len(order) - 1) / 2) * (width + gap)
    for j, cond in enumerate(CONDS):
        if cond not in MEASURED[ctrl]:
            continue
        lo, mid, hi = MEASURED[ctrl][cond]
        xpos = j + off
        ax.plot([xpos, xpos], [lo, hi], color=COLOUR[ctrl], lw=2.4,
                solid_capstyle="round", alpha=0.45, zorder=2)
        ax.plot([xpos], [mid], marker="o", ms=6.5, color=COLOUR[ctrl],
                markeredgecolor="white", markeredgewidth=1.1, zorder=3)
        anchor, dy = (hi, 8) if mid >= 0 else (lo, -14)
        ax.annotate(f"{mid:+.2f}", xy=(xpos, anchor), xytext=(0, dy),
                    textcoords="offset points", color=COLOUR[ctrl],
                    fontsize=8, ha="center")
    ax.plot([], [], color=COLOUR[ctrl], lw=2.4, label=ctrl)

ax.set_xticks(range(len(CONDS)))
ax.set_xticklabels(CONDS)
ax.set_ylabel("Measured deviation at end of run  (m)")
ax.set_ylim(-0.28, 0.95)
ax.set_xlim(-0.55, 2.55)
ax.legend(loc="upper right", ncol=4, columnspacing=1.3, handlelength=1.6)
ax.set_title("Marker is the mean of three runs, bar spans them. Positive is left of centre.",
             color=INK_2, fontsize=9)
style.tidy(ax)
fig.suptitle("Measured deviation at the end of each run",
             x=0.008, ha="left", color=INK, fontsize=11, fontweight="600")
fig.savefig(f"{OUT}/threepi-deviation.svg", format="svg")
plt.close(fig)

for ctrl in order:
    for cond, (lo, mid, hi) in MEASURED[ctrl].items():
        print(f"meas  {ctrl:7s} {cond:12s} mid={mid:+.2f}  span={hi - lo:.2f}")

# ---------------------------------------------------- 3. odometry vs tape measure
ODO = {
    "IMU":    {"no mass": "imu/test_[012]_no_mass.csv",
               "150 g left": "imu/test_*_left_mass.csv",
               "150 g right": "imu/test_*_right_mass.csv"},
    "IMU-IL": {"no mass": "imu-il/test_*_no_mass.csv",
               "150 g left": "imu-il/test_*_left_mass.csv",
               "150 g right": "imu-il/test_*_right_mass.csv"},
}

fig, ax = plt.subplots(figsize=(7.4, 3.9))
ax.axhline(0, color=MUTED, lw=1, ls=(0, (4, 3)), zorder=1)

labels, xs = [], []
pos = 0
for ctrl in ("IMU", "IMU-IL"):
    for cond in CONDS:
        runs = load(ODO[ctrl][cond])
        odo = float(np.mean([y[-1] for _, y in runs]))
        tape = MEASURED[ctrl][cond][1]
        ax.plot([pos - 0.16, pos - 0.16], [0, odo], color=COLOUR[ctrl], lw=8,
                solid_capstyle="butt", alpha=0.30, zorder=2)
        ax.plot([pos + 0.16, pos + 0.16], [0, tape], color=COLOUR[ctrl], lw=8,
                solid_capstyle="butt", alpha=0.85, zorder=2)
        print(f"drift {ctrl:7s} {cond:12s} odometry={odo:+.3f}  tape={tape:+.3f}  "
              f"gap={abs(odo - tape):.3f}")
        labels.append(f"{ctrl}\n{cond}")
        xs.append(pos)
        pos += 1
    pos += 0.4

ax.plot([], [], color=MUTED, lw=8, alpha=0.30, label="Odometry estimate")
ax.plot([], [], color=MUTED, lw=8, alpha=0.85, label="Tape measurement")
ax.set_xticks(xs)
ax.set_xticklabels(labels, fontsize=8)
ax.set_ylabel("Deviation at end of run  (m)")
ax.set_xlim(-0.7, pos - 0.7)
ax.legend(loc="upper left", ncol=2, columnspacing=1.4, handlelength=1.4)
ax.set_title("Mean of three runs. The gap within each pair is the robot's own position error.",
             color=INK_2, fontsize=9)
style.tidy(ax)
fig.suptitle("Odometry estimate against tape measurement",
             x=0.008, ha="left", color=INK, fontsize=11, fontweight="600")
fig.savefig(f"{OUT}/threepi-drift.svg", format="svg")
plt.close(fig)
