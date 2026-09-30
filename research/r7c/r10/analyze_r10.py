"""Endpoints of PROTOCOL_R10.md from study/results/r10/x_*.npz -> r10/r10_summary.txt/.json.
Day-cluster bootstrap 10,000 resamples (seed 20260930) and leave-one-day-out (LODO) range."""
import os, glob, json
import numpy as np
HERE = os.path.dirname(os.path.abspath(__file__)); RES = os.path.join(os.path.dirname(HERE), "study", "results", "r10")
D = [np.load(p) for p in sorted(glob.glob(os.path.join(RES, "x_*.npz")))]
days = np.array([str(d["day"]) for d in D]); ud = sorted(set(days)); scr = D[0]["scr_db"]; I10 = int(np.argmin(abs(scr - 10)))
rng = np.random.default_rng(20260930); lines, out = [], {}
log = lambda s="": (print(s), lines.append(s))
KS = (1, 2, 4, 8)


def scr_at(pd, level):
    pd = np.maximum.accumulate(pd)
    if pd[0] >= level: return scr[0]
    if pd[-1] < level: return np.nan
    i = np.argmax(pd >= level); x0, x1, y0, y1 = scr[i - 1], scr[i], pd[i - 1], pd[i]
    return x0 + (level - y0) * (x1 - x0) / (y1 - y0) if y1 > y0 else x1


def boot(v):
    v = np.asarray(v, float); by = {u: v[days == u] for u in ud}; est = np.nanmean(v); bs = []
    for _ in range(10000):
        bs.append(np.nanmean(np.concatenate([by[u] for u in rng.choice(ud, len(ud))])))
    loo = [np.nanmean(v[days != u]) for u in ud]
    return [float(est), *map(float, np.nanpercentile(bs, [2.5, 97.5])), float(min(loo)), float(max(loo))]


fmt = lambda b: f"{b[0]:6.2f} [{b[1]:6.2f},{b[2]:6.2f}] LODO {b[3]:5.2f}..{b[4]:5.2f}"
log(f"units {len(D)}; days {len(ud)}; test segments {sum(int(d['n']) for d in D)}")

# ---------------- Part C
log("\n=== Part C: dwell detectors at equal dwell Pfa (alpha = 0.01 unless stated) ===")
DW = ("IN1sum", "NA4sum", "CAlocsum", "PAMFH", "NPAMF", "MTDhann", "MTDrect")
for a in (0.01, 0.001):
    log(f"-- measured dwell Pfa on clean test segments, alpha = {a} (K' = 1 2 4 8) --")
    for d_ in DW:
        v = [np.mean([d[f"C|{d_}|K{k}|{a}|pfa"] for d in D]) if f"C|{d_}|K{k}|{a}|pfa" in D[0].files else np.nan for k in KS]
        log(f"   {d_:9s} " + " ".join(f"{x:.4f}" for x in v))
for dop in ("random", "matched", "opposite"):
    for a in ((0.01, 0.001) if dop == "random" else (0.01,)):
        log(f"-- SCR (dB) for dwell Pd = 0.5 / 0.9, Doppler {dop}, alpha {a}; mean over units --")
        for d_ in DW:
            row = []
            for k in KS:
                key = f"C|{d_}|K{k}|{a}|{dop}|pd"
                if key not in D[0].files: row.append("   -    "); continue
                s5 = np.nanmean([scr_at(d[key], .5) for d in D]); s9 = np.nanmean([scr_at(d[key], .9) for d in D])
                out[f"C|scr|{d_}|K{k}|{a}|{dop}"] = [float(s5), float(s9)]; row.append(f"{s5:5.1f}/{s9:5.1f}")
            log(f"   {d_:9s} " + "  ".join(row))
log("-- gains (dB, positive = first detector needs less SCR) at Pd = 0.5, random Doppler, alpha 0.01; 95% day bootstrap --")
pairs = [("IN1sum", "PAMFH"), ("NA4sum", "PAMFH"), ("IN1sum", "MTDhann"), ("NA4sum", "MTDhann"), ("PAMFH", "MTDhann"),
         ("IN1sum", "CAlocsum"), ("PAMFH", "CAlocsum"), ("MTDhann", "CAlocsum"), ("PAMFH", "NPAMF")]
for k in KS:
    for x, y in pairs:
        kx, ky = f"C|{x}|K{k}|0.01|random|pd", f"C|{y}|K{k}|0.01|random|pd"
        if kx not in D[0].files or ky not in D[0].files: continue
        for lvl in (0.5, 0.9):
            g = boot([scr_at(d[ky], lvl) - scr_at(d[kx], lvl) for d in D]); out[f"C|gain|{x}-{y}|K{k}|{lvl}"] = g
            log(f"   K'={k} Pd={lvl} {x:8s} vs {y:8s}: {fmt(g)}")
# C1
diff = max(np.max(abs(np.mean([d[f"C|PAMFH|K1|0.01|random|pd"] for d in D], 0) - np.mean([d[f"R|in|L1|IN4|look"][:, 0] for d in D], 0))), 0)
log(f"\nC1 check: max |Pd(PAMF-H, K'=1) - Pd(IN4 look 0)| over SCR = {diff:.4f}  (expectation < 0.005)")
c2 = out["C|gain|IN1sum-PAMFH|K8|0.5"]; log(f"C2: PAMF-H needs {-c2[0]:.2f} dB less SCR than IN1-sum at K'=8 (expectation >= 3 dB): {'OK' if -c2[0] >= 3 else 'FAILED'}")
c3 = out["C|gain|MTDhann-CAlocsum|K8|0.5"]; log(f"C3: MTD-CA needs {c3[0]:.2f} dB less SCR than CAloc-sum at K'=8 (expectation >= 5 dB): {'OK' if c3[0] >= 5 else 'FAILED'}")
c4 = out["C|scr|PAMFH|K8|0.01|matched"][0] - out["C|scr|PAMFH|K8|0.01|random"][0]
log(f"C4: PAMF-H matched-Doppler SCR is {c4:.2f} dB worse than random (expectation >= 3 dB): {'OK' if c4 >= 3 else 'FAILED'}")
out["C1"] = float(diff); out["C4"] = float(c4)

# ---------------- Part R
log("\n=== Part R: gradual emergence (random Doppler, alpha 0.01) ===")
LOOKM = ("IN1", "IN4", "NA4", "CA16", "CAloc")
for place in ("pre", "in"):
    log(f"-- placement {place}: per-look Pd at SCR 10 dB (looks 0..7), mean over units --")
    for L in (1, 4, 8, 16):
        for m in ("IN1", "NA4", "CAloc"):
            v = np.mean([d[f"R|{place}|L{L}|{m}|look"][I10] for d in D], 0)
            log(f"   L={L:2d} {m:6s} " + " ".join(f"{x:.3f}" for x in v))
    log(f"-- placement {place}: SCR for Pd 0.5 (single look 0 | any of 8 looks) and first-detection look at 10 dB --")
    for L in (1, 4, 8, 16):
        for m in LOOKM:
            s1 = np.nanmean([scr_at(d[f"R|{place}|L{L}|{m}|look"][:, 0], .5) for d in D])
            s8 = np.nanmean([scr_at(d[f"R|{place}|L{L}|{m}|cum"], .5) for d in D])
            fd = np.nanmean([float(d[f"R|{place}|L{L}|{m}|first10"]) for d in D])
            out[f"R|{place}|L{L}|{m}"] = [float(s1), float(s8), float(fd)]
            log(f"   L={L:2d} {m:6s} look0 {s1:5.1f} | cum8 {s8:5.1f} | first look {fd:4.2f}")
    log(f"-- placement {place}: SCR for dwell Pd 0.5 at K=8 (dwell detectors) --")
    for L in (1, 4, 8, 16):
        log(f"   L={L:2d} " + " ".join(f"{d_} {np.nanmean([scr_at(d[f'R|{place}|L{L}|{d_}|dwell'], .5) for d in D]):5.1f}" for d_ in DW))
g = [boot([scr_at(d[f"R|pre|L{L}|CAloc|look"][:, 0], .5) - scr_at(d[f"R|pre|L{L}|IN1|look"][:, 0], .5) for d in D]) for L in (1, 4, 8, 16)]
for L, x in zip((1, 4, 8, 16), g): out[f"R|gain_look0|pre|L{L}"] = x; log(f"   R-pre single-look gain IN1 vs CAloc, L={L:2d}: {fmt(x)}")
mono = all(g[i][0] > g[i + 1][0] for i in range(3))
log(f"R1: gain decreasing in L: {mono}; below 5 dB at L=16: {g[3][0] < 5} -> {'OK' if mono and g[3][0] < 5 else 'FAILED'}")
fl = [out[f"R|in|L{L}|IN1"][2] for L in (1, 4, 8, 16)]
log(f"R3: IN1 first-detection look (R-in) by L: {np.round(fl, 2).tolist()} -> {'OK' if all(fl[i] < fl[i + 1] for i in range(3)) else 'FAILED'}")

# ---------------- Part A
log("\n=== Part A: ACI with target-contaminated feedback (IN1, alpha 0.01) ===")
for pi in (0.0, 0.01, 0.05):
    row = []
    for arm in ("split", "naive0.005", "gated0.005", "naive0.02", "gated0.02"):
        pf = np.mean([float(d[f"A|{pi}|{arm}|pfa"]) for d in D]); pd = np.nanmean([float(d[f"A|{pi}|{arm}|pd"]) for d in D])
        out[f"A|{pi}|{arm}"] = [float(pf), float(pd)]; row.append(f"{arm} Pfa/a {pf / 0.01:4.2f} Pd {pd:5.3f}")
    log(f"   pi={pi:<5g} " + " | ".join(row))
a1 = out["A|0.05|naive0.02"]; a2 = out["A|0.05|gated0.02"]; sp = out["A|0.05|split"]
log(f"A1 (gamma 0.02): naive clean Pfa/alpha {a1[0] / .01:.2f} (< 0.8?) and Pd {a1[1]:.3f} vs split {sp[1]:.3f} -> {'OK' if a1[0] < .008 and a1[1] < sp[1] else 'FAILED'}")
log(f"A2 (gamma 0.02): gated clean Pfa/alpha {a2[0] / .01:.2f} within [0.8, 1.2]? -> {'OK' if .008 <= a2[0] <= .012 else 'FAILED'}")
json.dump(out, open(os.path.join(HERE, "r10_summary.json"), "w"), indent=1)
open(os.path.join(HERE, "r10_summary.txt"), "w").write("\n".join(lines) + "\n")
