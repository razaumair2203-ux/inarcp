"""Fig. 2 of the manuscript as one row: the four panels on the new results (post-onset law, visibility horizon, OS law
after onset, certified integration), replotted without re-simulation from the saved values of the full six-panel figure
(research/r7c/r12/fig_theory.json, written by r12/fig_theory.py). The full figure is in the Supplementary Material.
Usage: python make_fig_theory_row.py  ->  ../manuscript/figures/fig_theory_row.pdf"""
import json, os
import numpy as np
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt

HERE = os.path.dirname(os.path.abspath(__file__))
REPO = os.path.join(HERE, "..", "..", "02_paper_repo_inarcp", "research", "r7c")
if not os.path.isdir(REPO):
    REPO = r"C:\Users\DELL\Downloads\MS thess\02_paper_repo_inarcp\research\r7c"
D = json.load(open(os.path.join(REPO, "r12", "fig_theory.json")))
plt.rcParams.update({"font.size": 7.5, "axes.edgecolor": "#c3c2b7", "axes.labelcolor": "#52514e", "legend.frameon": False})
BLUE, ORANGE, GREEN, PINK, PURPLE, DARK, GREY = "#2a78d6", "#eb6834", "#1baf7a", "#e87ba4", "#7a4fd6", "#52514e", "#898781"
fig, axs = plt.subplots(1, 4, figsize=(7.16, 1.85))

ax = axs[0]; looks = np.arange(9)
for nm, c in (("clutter Doppler", PINK), ("quarter", BLUE), ("opposite", GREEN)):
    r = D[f"a|{nm}"]; ax.plot(looks, r["theory"], "-", color=c, lw=1.3, label=nm); ax.plot(looks, r["mc"], "o", color=c, ms=2.8, mfc="white")
ax.set_xlabel("Look after onset $\\ell$"); ax.set_ylabel("$P_{\\rm d}$"); ax.set_title("(a) After onset, SCR 10 dB", fontsize=7.5)
ax.legend(fontsize=5.6, loc="center right"); ax.grid(alpha=.3)

ax = axs[1]; scr = np.arange(-5, 41, 1.0)
for l, c in zip((1, 2, 3, 4, 5), (BLUE, GREEN, ORANGE, PINK, PURPLE)):
    r = D[f"b|{l}"]; ax.plot(scr, r["theory"], "-", color=c, lw=1.2, label=f"$\\ell={l}$"); ax.plot((0, 10, 20, 30, 40), r["mc"], "o", color=c, ms=2.8, mfc="white")
ax.set_xlabel("SCR (dB)"); ax.set_ylabel("$P_{\\rm d}$ at look $\\ell$")
ax.set_title(f"(b) Horizon $\\ell^*={D['b|lstar']:.2f}$ (opposite)", fontsize=7.5); ax.legend(fontsize=5.6, ncol=2, loc="center right"); ax.grid(alpha=.3)

ax = axs[2]; ls = np.arange(11)
for k, c in ((8, PURPLE), (12, ORANGE)):
    r = D[f"c|{k}"]; ax.plot(ls, r["theory"], "-", color=c, lw=1.3, label=f"$k={k}$"); ax.plot(ls, r["mc"], "o", color=c, ms=2.8, mfc="white")
ax.set_xticks(range(0, 11, 2)); ax.set_xlabel("Look after onset $\\ell$"); ax.set_ylabel("$P_{\\rm d}$")
ax.set_title("(c) OS scale, SCR 10 dB", fontsize=7.5); ax.legend(fontsize=5.6, loc="lower left"); ax.grid(alpha=.3)

ax = axs[3]; f = D["f"]; ps = 100 * np.array(f["p"])
for key, c, lst, lab in (("ca", DARK, ":", "CA integration"), ("clip0", ORANGE, "--", "clipped, clean thr."),
                         ("cert", BLUE, "-", "clipped, certified"), ("bin_cert", GREEN, "-.", "binary, certified")):
    ax.semilogy(ps, np.maximum(f[key], 1e-5), lst, marker="o", ms=2.8, color=c, lw=1.2, label=lab)
ax.axhline(0.01, color=GREY, lw=1); ax.text(5.2, 0.0125, "design $\\alpha$", fontsize=5.6, color=GREY)
ax.set_xlabel("Hit rate per pulse (%)"); ax.set_ylabel("$P_{\\rm fa}$"); ax.set_title("(d) Theorem 1, hits 30 dB", fontsize=7.5)
ax.set_ylim(1e-7, 1.5); ax.legend(fontsize=5.2, loc="lower left", handlelength=1.6); ax.grid(alpha=.3, which="both")
fig.tight_layout(pad=0.3, w_pad=0.6)
out = os.path.join(HERE, "..", "manuscript", "figures", "fig_theory_row.pdf")
fig.savefig(out); fig.savefig(os.path.join(HERE, "..", "..", "fig_theory_row_check.png"), dpi=170)
print("written", out)
