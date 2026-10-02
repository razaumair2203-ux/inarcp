"""Analyse the R14 IPIX outcomes against the frozen expectations of PROTOCOL_R14.md.
Usage: python analyze_r14.py  ->  r14_summary.json, r14_summary.txt (verdicts are computed mechanically)."""
import glob, json, os, sys
import numpy as np

HERE = os.path.dirname(os.path.abspath(__file__)); ROOT = os.path.dirname(HERE)
RES = os.path.join(ROOT, "study", "results", "r14")
U = [dict(np.load(f, allow_pickle=True)) for f in sorted(glob.glob(os.path.join(RES, "u_*.npz")))]
assert len(U) == 56, len(U)
SCR = U[0]["scr_db"]; I10 = int(np.argmin(abs(SCR - 10)))
days = sorted({str(u["day"]) for u in U}); dayidx = np.array([days.index(str(u["day"])) for u in U])
rng = np.random.default_rng(14)
BOOT = rng.integers(0, len(days), (10000, len(days)))
OUT, TXT = {}, []


def log(s=""):
    print(s); TXT.append(s)


def boot(stat_fn):
    """stat_fn(unit_weights) -> scalar; unit weights from resampled days."""
    vals = []
    for b in BOOT:
        w = np.bincount(b, minlength=len(days))[dayidx].astype(float)
        vals.append(stat_fn(w))
    return np.percentile(vals, [2.5, 97.5])


def pooled_counts(key, idx_e=0, idx_n=1):
    e = np.array([u[key][idx_e] for u in U], float); n = np.array([u[key][idx_n] for u in U], float)
    f = lambda w: (w * e).sum() / (w * n).sum()
    return f(np.ones(len(U))), boot(f)


def pooled_rate(key, weight_key, j=None):
    """weighted mean of per-unit rates (array or scalar), weights = number of test segments."""
    v = np.array([u[key] if j is None else u[key][j] for u in U], float)
    w0 = np.array([float(np.atleast_1d(u[weight_key])[-1]) for u in U])
    f = lambda w: (w * w0 * v.T).sum(-1) / (w * w0).sum() if v.ndim > 1 else (w * w0 * v).sum() / (w * w0).sum()
    return f(np.ones(len(U))), (boot(f) if v.ndim == 1 else None)


def scr50(pd):
    pd = np.asarray(pd)
    if pd[0] >= 0.5:
        return -np.inf
    i = np.argmax(pd >= 0.5)
    if pd[i] < 0.5:
        return np.inf
    return SCR[i - 1] + (0.5 - pd[i - 1]) / (pd[i] - pd[i - 1]) * (SCR[i] - SCR[i - 1])


def fmt(x):
    return "n.r." if x == np.inf else ("<=-5" if x == -np.inf else f"{x:.1f}")


V = {}
# ------------------------------------------------------------------ Part G
log("Part G: guarded history scale (56 units)")
gk = lambda g, a: f"G|clean|{g}|{a}"
spread = {}
for g in (0, 8, 16):
    for a in (0.01, 0.001):
        r, ci = pooled_counts(gk(g, a)); OUT[f"G|pfa|{g}|{a}"] = [r / a, *(ci / a)]
        log(f"  g={g:2d} alpha={a:g}: clean Pfa/alpha {r / a:.2f} [{ci[0] / a:.2f}, {ci[1] / a:.2f}]")
    e = np.sum([u[gk(g, 0.01)][2:7] for u in U], 0); nq = np.sum([u[gk(g, 0.01)][7:12] for u in U], 0)
    spread[g] = (e / nq).max() / (e / nq).min(); OUT[f"G|spread|{g}"] = spread[g]
    log(f"  g={g:2d} quintile spread at 0.01: {spread[g]:.2f}")
wkey = gk(0, 0.01)
for dop in ("random", "opposite", "matched"):
    for g in (0, 8, 16):
        look = np.average([u[f"G|abrupt|{dop}|{g}|look"] for u in U], axis=0, weights=[u[wkey][1] for u in U])
        cum = np.average([u[f"G|abrupt|{dop}|{g}|cum8"] for u in U], axis=0, weights=[u[wkey][1] for u in U])
        OUT[f"G|look10|{dop}|{g}"] = look[I10].tolist(); OUT[f"G|scr50cum8|{dop}|{g}"] = scr50(cum); OUT[f"G|scr50look0|{dop}|{g}"] = scr50(look[:, 0])
        log(f"  {dop:<8s} g={g:2d}: per-look Pd@10dB " + " ".join(f"{v:.2f}" for v in look[I10])
            + f" | mean looks1-8 {look[I10, 1:].mean():.2f} | SCR50 look0 {fmt(scr50(look[:, 0]))} | SCR50 within8 {fmt(scr50(cum))}")
for g in (0, 8, 16):
    law = np.average([u[f"G|law|random|{g}"] for u in U], axis=0, weights=[u[wkey][1] for u in U])
    log(f"  law (exploratory, AR(1) no noise) random g={g:2d}: " + " ".join(f"{v:.2f}" for v in law[I10]))
    OUT[f"G|law10|random|{g}"] = law[I10].tolist()
for Lr in (8, 16):
    for g in (0, 8, 16):
        cum = np.average([u[f"G|ramp{Lr}|random|{g}|cum8"] for u in U], axis=0, weights=[u[wkey][1] for u in U])
        OUT[f"G|ramp{Lr}|cum8@10|{g}"] = cum[I10]; OUT[f"G|ramp{Lr}|scr50|{g}"] = scr50(cum)
        log(f"  ramp L={Lr:2d} g={g:2d}: detection within 8 looks @10dB {cum[I10]:.3f}, SCR50 {fmt(scr50(cum))}")
for g in (0, 8, 16):
    for a in (0.001, 0.01):
        e = sum(u[f"G|target|{g}|{a}"][0] for u in U); n = sum(u[f"G|target|{g}|{a}"][1] for u in U)
        OUT[f"G|target|{g}|{a}"] = e / n
        log(f"  real target g={g:2d} alpha={a:g}: exceedance {e / n:.4f}")
look = lambda g: np.average([u[f"G|abrupt|random|{g}|look"] for u in U], axis=0, weights=[u[wkey][1] for u in U])
V["G1"] = all(0.8 <= OUT[f"G|pfa|16|{a}"][0] <= 1.25 for a in (0.01, 0.001)) and spread[16] <= 1.3 * spread[0]
V["G2"] = look(16)[I10, 1:].mean() >= 0.5 and look(0)[I10, 1:].mean() < 0.4
V["G3"] = abs(scr50(look(16)[:, 0]) - scr50(look(0)[:, 0])) <= 0.5
V["G4"] = OUT["G|ramp16|cum8@10|16"] - OUT["G|ramp16|cum8@10|0"] >= 0.2
V["G5"] = OUT["G|target|16|0.001"] < 2e-3

# ------------------------------------------------------------------ Parts K, T, X, B
log("\nParts K/T/X/B: dwell integration (56 units)")
tl = U[0]["trim_levels"]
log("  trim levels t (p, alpha, model): " + "; ".join(f"({p:g}, {a:g}, {'burst' if b else 'bern'}) -> {int(t) if t >= 0 else 'vacuous'}" for p, a, b, t in tl))
OUT["trim_levels"] = tl.tolist()
rules = {a: [float(u[f"K|rule|{a}"]) for u in U] for a in (0.01, 0.001)}
krule = {a: max(set(v), key=v.count) for a, v in rules.items()}
OUT["K|rule"] = krule
log(f"  kappa rule (mode over units): {krule}  (distribution: { {a: {k: v.count(k) for k in set(v)} for a, v in rules.items()} })")
nd = "n_dwell"


def rate(key, j):
    v, ci = pooled_rate(key, nd, j)
    return v, ci


def pd_curve(key):
    return np.average([u[key][1:] for u in U], axis=0, weights=[u[nd][1] for u in U])


base = {a: scr50(pd_curve(f"clean|clean|clip6|{a}")) for a in (0.01, 0.001)}
for nm in ("clip6", "clip9", "clip18", "blank"):
    for a in (0.01, 0.001):
        pc = pd_curve(f"clean|clean|{nm}|{a}"); OUT[f"clean|{nm}|{a}|pd10"] = float(pc[I10])
OUT["clean_clip6_scr50"] = base
log(f"  clean clipped (kappa 6) SCR50: alpha 0.01 {fmt(base[0.01])}, 0.001 {fmt(base[0.001])}")
for k in (4, 6, 9, 12, 18):
    for a in (0.01, 0.001):
        r, ci = rate(f"clean|clean|clip{k}|{a}", 0)
        OUT[f"K|clean|{k}|{a}"] = [r / a, *(ci / a)]
        log(f"  clip kappa={k:2d} alpha={a:g}: clean Pfa/alpha {r / a:.2f} [{ci[0] / a:.2f}, {ci[1] / a:.2f}], clean SCR50 {fmt(scr50(pd_curve(f'clean|clean|clip{k}|{a}')))}")
for a in (0.01, 0.001):
    r, ci = rate(f"clean|clean|blank|{a}", 0); OUT[f"X|clean|{a}"] = [r / a, *(ci / a)]
    log(f"  blank alpha={a:g}: clean Pfa/alpha {r / a:.2f} [{ci[0] / a:.2f}, {ci[1] / a:.2f}], clean SCR50 {fmt(scr50(pd_curve(f'clean|clean|blank|{a}')))}")

conds = [("bern", p, j) for p in (0.02, 0.05) for j in (10, 30)] + [("burst", p, 30) for p in (0.02, 0.05)]
tr_of = {(round(p, 3), a, int(b)): (int(t) if t >= 0 else None) for p, a, b, t in tl}
rows = []
for mdl, p, j in conds:
    for a in (0.01, 0.001):
        tag = f"I|{mdl}|{p}|{j}"
        cand = {"clean-thr clip6": f"{tag}|clean|clip6|{a}"}
        for k in (4, 6, 9, 12, 18):
            cand[f"cert(bern) clip{k}"] = f"{tag}|cert-bern|clip{k}|{p}|{a}"
            cand[f"cert(burst) clip{k}"] = f"{tag}|cert-burst|clip{k}|{p}|{a}"
        for m in ("bern", "burst"):
            t = tr_of.get((p, a, int(m == "burst")))
            if t is not None:
                cand[f"cert({m}) trim t={t}"] = f"{tag}|cert-{m}|trim|{p}|{a}|{m}|{p}|{a}"
        cand["blank(bern masks)"] = f"{tag}|mask-bern|blank|{p}|{a}"
        cand["blank(burst masks)"] = f"{tag}|mask-burst|blank|{p}|{a}"
        for name, key in cand.items():
            if key not in U[0]:
                continue
            r, ci = rate(key, 0); pc = pd_curve(key); s = scr50(pc); cost = s - base[a]
            OUT[f"{mdl}|{p}|{j}|{a}|{name}"] = dict(pfa=r / a, lo=ci[0] / a, hi=ci[1] / a, scr50=s, cost=cost, pd10=float(pc[I10]), pd25=float(pc[-1]))
            rows.append((mdl, p, j, a, name, r / a, ci[1] / a, s, cost, pc[I10], pc[-1]))
log("\n  condition                     alpha  statistic                Pfa/alpha [upper]   SCR50   cost vs clean clip6")
for mdl, p, j, a, name, r, hi, s, c, p10, p25 in rows:
    log(f"  {mdl:<5s} p={p:<4g} {j:2d} dB       {a:<6g} {name:<24s} {r:6.2f} [{hi:5.2f}]     {fmt(s):>5s}   {('n.r.' if c == np.inf else f'{c:+.1f}'):>6s}            {p10:.2f}     {p25:.2f}")

g = lambda mdl, p, j, a, name: OUT.get(f"{mdl}|{p}|{j}|{a}|{name}")
kr = {a: int(krule[a]) for a in krule}
V["K1"] = OUT["K|clean|6|0.001"][0] < 0.8 and all(0.8 <= OUT[f"K|clean|{kr[a]}|{a}"][0] <= 1.25 for a in (0.01, 0.001))
V["K2"] = all(g("bern", p, j, 0.001, f"cert(bern) clip{kr[0.001]}")["scr50"] < 25 for p in (0.02, 0.05) for j in (10, 30)) and \
          not all(g("bern", p, j, 0.001, "cert(bern) clip6")["scr50"] < 25 for p in (0.02, 0.05) for j in (10, 30))
trim_rows = [v for k, v in OUT.items() if isinstance(v, dict) and "trim" in k and k.startswith("bern")]
V["T1"] = all(v["hi"] <= 1.2 for v in trim_rows) if trim_rows else None
t2a = tr_of.get((0.02, 0.01, 0)) is not None and tr_of[(0.02, 0.01, 0)] >= 4
t2b = all((g("bern", p, j, 0.01, f"cert(bern) trim t={tr_of[(p, 0.01, 0)]}") or {"cost": np.inf})["cost"] > g("bern", p, j, 0.01, "cert(bern) clip6")["cost"]
          for p in (0.02, 0.05) for j in (10, 30) if tr_of.get((p, 0.01, 0)) is not None)
V["T2"] = t2a and t2b
V["X1"] = all(g("bern", p, j, 0.01, "blank(bern masks)")["pfa"] <= 1.25 for p in (0.02, 0.05) for j in (10, 30))
V["X2"] = all(g("bern", 0.05, j, 0.01, "blank(bern masks)")["cost"] <= 3 for j in (10, 30))
V["X3"] = all(0.8 <= OUT[f"X|clean|{a}"][0] <= 1.25 for a in (0.01, 0.001))
V["B1"] = any(g("burst", p, 30, a, "cert(bern) clip6")["pfa"] > 1 for p in (0.02, 0.05) for a in (0.01, 0.001))
V["B2"] = all(g("burst", p, 30, a, "cert(burst) clip6")["pfa"] <= 1.2 for p in (0.02, 0.05) for a in (0.01, 0.001))
V["B3"] = any(g("burst", p, 30, 0.01, "blank(bern masks)")["pfa"] > 1.25 for p in (0.02, 0.05))
log("\nVerdicts (frozen expectations): " + ", ".join(f"{k} {'met' if v else 'NOT met'}" for k, v in V.items()))
log(f"met {sum(bool(v) for v in V.values())} of {len(V)}")
OUT["verdicts"] = {k: bool(v) for k, v in V.items()}
json.dump(OUT, open(os.path.join(HERE, "r14_summary.json"), "w"), indent=1, default=lambda x: None if (isinstance(x, float) and not np.isfinite(x)) else float(x))
open(os.path.join(HERE, "r14_summary.txt"), "w", encoding="utf8").write("\n".join(TXT) + "\n")
