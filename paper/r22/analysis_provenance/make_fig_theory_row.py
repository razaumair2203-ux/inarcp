"""Main theory figure, replotted from immutable R12 arrays without simulation.

The 2-by-2 layout replaces four narrow panels. Saved zero-event Monte Carlo
estimates remain open downward triangles at 1/100000, never positive estimates.
Usage: python make_fig_theory_row.py
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
from matplotlib.lines import Line2D

HERE = Path(__file__).resolve().parent
if os.environ.get("R7C_DIR"):
    REPO = Path(os.environ["R7C_DIR"])
else:
    candidates = [p / sub for p in (HERE, *HERE.parents)
                  for sub in ("research/r7c", "02_paper_repo_inarcp/research/r7c")]
    REPO = next(p for p in candidates if p.is_dir())
DATA = Path(os.environ.get("FIG_INPUT", str(REPO / "r12/fig_theory.json")))
D = json.loads(DATA.read_text())
OUT = Path(os.environ.get("FIG_OUT", str(HERE.parent / "manuscript/figures")))
OUT.mkdir(parents=True, exist_ok=True)
plt.rcParams.update({"font.family": "sans-serif", "font.size": 9,
                     "axes.edgecolor": "#898781", "axes.labelcolor": "#333333",
                     "axes.linewidth": .6, "legend.frameon": False,
                     "axes.spines.top": False, "axes.spines.right": False,
                     "legend.fontsize": 9, "legend.handlelength": 1.9,
                     "legend.labelspacing": .3, "legend.borderaxespad": .2,
                     "legend.title_fontsize": 9, "pdf.fonttype": 42})
BLUE, ORANGE, GREEN, PINK, PURPLE, DARK, GREY = (
    "#2166AC", "#D95F02", "#087B51", "#B64A75", "#7551A8", "#333333", "#777777")
fig, axs = plt.subplots(2, 2, figsize=(7.16, 3.95))
axs = axs.ravel()

ax = axs[0]
looks = np.arange(9)
for key, lab, c, marker, ls in (
        ("clutter Doppler", "$0$ (clutter Doppler)", PINK, "o", ":"),
        ("quarter", "$\\pi/2$", BLUE, "s", "--"),
        ("opposite", "$\\pi$", GREEN, "^", "-")):
    r = D[f"a|{key}"]
    ax.plot(looks, r["theory"], ls, color=c, lw=1.4, label=lab)
    ax.plot(looks, r["mc"], marker, color=c, ms=3.3, mfc="white", mew=.8)
ax.set_xlabel("Look after onset $\\ell$")
ax.set_ylabel("$P_{\\rm d}$")
ax.set_title("(a) After onset, SCR 10 dB", fontsize=9)
ax.set_xticks(range(0, 9, 2)); ax.set_ylim(-.025, 1.025)
ax.legend(title="Doppler offset", loc="center right", bbox_to_anchor=(1., .57))
ax.grid(alpha=.22, lw=.5)

ax = axs[1]
scr = np.arange(-5, 41, 1.)
for l, c, marker, ls in zip((1, 2, 3, 4, 5),
        (BLUE, GREEN, ORANGE, PINK, PURPLE), ("o", "s", "^", "D", "v"),
        ("-", "--", "-.", ":", (0, (5, 1, 1, 1)))):
    r = D[f"b|{l}"]
    ax.plot(scr, r["theory"], ls=ls, color=c, lw=1.3, label=f"$\\ell={l}$")
    ax.plot((0, 10, 20, 30, 40), r["mc"], marker, color=c,
            ms=3.3, mfc="white", mew=.8)
ax.set_xlabel("SCR (dB)"); ax.set_ylabel("$P_{\\rm d}$ at look $\\ell$")
ax.set_title(f"(b) Opposite Doppler, $\\ell^*={D['b|lstar']:.1f}$", fontsize=9)
ax.set_ylim(-.025, 1.025); ax.legend(loc="center right")
ax.grid(alpha=.22, lw=.5)

ax = axs[2]
for k, c, marker, ls in ((8, PURPLE, "o", "-"), (12, ORANGE, "D", "--")):
    r = D[f"c|{k}"]
    ax.plot(range(11), r["theory"], ls, color=c, lw=1.4, label=f"$k={k}$")
    ax.plot(range(11), r["mc"], marker, color=c, ms=3.3, mfc="white", mew=.8)
ax.set_xticks(range(0, 11, 2)); ax.set_xlabel("Look after onset $\\ell$")
ax.set_ylabel("$P_{\\rm d}$"); ax.set_ylim(-.025, 1.025)
ax.set_title("(c) Order-statistic scale, SCR 10 dB", fontsize=9)
ax.legend(title="$m=16$", loc="lower left"); ax.grid(alpha=.22, lw=.5)

ax = axs[3]
f = D["f"]; ps = 100 * np.array(f["p"]); FLOOR = 1e-5
for key, c, ls, lab in (
        ("ca", DARK, ":", "Integration"),
        ("clip0", ORANGE, "--", "Clean-threshold clip"),
        ("cert", BLUE, "-", "Certified clip"),
        ("bin_cert", GREEN, "-.", "Certified binary")):
    v = np.array(f[key]); z = v == 0
    ax.semilogy(ps, np.where(z, FLOOR, v), ls, color=c, lw=1.3, label=lab)
    ax.semilogy(ps[~z], v[~z], "o", ms=3.3, color=c)
    ax.semilogy(ps[z], np.full(z.sum(), FLOOR), "v", color=c,
                ms=5.2 if key == "cert" else 3.2, mfc="white", mew=.9)
ax.axhline(.01, color=GREY, lw=.8)
ax.text(8.4, .013, "Design $\\alpha$", fontsize=9, color=GREY, ha="right")
ax.set_xlabel("Hit rate per pulse (%)"); ax.set_ylabel("$P_{\\rm fa}$")
ax.set_title("(d) Certified integration", fontsize=9)
ax.set_ylim(5e-6, 2); ax.set_yticks([1e-5, 1e-3, 1e-1, 1]); ax.set_xlim(-.4, 8.4)
ax.grid(alpha=.22, lw=.5)
fig.tight_layout(pad=.4, w_pad=1., h_pad=1., rect=[0., .075, 1., 1.])
h, labels = ax.get_legend_handles_labels()
fig.legend(h, labels, loc="lower center", ncol=4, fontsize=9,
           bbox_to_anchor=(.5, .003), handlelength=1.6, columnspacing=1.15)
fig.savefig(OUT / "fig_theory_row.pdf")
fig.savefig(OUT / "fig_theory_row_check.png", dpi=220)
(OUT / "theory_input_sha256.txt").write_text(
    f"{hashlib.sha256(DATA.read_bytes()).hexdigest()}  {DATA.name}\n")
print("Theory: 7.16 x 3.95 in, labels and legends 9 pt.")
