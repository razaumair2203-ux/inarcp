"""EXPLORATORY dwell-level analysis (equal dwell Pfa = 0.01). Writes dwell_summary.txt/.json."""
import os, glob, json
import numpy as np
from analyze_onset import scr_at as _scr_at_onset   # same interpolation rule
HERE = os.path.dirname(os.path.abspath(__file__)); RES = os.path.join(os.path.dirname(HERE), "study", "results", "dwell")
D = [np.load(p) for p in sorted(glob.glob(os.path.join(RES, "w_*.npz")))]; days = [str(d["day"]) for d in D]
scr = D[0]["scr_db"]; rng = np.random.default_rng(20260930); lines = []; out = {}
log = lambda s: (print(s), lines.append(s))


def scr_at(pd, level):
    pd = np.maximum.accumulate(pd)
    if pd[0] >= level: return scr[0]
    if pd[-1] < level: return np.nan
    i = np.argmax(pd >= level); return scr[i - 1] + (level - pd[i - 1]) * (scr[i] - scr[i - 1]) / (pd[i] - pd[i - 1])


def boot(v):
    v = np.asarray(v, float); ud = sorted(set(days)); by = {u: v[[d == u for d in days]] for u in ud}
    bs = [np.nanmean(np.concatenate([by[u] for u in rng.choice(ud, len(ud))])) for _ in range(10000)]
    return float(np.nanmean(v)), *map(float, np.nanpercentile(bs, [2.5, 97.5]))


log(f"EXPLORATORY: units {len(D)}; dwell Pfa design 0.01; persistent Swerling-1 targets, random Doppler")
for k in (1, 2, 4, 8):
    log(f"\n-- K = {k} looks --")
    for m in ("IN1", "NA4", "CAloc"):
        for s in ("max", "sum"):
            pf = np.mean([float(d[f"{m}|{s}|K{k}|pfa"]) for d in D])
            s5 = np.nanmean([scr_at(d[f"{m}|{s}|K{k}|pd"], .5) for d in D]); s9 = np.nanmean([scr_at(d[f"{m}|{s}|K{k}|pd"], .9) for d in D])
            out[f"{m}|{s}|K{k}"] = dict(pfa=pf, scr50=float(s5), scr90=float(s9))
            log(f"   {m:5s} {s}: measured dwell Pfa {pf:.4f} | SCR for Pd 0.5 {s5:5.1f} dB | Pd 0.9 {s9:5.1f} dB")
    for m, s in (("IN1", "max"), ("NA4", "max"), ("IN1", "sum"), ("NA4", "sum")):
        for lev in (.5, .9):
            g = boot([scr_at(d[f"CAloc|sum|K{k}|pd"], lev) - scr_at(d[f"{m}|{s}|K{k}|pd"], lev) for d in D])
            out[f"gain|{m}|{s}|K{k}|{lev}"] = g
            log(f"   gain of {m}-{s} over integrated power CFAR (CAloc-sum) at Pd {lev}: {g[0]:5.2f} [{g[1]:5.2f}, {g[2]:5.2f}] dB")
json.dump(out, open(os.path.join(HERE, "dwell_summary.json"), "w"), indent=1)
open(os.path.join(HERE, "dwell_summary.txt"), "w").write("\n".join(lines) + "\n")
