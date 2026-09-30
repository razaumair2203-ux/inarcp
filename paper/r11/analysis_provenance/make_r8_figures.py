"""Column-width versions of the R8 figures for the manuscript, from the saved summary JSONs (no refitting).
Usage: python make_r8_figures.py <repo>/research/r7c"""
import sys, os, json
import numpy as np
import matplotlib; matplotlib.use("Agg"); import matplotlib.pyplot as plt
R7C = sys.argv[1]; OUT = os.path.join(os.path.dirname(os.path.abspath(__file__)), "..", "manuscript", "figures")
plt.rcParams.update({"font.size": 8, "axes.edgecolor": "#c3c2b7", "axes.labelcolor": "#52514e", "legend.frameon": False})
det = json.load(open(os.path.join(R7C, "detection", "detection_summary.json")))
jku = json.load(open(os.path.join(R7C, "jku", "jku_summary.json")))
scr = np.arange(-5, 25.01, 2.5)

fig, ax = plt.subplots(figsize=(3.45, 2.5))
for m, c, ls, lab in (("CAloc", "#898781", ":", "Power CFAR, local (±1024)"), ("CA16", "#52514e", "--", "Power CFAR, same 16 pulses"),
                      ("IN1", "#2a78d6", "-", "IN-ARCP"), ("NA4", "#eb6834", "-", "Noise-aware AR(4)")):
    ax.plot(scr, det[f"{m}|0.01|pd"], ls, color=c, lw=1.8, label=lab)
ax.plot(scr, det["IN1|0.01|pred"], "o", color="#2a78d6", ms=3.5, mfc="white", label="IN-ARCP exact law (Cor. 2)")
ax.set_xlabel("SCR (dB)"); ax.set_ylabel("Detection probability"); ax.grid(alpha=.3); ax.legend(fontsize=6.5, loc="lower right")
ax.set_title("IPIX sea clutter, $P_{\\rm fa}$ design 0.01", fontsize=8)
fig.tight_layout(); fig.savefig(os.path.join(OUT, "fig_detection_col.pdf"), bbox_inches="tight")

import glob
U = [np.load(p) for p in glob.glob(os.path.join(R7C, "..", "r7c", "study", "results", "jku", "j_s*.npz"))]
x = np.nanmean([d["cls_mean_cnr_db"] for d in U], 0); k = np.isfinite(x)
Gs = []                                             # general form (5) with each unit's fitted r and rho (post hoc)
for d in U:
    rec = json.loads(str(d["rec"])); r_ = complex(rec["r"]); rho_ = complex(rec["rho1"]); c = 10 ** (d["cls_mean_cnr_db"] / 10)
    Gs.append(10 * np.log10((1 + c) / (c * (1 + abs(r_) ** 2 - 2 * (np.conj(r_) * rho_).real) + 1 + abs(r_) ** 2)))
gin = np.nanmean(Gs, 0)
fig, ax = plt.subplots(2, 1, figsize=(3.45, 3.75), sharex=True)
ax[0].plot(x[k], np.array(jku["IN1|0.1|pred"])[k], "-", color="#2a78d6", lw=1.8, label="IN-ARCP exact law")
ax[0].plot(x[k], np.array(jku["IN1|0.1|cls"])[k], "o", color="#2a78d6", ms=4, label="IN-ARCP measured")
ax[0].plot(x[k], np.array(jku["NA4|0.1|cls"])[k], "s--", color="#eb6834", ms=4, label="Noise-aware AR(4)")
ax[0].axhline(0.9, color="#898781", lw=1); ax[0].set_ylabel("Coverage (nominal 0.90)"); ax[0].grid(alpha=.3); ax[0].legend(fontsize=6.5)
for m, c, s, lab in (("IN1", "#2a78d6", "o-", "IN-ARCP"), ("NA4", "#eb6834", "s--", "Noise-aware AR(4)")):
    ax[1].plot(x[k], [jku[f"J3|{m}|{i}"][0] for i in range(6) if k[i]], s, color=c, ms=4, label=lab)
ax[1].plot(x[k], gin[k], ":", color="#52514e", label=r"form (5), fitted $r,\hat\rho$ (post hoc)")
ax[1].axhline(0, color="#898781", lw=1); ax[1].set_xlabel("Clutter-to-noise ratio (dB)"); ax[1].set_ylabel("SCR gain vs local power (dB)")
ax[1].grid(alpha=.3); ax[1].legend(fontsize=6.5)
fig.tight_layout(); fig.savefig(os.path.join(OUT, "fig_jku_col.pdf"), bbox_inches="tight")
ons = json.load(open(os.path.join(R7C, "detection", "onset_summary.json")))
oth = json.load(open(os.path.join(R7C, "detection", "onset_theory.json")))
fig, ax = plt.subplots(figsize=(3.45, 3.0)); j = np.arange(8)
for dop, c, lab in (("opposite", "#1baf7a", "IN-ARCP, opposite Doppler"), ("random", "#2a78d6", "IN-ARCP, random Doppler"), ("matched", "#e87ba4", "IN-ARCP, clutter Doppler")):
    ax.plot(j, np.mean([x["pred"][dop] for x in oth], 0), "-", color=c, lw=1.6)
    ax.plot(j, ons[f"look10|IN1|0.01|{dop}"], "o", color=c, ms=4, mfc="white", label=lab)
ax.plot(j, ons["look10|NA4|0.01|random"], "s--", color="#eb6834", ms=3.5, lw=1.2, label="Noise-aware AR(4), random")
ax.plot(j, ons["look10|CAloc|0.01|random"], ":", color="#52514e", lw=1.6, label="Power CFAR (local)")
r11 = json.load(open(os.path.join(R7C, "r11", "r11_summary.json")))                  # R11 order-statistic scores (frozen protocol)
ax.plot(j, r11["O3|OS1_8"], "D-", color="#7a4fd6", ms=3.2, lw=1.4, label="Order-statistic $k=8$, random")
ax.plot(j, r11["O3|OS1_12"], "D--", color="#7a4fd6", ms=2.8, lw=1.0, mfc="white", label="Order-statistic $k=12$, random")
ax.set_xlabel("Look after target onset (pulses)"); ax.set_ylabel("Per-look detection probability"); ax.grid(alpha=.3)
ax.legend(fontsize=5.6, loc="upper center", bbox_to_anchor=(0.5, -0.24), ncol=2, frameon=False); ax.set_title(r"IPIX, persistent target, SCR 10 dB, $P_{\rm fa}$ 0.01", fontsize=8)
fig.tight_layout(); fig.savefig(os.path.join(OUT, "fig_onset_col.pdf"), bbox_inches="tight")
print("ok")
