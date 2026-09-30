"""R12 analysis of the IPIX parts L, A, T, I (PROTOCOL_R12.md): pooled rates, day-cluster bootstrap intervals and the
verdict of every frozen expectation. Usage: python analyze_r12.py -> r12_summary.txt, r12_summary.json"""
import os, sys, glob, json
import numpy as np
HERE = os.path.dirname(os.path.abspath(__file__)); ROOT = os.path.dirname(HERE)
RES = os.path.join(ROOT, "study", "results", "r12")
NB = 10000
OUT, SUM = [], {}


def log(s=""):
    print(s); OUT.append(s)


def load_units():
    U = []
    for f in sorted(glob.glob(os.path.join(RES, "i_*_rot*.npz"))):
        d = np.load(f, allow_pickle=True); U.append({k: d[k] for k in d.files})
    return U


def boot_days(U, stat, rng):
    """Day-cluster bootstrap of a statistic computed from a list of units."""
    days = np.array([str(u["day"]) for u in U]); ud = np.unique(days)
    idx = {d: np.where(days == d)[0] for d in ud}
    vals = []
    for _ in range(NB):
        pick = rng.choice(ud, len(ud))
        vals.append(stat([U[i] for d in pick for i in idx[d]]))
    return np.nanpercentile(vals, [2.5, 97.5])


def pooled_L(U, key):
    a = np.sum([u[key] for u in U], 0)
    return a[0] / a[1], a[2:7] / np.maximum(a[7:12], 1)


def scr_at(scr, pd, level):
    pd = np.maximum.accumulate(np.asarray(pd, float))
    if pd[-1] < level: return np.nan
    if pd[0] >= level: return scr[0]
    return float(np.interp(level, pd, scr))


def main():
    U = load_units(); rng = np.random.default_rng(12)
    log(f"R12 IPIX analysis: {len(U)} units"); SUM["units"] = len(U)
    scr = U[0]["scr_db"]

    # ------------------------------------------------ Part L
    log("\nPart L: pooled Pfa / alpha [95% day-cluster interval]; texture-quintile spread (max/min)")
    mets = sorted({k.split("|")[1] for k in U[0] if k.startswith("L|") and k.count("|") == 3})
    L = {}
    for a in (1e-2, 1e-3, 1e-4):
        log(f"  alpha = {a:g}")
        for m in mets:
            for rule in ("conf", "anal", "boot"):
                key = f"L|{m}|{rule}|{a}"
                if key not in U[0]: continue
                p, qp = pooled_L(U, key)
                ci = boot_days(U, lambda V: pooled_L(V, key)[0], rng) / a if NB else (np.nan, np.nan)
                spread = qp.max() / max(qp.min(), 1e-12)
                L[(m, rule, a)] = (p / a, ci, spread)
                log(f"    {m:<12s} {rule:<5s} {p / a:7.2f} [{ci[0]:.2f}, {ci[1]:.2f}]  spread {spread:6.1f}")
    SUM["L"] = {f"{m}|{r}|{a}": [v[0], list(v[1]), v[2]] for (m, r, a), v in L.items()}
    conf = [(m, a, L[(m, "conf", a)][0]) for (m, r, a) in L if r == "conf"]
    l1 = all((0.8 <= v <= 1.25) if a > 5e-4 else (0.6 <= v <= 1.6) for m, a, v in conf)
    white = ("IN1", "IN4", "OS1_8", "NA4", "D-IN4", "PAMF-H(w)", "P-ANMF(bin)", "P-ANMF", "Clip-OS1")
    l2n = [m for m in white if (m, "anal", 1e-4) in L and L[(m, "anal", 1e-4)][0] > 2]
    l3 = (L[("ANMF-SCM(w)", "anal", 1e-3)][0] > 1.5) and (0.5 <= L[("ANMF-FP(w)", "anal", 1e-3)][0] <= 2)
    l4 = all(L[(m, "anal", 1e-3)][0] > 3 or L[(m, "anal", 1e-3)][0] < 1 / 3 for m in ("CA16", "OSraw"))
    l5 = L[("IN1", "boot", 1e-4)][0] > 1.2
    l6 = L[("IN1", "conf", 1e-3)][2] <= 3
    V = {"L1": l1, "L2": len(l2n) >= 3, "L3": l3, "L4": l4, "L5": l5, "L6": l6}
    log(f"  L1 conformal within band: {l1}; offenders: {[ (m, a, round(v, 2)) for m, a, v in conf if not ((0.8 <= v <= 1.25) if a > 5e-4 else (0.6 <= v <= 1.6))]}")
    log(f"  L2 analytic whitened rules > 2x at 1e-4: {l2n}")
    log(f"  L3 {l3}; L4 {l4}; L5 {l5}; L6 {l6}")

    # ------------------------------------------------ Part A
    log("\nPart A: SCR (dB) for Pd = 0.5 / 0.9 from pooled curves (alpha = 0.01 and 0.001), measured Pfa")
    dets = sorted({k.split("|")[1] for k in U[0] if k.startswith("A|") and k.endswith("|pd")})
    A = {}
    for a in (0.01, 0.001):
        for m in dets:
            pd = np.mean([u[f"A|{m}|{a}|pd"] for u in U], 0); pfa = np.mean([u[f"A|{m}|{a}|pfa"] for u in U])
            A[(m, a)] = (scr_at(scr, pd, .5), scr_at(scr, pd, .9), pfa)
            log(f"  {a:<6} {m:<10s} SCR50 {A[(m, a)][0]:6.2f}  SCR90 {A[(m, a)][1]:6.2f}  Pfa {pfa:.4f}")

    def diff(m1, m2, a=0.01, lev=.5):
        f = lambda V: scr_at(scr, np.mean([u[f"A|{m1}|{a}|pd"] for u in V], 0), lev) - scr_at(scr, np.mean([u[f"A|{m2}|{a}|pd"] for u in V], 0), lev)
        return f(U), boot_days(U, f, rng)
    SUM["A"] = {f"{m}|{a}": list(v) for (m, a), v in A.items()}
    d1 = diff("ANMF-FP", "PAMF-H"); d2 = diff("Clip-OS1", "D-IN1"); d3 = diff("OSraw", "IN1look")
    log(f"  A1 ANMF-FP minus PAMF-H: {d1[0]:.2f} dB [{d1[1][0]:.2f}, {d1[1][1]:.2f}]  (expect >= 1)")
    log(f"  A2 Clip-OS1 minus D-IN1: {d2[0]:.2f} dB [{d2[1][0]:.2f}, {d2[1][1]:.2f}]  (expect <= 1.5)")
    log(f"  A3 OSraw minus IN1 (first look): {d3[0]:.2f} dB [{d3[1][0]:.2f}, {d3[1][1]:.2f}]  (expect >= 5)")
    V.update({"A1": d1[0] >= 1, "A2": d2[0] <= 1.5, "A3": d3[0] >= 5})
    SUM["A_diffs"] = {"ANMF-FP-PAMF-H": [d1[0], list(d1[1])], "Clip-DIN1": [d2[0], list(d2[1])], "OSraw-IN1": [d3[0], list(d3[1])]}

    # ------------------------------------------------ Part T
    log("\nPart T: real target cell. Mean Pd over units (clutter Pfa), alpha = 1e-3 [1e-2]")
    NT = (8, 16, 32, 64, 128, 256, 512, 1024)
    T = {}
    for det, rule in (("P-ANMF", "conf"), ("P-ANMF", "anal"), ("CA-NCI", "conf"), ("ANMF-FP", "conf")):
        for N in NT:
            k3, k2 = f"T|{det}|{rule}|N{N}|0.001", f"T|{det}|{rule}|N{N}|0.01"
            if k3 not in U[0]: continue
            v3 = np.array([u[k3] for u in U]); v2 = np.array([u[k2] for u in U])
            T[(det, rule, N)] = v3
            log(f"  {det:<8s} {rule:<5s} N={N:<5d} Pd {v3[:, 0].mean():.3f} (Pfa {v3[:, 1].mean():.4f})  [Pd {v2[:, 0].mean():.3f}]")
    in1 = np.array([u["T|IN1|conf|look|0.001"][0] for u in U]); clp = np.array([u["T|Clip-OS1|conf|dwell|0.001"][0] for u in U])
    pin = np.array([u["L|IN1|conf|0.001"][0] / u["L|IN1|conf|0.001"][1] for u in U])
    pcl = np.array([u["L|Clip-OS1|conf|0.001"][0] / u["L|Clip-OS1|conf|0.001"][1] for u in U])
    t1 = (np.mean(in1 <= 3 * np.maximum(pin, 1e-3)) >= .8) and (np.mean(clp <= 3 * np.maximum(pcl, 1e-3)) >= .8)
    log(f"  history-normalized on target: IN1 Pd {in1.mean():.4f} (clutter Pfa {pin.mean():.4f}); Clip-OS1 Pd {clp.mean():.4f} (clutter Pfa {pcl.mean():.4f})")
    t2 = np.mean(T[("P-ANMF", "conf", 256)][:, 0] > T[("P-ANMF", "conf", 8)][:, 0]) >= .8
    t3 = np.mean(T[("P-ANMF", "conf", 64)][:, 0] >= T[("CA-NCI", "conf", 64)][:, 0]) >= .6
    log(f"  T1 {t1}; T2 {t2} ({np.mean(T[('P-ANMF', 'conf', 256)][:, 0] > T[('P-ANMF', 'conf', 8)][:, 0]):.2f} of units); "
        f"T3 {t3} ({np.mean(T[('P-ANMF', 'conf', 64)][:, 0] >= T[('CA-NCI', 'conf', 64)][:, 0]):.2f} of units)")
    log(f"  T4 descriptive: P-ANMF N=1024 mean Pd at 1e-3: {T[('P-ANMF', 'conf', 1024)][:, 0].mean():.3f}")
    V.update({"T1": t1, "T2": t2, "T3": t3})
    SUM["T"] = {f"{d}|{r}|{N}": [float(v[:, 0].mean()), float(v[:, 1].mean())] for (d, r, N), v in T.items()}

    # ------------------------------------------------ Part I
    log("\nPart I: injected pulsed interference. Pooled Pfa / alpha [upper day-cluster bound]; SCR50")
    I = {}
    for p in (0.02, 0.05):
        for jnr in (10, 30):
            for m in ("D-IN1", "PAMF-H", "P-ANMF", "ANMF-FP", "D-IN4", "Clip-OS1", "Clip-OS1-cert", "Bin-OS1", "Bin-OS1-cert", "Exc-D-IN1"):
                for a in (0.01, 0.001):
                    key = f"I|{p}|{jnr}|{m}|{a}"
                    if key not in U[0]: continue
                    f = lambda V: np.mean([u[key][0] for u in V])
                    pf = f(U); hi = boot_days(U, f, rng)[1]
                    pd = np.mean([u[key][1:] for u in U], 0)
                    I[(p, jnr, m, a)] = (pf / a, hi / a, scr_at(scr, pd, .5))
                    if a == 0.01:
                        log(f"  p={p} JNR={jnr} {m:<14s} Pfa/a {pf / a:6.2f} (upper {hi / a:5.2f})  SCR50 {I[(p, jnr, m, a)][2]:6.2f}")
    i1 = all(I[(p, j, m, 0.01)][1] <= 1.2 for p in (0.02, 0.05) for j in (10, 30) for m in ("Clip-OS1-cert", "Bin-OS1-cert"))
    i2 = all(I[(0.05, 30, m, 0.01)][0] >= 5 for m in ("D-IN1", "PAMF-H"))
    base = A[("Clip-OS1", 0.01)][0]
    i3 = all(I[(0.02, j, "Clip-OS1-cert", 0.01)][2] - base <= 2 for j in (10, 30))
    log(f"  I1 {i1}; I2 {i2}; I3 {i3} (Clip-OS1 clean SCR50 {base:.2f}; cert at p=0.02: "
        f"{I[(0.02, 10, 'Clip-OS1-cert', 0.01)][2]:.2f} / {I[(0.02, 30, 'Clip-OS1-cert', 0.01)][2]:.2f})")
    V.update({"I1": i1, "I2": i2, "I3": i3})
    SUM["I"] = {f"{p}|{j}|{m}|{a}": list(map(float, v)) for (p, j, m, a), v in I.items()}

    log("\nVerdicts: " + ", ".join(f"{k} {'✓' if v else '✗'}" for k, v in V.items()))
    SUM["verdicts"] = {k: bool(v) for k, v in V.items()}
    open(os.path.join(HERE, "r12_summary.txt"), "w", encoding="utf-8").write("\n".join(OUT) + "\n")
    json.dump(SUM, open(os.path.join(HERE, "r12_summary.json"), "w"), indent=1, default=float)


if __name__ == "__main__":
    if len(sys.argv) > 1 and sys.argv[1] == "--quick":
        NB = 200
    main()
