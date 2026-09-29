"""Gate V4 (real data): conformal prediction-residual detection of the IPIX floating sphere.
Per session and like-pol channel, m=16: calibrate scores on clutter-bin episodes (cal third);
flag a test episode if its score exceeds the conformal threshold at level alpha (conformal p-value
<= alpha). Report empirical false-alarm rate on clutter test episodes and detection rate on the
PRIMARY target bin (all times; target always present, TCR 0-6 dB per the site).
Pfa is controlled marginally by exchangeability; Pd is descriptive (single-pulse, no integration)."""
import sys, os, math
sys.path.insert(0, os.path.dirname(os.path.dirname(__file__)))
import numpy as np
from ipix import FILES, load, episodes
from methods import conformal_quantile, fit_ols, innovation_scale
from v2c_arp_diagnosis import fit_arp, center_scale
from v2b_ipix_within import T, t1, t2, GAP, STRIDE

m = 16
res = {k: {a: [] for a in (1e-2, 1e-3)} for k in ("AR(1) IN, conformal", "AR(1) IN, Gaussian F", "AR(4), conformal", "unnormalized, conformal")}
for num in FILES:
    dc, dt = load(num), load(num, keep="target")
    for pol in dc["z"]:
        zc, zt = dc["z"][pol], dt["z"][pol]
        Xtr, _, _ = episodes(zc, 0, t1 - GAP, m, STRIDE); Xca, _, _ = episodes(zc, t1, t2 - GAP, m, STRIDE)
        Xte, _, _ = episodes(zc, t2, T, m, STRIDE); Xtg, _, _ = episodes(zt, 0, T, m, 64)
        r = fit_ols(Xtr); a4 = fit_arp(Xtr, 4)
        sc = lambda X: abs(X[:, -1] - r * X[:, -2]) / innovation_scale(X[:, :-1], r)
        s4 = lambda X: (lambda c, s: abs(X[:, -1] - c) / s)(*center_scale(X, a4))
        su = lambda X: abs(X[:, -1] - r * X[:, -2])
        for a in (1e-2, 1e-3):
            for name, f, q in (("AR(1) IN, conformal", sc, conformal_quantile(sc(Xca), a)),
                               ("AR(1) IN, Gaussian F", sc, math.sqrt(m * (a ** (-1 / m) - 1))),
                               ("AR(4), conformal", s4, conformal_quantile(s4(Xca), a)),
                               ("unnormalized, conformal", su, conformal_quantile(su(Xca), a))):
                res[name][a].append((np.mean(f(Xte) > q), np.mean(f(Xtg) > q)))
for name, d in res.items():
    for a, v in d.items():
        v = np.array(v)
        print(f"{name:26s} alpha={a:g}: Pfa mean {v[:,0].mean():.4f} (max {v[:,0].max():.4f}) | Pd mean {v[:,1].mean():.3f} "
              f"(median {np.median(v[:,1]):.3f})")
