"""Endpoints of PROTOCOL_ONSET.md (frozen analysis). Writes onset_summary.txt/.json."""
import os, glob, json
import numpy as np
HERE = os.path.dirname(os.path.abspath(__file__)); RES = os.path.join(os.path.dirname(HERE), "study", "results", "onset")
D = [np.load(p) for p in sorted(glob.glob(os.path.join(RES, "o_*.npz")))]; days = [str(d["day"]) for d in D]
scr = D[0]["scr_db"]; KS = (1, 2, 4, 8); rng = np.random.default_rng(20260930); out = {}; lines = []
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


log(f"units {len(D)}; segments {sum(int(d['n']) for d in D)}")
M = ("IN1", "G1", "IN4", "NA4", "CA16", "CAloc")
for a in (0.01, 0.001):
    log(f"\n=== per-look Pfa design {a} ===")
    for m in M:
        pc = np.mean([d[f"{m}|{a}|pfa_cum"] for d in D], 0); out[f"pfa_cum|{m}|{a}"] = pc.tolist()
        log(f"clean cumulative false-alarm prob, K=1,2,4,8: {m:5s} " + " ".join(f"{x:.4f}" for x in pc))
    i10 = int(np.argmin(abs(scr - 10)))
    for dop in ("random", "matched", "opposite"):
        log(f"-- per-look Pd at SCR 10 dB, Doppler {dop} (looks j=0..7) --")
        for m in M:
            v = np.mean([d[f"{m}|{a}|{dop}|look"][i10] for d in D], 0); out[f"look10|{m}|{a}|{dop}"] = v.tolist()
            log(f"   {m:5s} " + " ".join(f"{x:.3f}" for x in v))
    for dop in ("random",):
        for lev in (0.5, 0.9):
            log(f"-- SCR (dB) for cumulative Pd={lev} by K, Doppler {dop}; gain vs CAloc [95% day-cluster CI] --")
            for m in ("IN1", "NA4", "IN4", "G1", "CA16"):
                row = []
                for ki, k in enumerate(KS):
                    g = [scr_at(d[f"CAloc|{a}|{dop}|cum"][:, ki], lev) - scr_at(d[f"{m}|{a}|{dop}|cum"][:, ki], lev) for d in D]
                    b = boot(g); out[f"gain|{m}|{a}|{dop}|{lev}|K{k}"] = b
                    row.append(f"K={k}: {b[0]:5.2f} [{b[1]:5.2f},{b[2]:5.2f}]")
                log(f"   {m:5s} " + " | ".join(row))
json.dump(out, open(os.path.join(HERE, "onset_summary.json"), "w"), indent=1)
open(os.path.join(HERE, "onset_summary.txt"), "w").write("\n".join(lines) + "\n")
