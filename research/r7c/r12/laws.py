"""Closed-form laws of whitened-innovation detection (R12).

Setting: complex AR(1) speckle with coefficient rho, pure compound-Gaussian clutter (the texture
cancels from every statistic here), true coefficient. Innovations eps_1 = sqrt(1-|rho|^2) x_1,
eps_t = x_t - rho x_{t-1}; under H0 they are i.i.d. CN(0, sigma_e^2). A Swerling-1 target
sqrt(S P) g e^{j w t} (g ~ CN(0,1), common to all pulses) that starts at pulse t0 has whitened
amplitude g sqrt(Sw) at t0 and g sqrt(Sw) d(w) at t > t0, with Sw = S / (1 - |rho|^2) and
d(w) = 1 - rho e^{-jw}. Sw |d|^2 = S P / S_c(w), the SCR times the whitening factor at w.

Every function returns an exact probability under this model unless its docstring says otherwise.
"""
import math
import numpy as np
from scipy.special import comb, gammaln, betaln, hyp2f1
from scipy.stats import beta as beta_dist


# ---------------------------------------------------------------- per-look (IN-ARCP) score
def q2_in(alpha, m):
    """Threshold q^2 of the IN-ARCP score |eps_Y| / s (s^2 = mean of m history innovation powers)."""
    return m * (alpha ** (-1.0 / m) - 1.0)


def pfa_in(q2, m):
    return (1.0 + q2 / m) ** (-m)


def pd_rank1(q2, m, a, b):
    """P(|w_Y + g u_Y|^2 > (q2/m) sum_{j<=m} |w_j + g u_j|^2) for w ~ CN(0, I), g ~ CN(0, 1),
    a = |u_Y|^2, b = ||u_H||^2 (any rank-one Swerling-1 signature). Exact closed form:
    the two nonzero eigenvalues solve lam^2 - (1 + a - beta - beta b) lam - beta (1 + a + b) = 0."""
    beta = q2 / m
    B = 1.0 + a - beta - beta * b
    disc = np.sqrt(B * B + 4.0 * beta * (1.0 + a + b))
    lp, lm = (B + disc) / 2.0, (B - disc) / 2.0
    return lp / (lp - lm) * (1.0 + beta / lp) ** (-(m - 1))


def onset_signature(Sw, d2, look):
    """(a, b) of a persistent target observed `look` pulses after its onset (look 0: target in Y only)."""
    if look == 0:
        return Sw, 0.0
    return Sw * d2, Sw * (1.0 + (look - 1) * d2)


def d2_of(rho, w):
    return np.abs(1.0 - rho * np.exp(-1j * np.asarray(w))) ** 2


def pd_onset(q2, m, S, rho, w, look):
    Sw = S / (1.0 - abs(rho) ** 2)
    a, b = onset_signature(Sw, d2_of(rho, w), look)
    return pd_rank1(q2, m, a, b)


def pd_onset_random_doppler(q2, m, S, rho, look, n=4096):
    w = -np.pi + 2 * np.pi * (np.arange(n) + 0.5) / n
    return float(np.mean(pd_onset(q2, m, S, rho, w, look)))


def visibility_horizon(q2, m, d2):
    """A persistent target of unbounded SCR is detected at look l with probability bounded away from 0
    iff l < 1 + m/q2 - 1/d2 (from the sign of lam_+ as Sw -> inf)."""
    return 1.0 + m / q2 - 1.0 / d2


# ---------------------------------------------------------------- order-statistic score
def pfa_os(q2, m, k):
    return float(np.prod([(m - i) / (m - i + q2) for i in range(k)]))


def q2_os(alpha, m, k):
    from scipy.optimize import brentq
    return brentq(lambda x: pfa_os(x, m, k) - alpha, 1e-9, 1e9)


def pd_os_strong(q2, m, k, a, j):
    """Strong-target limit: j contaminated history innovations (j <= m - k) dominate, so the scale is the
    k-th smallest of m - j clean powers; Y carries a Swerling-1 component of whitened power a."""
    if j > m - k:
        return 0.0
    return pfa_os(q2 / (1.0 + a), m - j, k)


def pd_os_exact(q2, m, k, sig_hist, a, ng=400, nx=4000):
    """Exact P(|w_Y + g u_Y|^2 > q2 * kth-smallest_j |w_j + g u_j|^2) by quadrature over |g|^2 and the
    order statistic; sig_hist: whitened target powers |u_j|^2 of the m history innovations (0 if clean)."""
    from scipy.stats import ncx2, expon
    sig = np.asarray(sig_hist, float)
    u = (np.arange(ng) + 0.5) / ng
    xg, wg = -np.log1p(-u), np.full(ng, 1.0 / ng)                    # |g|^2 ~ Exp(1), midpoint in its CDF
    x = np.linspace(0, 1, nx + 1)[1:] ** 2 * 60.0                      # support of the k-th smallest
    tot = 0.0
    for G, W in zip(xg, wg):
        F = np.empty((m, len(x)))
        for j in range(m):
            F[j] = expon.cdf(x) if sig[j] == 0 else ncx2.cdf(2 * x, 2, 2 * G * sig[j])
        # P(X_(k) <= x) = P(at least k of m below x): Poisson-binomial by dynamic programming
        pb = np.zeros((m + 1, len(x))); pb[0] = 1.0
        for j in range(m):
            pb[1:] = pb[1:] * (1 - F[j]) + pb[:-1] * F[j]; pb[0] *= (1 - F[j])
        cdf = pb[k:].sum(0)
        dens = np.gradient(cdf, x)
        py = ncx2.sf(2 * q2 * x, 2, 2 * G * a) if a > 0 else np.exp(-q2 * x)
        tot += W * np.trapezoid(py * dens, x)
    return float(tot)


# ---------------------------------------------------------------- dwell integration with a shared history
def pfa_dwell(t, m, K):
    """P(sum of K dwell innovation powers > t * mean of m history powers), i.i.d. innovations."""
    tau = t / m
    i = np.arange(K)
    return float(np.sum(np.exp(gammaln(m + i) - gammaln(m) - gammaln(i + 1)) * tau ** i / (1 + tau) ** (m + i)))


def t_dwell(alpha, m, K):
    from scipy.optimize import brentq
    return brentq(lambda t: pfa_dwell(t, m, K) - alpha, 1e-9, 1e9)


def pd_dwell(t, m, K, bD):
    """Swerling-1 target of whitened energy bD in the dwell (one eigenvalue 1 + bD, K - 1 unit ones):
    closed form of P((1 + bD) E + Gamma_{K-1} > (t/m) Gamma_m)."""
    tau = t / m; c = 1.0 + bD
    if bD < 1e-9:
        return pfa_dwell(t, m, K)
    i = np.arange(K - 1)
    lg = gammaln(m + i) - gammaln(m) - gammaln(i + 1)
    A1 = np.sum(np.exp(lg) * tau ** i / (1 + tau) ** (m + i))
    kap = tau * (1 - 1 / c)
    A2 = (1 + tau / c) ** (-m) - np.sum(np.exp(lg) * kap ** i / (1 + tau) ** (m + i))
    return float(A1 + (1 - 1 / c) ** (-(K - 1)) * A2)


def dwell_energy(Sw, d2, K):
    """Whitened energy of a persistent target that starts at the first dwell pulse."""
    return Sw * (1.0 + (K - 1) * d2)


def power_nci_eigs(rho, K):
    """Eigenvalues of the K-pulse clutter correlation; K_eff = K^2 / sum_ij |rho|^{2|i-j|}."""
    j = np.arange(K); R = np.abs(rho) ** np.abs(j[:, None] - j[None, :])
    lam = np.linalg.eigvalsh(np.where(j[:, None] >= j[None, :], rho ** np.abs(j[:, None] - j[None, :]),
                                      np.conj(rho) ** np.abs(j[:, None] - j[None, :])))
    return lam, K ** 2 / np.sum(R ** 2)


def sf_weighted_exp(lam, x):
    """P(sum_k lam_k E_k > x) for distinct positive lam (hypoexponential)."""
    lam = np.asarray(lam, float); out = 0.0
    for i, li in enumerate(lam):
        out += np.exp(-x / li) * np.prod([li / (li - lj) for j, lj in enumerate(lam) if j != i])
    return float(out)


# ---------------------------------------------------------------- self-normalized whitened Doppler (P-ANMF)
def pfa_snd_bin(t, K):
    """Known Doppler: |DFT_j(eps)|^2 / (K ||eps||^2) ~ Beta(1, K-1)."""
    return (1 - t) ** (K - 1)


def pd_snd_bin(t, K, Sw, d2):
    """Known on-grid Doppler, target present in every dwell innovation: the NMF/ACE law with SCR -> K Sw |d|^2."""
    return (1 + t / ((1 - t) * (1 + K * Sw * d2))) ** (-(K - 1))


def _pinter(t, mu, J):
    """P(I_j > t sum_i I_i for all j in J), I_i ~ Exp(mean mu_i) independent (|J| t < 1)."""
    if len(J) * t >= 1:
        return 0.0
    th = t * np.sum(1.0 / mu[list(J)]) / (1 - len(J) * t)
    return float(np.prod(1.0 / (1.0 + th * mu)) / (1 - len(J) * t))


def pfa_snd_max(t, K):
    """Fisher's g: P(max_j I_j / sum I > t) for K i.i.d. exponential periodogram ordinates."""
    r = np.arange(1, int(math.floor(1 / t)) + 1)
    r = r[r <= K]
    return float(np.sum((-1.0) ** (r - 1) * comb(K, r) * (1 - r * t) ** (K - 1)))


def pd_snd_max(t, K, Sw, d2):
    """P(max over the K DFT bins > t) with a Swerling-1 target on one bin (mean 1 + K Sw |d|^2):
    inclusion-exclusion with the exact intersection probability of _pinter."""
    c = 1.0 + K * Sw * d2
    mu = np.ones(K); mu[0] = c
    out = 0.0
    for r in range(1, K + 1):
        if r * t >= 1:
            break
        pno = _pinter(t, mu, list(range(1, r + 1))) if r <= K - 1 else 0.0
        pyes = _pinter(t, mu, [0] + list(range(1, r)))
        out += (-1) ** (r - 1) * (comb(K - 1, r) * pno + comb(K - 1, r - 1) * pyes)
    return float(out)


def t_snd_max(alpha, K):
    from scipy.optimize import brentq
    return brentq(lambda t: pfa_snd_max(t, K) - alpha, 1e-9, 1 - 1e-12)


# ---------------------------------------------------------------- ANMF (ACE) with sample covariance
def pfa_anmf_scm(t, N, Ks):
    """Kraut-Scharf law of the adaptive normalized matched filter with the SCM of Ks secondary vectors."""
    L = Ks - N + 1
    return float((1 - t) ** L * hyp2f1(L + 1, L, Ks + 1, t))


def t_anmf(alpha, N, Ks, fp=False):
    """Threshold from the SCM law; fp=True applies the fixed-point (Tyler) equivalence Ks -> Ks N/(N+1)."""
    from scipy.optimize import brentq
    Ke = Ks * N / (N + 1.0) if fp else Ks
    f = lambda t: _pfa_anmf_real(t, N, Ke) - alpha
    return brentq(f, 1e-9, 1 - 1e-9)


def _pfa_anmf_real(t, N, Ks):
    L = Ks - N + 1
    return float((1 - t) ** L * hyp2f1(L + 1, L, Ks + 1, t))


# ---------------------------------------------------------------- conformal calibration
def conformal_rank(n, alpha):
    return math.ceil((n + 1) * (1 - alpha))


def pfa_conditional_law(n, alpha):
    """Test false-alarm probability given the calibration set, for continuous i.i.d. scores: Beta(n+1-k, k)."""
    k = conformal_rank(n, alpha)
    return beta_dist(n + 1 - k, k)


def n_required(alpha, ratio=2.0, conf=0.95):
    """Smallest n with P(conditional Pfa > ratio * alpha) <= 1 - conf."""
    n = int(1 / alpha)
    while pfa_conditional_law(n, alpha).sf(ratio * alpha) > 1 - conf:
        n = int(n * 1.05) + 1
    return n


def mean_pd_conformal(n, alpha, gamma):
    """E[U^gamma], U ~ Beta(n+1-k, k): expected Pd of a known-scale Swerling-1 detector (Pd = Pfa^gamma,
    gamma = 1/(1+SNR)) whose threshold is the conformal quantile."""
    k = conformal_rank(n, alpha)
    return float(np.exp(betaln(n + 1 - k + gamma, k) - betaln(n + 1 - k, k)))


# ---------------------------------------------------------------- certified integration under pulsed interference
def clipped_stat(z, c):
    return np.minimum(z, c).sum(-1)


def trimmed_stat(z, t):
    return np.sort(z, -1)[..., :z.shape[-1] - t].sum(-1)


def corrupted_innovations(hits, p=1):
    """Innovation indices corrupted by hit pulses: innovation t uses samples t-p..t, so a hit at pulse h
    corrupts innovations h..h+p (clipped to the episode). hits: bool (n, L) -> bool (n, L)."""
    c = hits.copy()
    for i in range(1, p + 1):
        c[:, i:] |= hits[:, :-i]
    return c


def worst_case(hist_pow, dwell_pow, bad_hist, bad_dwell, kH, stat, **kw):
    """Largest value the dwell statistic can take over every interference amplitude on the given corrupted
    innovations, computed from the clean innovations only. The history scale is the kH-th smallest history
    power; its minimum over the corrupted entries is attained by setting them to zero. Clipped terms are at
    most c; for the trimmed sum a corrupted term is worst at +inf; for binary integration it is an exceedance.
    stat: 'clip' (kw c), 'trim' (kw t), 'bin' (kw eta: per-look threshold on z)."""
    s2 = np.partition(np.where(bad_hist, 0.0, hist_pow), kH - 1, 1)[:, kH - 1]
    with np.errstate(divide="ignore", invalid="ignore"):
        z = dwell_pow / s2[:, None]
    if stat == "clip":
        return np.where(bad_dwell, kw["c"], np.minimum(z, kw["c"])).sum(1)
    if stat == "trim":
        K = z.shape[1]
        return np.sort(np.where(bad_dwell, np.inf, z), 1)[:, :K - kw["t"]].sum(1)
    if stat == "bin":
        return (bad_dwell | (z > kw["eta"])).sum(1)
    raise ValueError(stat)


def robust_stat(hist_pow, dwell_pow, kH, stat, **kw):
    """The deployed statistic (no knowledge of hits): equals worst_case with no corrupted innovations."""
    f = np.zeros(hist_pow.shape, bool); g = np.zeros(dwell_pow.shape, bool)
    return worst_case(hist_pow, dwell_pow, f, g, kH, stat, **kw)


def hit_tail(L, p, J):
    """P(Binomial(L, p) > J)."""
    from scipy.stats import binom
    return float(binom.sf(J, L, p))
