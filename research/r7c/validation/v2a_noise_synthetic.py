"""Gate V2a (synthetic): recover (rho, nu) and compare conditional coverage vs CNR for
IN-ARCP, noise-aware IN-ARCP (NA), and their Mondrian variants. Clutter + noise, lognormal texture."""
import sys, os, math
sys.path.insert(0, os.path.dirname(os.path.dirname(__file__)))
import numpy as np
from methods import fit_ols, innovation_scale, fit_noise_model, fit_mixture_model, NoiseAware, EmpiricalBayes, conformal_quantile, ar1_corr

rng = np.random.default_rng(3)
m, rho, nu, alpha = 8, 0.93 * np.exp(-0.2j), 1.0, 0.1
L = np.linalg.cholesky(ar1_corr(m + 1, rho))


def gen(n):
    cn = lambda *s: (rng.standard_normal(s) + 1j * rng.standard_normal(s)) / np.sqrt(2)
    c = np.exp(rng.normal(np.log(10), 1.5, n))          # CNR, median 10 dB, wide spread
    X = np.sqrt(c)[:, None] * (cn(n, m + 1) @ L.T) + np.sqrt(nu) * cn(n, m + 1)
    return X, c


Xtr, _ = gen(20000); Xca, cca = gen(20000); Xte, cte = gen(200000)
rho_m, nu_m = fit_noise_model(Xtr); print(f"moment fit: rho={rho_m:.3f} nu={nu_m:.3f}")
rho_h, nu_h, w_h = fit_mixture_model(Xtr)
print(f"noise-model fit: rho_hat={rho_h:.3f} (true {rho:.3f}), nu_hat={nu_h:.3f} (true {nu})")
r = fit_ols(Xtr)
edges_db = [-np.inf, 0, 5, 10, 15, 20, np.inf]
cb = np.digitize(10 * np.log10(cte), edges_db) - 1


def report(name, cov, rad):
    by = [cov[cb == b].mean() for b in range(6)]
    print(f"  {name:28s} marginal {cov.mean():.3f} | by true CNR (<0,0-5,5-10,10-15,15-20,>20 dB) "
          f"{np.round(by,3)} | spread {max(by)-min(by):.3f}")


def mondrian(sc_cal, key_cal, key_te, sc_te, nb=5):
    e = np.quantile(key_cal, np.linspace(0, 1, nb + 1)[1:-1])
    bc, bt = np.digitize(key_cal, e), np.digitize(key_te, e)
    q = np.array([conformal_quantile(sc_cal[bc == b], alpha) for b in range(nb)])
    return sc_te <= q[bt]


# IN-ARCP
sc_ca = abs(Xca[:, -1] - r * Xca[:, -2]) / innovation_scale(Xca[:, :-1], r)
sc_te = abs(Xte[:, -1] - r * Xte[:, -2]) / innovation_scale(Xte[:, :-1], r)
report("IN-ARCP", sc_te <= conformal_quantile(sc_ca, alpha), None)
report("IN-ARCP Mondrian(scale)", mondrian(sc_ca, innovation_scale(Xca[:, :-1], r), innovation_scale(Xte[:, :-1], r), sc_te), None)
# noise-aware
na = NoiseAware(m, rho_h, nu_h)
cc, sc, jc = na.center_scale(Xca[:, :-1]); ct, st, jt = na.center_scale(Xte[:, :-1])
s_ca = abs(Xca[:, -1] - cc) / sc; s_te = abs(Xte[:, -1] - ct) / st
report("NA-IN-ARCP", s_te <= conformal_quantile(s_ca, alpha), None)
report("NA-IN-ARCP Mondrian(cnr_hat)", mondrian(s_ca, jc, jt, s_te), None)
report("NA Gaussian plug-in", s_te <= math.sqrt(-math.log(alpha)), None)
eb = EmpiricalBayes(m, rho_h, nu_h, np.logspace(-2, 5, 50), w_h)
cc, sc, kc = eb.center_scale(Xca[:, :-1]); ct, st, kt = eb.center_scale(Xte[:, :-1])
e_ca = abs(Xca[:, -1] - cc) / sc; e_te = abs(Xte[:, -1] - ct) / st
report("EB-IN-ARCP", e_te <= conformal_quantile(e_ca, alpha), None)
report("EB-IN-ARCP Mondrian(post logCNR)", mondrian(e_ca, kc, kt, e_te), None)
