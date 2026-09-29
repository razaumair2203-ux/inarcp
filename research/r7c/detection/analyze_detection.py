"""Endpoints of PROTOCOL_DETECTION.md from results/detection/det_*.npz. Writes detection_summary.txt/.json
and fig_detection.pdf/png. Day-cluster bootstrap: 10,000 resamples, seed 20260930."""
import os, glob, json
import numpy as np
HERE = os.path.dirname(os.path.abspath(__file__)); RES = os.path.join(os.path.dirname(HERE), "study", "results", "detection")
FILES = sorted(glob.glob(os.path.join(RES, "det_*.npz")))
D = [np.load(p) for p in FILES]; days = [str(d["day"]) for d in D]; scr = D[0]["scr_db"]
METHODS = ["CAloc", "CA16", "U", "RMS", "MLP", "LS", "MON", "G1", "IN1", "IN2", "IN4", "NA1", "NA2", "NA4", "NA4G"]
ALPHAS = (0.1, 0.01, 0.001); rng = np.random.default_rng(20260930); out = {}; lines = []
log = lambda s: (print(s), lines.append(s))


def scr_at(pd, level):
    pd = np.maximum.accumulate(pd)            # monotone envelope (Monte Carlo wiggles only)
    if pd[0] >= level: return scr[0]
    if pd[-1] < level: return np.nan
    i = np.argmax(pd >= level); x0, x1, y0, y1 = scr[i - 1], scr[i], pd[i - 1], pd[i]
    return x0 + (level - y0) * (x1 - x0) / (y1 - y0) if y1 > y0 else x1


def boot(vals):
    vals = np.asarray(vals); ud = sorted(set(days)); by = {u: vals[[d == u for d in days]] for u in ud}
    est = np.nanmean(vals); bs = []
    for _ in range(10000):
        pick = rng.choice(ud, len(ud)); bs.append(np.nanmean(np.concatenate([by[u] for u in pick])))
    return est, *np.nanpercentile(bs, [2.5, 97.5])


log(f"units: {len(D)}; days: {len(set(days))}; test episodes: {sum(int(d['n_test']) for d in D)}")
for a in ALPHAS:
    log(f"\n=== 1-alpha = {1 - a:g}  (Swerling 1; Pd pooled mean over units; SCR in dB rel. local clutter+noise power) ===")
    log("method  Pfa_meas  " + " ".join(f"{x:6.1f}" for x in scr))
    for mth in METHODS:
        pd = np.mean([d[f"{mth}|{a}|sw1"] for d in D], 0); pfa = np.mean([d[f"{mth}|{a}|pfa"] for d in D])
        out[f"{mth}|{a}|pd"] = pd.tolist(); out[f"{mth}|{a}|pfa"] = float(pfa)
        log(f"{mth:6s}  {pfa:.4f}   " + " ".join(f"{x:6.3f}" for x in pd))
    pred = np.mean([d[f"IN1|{a}|pred"] for d in D], 0); out[f"IN1|{a}|pred"] = pred.tolist()
    log(f"{'IN1 exact-law prediction':24s}" + " ".join(f"{x:6.3f}" for x in pred))
    mae = np.mean([np.abs(d[f"IN1|{a}|pred"] - d[f"IN1|{a}|sw1"]) for d in D]); out[f"exact_mae|{a}"] = float(mae)
    mae_pooled = float(np.mean(np.abs(pred - np.mean([d[f'IN1|{a}|sw1'] for d in D], 0))))
    log(f"exact-law MAE, IN1 Pd: per unit x SCR {mae:.4f}; pooled curve {mae_pooled:.4f}")
    for level in (0.5, 0.9):
        base = {r: np.array([scr_at(d[f"{r}|{a}|sw1"], level) for d in D]) for r in ("CA16", "CAloc")}
        log(f"-- SCR gain (dB) needed for Pd={level}; positive = less SCR than reference; 95% day-cluster CI --")
        for mth in ("IN1", "IN4", "NA4", "G1", "U", "MLP", "LS"):
            v = np.array([scr_at(d[f"{mth}|{a}|sw1"], level) for d in D])
            g1, g2 = boot(base["CA16"] - v), boot(base["CAloc"] - v)
            out[f"gain|{mth}|{a}|{level}"] = dict(vsCA16=g1, vsCAloc=g2, scr_mean=float(np.nanmean(v)))
            log(f"   {mth:5s} SCR {np.nanmean(v):5.1f} dB | vs CA16 {g1[0]:5.2f} [{g1[1]:5.2f},{g1[2]:5.2f}] | vs CAloc {g2[0]:5.2f} [{g2[1]:5.2f},{g2[2]:5.2f}]")
json.dump(out, open(os.path.join(HERE, "detection_summary.json"), "w"), indent=1)
open(os.path.join(HERE, "detection_summary.txt"), "w").write("\n".join(lines) + "\n")

import matplotlib; matplotlib.use("Agg"); import matplotlib.pyplot as plt
fig, axes = plt.subplots(1, 2, figsize=(7.0, 2.8), sharey=True)
sty = {"CAloc": ("#898781", ":", "Power CFAR (local, ±1024)"), "CA16": ("#52514e", "--", "Power CFAR (same 16 pulses)"),
       "IN1": ("#2a78d6", "-", "IN-ARCP"), "NA4": ("#eb6834", "-", "Noise-aware AR(4)")}
for ax, a in zip(axes, (0.01, 0.001)):
    for mth, (c, ls, lab) in sty.items():
        ax.plot(scr, out[f"{mth}|{a}|pd"], ls, color=c, lw=2, label=lab)
    ax.plot(scr, out[f"IN1|{a}|pred"], "o", color="#2a78d6", ms=4, mfc="white", label="IN-ARCP exact law (Prop. 1)")
    ax.set_title(f"Pfa design {a:g}", fontsize=9); ax.set_xlabel("SCR (dB)"); ax.grid(alpha=.3)
axes[0].set_ylabel("Detection probability"); axes[1].legend(fontsize=7, loc="lower right", frameon=False)
fig.tight_layout()
for ext in ("pdf", "png"): fig.savefig(os.path.join(HERE, f"fig_detection.{ext}"), bbox_inches="tight", dpi=200)
