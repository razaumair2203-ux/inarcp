"""Endpoints of PROTOCOL_JKU.md. Writes jku_summary.txt/.json and fig_jku.pdf/png."""
import os, glob, json, re
import numpy as np
HERE = os.path.dirname(os.path.abspath(__file__)); RES = os.path.join(os.path.dirname(HERE), "study", "results", "jku")
P = sorted(glob.glob(os.path.join(RES, "j_s*_rx*_rot*.npz"))); U = [np.load(p) for p in P]
clus = [re.search(r"j_(s\d_rx\d+)_", os.path.basename(p)).group(1) for p in P]
scr = U[0]["scr_db"]; CL = ["<-5", "-5..0", "0..5", "5..10", "10..20", ">=20"]
M = ["IN1", "IN4", "NA1", "NA4", "G1", "NA4G", "U", "RMS", "CA16", "CAloc"]
rng = np.random.default_rng(20260930); lines = []; out = {}
log = lambda s: (print(s), lines.append(s))


def boot(v):
    v = np.asarray(v, float); uc = sorted(set(clus)); by = {c: v[[x == c for x in clus]] for c in uc}
    bs = [np.nanmean(np.concatenate([by[c] for c in rng.choice(uc, len(uc))])) for _ in range(10000)]
    return float(np.nanmean(v)), *map(float, np.nanpercentile(bs, [2.5, 97.5]))


def scr_at(pd, level=0.5):
    if np.any(np.isnan(pd)): return np.nan
    pd = np.maximum.accumulate(pd)
    if pd[0] >= level: return scr[0]
    if pd[-1] < level: return np.nan
    i = np.argmax(pd >= level); return scr[i - 1] + (level - pd[i - 1]) * (scr[i] - scr[i - 1]) / (pd[i] - pd[i - 1])


n = np.sum([d["cls_n"] for d in U], 0)
log(f"units {len(U)} (station x Rx x rotation); test episodes per CNR class {dict(zip(CL, n.tolist()))}")
log("mean CNR per class (dB): " + " ".join(f"{x:6.1f}" for x in np.nanmean([d['cls_mean_cnr_db'] for d in U], 0)))
for a in (0.1, 0.01):
    log(f"\n=== 1-alpha = {1-a:g} ===")
    log("J1 marginal coverage: " + " | ".join(f"{m} {np.mean([float(d[f'{m}|{a}|cover']) for d in U]):.4f}" for m in M))
    log("J2 coverage by CNR class (mean over units):")
    for m in ("IN1", "NA1", "NA4", "U", "CA16"):
        c = np.nanmean([d[f"{m}|{a}|cls_cover"] for d in U], 0)
        md = np.nanmean([np.nanmax(np.abs(d[f"{m}|{a}|cls_cover"] - (1 - a))) for d in U])
        out[f"{m}|{a}|cls"] = c.tolist(); out[f"{m}|{a}|maxdev"] = float(md)
        log(f"   {m:5s} " + " ".join(f"{x:6.3f}" for x in c) + f" | mean max class deviation {md:.3f}")
    pr = np.nanmean([d[f"IN1|{a}|cls_pred"] for d in U], 0); out[f"IN1|{a}|pred"] = pr.tolist()
    mae = np.nanmean([np.abs(d[f"IN1|{a}|cls_pred"] - d[f"IN1|{a}|cls_cover"]) for d in U])
    out[f"J2_mae|{a}"] = float(mae)
    log(f"   IN1 exact law " + " ".join(f"{x:6.3f}" for x in pr) + f" | MAE per unit x class {mae:.4f}")
log("\nJ3 detection (Swerling 1, Pfa 0.01): SCR gain vs CAloc at Pd=0.5 per CNR class, mean [95% CI]; closed form G_IN")
gin = np.nanmean([d["G_IN_db"] for d in U], 0); log("   G_IN(c) dB   " + " ".join(f"{x:16.2f}" for x in gin))
for m in ("IN1", "IN4", "NA1", "NA4", "U", "CA16"):
    row = []
    for k in range(6):
        g = [scr_at(d["CAloc|0.01|pd_cls"][:, k]) - scr_at(d[f"{m}|0.01|pd_cls"][:, k]) for d in U]
        b = boot(g) if np.any(np.isfinite(g)) else (np.nan,) * 3; out[f"J3|{m}|{k}"] = b
        row.append(f"{b[0]:5.2f} [{b[1]:5.2f},{b[2]:5.2f}]")
    log(f"   {m:5s}        " + " ".join(f"{x:>16s}" for x in row))
j4p = os.path.join(RES, "j4_interference.npz")
if os.path.exists(j4p):
    d = np.load(j4p); log(f"\nJ4 interference scenario C (Y-chirp hit rate {float(d['hit_rate']):.3f}; hit episodes {int(d['n_hit'])}, clean {int(d['n_clean'])})")
    for m in ("IN1", "NA1", "NA4", "U", "CA16"):
        log(f"   {m:5s} coverage 0.90: clean {float(d[f'{m}|0.1|clean']):.3f} hit {float(d[f'{m}|0.1|hit']):.3f} | 0.99: clean {float(d[f'{m}|0.01|clean']):.3f} hit {float(d[f'{m}|0.01|hit']):.3f}")
json.dump(out, open(os.path.join(HERE, "jku_summary.json"), "w"), indent=1)
open(os.path.join(HERE, "jku_summary.txt"), "w").write("\n".join(lines) + "\n")

import matplotlib; matplotlib.use("Agg"); import matplotlib.pyplot as plt
x = np.nanmean([d["cls_mean_cnr_db"] for d in U], 0); k = np.isfinite(x)
fig, ax = plt.subplots(1, 2, figsize=(7.0, 2.7))
ax[0].plot(x[k], np.array(out["IN1|0.1|pred"])[k], "-", color="#2a78d6", lw=2, label="IN-ARCP exact law (Prop. 1)")
ax[0].plot(x[k], np.array(out["IN1|0.1|cls"])[k], "o", color="#2a78d6", label="IN-ARCP measured")
ax[0].plot(x[k], np.array(out["NA4|0.1|cls"])[k], "s--", color="#eb6834", label="Noise-aware AR(4)")
ax[0].axhline(0.9, color="#898781", lw=1); ax[0].set_xlabel("Clutter-to-noise ratio (dB)"); ax[0].set_ylabel("Coverage (nominal 0.90)")
ax[0].legend(fontsize=7, frameon=False); ax[0].grid(alpha=.3); ax[0].set_title("77 GHz FMCW ground clutter", fontsize=9)
for m, c, s in (("IN1", "#2a78d6", "o-"), ("NA4", "#eb6834", "s--")):
    ax[1].plot(x[k], [out[f"J3|{m}|{i}"][0] for i in range(6) if k[i]], s, color=c, label=m.replace("IN1", "IN-ARCP").replace("NA4", "Noise-aware AR(4)"))
ax[1].plot(x[k], gin[k], ":", color="#52514e", label="closed form $G_{IN}(c)$")
ax[1].axhline(0, color="#898781", lw=1); ax[1].set_xlabel("Clutter-to-noise ratio (dB)"); ax[1].set_ylabel("SCR gain vs power CFAR (dB)")
ax[1].legend(fontsize=7, frameon=False); ax[1].grid(alpha=.3); ax[1].set_title("Detection, Pfa 0.01, Pd 0.5", fontsize=9)
fig.tight_layout()
for e in ("pdf", "png"): fig.savefig(os.path.join(HERE, f"fig_jku.{e}"), bbox_inches="tight", dpi=200)
