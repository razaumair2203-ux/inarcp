"""V5: numerical checks of Proposition 3 (NA -> IN-ARCP as nu -> 0) and Proposition 4 (Mondrian tilt
under pure SIRV at the true coefficient, bins on the innovation scale)."""
import sys, os, math
sys.path.insert(0, os.path.dirname(os.path.dirname(__file__)))
import numpy as np
from methods import NoiseAware, innovation_scale, conformal_quantile, ar1_corr

rng = np.random.default_rng(9)
m, rho = 8, 0.93 * np.exp(-0.2j)
L = np.linalg.cholesky(ar1_corr(m + 1, rho))
cn = lambda *s: (rng.standard_normal(s) + 1j * rng.standard_normal(s)) / np.sqrt(2)

print("Prop 3: max relative gap between NA and IN-ARCP scores on 2000 pure-clutter episodes")
X = np.exp(rng.normal(0, 1.5, 2000))[:, None] * (cn(2000, m + 1) @ L.T)
s_in = abs(X[:, -1] - rho * X[:, -2]) / innovation_scale(X[:, :-1], rho)
for nu in (1e-1, 1e-3, 1e-5, 1e-7):
    na = NoiseAware(m, rho, nu, grid=np.logspace(-3, 12, 3001))
    c, s, _ = na.center_scale(X[:, :-1])
    print(f"   nu={nu:.0e}: median |NA/IN - 1| = {np.median(abs(abs(X[:, -1]-c)/s / s_in - 1)):.2e}")

print("Prop 4: texture-conditional coverage, pure SIRV, true coefficient, alpha=.1, 5 Mondrian bins on s(H)")
n_cal = 200000
sig = np.exp(rng.normal(0, 1.5, n_cal)); Xc = sig[:, None] * (cn(n_cal, m + 1) @ L.T)
Sc = abs(Xc[:, -1] - rho * Xc[:, -2]) / innovation_scale(Xc[:, :-1], rho); Tc = innovation_scale(Xc[:, :-1], rho)
q = conformal_quantile(Sc, .1); e = np.quantile(Tc, [.2, .4, .6, .8])
qb = np.array([conformal_quantile(Sc[np.digitize(Tc, e) == b], .1) for b in range(5)])
Z = cn(200000, m + 1) @ L.T
Sz = abs(Z[:, -1] - rho * Z[:, -2]) / innovation_scale(Z[:, :-1], rho); Tz = innovation_scale(Z[:, :-1], rho)
for s_ in (np.exp(-6), np.exp(-2), 1.0, np.exp(2), np.exp(6)):
    mon = np.mean(Sz <= qb[np.digitize(s_ * Tz, e)]); unb = np.mean(Sz <= q)
    print(f"   log sigma={np.log(s_):+.0f}: unbinned {unb:.4f} | Mondrian {mon:.4f}")
print(f"   predicted limits: sigma->inf F_S(q_top)={np.mean(Sz<=qb[-1]):.4f}, sigma->0 F_S(q_bottom)={np.mean(Sz<=qb[0]):.4f}")
