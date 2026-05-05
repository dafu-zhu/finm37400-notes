"""Lec 8 TikZ #3 — 1-period interest rate binomial tree."""
from pathlib import Path
import matplotlib.pyplot as plt

from lec08_02 import _node, _arrow  # reuse helpers

OUT = Path(__file__).resolve().parents[2] / "figures" / "L8_tikz_3.png"

def render():
    fig, ax = plt.subplots(figsize=(6, 3.5), dpi=200)
    _node(ax, 0, 0, r"$r_0 = 1.74\%$")
    _node(ax, 3.4, 1.0, r"$r_1^u = 3.39\%$", color="tab:blue")
    _node(ax, 3.4, -1.0, r"$r_1^d = 0.95\%$", color="tab:red")
    _arrow(ax, 0.85, 0.13, 2.55, 0.92, "up", "above")
    _arrow(ax, 0.85, -0.13, 2.55, -0.92, "down", "below")
    ax.set_xlim(-1.0, 4.8)
    ax.set_ylim(-1.8, 1.8)
    ax.axis("off")
    fig.tight_layout()
    OUT.parent.mkdir(parents=True, exist_ok=True)
    fig.savefig(OUT, dpi=200, bbox_inches="tight")
    plt.close(fig)
    print(f"  wrote {OUT.relative_to(OUT.parents[2])}")

