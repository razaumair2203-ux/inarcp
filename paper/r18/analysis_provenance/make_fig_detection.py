"""Fig. 3 of the manuscript: detection on IPIX in one two-column figure, drawn at its printed size (7.16 in, scale 1).
(a) a target that appears in the tested pulse, from research/r7c/detection/detection_summary.json (was fig_detection_col,
    make_r8_figures.py); (b) per-look detection after the onset of a persistent target, without and with the guard, from
    research/r7c/r14/study outcomes u_*.npz (was fig_guard_col, make_r14_outputs.py). Same data and weighting as before;
    only the layout changed, because the column versions had been scaled to 47% and 53% to hold the page limit.
Usage: python make_fig_detection.py  ->  ../manuscript/figures/fig_detection.pdf"""
import glob, json, os
import numpy as np
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt

HERE = os.path.dirname(os.path.abspath(__file__))
REPO = os.path.join(HERE, "..", "..", "02_paper_repo_inarcp", "research", "r7c")
if not os.path.isdir(REPO):
    REPO = r"C:\Users\DELL\Downloads\MS thess\02_paper_repo_inarcp\research\r7c"
det = json.load(open(os.path.join(REPO, "detection", "detection_summary.json")))
U = [dict(np.load(f, allow_pickle=True)) for f in sorted(glob.glob(os.path.join(REPO, "study", "results", "r14", "u_*.npz")))]
assert len(U) == 56
I10 = int(np.argmin(abs(U[0]["scr_db"] - 10)))
w = [u["G|clean|0|0.01"][1] for u in U]
pl = lambda key: np.average([u[key] for u in U], axis=0, weights=w)[I10]

BLUE, ORANGE, DARK, GREY, GRID = "#2a78d6", "#eb6834", "#52514e", "#898781", "#e4e3df"
plt.rcParams.update({"font.family": "sans-serif", "font.size": 8, "axes.edgecolor": "#c3c2b7", "axes.labelcolor": DARK,
                     "legend.frameon": False, "axes.linewidth": 0.6, "xtick.major.width": 0.6, "ytick.major.width": 0.6,
                     "axes.spines.top": False, "axes.spines.right": False})
fig, (a, b) = plt.subplots(1, 2, figsize=(7.16, 2.15), gridspec_kw={"width_ratios": [1, 1.12]})

scr = np.arange(-5, 25.01, 2.5)
for m, c, ls, lab in (("CAloc", GREY, ":", "CAloc"), ("CA16", DARK, "--", "CA16"),
                      ("NA4", ORANGE, "-", "NA-AR(4)"), ("IN1", BLUE, "-", "IN-ARCP")):
    a.plot(scr, det[f"{m}|0.01|pd"], ls, color=c, lw=1.5, label=lab)
a.plot(scr, det["IN1|0.01|pred"], "o", color=BLUE, ms=3.6, mfc="white", mew=0.9, label="law, Cor. 2")
h, l = a.get_legend_handles_labels(); o = [3, 4, 2, 1, 0]
a.legend([h[i] for i in o], [l[i] for i in o], fontsize=7.5, loc="lower right", bbox_to_anchor=(1.02, 0.0), handlelength=1.8,
         labelspacing=0.3, borderaxespad=0.1)
a.set_xlabel("SCR (dB)"); a.set_ylabel("$P_{\\rm d}$"); a.set_xlim(-5.5, 25.5); a.set_ylim(-0.02, 1.02)
a.set_title("(a) Target in the tested pulse", fontsize=8); a.grid(color=GRID, lw=0.6)

ls_ = np.arange(9); col = {0: DARK, 8: BLUE}
for g in (0, 8):
    b.plot(ls_, np.mean([u[f"G|law|random|{g}"] for u in U], 0)[I10], color=col[g], lw=1.0, alpha=0.7)
    dx = -0.12 if g else 0.12
    b.plot(ls_ + dx, pl(f"G|abrupt|random|{g}|look"), "o", zorder=4 - g / 8, color=col[g], ms=4.2, mfc=col[g] if g else "white", mew=0.9,
           label=f"random Doppler, {'no guard' if g == 0 else 'guard $\\Delta=8$'}")
    b.plot(ls_ + dx, pl(f"G|abrupt|opposite|{g}|look"), "^", zorder=4 - g / 8, color=col[g], ms=4.2, mfc=col[g] if g else "white", mew=0.9,
           label=f"opposite Doppler, {'no guard' if g == 0 else 'guard $\\Delta=8$'}")
b.plot([], [], color=DARK, lw=1.0, alpha=0.7, label="lines: law (Prop. 4),\nrandom Doppler")
h, l = b.get_legend_handles_labels(); o = [2, 3, 0, 1, 4]
b.legend([h[i] for i in o], [l[i] for i in o], fontsize=7.5, loc="center left", bbox_to_anchor=(1.0, 0.5), handlelength=1.6)
b.set_xlabel("Look after onset $\\ell$"); b.set_ylabel("Per-look $P_{\\rm d}$"); b.set_xticks(ls_); b.set_ylim(-0.02, 1.02)
b.set_title("(b) Persistent target, SCR 10 dB", fontsize=8); b.grid(axis="y", color=GRID, lw=0.6)

fig.tight_layout(pad=0.25, w_pad=1.2)
out = os.path.join(HERE, "..", "manuscript", "figures", "fig_detection.pdf")
fig.savefig(out); fig.savefig(os.path.join(os.environ.get("FIG_CHECK", HERE), "fig_detection_check.png"), dpi=200)
print("written", out)
