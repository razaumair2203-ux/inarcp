"""Supplementary long-guard figure (full delayed self-masking, IPIX and NetRAD) drawn from
inputs/guard_extension.json.
Usage: python figS_guard_extension.py   (FIG_OUT sets the output folder; default figures/out/supplement)
"""
import json
import os
from pathlib import Path
import numpy as np
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt

HERE = Path(__file__).resolve().parent
INPUT = Path(os.environ.get("FIG_INPUT", str(HERE / "inputs/guard_extension.json")))
D = json.loads(INPUT.read_text(encoding="utf-8"))
assert D["schema"] == "inarcp.supplement.guard_extension_plot_input.v1"
OUT = Path(os.environ.get("FIG_OUT", str(HERE / "out/supplement"))); OUT.mkdir(parents=True, exist_ok=True)
plt.rcParams.update({"font.family": "sans-serif", "font.size": 9,
    "axes.spines.top": False, "axes.spines.right": False,
    "axes.linewidth": .6, "legend.frameon": False, "pdf.fonttype": 42})
COLORS = ["#333333", "#2166AC", "#D95F02"]


def panel(ax, radar, scr):
    d = D["radars"][radar]
    looks = np.array(d["looks"])
    si = d["scr_db"].index(scr)
    for gi, (guard, color) in enumerate(zip(d["guards"], COLORS)):
        measured = np.array(d["probability"])[si, gi]
        interval = np.array(d["interval"])[si, gi]
        predicted = np.array(d["predicted"])[si, gi]
        ax.fill_between(looks, interval[:, 0], interval[:, 1], color=color, alpha=.10, lw=0)
        ax.plot(looks, measured, color=color, lw=1.7, label=f"$\\Delta={guard}$")
        ax.plot(looks, predicted, "--", color=color, lw=1., alpha=.9)
    ax.set(xlim=(-.5, 48.5), ylim=(-.015, 1.02), xticks=np.arange(0, 49, 8),
           xlabel="Look after onset $\\ell$", ylabel="Per-look $P_{\\rm d}$")
    ax.grid(axis="y", color="#e2e2e2", lw=.5)
    ax.set_title(f"{radar}, SCR {scr} dB", fontsize=9)


fig, axes = plt.subplots(2, 2, figsize=(7.16, 5.15))
for row, scr in enumerate((10, 20)):
    for col, radar in enumerate(("IPIX", "NetRAD")):
        panel(axes[row, col], radar, scr)
        axes[row, col].legend(loc="upper right", fontsize=9, handlelength=1.7,
                              title="Slow-time guard", title_fontsize=9)
fig.tight_layout(pad=.35, h_pad=1.5, w_pad=1.2)
fig.savefig(OUT / "fig_guard_extension.pdf")
fig.savefig(OUT / "fig_guard_extension_check.png", dpi=180)
plt.close(fig)
