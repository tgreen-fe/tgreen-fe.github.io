"""Shared figure style. Palette per dataviz reference instance (validated)."""
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt

SURFACE   = "#fcfcfb"
INK       = "#0b0b0b"
INK_2     = "#52514e"
MUTED     = "#898781"
GRID      = "#e1e0d9"
AXIS      = "#c3c2b7"
S1        = "#2a78d6"   # slot 1 blue
S2        = "#eb6834"   # slot 2 orange

SANS = ["DejaVu Sans", "Helvetica", "Arial", "sans-serif"]


def apply():
    plt.rcParams.update({
        "figure.facecolor": SURFACE,
        "axes.facecolor": SURFACE,
        "savefig.facecolor": SURFACE,
        "font.family": "sans-serif",
        "font.sans-serif": SANS,
        "font.size": 9,
        "axes.edgecolor": AXIS,
        "axes.linewidth": 0.8,
        "axes.labelcolor": INK_2,
        "axes.labelsize": 9,
        "axes.titlesize": 10,
        "axes.titlecolor": INK,
        "axes.titleweight": "600",
        "axes.titlelocation": "left",
        "axes.titlepad": 8,
        "axes.grid": True,
        "axes.grid.axis": "y",
        "grid.color": GRID,
        "grid.linewidth": 0.7,
        "xtick.color": MUTED,
        "ytick.color": MUTED,
        "xtick.labelcolor": MUTED,
        "ytick.labelcolor": MUTED,
        "xtick.labelsize": 8,
        "ytick.labelsize": 8,
        "xtick.direction": "out",
        "ytick.direction": "out",
        "xtick.major.size": 0,
        "ytick.major.size": 0,
        "legend.frameon": False,
        "legend.fontsize": 8.5,
        "legend.labelcolor": INK_2,
        "lines.linewidth": 2.0,
        "lines.solid_capstyle": "round",
        "svg.fonttype": "none",
        "figure.constrained_layout.use": True,
    })


def tidy(ax, hide_x=False):
    """Recessive chrome: drop top/right spines, soften the rest."""
    for s in ("top", "right"):
        ax.spines[s].set_visible(False)
    ax.spines["left"].set_color(AXIS)
    ax.spines["bottom"].set_color(AXIS)
    ax.set_axisbelow(True)
    if hide_x:
        ax.spines["bottom"].set_visible(False)
        ax.tick_params(axis="x", labelbottom=False)


def note(ax, x, y, text, color=INK_2, **kw):
    ax.annotate(text, xy=(x, y), color=color, fontsize=8.5, **kw)
