"""Lec 8 TikZ #1 — implied volatility smile (3 curves + ATM dots).

Reproduces the diagram at source-tex/lec08.tex L220-L234.
"""
from pathlib import Path
import matplotlib.pyplot as plt
import numpy as np

OUT = Path(__file__).resolve().parents[2] / "figures" / "L8_tikz_1.png"

def render():
    fig, ax = plt.subplots(figsize=(7, 4), dpi=200)
    x = np.linspace(0.3, 7.7, 200)
    blue  = 1.7 + 0.10 * (x - 3.8) ** 2
    red   = 2.4 + 0.10 * (x - 2.8) ** 2
    green = 1.2 + 0.10 * (x - 4.8) ** 2

    ax.plot(x, blue,  color="tab:blue",  linewidth=2)
    ax.plot(x, red,   color="tab:red",   linewidth=2)
    ax.plot(x, green, color="tab:green", linewidth=2)

    pts = [(3.8, 1.70, "tab:blue",  "ATM today",          "below"),
           (2.8, 2.40, "tab:red",   r"ATM if forward $\downarrow$", "above"),
           (4.8, 1.20, "tab:green", r"ATM if forward $\uparrow$",   "below")]
    for xv, yv, c, label, where in pts:
        ax.scatter([xv], [yv], color=c, s=40, zorder=3)
        offset = -0.3 if where == "below" else 0.3
        va = "top" if where == "below" else "bottom"
        ax.annotate(label, (xv, yv), xytext=(xv, yv + offset),
                    color=c, ha="center", va=va, fontsize=9)

    ax.set_xlabel("strike $K$")
    ax.set_ylabel(r"implied vol $\sigma$")
    ax.set_xlim(0, 8.5)
    ax.set_ylim(0, 4.6)
    ax.spines["top"].set_visible(False)
    ax.spines["right"].set_visible(False)
    fig.tight_layout()
    OUT.parent.mkdir(parents=True, exist_ok=True)
    fig.savefig(OUT, dpi=200, bbox_inches="tight")
    plt.close(fig)
    print(f"  wrote {OUT.relative_to(OUT.parents[2])}")

if __name__ == "__main__":
    render()
