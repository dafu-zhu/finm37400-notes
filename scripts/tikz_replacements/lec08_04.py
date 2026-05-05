"""Lec 8 TikZ #4 — multiperiod CRR recombining tree (depth 2)."""
from pathlib import Path
import matplotlib.pyplot as plt

from lec08_02 import _node

OUT = Path(__file__).resolve().parents[2] / "figures" / "L8_tikz_4.png"

NODES = [
    (0,  0,    "$S_0$",          "black"),
    (2,  1.4,  "$S_u$",          "black"),
    (2, -1.4,  "$S_d$",          "black"),
    (4,  2.8,  "$S_{uu}$",       "black"),
    (4,  0,    "$S_{ud}=S_0$",   "black"),
    (4, -2.8,  "$S_{dd}$",       "black"),
]
EDGES = [(0, 1), (0, 2), (1, 3), (1, 4), (2, 4), (2, 5)]
PAYOFFS = [
    (5.7,  2.8, r"$f_{uu}=\max(S_{uu}-K,0)$"),
    (5.7,  0,   r"$f_{ud}=\max(S_{ud}-K,0)$"),
    (5.7, -2.8, r"$f_{dd}=\max(S_{dd}-K,0)$"),
]

def render():
    fig, ax = plt.subplots(figsize=(8, 5), dpi=200)
    for x, y, label, color in NODES:
        _node(ax, x, y, label, color=color)
    for i, j in EDGES:
        x0, y0, *_ = NODES[i]
        x1, y1, *_ = NODES[j]
        ax.annotate("", xy=(x1 - 0.18, y1), xytext=(x0 + 0.18, y0),
                    arrowprops=dict(arrowstyle="->", lw=1.3, color="black"))
    for x, y, txt in PAYOFFS:
        ax.text(x, y, txt, color="tab:blue", fontsize=9, va="center")
    ax.text(-0.6, -3.6, "time grid:", fontsize=9)
    for x, label in [(0, "$0$"), (2, r"$\Delta t$"), (4, r"$2\Delta t$")]:
        ax.text(x, -3.6, label, ha="center", fontsize=9)
    ax.set_xlim(-1.0, 9.5)
    ax.set_ylim(-4.3, 3.6)
    ax.axis("off")
    fig.tight_layout()
    OUT.parent.mkdir(parents=True, exist_ok=True)
    fig.savefig(OUT, dpi=200, bbox_inches="tight")
    plt.close(fig)
    print(f"  wrote {OUT.relative_to(OUT.parents[2])}")

