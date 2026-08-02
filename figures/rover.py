"""Radiation rover: source-approach response, from the raw detector log."""
import sys, csv, numpy as np
import matplotlib.pyplot as plt
sys.path.insert(0, ".")
import style
from style import S1, S2, INK, INK_2, MUTED

style.apply()
SRC = ("/mnt/user-data/uploads/Individual Project/Data/Smoke detector measurments/"
       "Smoke Detector (no geolocation) 7th Jan CSV.csv")
OUT = "assets/fig"

rows = [r for r in csv.reader(open(SRC)) if len(r) > 4 and r[0] == "CPS"]
cpm = np.array([int(r[3]) for r in rows], float)
t = np.arange(1, len(cpm) + 1)

k = 9
smooth = np.convolve(cpm, np.ones(k) / k, mode="same")
smooth[: k // 2] = np.nan
smooth[-(k // 2):] = np.nan

bg = float(np.median(cpm[:80]))
peak_i = int(np.argmax(cpm))
peak = float(cpm[peak_i])

fig, ax = plt.subplots(figsize=(7.4, 3.9))
ax.plot(t, cpm, color=S1, lw=1.1, alpha=0.42, label="Raw count rate")
ax.plot(t, smooth, color=S1, lw=2.2, label=f"{k}-sample rolling mean")
ax.axhline(bg, color=MUTED, lw=1, ls=(0, (4, 3)), zorder=1)

ax.annotate(f"background {bg:.0f} CPM", xy=(len(cpm) - 4, bg), xytext=(0, -14),
            textcoords="offset points", color=INK_2, fontsize=8.5, ha="right")
ax.annotate(f"peak {peak:.0f} CPM\n{peak/bg:.1f}× background",
            xy=(t[peak_i], peak), xytext=(28, -4), textcoords="offset points",
            color=INK_2, fontsize=8.5, ha="left", va="top",
            arrowprops=dict(arrowstyle="-", color=MUTED, lw=0.9,
                            shrinkA=0, shrinkB=4))

ax.set_xlabel("Time  (s)")
ax.set_ylabel("Count rate  (CPM)")
ax.set_ylim(0, max(cpm) * 1.28)
ax.set_xlim(0, len(cpm) + 2)
ax.legend(loc="upper right", ncol=2, columnspacing=1.4, handlelength=1.8)
ax.set_title("Detector moved towards a domestic smoke detector, the americium-241 test source, then back",
             color=INK_2, fontsize=9)
style.tidy(ax)
fig.suptitle("Detector response to a known point source",
             x=0.008, ha="left", color=INK, fontsize=11, fontweight="600")
fig.savefig(f"{OUT}/rover-source-response.svg", format="svg")
plt.close(fig)

print(f"n={len(cpm)}  background={bg:.0f}  peak={peak:.0f}  ratio={peak/bg:.2f}  "
      f"peak at t={t[peak_i]}s")
