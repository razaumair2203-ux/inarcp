"""Independent Monte Carlo check of every closed form in the manuscript (written from scratch; does NOT import laws.py).

Checks: Prop. 1 (incl. repeated eigenvalues and singular Q), Cor. 2 / eq. (3), Prop. 4 / eq. (5), Cor. 4 (horizon),
eq. (7) (OS after onset, strong target), eqs. (8)-(9) (integration), eq. (10) (P-ANMF), the conformal Beta law and
calibration-size numbers, and Theorem 1 (certified clipped/binary integration) under adversarial amplitudes, plus a
deliberately MISSPECIFIED bursty hit pattern, where the theorem's dominance condition fails and a violation is expected.
GPU via CuPy when INARCP_GPU=1. Output: theory_check_independent_output.txt (z-scores; |z|<4 counts as agreement).
"""
import math
import os
import sys

import numpy as np
from scipy import optimize, special, stats

GPU = os.environ.get("INARCP_GPU") == "1"
if GPU:
    import cupy as xp
else:
    xp = np
rng = xp.random.default_rng(20261002)
OUT = []


def log(s):
    print(s)
    OUT.append(s)


def to_np(a):
    return a.get() if GPU else a


def cn(shape):
    return (rng.standard_normal(shape) + 1j * rng.standard_normal(shape)) / math.sqrt(2)


def check(name, mc_hits, n, law, tol_z=4.0):
    p = mc_hits / n
    se = math.sqrt(max(law * (1 - law), 1e-12) / n)
    z = (p - law) / se
    ok = abs(z) < tol_z
    log(f"{'OK ' if ok else 'BAD'} {name:<58s} MC {p:.5f}  law {law:.5f}  z {z:+.2f}")
    return ok


def ar1(n, m1, rho, tex=True):
    """n episodes of m1 complex AR(1) samples, unit power, optional lognormal texture (cancels in the scores)."""
    w = cn((n, m1))
    x = xp.empty((n, m1), dtype=xp.complex128)
    x[:, 0] = w[:, 0]
    a = math.sqrt(1 - abs(rho) ** 2)
    for t in range(1, m1):
        x[:, t] = rho * x[:, t - 1] + a * w[:, t]
    if tex:
        x *= xp.exp(0.5 * rng.standard_normal((n, 1)))
    return x


def innov(x, r):
    e = xp.empty_like(x)
    e[:, 0] = math.sqrt(1 - abs(r) ** 2) * x[:, 0]
    e[:, 1:] = x[:, 1:] - r * x[:, :-1]
    return e


ok_all = True
N = 2_000_000 if GPU else 400_000
m, rho = 16, 0.93 * complex(math.cos(-0.2), math.sin(-0.2))
q2 = m * (0.01 ** (-1 / m) - 1)          # CA-law threshold at Pfa 0.01
beta = q2 / m

# ---------- Prop. 1: exact law, general centre and scale (incl. singular Q, repeated eigenvalues) ----------
def prop1_law(Sigma, a, Q, q):
    mm = len(a)
    b = np.zeros(mm + 1, complex); b[-1] = 1; b[:mm] = -a
    Mq = np.outer(b.conj(), b) - (q ** 2 / mm) * np.pad(Q, ((0, 1), (0, 1)))
    w, V = np.linalg.eigh(Sigma)
    S12 = V @ np.diag(np.sqrt(w)) @ V.conj().T
    lam = np.linalg.eigvalsh(S12 @ Mq @ S12)
    lam = lam[np.abs(lam) > 1e-10 * np.abs(lam).max()]
    lp = lam[lam > 0]
    assert len(lp) == 1, lam
    lp = lp[0]
    return 1 - np.prod(lp / (lp - lam[lam < 0]))


def prop1_mc(Sigma, a, Q, q, n):
    L = xp.asarray(np.linalg.cholesky(Sigma))
    X = cn((n, len(a) + 1)) @ L.T
    H, Y = X[:, :-1], X[:, -1]
    num = xp.abs(Y - H @ xp.asarray(a)) ** 2
    s2 = xp.real(xp.einsum("ni,ij,nj->n", H.conj(), xp.asarray(Q), H)) / len(a)
    return int(xp.sum(num <= q ** 2 * s2))


mm = 6
idx = np.arange(mm + 1)
R = (0.8 * np.exp(-0.3j)) ** np.abs(idx[:, None] - idx[None, :])
R = np.where(idx[:, None] >= idx[None, :], R, R.conj())
Sig = 2.0 * (3.0 * R + np.eye(mm + 1))                     # clutter + noise
cases = [("Prop1 AR(1) centre, Q=I", np.r_[np.zeros(mm - 1), 0.7], np.eye(mm), 1.3),
         ("Prop1 zero centre, white Sigma (repeated eigenvalues)", np.zeros(mm), np.eye(mm), 1.1),
         ("Prop1 singular Q (rank 2)", np.r_[np.zeros(mm - 1), 0.5], np.diag([1, 1, 0, 0, 0, 0.0]), 1.0)]
for name, a, Q, q in cases:
    S = np.eye(mm + 1) if "white" in name else Sig
    ok_all &= check(name, prop1_mc(S, a.astype(complex), Q.astype(complex), q, N), N, prop1_law(S, a.astype(complex), Q.astype(complex), q))

# ---------- Cor. 2 / eq. (3) and Prop. 4 / eq. (5): look l after onset ----------
def prop4_law(S, l, d2):
    Sw = S / (1 - abs(rho) ** 2)
    E0, EH = (Sw, 0.0) if l == 0 else (Sw * d2, Sw * (1 + (l - 1) * d2))
    B = 1 + E0 - beta - beta * EH
    C = beta * (1 + E0 + EH)
    lp = (B + math.sqrt(B * B + 4 * C)) / 2
    lm = (B - math.sqrt(B * B + 4 * C)) / 2
    return lp / (lp - lm) * (1 + beta / lp) ** (-(m - 1))


def prop4_mc(S, l, omega, n):
    x = ar1(n, m + 1 + l, rho, tex=False)                  # clutter of the last m+1 samples used at look l
    g = cn((n, 1)) * math.sqrt(S)
    t = xp.arange(m + 1 + l)
    onset = m                                              # target starts at the first tested pulse
    sig = xp.where(t >= onset, g * xp.exp(1j * omega * t), 0)
    x = x + sig
    ep = x[:, l:]                                          # episode for look l: history = previous m samples
    e = innov(ep, rho)
    s2 = xp.mean(xp.abs(e[:, :m]) ** 2, axis=1)
    return int(xp.sum(xp.abs(e[:, m]) ** 2 > q2 * s2))


for S_db in (0.0, 10.0):
    S = 10 ** (S_db / 10)
    for lab, omega in (("opposite", -0.2 + math.pi), ("random", 1.3)):
        d2 = abs(1 - rho * complex(math.cos(-omega), math.sin(-omega))) ** 2
        for l in (0, 1, 2, 4, 8):
            ok_all &= check(f"Prop4 S={S_db:.0f}dB {lab} look {l}", prop4_mc(S, l, omega, N // 2), N // 2, prop4_law(S, l, d2))
# eq. (3) explicit
S = 10.0
law3 = (1 + q2 / m * (1 - abs(rho) ** 2) / (1 - abs(rho) ** 2 + S)) ** (-m)
ok_all &= check("Cor2 eq.(3) onset, 10 dB", prop4_mc(S, 0, 0.7, N // 2), N // 2, law3)

# ---------- Cor. 4: horizon (strong target, sign of chi) ----------
d2opp = (1 + abs(rho)) ** 2
lstar = 1 + m / q2 - 1 / d2opp
log(f"    horizon l* (opposite Doppler, |rho|=0.93, m=16, Pfa 0.01) = {lstar:.3f}  (paper: 3.73)")
for l in (3, 4):
    p = prop4_law(10 ** 6.0, l, d2opp)
    log(f"    law at S=60 dB, look {l}: Pd = {p:.4f}  (expected -> {'1' if l < lstar else '0'})")
    ok_all &= (p > 0.9) if l < lstar else (p < 0.1)

# ---------- eq. (7): OS scale after onset, strong-target approximation ----------
def os_mc(S, l, omega, k, n):
    x = ar1(n, m + 1 + l, rho, tex=False)
    g = cn((n, 1)) * math.sqrt(S)
    t = xp.arange(m + 1 + l)
    x = x + xp.where(t >= m, g * xp.exp(1j * omega * t), 0)
    e = innov(x[:, l:], rho)
    p = xp.sort(xp.abs(e[:, :m]) ** 2, axis=1)[:, k - 1]
    return e, p


k = 8
qos = optimize.root_scalar(lambda q: np.prod([(m - i) / (m - i + q) for i in range(k)]) - 0.01, bracket=[0.01, 50]).root
for l in (2, 4):
    S = 10 ** 3.0
    omega = -0.2 + math.pi
    d2 = abs(1 - rho * complex(math.cos(-omega), math.sin(-omega))) ** 2
    Sw = S / (1 - abs(rho) ** 2)
    law7 = np.prod([(m - l - i) / (m - l - i + qos / (1 + Sw * d2)) for i in range(k)])
    e, p = os_mc(S, l, omega, k, N // 4)
    ok_all &= check(f"eq.(7) OS k=8 look {l}, 30 dB (strong-target approx.)", int(xp.sum(xp.abs(e[:, m]) ** 2 > qos * p)), N // 4, law7, tol_z=6)
l = 10   # l > m-k: Pd -> 0
e, p = os_mc(10 ** 4.0, l, -0.2 + math.pi, k, N // 4)
pd10 = float(xp.mean(xp.abs(e[:, m]) ** 2 > qos * p))
log(f"{'OK ' if pd10 < 0.01 else 'BAD'} eq.(7) OS look {l} > m-k at 40 dB: Pd = {pd10:.4f} (expected -> 0)")
ok_all &= pd10 < 0.01

# ---------- eqs. (8)-(9): K-look integration ----------
K, tau = 8, None
def nci_pfa(tau):
    return sum(special.comb(m + i - 1, i) * tau ** i / (1 + tau) ** (m + i) for i in range(K))
tau = optimize.root_scalar(lambda t: nci_pfa(t) - 0.01, bracket=[1e-4, 10]).root
def nci_pd(S, d2):
    Sw = S / (1 - abs(rho) ** 2); ED = Sw * (1 + (K - 1) * d2); dl = 1 + ED; tp = tau * (1 - 1 / dl)
    a = sum(special.comb(m + i - 1, i) * tau ** i / (1 + tau) ** (m + i) for i in range(K - 1))
    b = sum(special.comb(m + i - 1, i) * tp ** i / (1 + tau) ** (m + i) for i in range(K - 1))
    return a + (1 - 1 / dl) ** (-(K - 1)) * ((1 + tau / dl) ** (-m) - b)
for S_db in (None, 0.0, 5.0):
    S = 0.0 if S_db is None else 10 ** (S_db / 10)
    omega = 1.3
    d2 = abs(1 - rho * complex(math.cos(-omega), math.sin(-omega))) ** 2
    nn = N // 2
    x = ar1(nn, m + K, rho, tex=(S_db is None))           # texture only under H0 (SCR is relative to local power)
    t = xp.arange(m + K)
    x = x + (xp.where(t >= m, cn((nn, 1)) * math.sqrt(S) * xp.exp(1j * omega * t), 0) if S else 0)
    e = innov(x, rho)
    stat = xp.sum(xp.abs(e[:, m:]) ** 2, axis=1) / xp.mean(xp.abs(e[:, :m]) ** 2, axis=1)
    hits = int(xp.sum(stat > tau * m))
    ok_all &= check(f"eq.(8)/(9) integration K=8 {'H0' if S_db is None else f'{S_db:.0f} dB'}", hits, nn, 0.01 if S_db is None else nci_pd(S, d2))

# ---------- eq. (10): P-ANMF, known on-grid Doppler ----------
Nd = 16
t_thr = 1 - 0.01 ** (1 / (Nd - 1))
for S_db in (None, -5.0, 0.0):
    S = 0.0 if S_db is None else 10 ** (S_db / 10)
    nn = N // 2
    kbin = 5
    omega = 2 * math.pi * kbin / Nd
    x = ar1(nn, Nd + 1, rho, tex=(S_db is None))
    t = xp.arange(Nd + 1)
    x = x + (cn((nn, 1)) * math.sqrt(S) * xp.exp(1j * omega * t) if S else 0)   # target present throughout
    e = innov(x, rho)[:, 1:]                                                    # N conditional innovations
    F = xp.fft.fft(e, axis=1)
    stat = xp.abs(F[:, kbin]) ** 2 / (Nd * xp.sum(xp.abs(e) ** 2, axis=1))
    wfac = abs(1 - rho * complex(math.cos(-omega), math.sin(-omega))) ** 2 / (1 - abs(rho) ** 2)
    law10 = 0.01 if S_db is None else (1 + (0.01 ** (-1 / (Nd - 1)) - 1) / (1 + Nd * S * wfac)) ** (-(Nd - 1))
    ok_all &= check(f"eq.(10) P-ANMF known bin, {'H0' if S_db is None else f'{S_db:.0f} dB'}", int(xp.sum(stat > t_thr)), nn, law10)

# ---------- Conformal calibration: Beta law and calibration-size numbers ----------
def p_exceed(n, a):
    kk = math.ceil((n + 1) * (1 - a))
    if kk > n:
        return 1.0
    return float(stats.beta.sf(2 * a, n + 1 - kk, kk))
for a, paper_first in ((1e-2, 149), (1e-3, 1497), (1e-4, 14978)):
    first = next(n for n in range(10, 10 ** 6) if p_exceed(n, a) <= 0.05)
    # 'for every n beyond about 3.15/alpha'
    beyond = 3.15 / a
    viol = [n for n in range(int(beyond), int(beyond) + int(2 / a)) if p_exceed(n, a) > 0.05]
    ok = first == paper_first and not viol
    log(f"{'OK ' if ok else 'BAD'} calibration size alpha={a:g}: first n = {first} (paper {paper_first}); violations beyond 3.15/alpha in next 2/alpha: {len(viol)}")
    ok_all &= ok
log(f"    P(Pfa>2a) at n=23000, a=1e-4: {p_exceed(23000, 1e-4):.4f} (paper 0.056)")
# Beta law by simulation (conditional Pfa of the k-th order statistic)
n_cal, a = 1000, 0.01
kk = math.ceil((n_cal + 1) * (1 - a))
U = xp.sort(rng.random((20000, n_cal)), axis=1)[:, kk - 1]
pfa_cond = to_np(1 - U)
ks = stats.kstest(pfa_cond, stats.beta(n_cal + 1 - kk, kk).cdf)
log(f"{'OK ' if ks.pvalue > 1e-3 else 'BAD'} conditional Pfa ~ Beta(n+1-k,k): KS p = {ks.pvalue:.3f}")
ok_all &= ks.pvalue > 1e-3

# ---------- Theorem 1: certified clipped / binary integration ----------
def certified_trial(n_cal, n_test, hit_cal, hit_test, attack, kappa=6.0, eta=6.0, kH=8, alpha=0.01):
    """hit_* : functions returning boolean (n, m+K) pulse-hit masks; attack: how corrupted values are chosen."""
    def episode(n):
        return ar1(n, m + K, rho, tex=True)
    def corrupted_innov_mask(pulse_hits):
        # a hit at pulse t corrupts innovations t and t+1 (AR(1))
        c = pulse_hits.copy()
        c[:, 1:] |= pulse_hits[:, :-1]
        return c
    def stats_from(e2, cmask, worst):
        hist, dw = e2[:, :m], e2[:, m:]
        if worst:
            hist = xp.where(cmask[:, :m], 0.0, hist)
        s2 = xp.sort(hist, axis=1)[:, kH - 1]
        r = dw / s2[:, None]
        clip = xp.minimum(r, kappa)
        binr = (r > eta).astype(float)
        if worst:
            clip = xp.where(cmask[:, m:], kappa, clip)
            binr = xp.where(cmask[:, m:], 1.0, binr)
        return clip.sum(1), binr.sum(1)
    # calibration: worst case over amplitudes with hits from the hit model
    xc = episode(n_cal)
    e2c = xp.abs(innov(xc, rho)) ** 2
    Wc, Bc = stats_from(e2c, corrupted_innov_mask(hit_cal(n_cal)), True)
    kk = math.ceil((n_cal + 1) * (1 - alpha))
    qW, qB = xp.sort(Wc)[kk - 1], xp.sort(Bc)[kk - 1]
    # test: actual interference values chosen by the attack
    xt = episode(n_test)
    ht = hit_test(n_test)
    if attack == "huge":
        xt = xt + xp.where(ht, cn(xt.shape) * 1e3, 0)
    elif attack == "matched":            # amplitude just large enough to push each corrupted dwell ratio near the clip
        xt = xt + xp.where(ht, cn(xt.shape) * 2.5 * xp.sqrt(xp.mean(xp.abs(xt) ** 2, 1, keepdims=True)), 0)
    elif attack == "cancel":             # adversary zeroes the hit samples (shrinks the history scale)
        xt = xp.where(ht, 0, xt)
    e2t = xp.abs(innov(xt, rho)) ** 2
    T, Bt = stats_from(e2t, None, False)
    return float(xp.mean(T > qW)), float(xp.mean(Bt > qB))


def bern(p):
    return lambda n: rng.random((n, m + K)) < p


def bursty(p, L):                      # bursts of L consecutive pulses, same average rate p
    def f(n):
        starts = rng.random((n, m + K)) < p / L
        out = xp.zeros((n, m + K), dtype=bool)
        for j in range(L):
            out[:, j:] |= starts[:, :m + K - j]
        return out
    return f


nc, nt = 200_000, 1_000_000 if GPU else 200_000
for attack in ("huge", "matched", "cancel"):
    pc, pb = certified_trial(nc, nt, bern(0.05), bern(0.05), attack)
    ok = pc <= 0.01 + 4 * math.sqrt(0.01 * 0.99 / nt) and pb <= 0.01 + 4 * math.sqrt(0.01 * 0.99 / nt)
    log(f"{'OK ' if ok else 'BAD'} Thm1 Bernoulli 5% hits, attack={attack:<8s}: certified clip Pfa {pc:.4f}, binary {pb:.4f} (bound 0.01)")
    ok_all &= ok
pc, pb = certified_trial(nc, nt, bern(0.05), bursty(0.05, 6), "huge")
log(f"    Thm1 MISSPECIFIED (bursty L=6, same 5% rate, calibrated on Bernoulli): clip Pfa {pc:.4f}, binary {pb:.4f} "
    f"-> {'violates' if max(pc, pb) > 0.0125 else 'does not violate'} the bound, as the dominance condition fails")
pc, pb = certified_trial(nc, nt, bursty(0.05, 6), bursty(0.05, 6), "huge")
ok = max(pc, pb) <= 0.01 + 4 * math.sqrt(0.01 * 0.99 / nt)
log(f"{'OK ' if ok else 'BAD'} Thm1 bursty hits, calibrated on the bursty model: clip Pfa {pc:.4f}, binary {pb:.4f}")
ok_all &= ok

log(f"\nALL CHECKS {'PASSED' if ok_all else 'FAILED'}  (GPU={GPU}, N={N})")
open(os.path.join(os.path.dirname(os.path.abspath(__file__)), "theory_check_independent_output.txt"), "w", encoding="utf8").write("\n".join(OUT) + "\n")
sys.exit(0 if ok_all else 1)
