"""Fig. 2 of the manuscript as one row: the four panels on the new results (post-onset law, visibility horizon, OS law
after onset, certified integration), replotted without re-simulation from the saved values of the full six-panel figure
(research/r7c/r12/fig_theory.json, written by r12/fig_theory.py). The full figure is in the Supplementary Material.
Drawn at its printed size (7.16 in, scale 1), 8-pt text. In (d), a rate of zero (no false alarm in 10^5 episodes) is drawn
as an open downward marker at the Monte Carlo resolution 10^-5, not as a measured value.
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
plt.rcParams.update({"font.size": 8, "axes.edgecolor": "#c3c2b7", "axes.labelcolor": "#52514e", "legend.frameon": False,
                     "axes.spines.top": False, "axes.spines.right": False, "legend.fontsize": 6.8, "legend.handlelength": 1.6,
                     "legend.labelspacing": 0.3, "legend.borderaxespad": 0.2, "legend.title_fontsize": 6.8})
BLUE, ORANGE, GREEN, PINK, PURPLE, DARK, GREY = "#2a78d6", "#eb6834", "#1baf7a", "#e87ba4", "#7a4fd6", "#52514e", "#898781"
fig, axs = plt.subplots(1, 4, figsize=(7.16, 1.75))

ax = axs[0]; looks = np.arange(9)
# target Doppler offset from the clutter Doppler (r12/fig_theory.py); curves labelled directly, the panel is too small for a legend box
for key, lab, c, xy, ha in (("clutter Doppler", "0", PINK, (1.25, 0.04), "left"), ("quarter", "$\\pi/2$", BLUE, (2.6, 0.6), "right"),
                            ("opposite", "$\\pi$", GREEN, (3.3, 0.86), "left")):
    r = D[f"a|{key}"]
    ax.plot(looks, r["theory"], "-", color=c, lw=1.3); ax.plot(looks, r["mc"], "o", color=c, ms=2.8, mfc="white")
    ax.text(*xy, lab, color=c, fontsize=6.8, ha=ha, va="bottom")
ax.text(8.3, 0.74, "Doppler offset\nfrom clutter", color=GREY, fontsize=6.8, ha="right", va="center")
ax.set_xlabel("Look after onset $\\ell$"); ax.set_ylabel("$P_{\\rm d}$"); ax.set_title("(a) After onset, SCR 10 dB", fontsize=8)
ax.grid(alpha=.3)

ax = axs[1]; scr = np.arange(-5, 41, 1.0)
for l, c in zip((1, 2, 3, 4, 5), (BLUE, GREEN, ORANGE, PINK, PURPLE)):
    r = D[f"b|{l}"]; ax.plot(scr, r["theory"], "-", color=c, lw=1.2, label=f"$\\ell={l}$"); ax.plot((0, 10, 20, 30, 40), r["mc"], "o", color=c, ms=2.8, mfc="white")
ax.set_xlabel("SCR (dB)"); ax.set_ylabel("$P_{\\rm d}$ at look $\\ell$")
ax.set_title(f"(b) Opposite Doppler, $\\ell^*={D['b|lstar']:.1f}$", fontsize=8)
ax.legend(loc="center right", bbox_to_anchor=(1.0, 0.5)); ax.grid(alpha=.3)   # clear of the curves: all > 0.9 beyond 12 dB

ax = axs[2]; ls = np.arange(11)
for k, c in ((8, PURPLE), (12, ORANGE)):
    r = D[f"c|{k}"]; ax.plot(ls, r["theory"], "-", color=c, lw=1.3, label=f"$k={k}$"); ax.plot(ls, r["mc"], "o", color=c, ms=2.8, mfc="white")
ax.set_xticks(range(0, 11, 2)); ax.set_xlabel("Look after onset $\\ell$"); ax.set_ylabel("$P_{\\rm d}$")
ax.set_title("(c) OS scale, SCR 10 dB", fontsize=8); ax.legend(title="$m=16$", loc="lower left"); ax.grid(alpha=.3)

ax = axs[3]; f = D["f"]; ps = 100 * np.array(f["p"]); FLOOR = 1e-5          # 1/(10^5 episodes)
for key, c, lst, lab in (("ca", DARK, ":", "integration"), ("clip0", ORANGE, "--", "clipped, clean thr."),
                         ("cert", BLUE, "-", "clipped, certified"), ("bin_cert", GREEN, "-.", "binary, certified")):
    v = np.array(f[key]); z = v == 0
    ax.semilogy(ps, np.where(z, FLOOR, v), lst, color=c, lw=1.2, label=lab)
    ax.semilogy(ps[~z], v[~z], "o", ms=2.8, color=c)
    ax.semilogy(ps[z], np.full(z.sum(), FLOOR), "v", ms=4.8 if key == "cert" else 2.8, color=c, mfc="white")  # nested, so both are visible
ax.axhline(0.01, color=GREY, lw=0.9); ax.text(8.4, 0.007, "$\\alpha$", fontsize=7.5, color=GREY, ha="right", va="top")
ax.set_xlabel("Hit rate per pulse (%)"); ax.set_ylabel("$P_{\\rm fa}$"); ax.set_title("(d) Theorem 1", fontsize=8)
ax.set_ylim(1e-8, 2); ax.set_yticks([1e-7, 1e-5, 1e-3, 1e-1]); ax.set_xlim(-0.4, 8.4)
ax.legend(loc="lower left", fontsize=6.3, handlelength=1.8, borderaxespad=0.1); ax.grid(alpha=.3)
fig.tight_layout(pad=0.3, w_pad=0.7)
out = os.path.join(HERE, "..", "manuscript", "figures", "fig_theory_row.pdf")
fig.savefig(out); fig.savefig(os.path.join(os.environ.get("FIG_CHECK", HERE), "fig_theory_row_check.png"), dpi=200)
print("written", out)
