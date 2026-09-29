"""Numerical checks of the R8 detection theory (Monte Carlo against closed forms and the exact law).

T1  Exact detection law: Pd = 1 - G_{Sigma + S e e^H}(q)   (Prop. 1 with the target in the covariance)
T2  Pure AR(1) clutter, true coefficient: Pd = (1 + q^2 (1-|rho|^2) / (m (1-|rho|^2 + S)))^(-m)
T3  Noise-limited whitening gains (large m; SCR relative to local clutter+noise power, CNR c):
      IN-ARCP (AR(1) predictor at r = rho):   G_IN(c) = (1+c) / (1+|rho|^2 + c(1-|rho|^2))
      oracle one-step predictor (AR(1)+noise): G_opt(c) = (1+c) / K(c),
      K(c) = [b + sqrt(b^2 - 4|rho|^2)]/2, b = 1+|rho|^2+c(1-|rho|^2)   (Kolmogorov-Szego)
    checked against the empirical ratio (clutter+noise power) / (one-step prediction-error power).
T4  Persistent-target blindness: target phasor A e^{j w t} in every sample, A -> infinity:
      score -> sqrt(m)|1 - r e^{-jw}| / sqrt((1-|r|^2) + (m-1)|1 - r e^{-jw}|^2) < sqrt(m/(m-1)),
    so Pd -> 0 whenever q > sqrt(m/(m-1)).
Run: python theory_checks.py  (writes theory_checks_output.txt)
"""
import os, sys, math
import numpy as np
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from cgauss import coverage, ar1_corr

rng = np.random.default_rng(11); OUT = []
def log(s): print(s); OUT.append(s)
m = 16


def cn(*s): return np.sqrt(.5) * (rng.standard_normal(s) + 1j * rng.standard_normal(s))


def draw(n, rho, c=None):
    """episodes of AR(1) clutter (power c, or 1 if pure) + unit noise (if c given)."""
    L = np.linalg.cholesky(ar1_corr(m + 1, rho))
    X = cn(n, m + 1) @ L.T
    return X if c is None else np.sqrt(c) * X + cn(n, m + 1)


def score(X, r):
    H, Y = X[:, :-1], X[:, -1]
    s2 = ((1 - abs(r) ** 2) * abs(H[:, 0]) ** 2 + np.sum(abs(H[:, 1:] - r * H[:, :-1]) ** 2, 1)) / m
    return abs(Y - r * H[:, -1]) / np.sqrt(s2)


log("T1/T2  exact detection law vs Monte Carlo (Swerling-1 target in Y only; 400k draws)")
for rho, c, r, S, q in [(0.93 * np.exp(-0.2j), None, 0.93 * np.exp(-0.2j), 1.0, 2.31),
                        (0.93 * np.exp(-0.2j), 10.0, 0.9 * np.exp(-0.2j), 3.0, 2.31),
                        (0.7, 1.0, 0.65, 10.0, 3.2)]:
    n = 400000; X = draw(n, rho, c); P = 1.0 if c is None else c + 1.0
    X[:, -1] += np.sqrt(S * P) * cn(n)
    mc = np.mean(score(X, r) > q)
    Sig = ar1_corr(m + 1, rho) * (1 if c is None else c) + (0 if c is None else np.eye(m + 1))
    e = np.zeros(m + 1); e[m] = 1
    ex = 1 - coverage(Sig + S * P * np.outer(e, e), m, r, q)
    line = f"  rho={rho:.2f} c={c} r={r:.2f} SCR={S}: MC {mc:.4f}  exact {ex:.4f}"
    if c is None:
        a = 1 - abs(rho) ** 2; line += f"  closed form {(1 + q*q*a/(m*(a+S)))**(-m):.4f}"
    log(line)

log("\nT3  noise-limited whitening gain: empirical (c+1)/E|Y-pred|^2 vs closed forms (m=16 history, 200k draws)")
for arho in (0.7, 0.93, 0.98):
    rho = arho * np.exp(-0.2j)
    for c in (0.1, 1.0, 10.0, 100.0):
        X = draw(200000, rho, c)
        e_in = np.mean(abs(X[:, -1] - rho * X[:, -2]) ** 2)
        Sig = c * ar1_corr(m + 1, rho) + np.eye(m + 1)
        w = np.linalg.solve(Sig[:m, :m], Sig[:m, m])            # oracle linear predictor on 16 samples
        e_op = np.mean(abs(X[:, -1] - X[:, :-1] @ np.conj(w)) ** 2)
        a = abs(rho) ** 2; b = 1 + a + c * (1 - a); K = (b + math.sqrt(b * b - 4 * a)) / 2
        gin, gop = (1 + c) / (1 + a + c * (1 - a)), (1 + c) / K
        log(f"  |rho|={arho} c={c:6.1f}: IN emp {10*np.log10((1+c)/e_in):6.2f} dB  closed {10*np.log10(gin):6.2f} | "
            f"oracle emp {10*np.log10((1+c)/e_op):6.2f} dB  closed(m=inf) {10*np.log10(gop):6.2f} | "
            f"clutter-only bound {10*np.log10(1/(1-a)):5.2f}")

log("\nT4  persistent strong target: limiting score and Pd (IN-ARCP, r fitted = 0.93e^{-0.2j})")
r = 0.93 * np.exp(-0.2j); qs = {0.1: math.sqrt(m * (0.1 ** (-1 / m) - 1)), 0.01: math.sqrt(m * (0.01 ** (-1 / m) - 1))}
log(f"  sqrt(m/(m-1)) = {math.sqrt(m/(m-1)):.3f}; thresholds q(0.1)={qs[0.1]:.3f} q(0.01)={qs[0.01]:.3f}")
for w in (0.0, -0.2, 1.0):
    d = abs(1 - r * np.exp(-1j * w)); lim = math.sqrt(m) * d / math.sqrt((1 - abs(r) ** 2) + (m - 1) * d * d)
    t = np.arange(m + 1); row = []
    for S in (1, 100, 1e4):
        X = draw(100000, r, 10.0)
        X += np.sqrt(S * 11.0) * np.exp(1j * (w * t[None, :] + 2 * np.pi * rng.random((100000, 1))))
        row.append(f"SCR {10*np.log10(S):4.0f} dB: Pd(0.01) {np.mean(score(X, r) > qs[0.01]):.3f}")
    log(f"  Doppler w={w:+.1f}: limiting score {lim:.3f} | " + " | ".join(row))
open(os.path.join(os.path.dirname(os.path.abspath(__file__)), "theory_checks_output.txt"), "w").write("\n".join(OUT) + "\n")
