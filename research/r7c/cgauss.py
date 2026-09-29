"""Exact coverage laws for complex-Gaussian AR episodes (optionally plus white noise).

Model (per episode, conditional on its texture): X = (H_1..H_m, Y) ~ CN(0, S), with
S = c * R_rho + I (noise power 1, clutter-to-noise ratio c), or S = R_rho (pure clutter).
R_rho[j,k] = rho^(j-k) for j >= k and conj for j < k (unit-variance stationary complex AR(1)).

For any fitted coefficient r and threshold q, the normalized-score event
    |Y - r H_m|^2 <= q^2 s_r(H)^2,   s_r^2 = ((1-|r|^2)|H_1|^2 + sum_j |H_j - r H_{j-1}|^2)/m
is {X^H M X <= 0} for a Hermitian M. With X = L xi, xi ~ CN(0, I):
    X^H M X = sum_j lam_j E_j,  E_j iid Exp(1),  lam = eig(L^H M L).
For distinct nonzero lam (signed), P(sum lam_j E_j > 0) = sum_{lam_j>0} prod_{k!=j} lam_j/(lam_j-lam_k).
This is exact and elementary (no integration), unlike the real-valued case.
"""
import numpy as np
from scipy.special import betainc


def ar1_corr(p, rho):
    j = np.arange(p)
    d = j[:, None] - j[None, :]
    R = np.where(d >= 0, rho ** np.abs(d), np.conj(rho) ** np.abs(d))
    return R.astype(complex)


def whitening(m, r):
    W = np.eye(m, dtype=complex)
    W[0, 0] = np.sqrt(1 - abs(r) ** 2)
    W[np.arange(1, m), np.arange(m - 1)] = -r
    return W


def score_matrix(m, r, q):
    """Hermitian M with X^H M X = |Y - r H_m|^2 - q^2 s_r(H)^2."""
    p = m + 1
    c = np.zeros(p, complex); c[m] = 1; c[m - 1] = -r
    M = np.outer(np.conj(c), c)
    W = whitening(m, r)
    M[:m, :m] -= (q * q / m) * (W.conj().T @ W)
    return M


def _prob_positive(lam, tol=1e-12):
    lam = lam[np.abs(lam) > tol * np.max(np.abs(lam))]
    pos = lam[lam > 0]
    if len(pos) == 0:
        return 0.0
    out = 0.0
    for lj in pos:
        others = lam[lam != lj]
        out += np.prod(lj / (lj - others))
    return float(out)


def coverage(S, m, r, q):
    """P(score <= q) exactly, for X ~ CN(0, S)."""
    L = np.linalg.cholesky(S)
    M = score_matrix(m, r, q)
    lam = np.linalg.eigvalsh(L.conj().T @ M @ L)
    # tiny deterministic jitter guards against exactly repeated eigenvalues
    lam = lam * (1 + 1e-10 * np.arange(len(lam)))
    return 1.0 - _prob_positive(lam)


def cov_matrix(m, rho, cnr=None):
    R = ar1_corr(m + 1, rho)
    return R if cnr is None else cnr * R + np.eye(m + 1)


def quantile(S, m, r, level, lo=0.0, hi=50.0, iters=80):
    for _ in range(iters):
        mid = (lo + hi) / 2
        if coverage(S, m, r, mid) < level: lo = mid
        else: hi = mid
    return (lo + hi) / 2


def expected_coverage_shift(S_cal, S_test, m, r, n, alpha, nodes=400):
    """E over calibration of test coverage when q_hat = k-th of n calibration scores.
    q_hat = G_cal^{-1}(B), B ~ Beta(k, n+1-k). Integrate via survival of B on a q grid:
    E[G_test(q_hat)] = int G_test(q) dP(q_hat <= q) = int G_test(q) d I_{G_cal(q)}(k, n+1-k).
    """
    k = int(np.ceil((n + 1) * (1 - alpha)))
    qs = np.linspace(0, 1, nodes) ** 2 * 30  # denser near 0
    Gc = np.array([coverage(S_cal, m, r, q) for q in qs])
    Gt = np.array([coverage(S_test, m, r, q) for q in qs])
    F = betainc(k, n + 1 - k, np.clip(Gc, 0, 1))
    return float(np.sum(0.5 * (Gt[1:] + Gt[:-1]) * np.diff(F)))
