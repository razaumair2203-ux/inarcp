"""R10 audit of EXISTING outcomes (no new runs; descriptive/sensitivity analyses requested by the external review):
 1. IPIX: false-alarm rate by texture quintile (Pfa/alpha), episode and exceedance counts, and a dependence-aware
    reference for the maximum quintile deviation (texture series circularly shifted in time within each bin, which
    keeps the dependence of the exceedance series and breaks its association with texture).
 2. IPIX: dependence diagnostics of exceedance indicators (lag-1 correlation along time within a bin; correlation
    across bins at the same time).
 3. IPIX: leave-one-day-out (LODO) range of the headline effects.
 4. IPIX: fit diagnostics (|r| clamp binding, NA-AR(2)/(4) Nelder-Mead convergence, fit time per unit).
 5. JKU: Pfa/alpha by CNR class with episode counts and contributing units, vs the exact law.
Writes r10/audit_existing.txt/.json."""
import os, sys, glob, json
HERE = os.path.dirname(os.path.abspath(__file__)); ROOT = os.path.dirname(HERE)
sys.path.insert(0, ROOT); sys.path.insert(0, os.path.join(ROOT, "study"))
import numpy as np
from ipix import FILES, NRANGE

RES = os.path.join(ROOT, "study", "results")
lines, out = [], {}
log = lambda s="": (print(s), lines.append(s))
rng = np.random.default_rng(20260930)


def nbins(num):
    lo, hi = FILES[num][2]
    return NRANGE - len(set(range(lo - 2, hi + 1)) & set(range(NRANGE)))


def parse(p):
    b = os.path.basename(p).split("_"); return int(b[1]), b[2], int(b[3][3:])


CONF = sorted(p for p in glob.glob(os.path.join(RES, "confirmatory", "unit_*_m16.npz")) if "_rot1_" not in p)
U = [(parse(p), np.load(p)) for p in CONF]
DAYS = [FILES[num][1] for (num, _, _), _ in U]
METH = ("IN1", "IN4", "NA4", "U", "RMS", "MLP", "MON")


def quint(tex):
    return np.digitize(tex, np.quantile(tex, [.2, .4, .6, .8]))


def maxdev(cover, qb, a):
    return float(np.max(np.abs([cover[qb == b].mean() - (1 - a) for b in range(5)])))


# ---------------------------------------------------------------- 1. quintile Pfa, counts, dependence-aware reference
log("=== 1. IPIX false-alarm rate by texture quintile (confirmatory, m = 16, +-1024 proxy) ===")
for a in (0.1, 0.01):
    log(f"-- design alpha = {a}: Pfa/alpha per quintile (low -> high texture), mean over units; exceedances pooled --")
    for m in METH:
        key = f"{m}|{a}|cover"
        if key not in U[0][1].files: continue
        ratios, exc, nep = [], np.zeros(5), np.zeros(5)
        for _, d in U:
            c = d[key].astype(bool); qb = quint(d["texture|1024"])
            ratios.append([(1 - c[qb == b].mean()) / a for b in range(5)])
            for b in range(5): exc[b] += np.sum(~c[qb == b]); nep[b] += np.sum(qb == b)
        r = np.mean(ratios, 0); out[f"q|{m}|{a}"] = dict(ratio=r.tolist(), exceed=exc.tolist(), n=nep.tolist())
        log(f"   {m:4s} " + " ".join(f"{x:5.2f}" for x in r) + f" | spread {r.max() / max(r.min(), 1e-9):6.1f}x | exceedances "
            + " ".join(f"{int(x)}" for x in exc) + f" of {int(nep.sum())} episodes")
log("-- maximum quintile deviation: observed vs binomial reference vs dependence-aware (time-shift) reference, alpha = 0.1 --")
for m in ("IN1", "IN4", "NA4", "U"):
    obs, binref, shref = [], [], []
    for (num, _, _), d in U:
        c = d[f"{m}|0.1|cover"].astype(bool); tex = d["texture|1024"]; B = nbins(num); S = len(c) // B
        obs.append(maxdev(c, quint(tex), 0.1))
        sims = [maxdev(rng.random(len(c)) < 0.9, quint(tex), 0.1) for _ in range(100)]; binref.append(np.mean(sims))
        C2, T2 = c[:S * B].reshape(S, B), tex[:S * B].reshape(S, B); sh = []
        for _ in range(100):
            k = rng.integers(S // 4, 3 * S // 4); sh.append(maxdev(C2.reshape(-1), quint(np.roll(T2, k, 0).reshape(-1)), 0.1))
        shref.append(np.mean(sh))
    out[f"maxdev|{m}"] = dict(obs=float(np.mean(obs)), binomial=float(np.mean(binref)), shift=float(np.mean(shref)))
    log(f"   {m:4s} observed {np.mean(obs):.3f} | binomial ref {np.mean(binref):.3f} | time-shift ref {np.mean(shref):.3f}")

# ---------------------------------------------------------------- 2. dependence of exceedances
log("\n=== 2. Dependence of IN1 exceedance indicators (alpha = 0.1), mean over units ===")
lag1, xbin = [], []
for (num, _, _), d in U:
    e = ~d["IN1|0.1|cover"].astype(bool); B = nbins(num); S = len(e) // B; E = e[:S * B].reshape(S, B).astype(float)
    Ec = E - E.mean()
    lag1.append(np.sum(Ec[1:] * Ec[:-1]) / np.sum(Ec ** 2) * S / (S - 1))
    cc = [np.corrcoef(E[:, i], E[:, j])[0, 1] for i in range(B) for j in range(i + 1, B) if E[:, i].std() > 0 and E[:, j].std() > 0]
    xbin.append(np.nanmean(cc))
out["dep"] = dict(lag1=float(np.mean(lag1)), crossbin=float(np.nanmean(xbin)))
log(f"   lag-1 (256 pulses) autocorrelation within bin: {np.mean(lag1):.3f} (range {np.min(lag1):.3f} to {np.max(lag1):.3f})")
log(f"   correlation across bins at the same time:      {np.nanmean(xbin):.3f}")

# ---------------------------------------------------------------- 3. leave-one-day-out
log("\n=== 3. Leave-one-day-out range of headline effects (estimate on all 6 days; min..max over the 6 LODO fits) ===")
udays = sorted(set(DAYS))


def lodo(vals, days, agg=np.nanmean):
    vals = np.asarray(vals, float); days = np.asarray(days)
    full = agg(vals); loo = [agg(vals[days != u]) for u in udays]
    return float(full), float(np.min(loo)), float(np.max(loo))


gm = lambda v: float(np.exp(np.nanmean(np.log(v))))
rat = [float(np.mean(d["NA4|0.1|radius"]) / np.mean(d["IN4|0.1|radius"])) for _, d in U]
res = lodo(rat, DAYS, gm); out["lodo|same_order_ratio"] = res
log(f"   NA-AR(4)/IN-AR(4) radius ratio (0.90): {res[0]:.3f}  LODO {res[1]:.3f}..{res[2]:.3f}")
sp = []
for u in [None] + udays:
    rr = np.mean([[(1 - d['IN1|0.01|cover'][quint(d['texture|1024']) == b].mean()) / 0.01 for b in range(5)]
                  for (_, d), dy in zip(U, DAYS) if dy != u], 0); sp.append(rr.max() / rr.min())
out["lodo|IN1_quintile_spread"] = [sp[0], min(sp[1:]), max(sp[1:])]
log(f"   IN1 quintile Pfa spread (alpha 0.01): {sp[0]:.2f}x  LODO {min(sp[1:]):.2f}..{max(sp[1:]):.2f}x")
sys.path.insert(0, os.path.join(ROOT, "detection"))
DET = sorted(glob.glob(os.path.join(RES, "detection", "det_*.npz"))); Dd = [np.load(p) for p in DET]; ddays = [str(d["day"]) for d in Dd]
scr = Dd[0]["scr_db"]


def scr_at(pd, level):
    pd = np.maximum.accumulate(pd)
    if pd[0] >= level: return scr[0]
    if pd[-1] < level: return np.nan
    i = np.argmax(pd >= level); x0, x1, y0, y1 = scr[i - 1], scr[i], pd[i - 1], pd[i]
    return x0 + (level - y0) * (x1 - x0) / (y1 - y0) if y1 > y0 else x1


for lvl in (0.5, 0.9):
    s = {m: np.array([scr_at(d[f"{m}|0.01|sw1"], lvl) for d in Dd]) for m in ("IN1", "NA4", "CA16", "CAloc", "IN4")}
    for nm, v in (("IN1 vs CA16", s["CA16"] - s["IN1"]), ("IN1 vs CAloc", s["CAloc"] - s["IN1"]),
                  ("NA4 vs IN1", s["IN1"] - s["NA4"]), ("NA4 vs IN4", s["IN4"] - s["NA4"])):
        res = lodo(v, ddays); out[f"lodo|det|{nm}|{lvl}"] = res
        log(f"   single-pulse gain {nm:12s} Pd={lvl}: {res[0]:5.2f} dB  LODO {res[1]:5.2f}..{res[2]:5.2f}")
DW = sorted(glob.glob(os.path.join(RES, "dwell", "w_*.npz"))); Dw = [np.load(p) for p in DW]; wdays = [str(d["day"]) for d in Dw]
for m in ("IN1", "NA4"):
    v = np.array([scr_at(d["CAloc|sum|K8|pd"], .5) - scr_at(d[f"{m}|sum|K8|pd"], .5) for d in Dw])
    res = lodo(v, wdays); out[f"lodo|dwell|{m}"] = res
    log(f"   eight-look dwell gain {m} vs CAloc-sum Pd=0.5: {res[0]:5.2f} dB  LODO {res[1]:5.2f}..{res[2]:5.2f}")
log("   per-day values of the single-pulse IN1 vs CAloc gain (Pd 0.5): " + ", ".join(
    f"{u} {np.nanmean((np.array([scr_at(d['CAloc|0.01|sw1'], .5) for d in Dd]) - np.array([scr_at(d['IN1|0.01|sw1'], .5) for d in Dd]))[np.array(ddays) == u]):.1f}"
    for u in udays))

# ---------------------------------------------------------------- 4. fit diagnostics
log("\n=== 4. Fit diagnostics (all confirmatory units, training thirds) ===")
absr, c2, c4, n4, secs = [], [], [], [], []
for _, d in U:
    fr = json.loads(str(d["fit_record"])); absr.append(abs(complex(*fr["r_ols"])))
    c2.append(fr["na2"]["converged"]); c4.append(fr["na4"]["converged"]); n4.append(fr["na4"]["nit"]); secs.append(float(d["seconds"]))
absr = np.array(absr)
out["fit"] = dict(absr_max=float(absr.max()), clamp_binding=int(np.sum(absr >= 0.98 - 1e-9)), na2_conv=int(np.sum(c2)), na4_conv=int(np.sum(c4)), n=len(U),
                  na4_nit_median=float(np.median(n4)), unit_seconds_median=float(np.median(secs)))
log(f"   |r| of IN-ARCP: median {np.median(absr):.3f}, max {absr.max():.3f}; clamp |r| <= 0.98 binding in {np.sum(absr >= 0.98 - 1e-9)} of {len(U)} units")
log(f"   NA-AR(2) Nelder-Mead converged in {np.sum(c2)} of {len(U)} units; NA-AR(4) in {np.sum(c4)} of {len(U)} (median iterations {np.median(n4):.0f}, cap 1500)")
log(f"   whole-unit time (all 13 procedures, GPU): median {np.median(secs):.0f} s")

# ---------------------------------------------------------------- 5. JKU
log("\n=== 5. Second radar: Pfa/alpha by CNR class (mean over units with data), exact law, counts ===")
J = [np.load(p) for p in sorted(glob.glob(os.path.join(RES, "jku", "j_s*.npz")))]
js = json.load(open(os.path.join(ROOT, "jku", "jku_summary.json")))
cls = ["<-5", "-5..0", "0..5", "5..10", "10..20", ">=20"]
cnt = [721095, 265416, 229845, 68556, 31870, 338]
law = {0.1: [0.896, 0.900, 0.905, 0.914, 0.932, 0.966], 0.01: [0.989, 0.990, 0.991, 0.993, 0.995, 0.998]}
log("   class (dB)       " + " ".join(f"{c:>8s}" for c in cls))
log("   test episodes    " + " ".join(f"{c:8d}" for c in cnt))
for a in (0.1, 0.01):
    for m in ("IN1", "NA4", "CA16"):
        C = np.array([d[f"{m}|{a}|cls_cover"] for d in J], float)
        r = (1 - np.nanmean(C, 0)) / a; nu = np.sum(np.isfinite(C), 0)
        out[f"jku|{m}|{a}"] = dict(ratio=r.tolist(), units=nu.tolist())
        log(f"   {m:4s} a={a:<5g}    " + " ".join(f"{x:8.2f}" for x in r) + "   units: " + " ".join(str(x) for x in nu))
    lr = (1 - np.array(law[a])) / a; out[f"jku|law|{a}"] = lr.tolist()
    log(f"   law  a={a:<5g}    " + " ".join(f"{x:8.2f}" for x in lr) + "   (exact law, 3-decimal coverage from jku_summary)")

json.dump(out, open(os.path.join(HERE, "audit_existing.json"), "w"), indent=1)
open(os.path.join(HERE, "audit_existing.txt"), "w").write("\n".join(lines) + "\n")
