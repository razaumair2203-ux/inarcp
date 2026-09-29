"""Locate the largest exact-vs-MC discrepancy in V1a and cross-check it with an independent
exact method (Gil-Pelaez inversion of the characteristic function of sum lam_j E_j)."""
import sys, os
sys.path.insert(0, os.path.dirname(os.path.dirname(__file__)))
import numpy as np
from scipy.integrate import quad
from cgauss import cov_matrix, coverage, score_matrix, whitening

rng = np.random.default_rng(11)


def gil_pelaez(S, m, r, q):
    L = np.linalg.cholesky(S)
    lam = np.linalg.eigvalsh(L.conj().T @ score_matrix(m, r, q) @ L)
    phi = lambda t: np.prod(1 / (1 - 1j * t * lam))
    f = lambda t: (np.exp(0) * phi(t)).imag / t
    val, _ = quad(f, 0, np.inf, limit=500, epsabs=1e-11)
    return 0.5 - val / np.pi   # Gil-Pelaez: P(Q <= 0) = 1/2 - (1/pi) int_0^inf Im(phi(t))/t dt


def draw(S, n):
    L = np.linalg.cholesky(S)
    xi = (rng.standard_normal((n, S.shape[0])) + 1j * rng.standard_normal((n, S.shape[0]))) / np.sqrt(2)
    return xi @ L.T


rows = []
for m in (4, 8, 16):
    for rho, r in ((0.9 * np.exp(0.5j), 0.9 * np.exp(0.5j)), (0.9 * np.exp(0.5j), 0.8 * np.exp(0.3j)),
                   (0.95, 0.7), (0.5j, 0.0)):
        for cnr in (None, 0.3, 3.0, 30.0):
            S = cov_matrix(m, rho, cnr)
            X = draw(S, 300000)
            H, Y = X[:, :m], X[:, m]
            s = np.sqrt(np.sum(abs(H @ whitening(m, r).T) ** 2, 1) / m)
            sc = abs(Y - r * H[:, -1]) / s
            for q in (1.0, 2.0, 3.5):
                ex = coverage(S, m, r, q); gp = gil_pelaez(S, m, r, q); mc = np.mean(sc <= q)
                se = np.sqrt(mc * (1 - mc) / len(sc))
                rows.append((abs(ex - mc) / max(se, 1e-9), abs(ex - gp), m, rho, r, cnr, q, ex, gp, mc))
rows.sort(key=lambda t: -t[0])
print("largest |z| of exact vs MC (1e6 draws) and |closed form - Gil-Pelaez|:")
for t in rows[:5]:
    print(f"  z={t[0]:.2f} |cf-gp|={t[1]:.1e} m={t[2]} rho={t[3]:.2f} r={t[4]:.2f} cnr={t[5]} q={t[6]} exact={t[7]:.5f} gp={t[8]:.5f} mc={t[9]:.5f}")
print(f"max |closed form - Gil-Pelaez| over all: {max(t[1] for t in rows):.2e}; count |z|>3: {sum(t[0]>3 for t in rows)} of {len(rows)}")
