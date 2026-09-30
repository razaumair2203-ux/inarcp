"""R12 Part J analysis (PROTOCOL_R12.md): pooled Pfa and SCR for Pd = 0.5 per run, mitigation and detector; J1-J3.
Usage: python analyze_r12_jku.py -> r12_jku_summary.txt / .json"""
import os, glob, json
import numpy as np
HERE = os.path.dirname(os.path.abspath(__file__)); ROOT = os.path.dirname(HERE)
RES = os.path.join(ROOT, "study", "results", "r12")
OUT, SUM = [], {}
A = 0.01


def log(s=""):
    print(s); OUT.append(s)


def scr_at(scr, pd, level=.5):
    pd = np.maximum.accumulate(np.asarray(pd, float))
    if not np.isfinite(pd).all() or pd[-1] < level: return np.nan
    return float(scr[0]) if pd[0] >= level else float(np.interp(level, pd, scr))


U = [dict(np.load(f, allow_pickle=True)) for f in sorted(glob.glob(os.path.join(RES, "j_st*_rx*.npz")))]
scr = U[0]["scr_db"]; dets = [str(d) for d in U[0]["detectors"]]; mits = [str(m) for m in U[0]["mitigations"]]
strata = [str(s) for s in U[0]["strata"]]
log(f"R12 Part J: {len(U)} (station, rx) units; hit rate (test frames): " +
    ", ".join(f"{k} {np.mean([u[f'hitrate_test|{k}'] for u in U]):.3f}" for k in ("ref", "A", "C")))
log("zeroed fraction (test frames): " + ", ".join(f"{k} {np.mean([u[f'zeroed_test|{k}'] for u in U]):.3f}" for k in ("ref", "A", "C")))
R = {}
for k in ("ref", "A", "C"):
    for m in mits:
        log(f"\nrun {k}, mitigation {m}:  Pfa/alpha (all | by hit stratum {strata[:-1]}) ; SCR50 all [hit-free stratum]")
        for d in dets:
            n = {s: np.array([u[f"n|{m}|{k}|{s}"] for u in U], float) for s in strata}
            pf = {s: np.nansum([u[f"pfa|{m}|{k}|{d}|{s}"] * u[f"n|{m}|{k}|{s}"] for u in U]) / max(n[s].sum(), 1) for s in strata}
            pd = {s: np.nansum([np.nan_to_num(u[f"pd|{m}|{k}|{d}|{s}"]) * u[f"n|{m}|{k}|{s}"] for u in U], 0) / max(n[s].sum(), 1) for s in strata}
            R[(k, m, d)] = dict(pfa={s: float(v) for s, v in pf.items()}, n={s: int(n[s].sum()) for s in strata},
                                scr50={s: scr_at(scr, pd[s]) for s in strata})
            log(f"  {d:<14s} {pf['all'] / A:6.2f} | " + " ".join(f"{pf[s] / A:6.2f}" for s in strata[:-1]) +
                f" ; SCR50 {R[(k, m, d)]['scr50']['all']:6.2f} [{R[(k, m, d)]['scr50']['s0']:6.2f}]")
j1 = all(R[("C", m, "Clip-OS1-cert")]["pfa"]["all"] <= 1.2 * A for m in ("N", "Z"))
j2 = all(R[(k, "N", "D-IN1")]["pfa"]["all"] >= 5 * A for k in ("A", "C"))
j3v = R[("A", "Z", "IN1")]["scr50"]["all"] - R[("A", "ZAR", "IN1")]["scr50"]["all"]
j3 = j3v >= 1
log(f"\nJ1 (Clip-OS1-cert Pfa <= 1.2 alpha in run C under N and Z): {j1}  "
    f"[N {R[('C', 'N', 'Clip-OS1-cert')]['pfa']['all']:.4f}, Z {R[('C', 'Z', 'Clip-OS1-cert')]['pfa']['all']:.4f}]")
log(f"J2 (D-IN1 under N Pfa >= 5 alpha in runs A and C): {j2}  "
    f"[A {R[('A', 'N', 'D-IN1')]['pfa']['all']:.4f}, C {R[('C', 'N', 'D-IN1')]['pfa']['all']:.4f}]")
log(f"J3 (ZAR improves IN1 SCR50 over Z by >= 1 dB in run A): {j3}  [{j3v:.2f} dB]")
SUM["R"] = {"|".join(k): v for k, v in R.items()}; SUM["verdicts"] = dict(J1=bool(j1), J2=bool(j2), J3=bool(j3))
open(os.path.join(HERE, "r12_jku_summary.txt"), "w", encoding="utf-8").write("\n".join(OUT) + "\n")
json.dump(SUM, open(os.path.join(HERE, "r12_jku_summary.json"), "w"), indent=1)
