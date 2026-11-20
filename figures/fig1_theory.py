"""Fig. 1: closed-form laws against Monte Carlo, replotted from inputs/fig1_theory.json.
Usage: python fig1_theory.py   (FIG_OUT sets the output folder; default figures/out)
"""
import hashlib
import json
import os
from pathlib import Path

import numpy as np
import matplotlib.pyplot as plt

import figstyle as S

HERE = Path(__file__).resolve().parent
DATA = Path(os.environ.get("FIG_INPUT", str(HERE / "inputs/fig1_theory.json")))
D = json.loads(DATA.read_text())
OUT = Path(os.environ.get("FIG_OUT", str(HERE / "out")))
OUT.mkdir(parents=True, exist_ok=True)
S.apply(8)
MS, MEW = 3.6, .8
W, H = 7.16, 2.60

# Fixed grid in inches: four equal plot areas; the right-hand column keeps a key column.
L, AW, GAP, B, TOP, VG = .50, 2.26, .60, .40, .19, .55
AH = (H - B - TOP - VG) / 2
fig = plt.figure(figsize=(W, H))
axs = [fig.add_axes([(L + c * (AW + GAP)) / W, (B + r * (AH + VG)) / H, AW / W, AH / H])
       for r in (1, 0) for c in (0, 1)]
KEY = dict(loc="center left", bbox_to_anchor=(1.02, .5), handlelength=2.4, labelspacing=.12,
           borderaxespad=0., handletextpad=.5)


def key_line(ax, ls, mk, c, lab, lw=1.3, mfc="white"):
    ax.plot([], [], ls=ls, marker=mk, color=c, lw=lw, ms=MS, mfc=mfc, mew=MEW, label=lab)


# (a) Doppler offset relative to clutter: pi and pi/2 detected for a few looks, clutter Doppler lost at once.
ax = axs[0]
looks = np.arange(9)
for key, lab, c, mk, ls in (("opposite", r"$\pi$", S.BLUE, "^", "-"),
                            ("quarter", r"$\pi/2$", S.TEAL, "s", "--"),
                            ("clutter Doppler", r"$0$ (clutter)", S.ORANGE, "o", ":")):
    r = D[f"a|{key}"]
    ax.plot(looks, r["theory"], ls, color=c, lw=1.4)
    ax.plot(looks, r["mc"], mk, color=c, ms=MS, mfc="white", mew=MEW)
    key_line(ax, ls, mk, c, lab, 1.4)
lstar = D["a|opposite"]["horizon"]
ax.axvline(lstar, color=S.GREY, lw=.8, ls=(0, (2, 2)))
ax.text(lstar - .1, .18, rf"$\ell^*={lstar:.1f}$ ($\pi$)", color=S.DARK, ha="right", va="center")
ax.set(xlabel=r"Look after onset $\ell$", ylabel=r"$P_{\rm d}$", xticks=range(0, 9, 2),
       yticks=[0, .5, 1], ylim=(-.04, 1.06), xlim=(-.3, 8.3))
ax.set_title("(a) Persistent target, SCR 10 dB")
ax.legend(loc="upper right", bbox_to_anchor=(1., 1.02), title="Doppler offset", handlelength=2.4,
          labelspacing=.12, borderaxespad=.2)
S.grid(ax)

# (b) Opposite Doppler: looks before the horizon (blue) are detected as SCR grows; looks after it
# (orange) are masked.
ax = axs[1]
scr = np.arange(-5, 41, 1.)
styles = {1: (S.BLUE, "o", "-"), 2: (S.BLUE, "s", "--"), 3: (S.BLUE, "^", "-."),
          4: (S.ORANGE, "D", ":"), 5: (S.ORANGE, "v", (0, (5, 1, 1, 1)))}
for l, (c, mk, ls) in styles.items():
    r = D[f"b|{l}"]
    ax.plot(scr, r["theory"], ls=ls, color=c, lw=1.3)
    ax.plot((0, 10, 20, 30, 40), r["mc"], mk, color=c, ms=MS, mfc="white", mew=MEW)
    key_line(ax, ls, mk, c, rf"$\ell={l}$")
ax.text(39, .80, r"$\ell<\ell^*$: detected", color=S.BLUE, ha="right", va="top")
ax.text(39, .22, r"$\ell>\ell^*$: masked", color=S.ORANGE, ha="right", va="bottom")
ax.set(xlabel="SCR (dB)", ylabel=r"$P_{\rm d}$ at look $\ell$", yticks=[0, .5, 1], ylim=(-.04, 1.06),
       xlim=(-6, 41))
ax.set_title(rf"(b) Opposite Doppler, $\ell^*={D['b|lstar']:.1f}$")
ax.legend(**KEY)
S.grid(ax)

# (c) OS scale: detection holds while the target occupies at most m-k history innovations.
ax = axs[2]
for k, c, mk, ls in ((8, S.BLUE, "o", "-"), (12, S.ORANGE, "D", "--")):
    r = D[f"c|{k}"]
    ax.plot(range(11), r["theory"], ls, color=c, lw=1.4)
    ax.plot(range(11), r["mc"], mk, color=c, ms=MS, mfc="white", mew=MEW)
    key_line(ax, ls, mk, c, f"$k={k}$", 1.4)
    ax.axvline(16 - k, color=c, lw=.7, ls=(0, (2, 2)), alpha=.8)
    ax.text(16 - k - .15, .6, f"$m-k={16 - k}$", color=c, ha="right", va="center")
ax.set(xlabel=r"Look after onset $\ell$", ylabel=r"$P_{\rm d}$", xticks=range(0, 11, 2),
       yticks=[0, .5, 1], ylim=(-.04, 1.06), xlim=(-.3, 10.3))
ax.set_title("(c) Order-statistic scale, $m=16$, SCR 10 dB")
ax.legend(loc="lower left", bbox_to_anchor=(0., .04), handlelength=2.4, labelspacing=.12, borderaxespad=.2)
S.grid(ax)

# (d) Certified integration under Gaussian hits 30 dB above local power.
ax = axs[3]
f = D["f"]; ps = 100 * np.array(f["p"]); FLOOR = 1e-5
for key, c, ls, mk, lab in (("ca", S.DARK, ":", "o", "Integration"),
                            ("clip0", S.ORANGE, "--", "s", "Clean-threshold clip"),
                            ("cert", S.BLUE, "-", "o", "Certified clip"),
                            ("bin_cert", S.TEAL, "-.", "D", "Certified binary")):
    v = np.array(f[key]); z = v == 0
    mfc = "white" if key == "bin_cert" else c
    ax.semilogy(ps, np.where(z, FLOOR, v), ls, color=c, lw=1.3)
    ax.semilogy(ps[~z], v[~z], mk, ms=MS, color=c, mfc=mfc, mew=MEW)
    ax.semilogy(ps[z], np.full(z.sum(), FLOOR), "v", color=c, ms=5.6 if key == "cert" else 3.8,
                mfc="white", mew=.9)
    key_line(ax, ls, mk, c, lab, mfc=mfc)
ax.axhline(.01, color=S.GREY, lw=.8)
ax.plot([], [], color=S.GREY, lw=.8, label=r"design $\alpha=10^{-2}$")
ax.plot([], [], "v", color=S.DARK, ms=3.8, mfc="white", mew=.9, label="no event")
ax.set(xlabel="Hit rate per pulse (%)", ylabel=r"$P_{\rm fa}$", ylim=(5e-6, 2),
       yticks=[1e-5, 1e-3, 1e-1, 1], xlim=(-.3, 8.3), xticks=range(0, 9, 2))
ax.minorticks_off()
ax.set_title("(d) False alarms, pulsed interference")
ax.legend(**KEY)
S.grid(ax)

fig.savefig(OUT / "fig_theory_row.pdf")
fig.savefig(OUT / "fig_theory_row_check.png", dpi=220)
(OUT / "theory_input_sha256.txt").write_text(
    f"{hashlib.sha256(DATA.read_bytes()).hexdigest()}  {DATA.name}\n")
print("Fig. 1: %.2f x %.2f in, printed at 100%%; 8 pt text." % tuple(fig.get_size_inches()))
