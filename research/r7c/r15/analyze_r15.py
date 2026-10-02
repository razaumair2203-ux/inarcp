"""Analyse the R15 NetRAD outcomes against the frozen expectations of PROTOCOL_R15.md (written before any outcome).
Usage: python analyze_r15.py  ->  r15_summary.json, r15_summary.txt (verdicts computed mechanically).
Intervals: recording-cluster bootstrap (14 recordings, 10,000 resamples). Pooling follows analyze_r12.py / analyze_r14.py."""
import glob, json, os
import numpy as np

HERE = os.path.dirname(os.path.abspath(__file__)); ROOT = os.path.dirname(HERE)
RES = os.environ.get("R15_RES", os.path.join(ROOT, "study", "results", "r15"))
FILES_ = sorted(glob.glob(os.path.join(RES, "n_*_rot*.npz")))
U = [dict(np.load(f, allow_pickle=True)) for f in FILES_]
TAGS = [os.path.basename(f)[2:9] for f in FILES_]
assert len(U) == 28, len(U)
SCR = U[0]["scr_db"]; I10 = int(np.argmin(abs(SCR - 10)))
recs = sorted(set(TAGS)); ridx = np.array([recs.index(t) for t in TAGS])
rng = np.random.default_rng(15)
BOOT = rng.integers(0, len(recs), (10000, len(recs)))
OUT, TXT, V = {}, [], {}


def log(s=""):
    print(s); TXT.append(s)


def boot(f):
    vals = [f(np.bincount(b, minlength=len(recs))[ridx].astype(float)) for b in BOOT]
    return np.nanpercentile(vals, [2.5, 97.5])


def counts(key, ie=0, inn=1, sel=None):
    sel = np.ones(len(U), bool) if sel is None else sel
    e = np.array([u[key][ie] for u in U], float); n = np.array([u[key][inn] for u in U], float)
    f = lambda w: (w * e * sel).sum() / max((w * n * sel).sum(), 1e-300)
    return f(np.ones(len(U))), boot(f)


def wmean(key, wkey, sel=None, j=None):
    sel = np.ones(len(U), bool) if sel is None else sel
    v = np.array([u[key] if j is None else u[key][j] for u in U], float)
    w0 = np.array([float(np.atleast_1d(u[wkey])[-1]) for u in U]) * sel
    return np.average(v, axis=0, weights=w0) if w0.sum() > 0 else np.nan


def scr50(pd, level=0.5):
    pd = np.maximum.accumulate(np.asarray(pd, float))
    if pd[0] >= level: return -np.inf
    if pd[-1] < level: return np.inf
    return float(np.interp(level, pd, SCR))


fmt = lambda x: "n.r." if x == np.inf else ("<=-5" if x == -np.inf else f"{x:.1f}")

log(f"R15 NetRAD analysis: {len(U)} units, {len(recs)} recordings ({sum(str(U[TAGS.index(t)]['pol']) == 'HH' for t in recs)} HH)")
for t in recs:
    u = U[TAGS.index(t)]
    log(f"  {t} {str(u['pol'])}: T {int(u['T'])}, cells {int(u['B'])}, |r| {abs(complex(*u['r'])):.3f}, nu4 {float(u['nu4']):.3g}, "
        f"hit rate {float(u['W|hit_rate']):.4f}, mean hit run {float(u['W|run_mean']):.2f}")
OUT["recordings"] = {t: dict(pol=str(U[TAGS.index(t)]["pol"]), hit_rate=float(U[TAGS.index(t)]["W|hit_rate"]),
                             r=abs(complex(*U[TAGS.index(t)]["r"]))) for t in recs}

# ------------------------------------------------------------------ Part L
log("\nPart L: pooled Pfa / alpha [95% recording-cluster interval]; texture-quintile spread (max/min)")
mets = sorted({k.split("|")[1] for k in U[0] if k.startswith("L|") and k.count("|") == 3})
Lr = {}
for a in (1e-2, 1e-3, 1e-4):
    log(f"  alpha = {a:g}")
    for m in mets:
        for rule in ("conf", "anal", "boot"):
            key = f"L|{m}|{rule}|{a}"
            if key not in U[0]: continue
            p, ci = counts(key)
            S = np.sum([u[key] for u in U], 0); qp = S[2:7] / np.maximum(S[7:12], 1)
            Lr[(m, rule, a)] = (p / a, ci / a, qp.max() / max(qp.min(), 1e-12))
            log(f"    {m:<12s} {rule:<5s} {p / a:7.2f} [{ci[0] / a:.2f}, {ci[1] / a:.2f}]  spread {Lr[(m, rule, a)][2]:6.2f}")
OUT["L"] = {f"{m}|{r}|{a}": [v[0], *v[1], v[2]] for (m, r, a), v in Lr.items()}
conf13 = [m for m in mets if (m, "conf", 1e-3) in Lr]
inband = {a: [m for m in conf13 if 0.5 <= Lr[(m, "conf", a)][0] <= 2] for a in (1e-3, 1e-4)}
V["N1"] = all(len(inband[a]) >= 12 for a in (1e-3, 1e-4))
log(f"  N1: conformal statistics within [0.5, 2]: 1e-3 {len(inband[1e-3])}/{len(conf13)}, 1e-4 {len(inband[1e-4])}/{len(conf13)}; "
    f"outside: {[(m, a, round(Lr[(m, 'conf', a)][0], 2)) for a in (1e-3, 1e-4) for m in conf13 if m not in inband[a]]}")
white = ("IN1", "IN4", "OS1_8", "NA4", "D-IN4", "PAMF-H(w)", "P-ANMF(bin)", "P-ANMF", "Clip-OS1")
over = [m for m in white if (m, "anal", 1e-4) in Lr and Lr[(m, "anal", 1e-4)][0] > 2]
V["N2"] = len(over) >= 5
V["N3"] = Lr[("IN1", "anal", 1e-4)][0] <= 2
V["N4"] = Lr[("IN1", "conf", 1e-2)][2] <= 2.0 and Lr[("IN1", "conf", 1e-2)][2] < Lr[("CA16", "conf", 1e-2)][2]
log(f"  N2: whitened model-based laws > 2x at 1e-4: {len(over)} of {len(white)} {over}")
log(f"  N3: IN1 CA law at 1e-4: {Lr[('IN1', 'anal', 1e-4)][0]:.2f}")
log(f"  N4: quintile spread at 1e-2: IN1 {Lr[('IN1', 'conf', 1e-2)][2]:.2f}, CA16 {Lr[('CA16', 'conf', 1e-2)][2]:.2f}")

# ------------------------------------------------------------------ Part A
log("\nPart A: SCR (dB) for Pd = 0.5 / 0.9 (pooled curves, alpha = 0.01), measured Pfa")
dets = sorted({k.split("|")[1] for k in U[0] if k.startswith("A|") and k.endswith("|0.01|pd")})
A = {}
for m in dets:
    pd = np.mean([u[f"A|{m}|0.01|pd"] for u in U], 0); pfa = np.mean([u[f"A|{m}|0.01|pfa"] for u in U])
    A[m] = (scr50(pd), scr50(pd, .9), pfa, float(pd[I10]))
    log(f"  {m:<10s} SCR50 {fmt(A[m][0]):>6s}  SCR90 {fmt(A[m][1]):>6s}  Pd@10dB {A[m][3]:.2f}  Pfa {pfa:.4f}")
OUT["A"] = {m: list(v) for m, v in A.items()}
dw = [m for m in ("PAMF-H", "D-IN1", "D-IN4", "Clip-OS1", "Bin-OS1", "P-ANMF", "ANMF-SCM", "ANMF-FP") if m in A]
best = min(A[m][0] for m in dw)
V["N5"] = A["PAMF-H"][0] <= best + 0.5
g6 = A["OSraw"][0] - A["IN1look"][0]
V["N6"] = g6 > 0
log(f"  N5: PAMF-H SCR50 {fmt(A['PAMF-H'][0])} vs best dwell detector {fmt(best)} ({[m for m in dw if A[m][0] == best]})")
log(f"  N6: OSraw minus IN1look at Pd 0.5: {g6:.2f} dB")
OUT["A|OSraw-IN1look"] = g6

# ------------------------------------------------------------------ Part G
log("\nPart G: guarded history scale")
wkey = "G|clean|0|0.01"
for g in (0, 8, 16):
    for a in (0.01, 0.001):
        r, ci = counts(f"G|clean|{g}|{a}"); OUT[f"G|pfa|{g}|{a}"] = [r / a, *(ci / a)]
        log(f"  g={g:2d} alpha={a:g}: clean Pfa/alpha {r / a:.2f} [{ci[0] / a:.2f}, {ci[1] / a:.2f}]")
look = {}
for dop in ("random", "opposite", "matched"):
    for g in (0, 8, 16):
        lk = wmean(f"G|abrupt|{dop}|{g}|look", wkey); look[(dop, g)] = lk
        OUT[f"G|look10|{dop}|{g}"] = lk[I10].tolist()
        log(f"  {dop:<8s} g={g:2d}: per-look Pd@10dB " + " ".join(f"{v:.2f}" for v in lk[I10]) + f" | mean looks1-8 {lk[I10, 1:].mean():.2f} | SCR50 look0 {fmt(scr50(lk[:, 0]))}")
for g in (0, 8, 16):
    law = wmean(f"G|law|random|{g}", wkey); OUT[f"G|law10|random|{g}"] = law[I10].tolist()
    log(f"  law (exploratory, AR(1) no noise) random g={g:2d}: " + " ".join(f"{v:.2f}" for v in law[I10]))
for Lr_ in (8, 16):
    for g in (0, 8, 16):
        cum = wmean(f"G|ramp{Lr_}|random|{g}|cum8", wkey); OUT[f"G|ramp{Lr_}|cum8@10|{g}"] = float(cum[I10])
        log(f"  ramp L={Lr_:2d} g={g:2d}: detection within 8 looks @10dB {cum[I10]:.3f}")
l0, l8 = look[("random", 0)][I10], look[("random", 8)][I10]
V["N7"] = l0[4] <= 0.5 * l0[0]
V["N8"] = l8[1:].mean() >= 0.6 and l8[1:].mean() >= 3 * l0[1:].mean()
V["N9"] = 0.8 <= OUT["G|pfa|8|0.01"][0] <= 1.25
OUT["G|onset_cost"] = scr50(look[("random", 8)][:, 0]) - scr50(look[("random", 0)][:, 0])
log(f"  N7: g=0 look0 {l0[0]:.2f}, look4 {l0[4]:.2f}; N8: g=8 mean looks1-8 {l8[1:].mean():.2f} vs g=0 {l0[1:].mean():.2f}; "
    f"N9: g=8 clean Pfa/a {OUT['G|pfa|8|0.01'][0]:.2f}; onset cost {OUT['G|onset_cost']:.1f} dB")

# ------------------------------------------------------------------ Part I (R12)
log("\nPart I (R12 code): injected interference, pooled Pfa / alpha [upper], Pd@10dB, alpha = 0.01")
for p in (0.02, 0.05):
    for j in (10, 30):
        for m in ("D-IN1", "PAMF-H", "P-ANMF", "ANMF-FP", "Clip-OS1", "Clip-OS1-cert", "Bin-OS1-cert"):
            key = f"I|{p}|{j}|{m}|0.01"
            v = np.array([u[key] for u in U]); f = lambda w, v=v: (w * v[:, 0]).sum() / w.sum()
            pf = f(np.ones(len(U))); hi = boot(f)[1]
            OUT[f"I|{p}|{j}|{m}"] = [pf / .01, hi / .01, float(v[:, 1 + I10].mean())]
            log(f"  p={p} {j} dB {m:<14s} Pfa/a {pf / .01:6.2f} [{hi / .01:5.2f}]  Pd@10dB {v[:, 1 + I10].mean():.2f}")
V["N10"] = OUT["I|0.05|30|D-IN1"][0] > 2 and OUT["I|0.05|30|Clip-OS1-cert"][0] <= 1

# ------------------------------------------------------------------ Parts K, X, B (R14)
log("\nParts K/X/B (R14 code): dwell integration, Pfa/alpha [upper], Pd@10dB")
nd = "n_dwell"


def counts_rate(key):
    v = np.array([u[key][0] for u in U]); w0 = np.array([float(u[nd][1]) for u in U])
    f = lambda w: (w * w0 * v).sum() / (w * w0).sum()
    return f(np.ones(len(U))), boot(f)


pdc = lambda key: np.average([u[key][1:] for u in U], axis=0, weights=[u[nd][1] for u in U])
for k in (4, 6, 9, 12, 18):
    for a in (0.01, 0.001):
        r, ci = counts_rate(f"clean|clean|clip{k}|{a}"); OUT[f"K|clean|{k}|{a}"] = [r / a, *(ci / a), float(pdc(f"clean|clean|clip{k}|{a}")[I10])]
        log(f"  clean clip{k:<2d} alpha={a:g}: Pfa/a {r / a:.2f} [{ci[0] / a:.2f}, {ci[1] / a:.2f}]  Pd@10dB {OUT[f'K|clean|{k}|{a}'][3]:.2f}")
for a in (0.01, 0.001):
    r, ci = counts_rate(f"clean|clean|blank|{a}"); OUT[f"X|clean|{a}"] = [r / a, *(ci / a), float(pdc(f"clean|clean|blank|{a}")[I10])]
    log(f"  clean blank alpha={a:g}: Pfa/a {r / a:.2f} [{ci[0] / a:.2f}, {ci[1] / a:.2f}]  Pd@10dB {OUT[f'X|clean|{a}'][3]:.2f}")
conds = [("bern", p, 30) for p in (0.02, 0.05)] + [("bern", p, 10) for p in (0.02, 0.05)] + [("burst", p, 30) for p in (0.02, 0.05)]
for mdl, p, j in conds:
    for a in (0.01, 0.001):
        tag = f"I|{mdl}|{p}|{j}"
        cand = {"clean-thr clip6": f"{tag}|clean|clip6|{a}", "cert(bern) clip6": f"{tag}|cert-bern|clip6|{p}|{a}",
                "cert(bern) clip9": f"{tag}|cert-bern|clip9|{p}|{a}", "cert(burst) clip6": f"{tag}|cert-burst|clip6|{p}|{a}",
                "blank(bern masks)": f"{tag}|mask-bern|blank|{p}|{a}"}
        for name, key in cand.items():
            if key not in U[0]: continue
            r, ci = counts_rate(key); pc = pdc(key)
            OUT[f"{mdl}|{p}|{j}|{a}|{name}"] = dict(pfa=r / a, hi=ci[1] / a, pd10=float(pc[I10]))
            log(f"  {mdl:<5s} p={p:<4g} {j} dB a={a:<6g} {name:<18s} Pfa/a {r / a:6.2f} [{ci[1] / a:5.2f}]  Pd@10dB {pc[I10]:.2f}")
gk = lambda mdl, p, j, a, n: OUT[f"{mdl}|{p}|{j}|{a}|{n}"]
V["N11"] = gk("bern", 0.05, 30, 0.01, "cert(bern) clip9")["pd10"] >= 0.5
V["N12"] = all(gk("bern", p, 30, 0.01, "blank(bern masks)")["pfa"] <= 1.25 for p in (0.02, 0.05)) and gk("burst", 0.05, 30, 0.01, "blank(bern masks)")["pfa"] > 1.25
V["N13"] = gk("burst", 0.05, 30, 0.01, "cert(bern) clip6")["pfa"] > 1

# ------------------------------------------------------------------ Part W
log("\nPart W: real interference (hit rule: >10% of range bins above 10x the bin median)")
elig = np.array([bool(u["W|eligible"]) for u in U])
nrec = len({t for t, e in zip(TAGS, elig) if e})
log(f"  recordings with >= 0.5% hit pulses: {nrec} of {len(recs)}")
OUT["W|eligible_recordings"] = nrec
if nrec >= 1:
    for a in (0.01, 0.001):
        for nm in ("D-IN1|clean", "clip6|clean", "clip9|clean", "clip6|cert", "clip9|cert", "blank|mask"):
            row = []
            for s in ("all", "s0", "s12", "s3"):
                key = f"W|{nm}|{a}|{s}"
                v = np.array([u[key][0] if key in u else np.nan for u in U]); n = np.array([u["W|n"][2 + ("s0", "s12", "s3", "all").index(s)] if "W|n" in u else 0 for u in U], float)
                ok = elig & np.isfinite(v) & (n > 0)
                f = lambda w, v=v, n=n, ok=ok: np.sum((w * v * n)[ok]) / max(np.sum((w * n)[ok]), 1e-300)
                pf = f(np.ones(len(U))); hi = boot(f)[1]
                pd = np.array([u[key][1 + I10] if key in u else np.nan for u in U])
                pd10 = np.sum((pd * n)[ok]) / max(n[ok].sum(), 1e-300)
                OUT[f"W|{nm}|{a}|{s}"] = [pf / a, hi / a, pd10, float(n[ok].sum())]
                row.append(f"{s} {pf / a:6.2f} [{hi / a:5.2f}] Pd10 {pd10:.2f}")
            log(f"  a={a:<6g} {nm:<12s} " + " | ".join(row))
if nrec >= 4:
    V["W1"] = OUT["W|clip6|cert|0.01|all"][0] <= 1.2
    V["W2"] = OUT["W|D-IN1|clean|0.01|s12"][0] > 1.5 or OUT["W|D-IN1|clean|0.01|s3"][0] > 1.5
else:
    log("  fewer than 4 recordings qualify: Part W descriptive only (W1, W2 not evaluated)")

log("\nVerdicts (frozen expectations): " + ", ".join(f"{k} {'met' if v else 'NOT met'}" for k, v in V.items()))
log(f"met {sum(bool(v) for v in V.values())} of {len(V)}")
OUT["verdicts"] = {k: bool(v) for k, v in V.items()}
json.dump(OUT, open(os.path.join(HERE, "r15_summary.json"), "w"), indent=1,
          default=lambda x: None if (isinstance(x, float) and not np.isfinite(x)) else (float(x) if np.isscalar(x) else str(x)))
open(os.path.join(HERE, "r15_summary.txt"), "w", encoding="utf8").write("\n".join(TXT) + "\n")
