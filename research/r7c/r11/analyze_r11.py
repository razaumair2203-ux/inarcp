"""Endpoints of PROTOCOL_R11.md -> r11/r11_summary.txt/.json. Part O: day-cluster bootstrap (10,000; seed 20260930) and
LODO range. Part J: pooled over the 8 station x Rx units, 95% bootstrap over units."""
import os, glob, json
import numpy as np
HERE = os.path.dirname(os.path.abspath(__file__)); RES = os.path.join(os.path.dirname(HERE), "study", "results", "r11")
rng = np.random.default_rng(20260930); lines, out = [], {}
log = lambda s="": (print(s), lines.append(s))


def scr_at(scr, pd, level):
    pd = np.maximum.accumulate(np.nan_to_num(pd))
    if pd[0] >= level: return scr[0]
    if pd[-1] < level: return np.nan
    i = np.argmax(pd >= level); x0, x1, y0, y1 = scr[i - 1], scr[i], pd[i - 1], pd[i]
    return x0 + (level - y0) * (x1 - x0) / (y1 - y0) if y1 > y0 else x1


# ---------------- Part O
O = [np.load(p) for p in sorted(glob.glob(os.path.join(RES, "o_*.npz")))]
days = np.array([str(d["day"]) for d in O]); ud = sorted(set(days)); scr = O[0]["scr_db"]; I10 = int(np.argmin(abs(scr - 10)))


def boot(v):
    v = np.asarray(v, float); by = {u: v[days == u] for u in ud}; bs = [np.nanmean(np.concatenate([by[u] for u in rng.choice(ud, len(ud))])) for _ in range(10000)]
    loo = [np.nanmean(v[days != u]) for u in ud]
    return [float(np.nanmean(v)), *map(float, np.nanpercentile(bs, [2.5, 97.5])), float(min(loo)), float(max(loo))]


fmt = lambda b: f"{b[0]:6.2f} [{b[1]:6.2f},{b[2]:6.2f}] LODO {b[3]:5.2f}..{b[4]:5.2f}"
LOOK = ("IN1", "OS1_8", "OS1_12", "IN4", "OS4", "NA4", "CAloc"); DW = ("IN1sum", "OS1_8sum", "PAMFH", "PAMFOS", "CAlocsum")
log(f"=== Part O: IPIX, {len(O)} units, {sum(int(d['n']) for d in O)} test segments ===")
log("-- O1: look-0 Pfa (alpha 0.01) and texture-quintile Pfa/alpha (low -> high), spread --")
for m in LOOK:
    q = np.mean([d[f"L|{m}|0.01|qpfa"] for d in O], 0) / 0.01; pf = np.mean([d[f"L|{m}|0.01|pfa"] for d in O])
    out[f"O1|{m}"] = dict(pfa=float(pf), q=q.tolist(), spread=float(q.max() / q.min()))
    log(f"   {m:7s} Pfa {pf:.4f} | " + " ".join(f"{x:4.2f}" for x in q) + f" | spread {q.max() / q.min():.2f}")
log("-- dwell Pfa at K=8 (design 0.01): " + " ".join(f"{d_} {np.mean([d[f'D|{d_}|K8|pfa'] for d in O]):.4f}" for d_ in DW))
log("-- O2: abrupt target (L=1, look 0) SCR for Pd 0.5; difference vs IN1 --")
s1 = {m: np.array([scr_at(scr, d[f"R|in|L1|{m}|look"][:, 0], .5) for d in O]) for m in LOOK}
for m in LOOK:
    b = boot(s1[m] - s1["IN1"]); out[f"O2|{m}"] = [float(np.nanmean(s1[m])), *b]
    log(f"   {m:7s} SCR {np.nanmean(s1[m]):5.2f} dB | minus IN1 {fmt(b)}")
log("-- O3: persistent target (L=1), per-look Pd at SCR 10 dB, looks 0..7 --")
for m in LOOK:
    v = np.mean([d[f"R|in|L1|{m}|look"][I10] for d in O], 0); out[f"O3|{m}"] = v.tolist()
    log(f"   {m:7s} " + " ".join(f"{x:.3f}" for x in v))
log("-- O4: ramps; first-look SCR for Pd .5 | SCR for Pd .5 within 8 looks | dwell SCR (K=8) --")
for place in ("pre", "in"):
    for L in (1, 4, 8, 16):
        row = []
        for m in ("IN1", "OS1_8", "OS1_12", "OS4", "NA4", "CAloc"):
            a = np.nanmean([scr_at(scr, d[f"R|{place}|L{L}|{m}|look"][:, 0], .5) for d in O])
            c = np.nanmean([scr_at(scr, d[f"R|{place}|L{L}|{m}|cum"], .5) for d in O])
            out[f"O4|{place}|L{L}|{m}"] = [float(a), float(c)]; row.append(f"{m} {a:5.1f}|{c:5.1f}")
        log(f"   {place} L={L:2d}: " + "  ".join(row))
        row = []
        for d_ in DW:
            v = np.nanmean([scr_at(scr, d[f"R|{place}|L{L}|{d_}|dwell"], .5) for d in O]); v9 = np.nanmean([scr_at(scr, d[f"R|{place}|L{L}|{d_}|dwell"], .9) for d in O])
            out[f"O4dw|{place}|L{L}|{d_}"] = [float(v), float(v9)]; row.append(f"{d_} {v:5.1f}/{v9:5.1f}")
        log(f"        dwell Pd.5/.9: " + "  ".join(row))
g_in = boot([scr_at(scr, d["R|pre|L8|IN1|look"][:, 0], .5) - scr_at(scr, d["R|pre|L8|OS1_8|look"][:, 0], .5) for d in O])
log(f"   R-pre L=8 first-look SCR, IN1 minus OS1_8: {fmt(g_in)}")
out["O4gain"] = g_in
gap = lambda a, b, lvl: boot([scr_at(scr, d[f"R|in|L1|{a}|dwell"], lvl) - scr_at(scr, d[f"R|in|L1|{b}|dwell"], lvl) for d in O])
for lvl in (0.5, 0.9):
    for a, b in (("IN1sum", "PAMFH"), ("OS1_8sum", "PAMFH"), ("PAMFOS", "PAMFH"), ("OS1_8sum", "IN1sum")):
        x = gap(a, b, lvl); out[f"O5|{a}-{b}|{lvl}"] = x
        log(f"   dwell K=8 Pd={lvl}: SCR({a}) - SCR({b}) = {fmt(x)}")
log("-- O7: OS exact law vs measured coverage (MAE per unit) --")
for m in ("OS1_8", "OS1_12", "OS4"):
    for a in (0.1, 0.01):
        v = np.array([d[f"law|{m}|{a}"] for d in O]); mae = float(np.mean(abs(v[:, 0] - v[:, 1])))
        out[f"O7|{m}|{a}"] = [mae, float(v[:, 0].mean()), float(v[:, 1].mean())]
        log(f"   {m:7s} 1-a={1 - a:g}: law {v[:, 0].mean():.4f} measured {v[:, 1].mean():.4f} MAE {mae:.4f}")
# verdicts
o1 = out["O1|OS1_8"]["spread"]; o2 = out["O2|OS1_8"][1]; o3 = out["O3|OS1_8"][4]; o4 = g_in[0]
o5 = (out["O5|IN1sum-PAMFH|0.9"][0] - out["O5|OS1_8sum-PAMFH|0.9"][0]) / out["O5|IN1sum-PAMFH|0.9"][0] if out["O5|IN1sum-PAMFH|0.9"][0] > 0 else np.nan
o6 = out["O5|PAMFOS-PAMFH|0.5"][0]; o7 = out["O7|OS1_8|0.1"][0]
log("\nVERDICTS Part O")
log(f"O1 spread {o1:.2f} <= 2.0: {'OK' if o1 <= 2 else 'FAILED'}")
log(f"O2 OS1_8 - IN1 = {o2:.2f} dB in [0, 1.5]: {'OK' if 0 <= o2 <= 1.5 else 'FAILED'}")
log(f"O3 OS1_8 look-4 Pd {o3:.3f} >= 0.5: {'OK' if o3 >= .5 else 'FAILED'}")
log(f"O4 R-pre L=8 IN1 - OS1_8 first-look SCR = {o4:.2f} dB >= 3: {'OK' if o4 >= 3 else 'FAILED'}")
log(f"O5 fraction of IN1sum's Pd.9 gap to PAMF-H closed by OS1_8sum = {o5:.2f} >= 0.5: {'OK' if o5 >= .5 else 'FAILED'}")
log(f"O6 PAMF-OS - PAMF-H at Pd .5 = {o6:.2f} dB within 1: {'OK' if abs(o6) <= 1 else 'FAILED'}")
log(f"O7 OS1_8 law MAE at 0.90 = {o7:.4f} <= 0.015: {'OK' if o7 <= .015 else 'FAILED'}")

# ---------------- Part J
J = [np.load(p) for p in sorted(glob.glob(os.path.join(RES, "j_st*_rx*.npz")))]
if J:
    sj = J[0]["scr_db"]; METH = ("IN1", "OS1_8", "CA16", "OS16_8"); STR = ("0", "1-2", "3-5", ">=6")
    jb = lambda v: [float(np.nanmean(v)), *map(float, np.nanpercentile([np.nanmean(rng.choice(v, len(v))) for _ in range(10000)], [2.5, 97.5]))]
    log(f"\n=== Part J: JKU, {len(J)} station x Rx units ===")
    for run in ("ref", "A", "C"):
        log(f"-- run {run}: chirp hit rate {np.mean([d[f'hitrate|{run}'] for d in J]):.3f}; zeroed fraction N/Z {np.mean([d[f'zeroed|N|{run}'] for d in J]):.4f}/{np.mean([d[f'zeroed|Z|{run}'] for d in J]):.4f}")
        for tag in ("N", "Z"):
            ns = [int(sum(d[f"n|{tag}|{run}|s{s}"] for d in J)) for s in range(4)]; ny = int(sum(d[f"n|{tag}|{run}|yhit"] for d in J))
            log(f"   [{tag}] episodes non-hit Y by history hits {dict(zip(STR, ns))}; hit-Y {ny}")
            for m in METH:
                pf = [np.nanmean([d[f"pfa|{tag}|{run}|{m}|s{s}"] for d in J]) for s in range(4)]; py = np.nanmean([d[f"pfa|{tag}|{run}|{m}|yhit"] for d in J])
                pd10 = [np.nanmean([d[f"pd|{tag}|{run}|{m}|s{s}"][int(np.argmin(abs(sj - 10)))] for d in J]) for s in range(4)]
                s50 = [np.nanmean([scr_at(sj, d[f"pd|{tag}|{run}|{m}|s{s}"], .5) for d in J]) for s in range(4)]
                out[f"J|{tag}|{run}|{m}"] = dict(pfa=pf, pfa_yhit=float(py), pd10=pd10, scr50=s50, n=ns, n_yhit=ny)
                log(f"   [{tag}] {m:6s} Pfa by stratum " + " ".join(f"{x:.4f}" for x in pf) + f" | Y-hit {py:.4f} | Pd@10 " + " ".join(f"{x:.3f}" for x in pd10)
                    + " | SCR50 " + " ".join(f"{x:5.1f}" for x in s50))
    ref = lambda tag, m: out[f"J|{tag}|ref|{m}"]["pd10"][0]
    dropIN = ref("N", "IN1") - out["J|N|A|IN1"]["pd10"][3]; dropOS = ref("N", "OS1_8") - out["J|N|A|OS1_8"]["pd10"][3]
    log("\nVERDICTS Part J")
    log(f"J1 run A >=6-hit stratum Pd@10 drop vs ref: IN1 {dropIN:.3f} (>=0.2?), OS1_8 {dropOS:.3f} (<= half?) -> {'OK' if dropIN >= .2 and dropOS <= dropIN / 2 else 'FAILED'}  [n>=6 stratum: {out['J|N|A|IN1']['n'][3]}]")
    for run in ("A", "C"):
        n_, z_ = out[f"J|N|{run}|IN1"]["pfa_yhit"], out[f"J|Z|{run}|IN1"]["pfa_yhit"]
        log(f"J2 run {run}: IN1 hit-Y Pfa N {n_:.4f} -> Z {z_:.4f}; reduction {1 - z_ / n_ if n_ > 0 else np.nan:.2f} (>=0.5?) -> {'OK' if n_ > 0 and z_ <= n_ / 2 else 'FAILED'}")
    # J3: overall SCR50 on non-hit Y in run A, pooled over strata (episode-weighted)
    def overall(tag, run, m):
        vals = []
        for d in J:
            w = np.array([d[f"n|{tag}|{run}|s{s}"] for s in range(4)], float); P = np.array([np.nan_to_num(d[f"pd|{tag}|{run}|{m}|s{s}"]) for s in range(4)])
            vals.append(scr_at(sj, (w[:, None] * P).sum(0) / w.sum(), .5))
        return np.array(vals)
    zo, zi = overall("Z", "A", "OS1_8"), overall("Z", "A", "IN1"); dd = jb(zo - zi); out["J3"] = dd
    log(f"J3 run A overall SCR50: Z+OS1_8 - Z+IN1 = {dd[0]:.2f} [{dd[1]:.2f},{dd[2]:.2f}] dB (<= +0.5?) -> {'OK' if dd[0] <= .5 else 'FAILED'}")
    for tag in ("N", "Z"):
        for run in ("ref", "A", "C"):
            for m in ("IN1", "OS1_8", "CA16", "OS16_8"): out[f"Jall|{tag}|{run}|{m}"] = float(np.nanmean(overall(tag, run, m)))
    log("   overall SCR50 (non-hit Y, all strata): " + " | ".join(f"{tag}-{run}: " + " ".join(f"{m} {out[f'Jall|{tag}|{run}|{m}']:.1f}" for m in METH) for tag in ("N", "Z") for run in ("ref", "A", "C")))
    j4 = out["J|N|ref|CA16"]["scr50"][0] - out["J|N|ref|IN1"]["scr50"][0]
    log(f"J4 ref: CA16 - IN1 SCR50 = {j4:.2f} dB (>0?) -> {'OK' if j4 > 0 else 'FAILED'}")
json.dump(out, open(os.path.join(HERE, "r11_summary.json"), "w"), indent=1)
open(os.path.join(HERE, "r11_summary.txt"), "w").write("\n".join(lines) + "\n")
