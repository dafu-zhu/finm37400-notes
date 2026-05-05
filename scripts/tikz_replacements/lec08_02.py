"""Lec 8 TikZ #2 — 1-period stock binomial tree."""
from pathlib import Path
import matplotlib.pyplot as plt

OUT = Path(__file__).resolve().parents[2] / "figures" / "L8_tikz_2.png"

def _node(ax, x, y, text, color="black"):
    ax.annotate(
        text, (x, y), ha="center", va="center", color=color, fontsize=12,
        bbox=dict(boxstyle="round,pad=0.4", fc="white", ec=color, lw=1.2),
    )

def _arrow(ax, x0, y0, x1, y1, label, where):
    ax.annotate("", xy=(x1, y1), xytext=(x0, y0),
                arrowprops=dict(arrowstyle="->", lw=1.5, color="black"))
    mx, my = (x0 + x1) / 2, (y0 + y1) / 2
    dy = 0.18 if where == "above" else -0.18
    va = "bottom" if where == "above" else "top"
    ax.text(mx, my + dy, label, ha="center", va=va, fontsize=10)

def render():
    fig, ax = plt.subplots(figsize=(6, 3.5), dpi=200)
    _node(ax, 0, 0, "$S_0 = 100$")
    _node(ax, 3, 1.2, "$S_u = 110$", color="tab:blue")
    _node(ax, 3, -1.2, "$S_d = 90$", color="tab:red")
    _arrow(ax, 0.6, 0.15, 2.4, 1.10, "up", "above")
    _arrow(ax, 0.6, -0.15, 2.4, -1.10, "down", "below")
    ax.set_xlim(-0.8, 4.2)
    ax.set_ylim(-2.0, 2.0)
    ax.axis("off")
    fig.tight_layout()
    OUT.parent.mkdir(parents=True, exist_ok=True)
    fig.savefig(OUT, dpi=200, bbox_inches="tight")
    plt.close(fig)
    print(f"  wrote {OUT.relative_to(OUT.parents[2])}")

if __name__ == "__main__":
    render()
