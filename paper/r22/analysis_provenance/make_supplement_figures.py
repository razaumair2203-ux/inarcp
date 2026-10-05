r"""All five active supplementary figures from small frozen plot-input JSON.

No large NPZs, data fitting, or simulation are required to redraw these figures.
PDFs are fixed 7.16 in wide, with 9 pt labels and legends; set \includegraphics width
to 7.16 in to preserve that print size in the letter-page supplement.
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
INPUT = Path(os.environ.get("FIG_INPUT", str(HERE / "supplement_figures_r21.json")))
if not INPUT.is_file():
    candidates = [p / sub for p in (HERE, *HERE.parents)
                  for sub in ("research/r7c", "02_paper_repo_inarcp/research/r7c")]
    REPO = Path(os.environ["R7C_DIR"]) if os.environ.get("R7C_DIR") else next(p for p in candidates if p.is_dir())
    INPUT = REPO / "presentation/supplement_figures_r21.json"
D = json.loads(INPUT.read_text(encoding="utf-8"))
assert D["schema"] == "inarcp.supplement.frozen_plot_input.v1"
OUT = Path(os.environ.get("FIG_OUT", str(HERE.parent / "supplement"))); OUT.mkdir(parents=True, exist_ok=True)
BLUE, ORANGE, GREEN, PINK, PURPLE, DARK, GREY, YELLOW = (
    "#2166AC", "#D95F02", "#087B51", "#B64A75", "#7551A8", "#333333", "#777777", "#B18400")
plt.rcParams.update({"font.family": "sans-serif", "font.size": 9, "axes.titlesize": 9,
    "axes.edgecolor": "#898781", "axes.labelcolor": DARK, "axes.linewidth": .6,
    "axes.spines.top": False, "axes.spines.right": False, "legend.frameon": False,
    "legend.fontsize": 9, "legend.title_fontsize": 9, "legend.labelspacing": .3,
    "legend.handlelength": 1.6, "legend.borderaxespad": .2, "pdf.fonttype": 42})

def save(fig, name):
    fig.savefig(OUT / (name + ".pdf"))
    fig.savefig(OUT / (name + "_check.png"), dpi=180)
    plt.close(fig)

def pdax(ax, title, xlabel="SCR (dB)"):
    ax.set_title(title); ax.set_xlabel(xlabel); ax.set_ylabel("$P_{\\rm d}$")
    ax.set_ylim(-.025, 1.025); ax.grid(alpha=.22, lw=.5)

# S1: The same six tests, with two wide columns instead of three narrow ones.
T = D["theory"]; fig, axes = plt.subplots(3, 2, figsize=(7.16, 5.95)); axes = axes.ravel()
a = axes[0]
for key, lab, c, mk, ls in (("clutter Doppler", "$0$", PINK, "o", ":"),
    ("quarter", "$\\pi/2$", BLUE, "s", "--"), ("opposite", "$\\pi$", GREEN, "^", "-")):
    r = T[f"a|{key}"]; a.plot(range(9), r["theory"], ls, color=c, lw=1.4, label=lab)
    a.plot(range(9), r["mc"], mk, color=c, ms=3.3, mfc="white")
pdax(a, "(a) After onset, SCR 10 dB", "Look after onset $\\ell$")
a.set_xticks(range(0, 9, 2)); a.legend(title="Doppler offset", loc="center right")
a = axes[1]
for l, c, mk, ls in zip((1, 2, 3, 4, 5), (BLUE, GREEN, ORANGE, PINK, PURPLE),
                       ("o", "s", "^", "D", "v"), ("-", "--", "-.", ":", (0, (5, 1, 1, 1)))):
    r = T[f"b|{l}"]; a.plot(np.arange(-5, 41.), r["theory"], ls=ls, color=c, lw=1.3, label=f"$\\ell={l}$")
    a.plot((0, 10, 20, 30, 40), r["mc"], mk, color=c, ms=3.3, mfc="white")
pdax(a, f"(b) Opposite Doppler, $\\ell^*={T['b|lstar']:.1f}$"); a.legend(loc="center right")
a = axes[2]
for k, c, mk, ls in ((8, PURPLE, "o", "-"), (12, ORANGE, "D", "--")):
    r = T[f"c|{k}"]; a.plot(range(11), r["theory"], ls, color=c, lw=1.4, label=f"$k={k}$")
    a.plot(range(11), r["mc"], mk, color=c, ms=3.3, mfc="white")
a.plot(range(11), T["c|rms"], ":", color=BLUE, lw=1.3, label="RMS scale")
pdax(a, "(c) Order-statistic scale, SCR 10 dB", "Look after onset $\\ell$")
a.set_xticks(range(0, 11, 2)); a.legend(loc="lower left", title="$m=16$")
a = axes[3]
for n, c, mk, ls in zip((1, 2, 4, 8), (DARK, BLUE, GREEN, ORANGE),
                       ("o", "s", "^", "D"), (":", "-", "--", "-.")):
    r = T[f"d|{n}"]; a.plot(np.arange(-15, 21.), r["theory"], ls, color=c, lw=1.3, label=f"$K={n}$")
    a.plot((-10, -5, 0, 5), r["mc"], mk, color=c, ms=3.3, mfc="white")
pdax(a, f"(d) Whitened noncoherent integration\nPower: $K_{{\\rm eff}}={T['d|keff']:.2f}$ over 8 pulses")
a.legend(loc="lower right", ncol=2)
a = axes[4]
for n, c, mk, ls in ((8, BLUE, "o", "-"), (16, GREEN, "s", "--"), (64, ORANGE, "^", "-.")):
    r = T[f"e|{n}"]; a.plot(np.arange(-25, 6.), r["theory"], ls, color=c, lw=1.3, label=f"$N={n}$")
    a.plot((-20, -15, -10, -5, 0), r["mc"], mk, color=c, ms=3.3, mfc="white")
pdax(a, "(e) P-ANMF, unknown Doppler"); a.legend(loc="lower right")
a = axes[5]; f = T["f"]; x = 100*np.array(f["p"])
for key, c, ls, lab in (("ca", DARK, ":", "Integration"), ("clip0", ORANGE, "--", "Clean-threshold clip"),
                       ("cert", BLUE, "-", "Certified clip"), ("bin_cert", GREEN, "-.", "Certified binary")):
    y = np.array(f[key]); zero = y == 0
    a.semilogy(x, np.where(zero, 1e-5, y), ls, color=c, lw=1.3, label=lab)
    a.semilogy(x[~zero], y[~zero], "o", color=c, ms=3.3)
    a.semilogy(x[zero], np.full(zero.sum(), 1e-5), "v", color=c, mfc="white", ms=5.2 if key=="cert" else 3.2)
a.set_title("(f) Certified integration"); a.set_ylabel("$P_{\\rm fa}$")
a.set_xlabel("Hit rate per pulse (%)"); a.set_xlim(-.4, 8.4); a.set_ylim(5e-6, 2)
a.set_yticks([1e-5, 1e-3, 1e-1, 1]); a.axhline(.01, color=GREY, lw=.8)
a.text(8.4, .013, "Design $\\alpha$", ha="right", color=GREY); a.grid(alpha=.22, lw=.5)
fig.tight_layout(pad=.4, w_pad=1., h_pad=1., rect=[0., .06, 1., 1.])
h, labels = a.get_legend_handles_labels(); fig.legend(h, labels, loc="lower center", ncol=4,
    bbox_to_anchor=(.5, .003), handlelength=1.6, columnspacing=1.15)
save(fig, "fig_theory_full")

# S2: Synthetic conditional coverage, same arm/order means as original plot.
fig, axes = plt.subplots(1, 2, figsize=(7.16, 3.05), sharey=True)
names = {"sirv": "(a) Pure compound-Gaussian", "noise": "(b) Clutter + thermal noise"}
for a, arm in zip(axes, ("sirv", "noise")):
    s = D["synthetic"][arm]; x = np.arange(6)
    a.axhline(.9, color=GREY, lw=.8)
    a.plot(x, s["IN1_exact_by"], color=BLUE, lw=1.4, label="IN-ARCP law (Prop. 1)")
    a.plot(x, s["IN1"], "o", color=BLUE, ms=4.5, mfc="white", label="IN-ARCP simulation")
    a.plot(x, s["MON"], "^--", color=GREEN, ms=4, lw=1.2, label="Mondrian simulation")
    if arm == "noise":
        a.plot(x, s["NA1"], "s-.", color=ORANGE, ms=4, lw=1.2, label="Noise-aware simulation")
        a.plot(x, s["NA1G"], "D:", color=YELLOW, ms=4, lw=1.2, label="Noise-aware plug-in")
    a.set_xticks(x, ["<0", "0–5", "5–10", "10–15", "15–20", ">20"])
    a.set_xlabel("True clutter-to-noise ratio (dB)"); a.set_title(names[arm]); a.grid(alpha=.22, lw=.5)
axes[0].set_ylabel("Conditional coverage"); axes[0].set_ylim(.85, .94)
fig.tight_layout(pad=.4, rect=[0., .24, 1., 1.])
h, labels = axes[1].get_legend_handles_labels(); fig.legend(h, labels, loc="lower center", ncol=3,
    bbox_to_anchor=(.5, .012), columnspacing=1.15)
save(fig, "fig_synthetic_exact")

# S3: Texture-conditional coverage with all original methods and sampling band.
fig, axes = plt.subplots(1, 2, figsize=(7.16, 3.2))
series = (("IN1", "IN-ARCP", BLUE, "o", "-"), ("NA4", "Noise-aware AR(4)", ORANGE, "s", "-."),
    ("MON", "Mondrian IN-ARCP", GREEN, "^", "--"), ("U", "Unnormalized CP", YELLOW, "D", ":"),
    ("RMS", "Raw-RMS CP", PINK, "v", (0, (5, 1, 1, 1))), ("MLP", "Invariant MLP CP", PURPLE, "P", (0, (5, 1))))
for a, alpha, panel in zip(axes, (.1, .01), ("a", "b")):
    s = D["texture"][str(alpha)]; x = np.arange(1, 6); ref = s["sampling_reference"]
    a.axhspan(1-alpha-ref, 1-alpha+ref, color="#e2e2e2", alpha=.7, lw=0)
    a.axhline(1-alpha, color=GREY, lw=.8)
    for key, lab, c, mk, ls in series:
        a.plot(x, s[key], marker=mk, ls=ls, color=c, ms=4.5, lw=1.3, label=lab)
    a.set_xticks(x, ["1\n(lowest)", "2", "3", "4", "5\n(highest)"])
    a.set_xlabel("Texture quintile (local clutter power)"); a.set_title(f"({panel}) Nominal coverage {1-alpha:.2f}")
    a.set_ylabel("Coverage"); a.grid(alpha=.22, lw=.5)
axes[0].set_ylim(.72, 1.); axes[1].set_ylim(.945, 1.)
fig.tight_layout(pad=.4, rect=[0., .24, 1., 1.])
h, labels = axes[0].get_legend_handles_labels(); fig.legend(h, labels, loc="lower center", ncol=3,
    bbox_to_anchor=(.5, .012), columnspacing=1.15)
save(fig, "fig_texture_conditional")

# S4: Both original design rates, shorter method names and contextual law label.
fig, axes = plt.subplots(1, 2, figsize=(7.16, 2.95), sharey=True)
scr = np.arange(-5, 25.01, 2.5)
for a, alpha, panel in zip(axes, (.01, .001), ("a", "b")):
    s = D["detection"][str(alpha)]
    for m, c, ls, lab in (("CAloc", GREY, ":", "CAloc"), ("CA16", DARK, "--", "CA16"),
        ("NA4", ORANGE, "-.", "NA-AR(4)"), ("IN1", BLUE, "-", "IN-ARCP")):
        a.plot(scr, s[f"{m}|{alpha}|pd"], ls, color=c, lw=1.5, label=lab)
    a.plot(scr, s[f"IN1|{alpha}|pred"], "o", color=BLUE, ms=3.8, mfc="white", label="Law (Cor. 2)")
    pdax(a, f"({panel}) Design $P_{{\\rm fa}}={alpha:g}$")
    a.set_xlim(-5.5, 25.5)
    h, labels = a.get_legend_handles_labels(); order=[3,4,2,1,0]
    a.legend([h[i] for i in order], [labels[i] for i in order], loc="lower right")
fig.tight_layout(pad=.4, w_pad=1.)
save(fig, "fig_detection")

# S5: Coverage and onset gain in ground clutter, original class summaries.
fig, axes = plt.subplots(1, 2, figsize=(7.16, 3.3)); s = D["ground"]
x=np.array(s["cnr_db"]); ok=np.isfinite(x); a=axes[0]
a.plot(x[ok], np.array(s["IN1|0.1|pred"])[ok], "-", color=BLUE, lw=1.4, label="IN-ARCP law (Prop. 1)")
a.plot(x[ok], np.array(s["IN1|0.1|cls"])[ok], "o", color=BLUE, ms=4.2, mfc="white", label="IN-ARCP measured")
a.plot(x[ok], np.array(s["NA4|0.1|cls"])[ok], "s--", color=ORANGE, ms=4.2, lw=1.3, label="NA-AR(4)")
a.axhline(.9, color=GREY, lw=.8); a.set_xlabel("Clutter-to-noise ratio (dB)")
a.set_ylabel("Coverage"); a.set_title("(a) 77 GHz, nominal coverage 0.90")
a.grid(alpha=.22, lw=.5)
handles_a, labels_a = a.get_legend_handles_labels()
a=axes[1]
for key,c,mk,ls,lab in (("gain_IN1_db",BLUE,"o","-","IN-ARCP"),
    ("gain_NA4_db",ORANGE,"s","--","NA-AR(4)")):
    a.plot(x[ok], np.array(s[key])[ok], marker=mk, ls=ls, color=c, ms=4.2, lw=1.3, label=lab)
a.plot(x[ok],np.array(s["gain_closed_form_db"])[ok],":",color=DARK,lw=1.3,label="$G_{\\rm IN}(c)$, post hoc")
a.axhline(0,color=GREY,lw=.8); a.set_xlabel("Clutter-to-noise ratio (dB)")
a.set_ylabel("SCR gain over\nlocal power (dB)"); a.set_title("(b) $P_{\\rm fa}=0.01$, $P_{\\rm d}=0.5$")
a.grid(alpha=.22,lw=.5)
handles_b, labels_b = a.get_legend_handles_labels()
fig.tight_layout(pad=.85,w_pad=1.,rect=[0., .25, 1., 1.])
fig.legend(handles_a + [handles_b[0], handles_b[2]], labels_a + [labels_b[0], labels_b[2]],
    loc="lower center", ncol=3, bbox_to_anchor=(.5, .012), columnspacing=1.15)
save(fig,"fig_jku")
(OUT / "supplement_input_sha256.txt").write_text(
    f"{hashlib.sha256(INPUT.read_bytes()).hexdigest()}  {INPUT.name}\n")
print("Replotted five supplementary figures: 7.16 in wide; 9 pt labels and legends.")
