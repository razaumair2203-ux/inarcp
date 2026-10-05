"""Main detection figure from frozen arrays; no fitting or simulation.

Keep original episode weighting and unweighted unit-average model curves.
The second panel uses the full panel width, with a compact inset legend.
Usage: python make_fig_detection.py
Optional FIG_OUT sets the destination; default is ../manuscript/figures.
"""
import hashlib
import json
import os
from pathlib import Path

import numpy as np
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt

HERE = Path(__file__).resolve().parent
if os.environ.get("R7C_DIR"):
    REPO = Path(os.environ["R7C_DIR"])
else:
    candidates = [p / sub for p in (HERE, *HERE.parents)
                  for sub in ("research/r7c", "02_paper_repo_inarcp/research/r7c")]
    REPO = next((p for p in candidates if p.is_dir()), None)
INPUT = Path(os.environ.get("FIG_INPUT", str(HERE / "fig_detection_r21.json")))
if not INPUT.is_file() and REPO is not None:
    INPUT = REPO / "presentation/fig_detection_r21.json"
OUT = Path(os.environ.get("FIG_OUT", str(HERE.parent / "manuscript/figures")))
OUT.mkdir(parents=True, exist_ok=True)
D = json.loads(INPUT.read_text(encoding="utf-8"))
assert D["schema"] == "inarcp.figure3.frozen_plot_input.v1"
assert D["provenance"]["unit_count"] == 56
det = D["panel_a"]
BLUE, ORANGE, DARK, GREY, GRID = "#2166AC", "#D95F02", "#333333", "#777777", "#e2e2e2"
plt.rcParams.update({"font.family": "sans-serif", "font.size": 9,
    "axes.edgecolor": "#898781", "axes.labelcolor": DARK,
    "legend.frameon": False, "axes.linewidth": .6,
    "xtick.major.width": .6, "ytick.major.width": .6,
    "axes.spines.top": False, "axes.spines.right": False, "pdf.fonttype": 42})
fig, (a, b) = plt.subplots(1, 2, figsize=(7.16, 2.65))

scr = np.array(D["scr_db"])
for m, c, ls, lab in (("CAloc", GREY, ":", "CAloc"),
    ("CA16", DARK, "--", "CA16"), ("NA4", ORANGE, "-.", "NA-AR(4)"),
    ("IN1", BLUE, "-", "IN-ARCP")):
    a.plot(scr, det[f"{m}|0.01|pd"], ls, color=c, lw=1.5, label=lab)
a.plot(scr, det["IN1|0.01|pred"], "o", color=BLUE, ms=3.8, mfc="white",
    mew=.9, label="Law (Cor. 2)")
h, l = a.get_legend_handles_labels(); order = [3, 4, 2, 1, 0]
a.legend([h[i] for i in order], [l[i] for i in order], fontsize=9,
    loc="lower right", handlelength=1.8, labelspacing=.3, borderaxespad=.2)
a.set_xlabel("SCR (dB)"); a.set_ylabel("$P_{\\rm d}$")
a.set_xlim(-5.5, 25.5); a.set_ylim(-.02, 1.02)
a.set_title("(a) Target in the tested pulse", fontsize=9)
a.grid(color=GRID, lw=.5)

ls_ = np.array(D["looks"]); colors = {0: DARK, 8: BLUE}
for g in (0, 8):
    b.plot(ls_, D["panel_b"][f"G|law|random|{g}"],
        color=colors[g], lw=1.2, alpha=.8)
    dx = -.12 if g else .12
    for doppler, marker in (("random", "o"), ("opposite", "^")):
        b.plot(ls_ + dx, D["panel_b"][f"G|abrupt|{doppler}|{g}|look"], marker,
            zorder=4 - g/8, color=colors[g], ms=4.5,
            mfc=colors[g] if g else "white", mew=.9,
            label=f"$\\Delta={g}$, {doppler}")
h, l = b.get_legend_handles_labels(); order = [2, 3, 0, 1]
b.legend([h[i] for i in order], [l[i] for i in order], fontsize=9,
    loc="center right", bbox_to_anchor=(1., .46), handlelength=1.2,
    labelspacing=.35, borderaxespad=.2, title="Guard, target Doppler", title_fontsize=9)
b.set_xlabel("Look after onset $\\ell$"); b.set_ylabel("Per-look $P_{\\rm d}$")
b.set_xticks(ls_); b.set_ylim(-.02, 1.02)
b.set_title("(b) Persistent target, SCR 10 dB", fontsize=9)
b.grid(axis="y", color=GRID, lw=.5)
fig.tight_layout(pad=.35, w_pad=1.2)
fig.savefig(OUT / "fig_detection.pdf")
fig.savefig(OUT / "fig_detection_check.png", dpi=220)
(OUT / "detection_input_sha256.txt").write_text(
    f"{hashlib.sha256(INPUT.read_bytes()).hexdigest()}  {INPUT.name}\n")
print("Detection: 7.16 x 2.65 in, labels and legends 9 pt.")
