"""Targeted synthetic verification (theory claims C1, C2a, C2b, C3) with finite fitting/calibration.

Model: complex AR(1) clutter rho = 0.93 exp(-0.2i) + white noise nu = 1; texture (CNR) lognormal,
median 10 dB, log-sd 1.5. Also a pure-SIRV arm (no noise). Per replication: N=2000 training,
n=2000 calibration, 20000 test episodes; 200 replications per (arm, m). alpha = 0.1.
Saved: per replication, coverage by true-CNR bin for each method, mean radius, and for IN1 the
EXACT conditional coverage (Corollary 1) at the replication's fitted r and q_hat, averaged within bin.
"""
import sys, os, json, math, time
HERE = os.path.dirname(os.path.abspath(__file__)); sys.path.insert(0, os.path.dirname(HERE))
import numpy as np
from methods import fit_ols, innovation_scale, conformal_quantile, fit_mixture_model, NoiseAware, ar1_corr
from cgauss import coverage as exact_cov, cov_matrix

RHO, NU, ALPHA, REPS = 0.93 * np.exp(-0.2j), 1.0, 0.1, 200
EDGES = np.array([-np.inf, 0, 5, 10, 15, 20, np.inf])


def one(args):
    arm, m, rep = args
    rng = np.random.default_rng([2026, 929, m, rep, 0 if arm == "noise" else 1])
    L = np.linalg.cholesky(ar1_corr(m + 1, RHO))
    cn = lambda *s: (rng.standard_normal(s) + 1j * rng.standard_normal(s)) / np.sqrt(2)

    def gen(n):
        c = np.exp(rng.normal(np.log(10), 1.5, n))
        X = np.sqrt(c)[:, None] * (cn(n, m + 1) @ L.T)
        if arm == "noise": X = X + math.sqrt(NU) * cn(n, m + 1)
        return X, c
    Xtr, _ = gen(2000); Xca, _ = gen(2000); Xte, cte = gen(20000)
    b = np.digitize(10 * np.log10(cte), EDGES) - 1
    r = fit_ols(Xtr); out = dict(arm=arm, m=m, rep=rep, r=[r.real, r.imag])
    sc = lambda X: abs(X[:, -1] - r * X[:, -2]) / innovation_scale(X[:, :-1], r)
    s_ca, s_te = sc(Xca), sc(Xte); q = conformal_quantile(s_ca, ALPHA)
    res = {"IN1": (s_te <= q, q * innovation_scale(Xte[:, :-1], r))}
    t_ca, t_te = innovation_scale(Xca[:, :-1], r), innovation_scale(Xte[:, :-1], r)
    e = np.quantile(t_ca, [.2, .4, .6, .8])
    qb = np.array([conformal_quantile(s_ca[np.digitize(t_ca, e) == k], ALPHA) for k in range(5)])
    res["MON"] = (s_te <= qb[np.digitize(t_te, e)], qb[np.digitize(t_te, e)] * t_te)
    if arm == "noise":
        rho_h, nu_h, _ = fit_mixture_model(Xtr); out["na_fit"] = [rho_h.real, rho_h.imag, nu_h]
        na = NoiseAware(m, rho_h, nu_h)
        cc, scc, _ = na.center_scale(Xca[:, :-1]); ct, sct, _ = na.center_scale(Xte[:, :-1])
        n_ca = abs(Xca[:, -1] - cc) / scc; n_te = abs(Xte[:, -1] - ct) / sct
        qn = conformal_quantile(n_ca, ALPHA)
        res["NA1"] = (n_te <= qn, qn * sct)
        res["NA1G"] = (n_te <= math.sqrt(-math.log(ALPHA)), math.sqrt(-math.log(ALPHA)) * sct)
    for k, (cov, rad) in res.items():
        out[k] = dict(by=[float(cov[b == j].mean()) for j in range(6)], cover=float(cov.mean()), radius=float(rad.mean()))
    # exact conditional coverage of IN1 at this replication's (r, q), averaged over test CNRs in each bin
    ex = []
    for j in range(6):
        cs = cte[b == j]; grid = np.quantile(cs, np.linspace(0.05, 0.95, 7))
        ex.append(float(np.mean([exact_cov(cov_matrix(m, RHO, c if arm == "noise" else None), m, r, q) for c in grid])))
    out["IN1_exact_by"] = ex
    return out


if __name__ == "__main__":
    import os as _o
    _o.environ["OPENBLAS_NUM_THREADS"] = "1"
    from concurrent.futures import ProcessPoolExecutor
    jobs = [(arm, m, rep) for arm in ("noise", "sirv") for m in (8, 16) for rep in range(REPS)]
    t0 = time.time(); rows = []
    with ProcessPoolExecutor(6) as ex:
        for i, o in enumerate(ex.map(one, jobs, chunksize=4)):
            rows.append(o)
            if i % 100 == 0: print(i, round(time.time() - t0), flush=True)
    json.dump(rows, open(os.path.join(HERE, "synthetic_results.json"), "w"))
    print("done", round(time.time() - t0))
