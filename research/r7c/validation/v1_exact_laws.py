"""Gate V1: exact complex coverage law vs Monte Carlo (pure clutter and clutter+noise, fitted r != rho),
and exact expected coverage under calibration->test dynamics shift vs Monte Carlo."""
import sys, os, math
sys.path.insert(0, os.path.dirname(os.path.dirname(__file__)))
import numpy as np
from cgauss import cov_matrix, coverage, expected_coverage_shift, whitening

rng = np.random.default_rng(7)


def draw(S, n):
    L = np.linalg.cholesky(S)
    xi = (rng.standard_normal((n, S.shape[0])) + 1j * rng.standard_normal((n, S.shape[0]))) / np.sqrt(2)
    return xi @ L.T


def scores(X, m, r):
    H, Y = X[:, :m], X[:, m]
    W = whitening(m, r)
    s = np.sqrt(np.sum(abs(H @ W.T) ** 2, 1) / m)
    return abs(Y - r * H[:, -1]) / s


print("V1a: exact vs MC single-episode coverage (400k draws; MC se ~ 0.0005)")
worst = 0
for m in (4, 8, 16):
    for rho, r in ((0.9 * np.exp(0.5j), 0.9 * np.exp(0.5j)), (0.9 * np.exp(0.5j), 0.8 * np.exp(0.3j)),
                   (0.95, 0.7), (0.5j, 0.0)):
        for cnr in (None, 0.3, 3.0, 30.0):
            S = cov_matrix(m, rho, cnr)
            sc = scores(draw(S, 400000), m, r)
            for q in (1.0, 2.0, 3.5):
                ex, mc = coverage(S, m, r, q), np.mean(sc <= q)
                worst = max(worst, abs(ex - mc))
print(f"   max |exact - MC| over 144 cases = {worst:.4f}")

print("V1b: conditional coverage vs CNR of IN-ARCP calibrated on a clutter+noise mixture (m=8, alpha=.1)")
m, rho, r = 8, 0.93 * np.exp(-0.2j), 0.93 * np.exp(-0.2j)
cnrs = np.exp(rng.normal(np.log(10), 1.5, 200000))   # lognormal texture, CNR median 10 dB
X = np.concatenate([draw(cov_matrix(m, rho, c), 1) for c in cnrs[:20000]])
sc = scores(X, m, r); n = len(sc); q = np.sort(sc)[math.ceil((n + 1) * .9) - 1]
for c in (0.1, 0.3, 1, 3, 10, 30, 100, 1000):
    print(f"   CNR {10*np.log10(c):6.1f} dB: exact conditional coverage {coverage(cov_matrix(m, rho, c), m, r, q):.3f}")
print(f"   pure clutter limit: {coverage(cov_matrix(m, rho), m, r, q):.3f}")

print("V1c: exact expected coverage under dynamics shift vs MC (n=199 calibration, 4000 reps)")
for rc, rt in ((0.9 * np.exp(0.5j), 0.9 * np.exp(0.5j)), (0.9 * np.exp(0.5j), 0.9 * np.exp(0.9j)),
               (0.9 * np.exp(0.5j), 0.6 * np.exp(0.5j))):
    Sc, St = cov_matrix(8, rc), cov_matrix(8, rt)
    ex = expected_coverage_shift(Sc, St, 8, rc, 199, 0.1)
    cov = []
    for _ in range(4000):
        qh = np.sort(scores(draw(Sc, 199), 8, rc))[179]
        cov.append(np.mean(scores(draw(St, 50), 8, rc) <= qh))
    print(f"   rho_cal={rc:.2f} rho_test={rt:.2f}: exact {ex:.4f}  MC {np.mean(cov):.4f} +- {np.std(cov)/np.sqrt(4000):.4f}")
