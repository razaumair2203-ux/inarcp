"""Texture-invariant conformal prediction discs for complex (I/Q) autoregressive episodes.

Each row of the input arrays is one independent episode of complex samples. The history is
the first m columns; the response is the next sample. Regions are discs
    {y : |y - center(h)| <= q * scale(h)}.

ComplexINARCP  : AR(p) centre, conditional-innovation RMS scale (texture-equivariant), or with
                  os_rank=k the k-th smallest innovation power (order-statistic scale, OS-CFAR).
NoiseAwareINARCP: clutter + white-noise model X | c ~ CN(0, nu (c R + I)) fitted by marginal
                  likelihood with a nonparametric texture distribution; per-episode CNR by history
                  likelihood; Gaussian predictive centre/scale. nu -> 0 recovers the IN-ARCP score.
                  R is AR(1) or, with order=p, AR(p) parametrized by reflection coefficients.
exact_coverage : elementary exact P(score <= q) for X ~ CN(0, Sigma) and a linear normalized score.
os_coverage    : exact P(score <= q) of the order-statistic score under pure AR(1) compound-Gaussian
                  clutter at the true coefficient (the OS-CFAR law read as coverage).

Split conformal calibration (rank ceil((n+1)(1-alpha))) gives marginal coverage >= 1-alpha for
exchangeable calibration/test episodes. Coverage conditional on texture is exact only for the
equivariant score under pure compound-Gaussian clutter (no additive noise).
"""
import math
import numpy as np


def _complex_rows(values, name, width=None):
    x = np.asarray(values)
    if x.ndim != 2 or len(x) == 0:
        raise ValueError(f"{name} must be a nonempty 2-D array (episodes, samples).")
    if width is not None and x.shape[1] != width:
        raise ValueError(f"{name} has {x.shape[1]} columns; expected {width}.")
    x = x.astype(complex)
    if not np.isfinite(x).all():
        raise ValueError(f"{name} must be finite.")
    return x


def _rank_quantile(scores, alpha):
    n = len(scores); k = math.ceil((n + 1) * (1 - alpha))
    return (math.inf if k > n else float(np.partition(scores, k - 1)[k - 1])), k


def _fit_arp(X, p):
    L = X.shape[1]
    Y = X[:, p:].reshape(-1)
    Z = np.stack([X[:, p - k:L - k] for k in range(1, p + 1)], -1).reshape(-1, p)
    return np.linalg.lstsq(Z, Y, rcond=None)[0]


def _innovation_powers(H, a, stationary_first):
    p, m = len(a), H.shape[1]
    res = np.abs(H[:, p:] - sum(a[k] * H[:, p - 1 - k:m - 1 - k] for k in range(p))) ** 2
    if stationary_first:                                  # AR(1): (1-|a|^2)|h_1|^2, as in Corollary 3
        res = np.concatenate([(1 - abs(a[0]) ** 2) * np.abs(H[:, :1]) ** 2, res], 1)
    return res


def _arp_center_scale(H, a, os_rank=None):
    p, m = len(a), H.shape[1]
    center = sum(a[k] * H[:, m - 1 - k] for k in range(p))
    if os_rank is None:
        scale = np.sqrt(np.mean(_innovation_powers(H, a, False), 1))
    else:
        scale = np.sqrt(np.partition(_innovation_powers(H, a, p == 1), os_rank - 1, 1)[:, os_rank - 1])
    if np.any(scale <= 0):
        raise ValueError("A history has zero innovation energy; its normalized score is undefined.")
    return center, scale


def os_coverage(q, n, k):
    """P(|Y - rho H_m| <= q s_k) when s_k^2 is the k-th smallest of n i.i.d. exponential innovation
    powers with the mean of |Y - rho H_m|^2: 1 - prod_{i<k} (n-i)/(n-i+q^2) (Corollary 3)."""
    if not (1 <= k <= n):
        raise ValueError("k must satisfy 1 <= k <= n.")
    return 1.0 - float(np.prod([(n - i) / (n - i + q * q) for i in range(k)]))


class _SplitConformalDisc:
    def __init__(self, alpha=0.1):
        if not (np.isfinite(alpha) and 0 < alpha < 1):
            raise ValueError("alpha must lie strictly between zero and one.")
        self.alpha = float(alpha)

    def calibrate(self, episodes):
        X = _complex_rows(episodes, "episodes", self.m_ + 1)
        c, s = self._center_scale(X[:, :-1])
        self.q_, self.rank_ = _rank_quantile(np.abs(X[:, -1] - c) / s, self.alpha)
        self.calibration_size_ = len(X)
        return self

    def predict_disc(self, histories):
        """Return (center, radius) arrays; radius is inf if the calibration set is too small."""
        if getattr(self, "q_", None) is None:
            raise RuntimeError("Call fit and calibrate before prediction.")
        c, s = self._center_scale(_complex_rows(histories, "histories", self.m_))
        return c, self.q_ * s


class ComplexINARCP(_SplitConformalDisc):
    """AR(p) centre fitted by pooled least squares on training episodes (all transitions).

    os_rank: None for the RMS innovation scale; k for the k-th smallest of the history's innovation
    powers. These are the m-p conditional innovations, plus for order 1 the stationary first term
    (1-|a|^2)|h_1|^2, so n_innovations_ = m for order 1 and m-p otherwise. The OS scale ignores up to
    n_innovations_ - k outlying powers; a target present for j looks occupies j of them.
    """

    def __init__(self, order=1, alpha=0.1, os_rank=None):
        super().__init__(alpha)
        if int(order) != order or order < 1:
            raise ValueError("order must be a positive integer.")
        if os_rank is not None and (int(os_rank) != os_rank or os_rank < 1):
            raise ValueError("os_rank must be None or a positive integer.")
        self.order = int(order)
        self.os_rank = None if os_rank is None else int(os_rank)

    def fit(self, episodes):
        X = _complex_rows(episodes, "episodes")
        if X.shape[1] < self.order + 2:
            raise ValueError("Episodes are too short for this AR order.")
        self.m_ = X.shape[1] - 1
        self.n_innovations_ = self.m_ if self.order == 1 else self.m_ - self.order
        if self.os_rank is not None and self.os_rank > self.n_innovations_:
            raise ValueError(f"os_rank exceeds the {self.n_innovations_} innovation powers per history.")
        self.coef_ = _fit_arp(X, self.order)
        self.q_ = None
        return self

    def _center_scale(self, H):
        return _arp_center_scale(H, self.coef_, self.os_rank)


def ar1_corr(dim, rho):
    j = np.arange(dim); d = j[:, None] - j[None, :]
    return np.where(d >= 0, rho ** np.abs(d), np.conj(rho) ** np.abs(d)).astype(complex)


def reflection_to_ar(kappa):
    """Step-up (Levinson) recursion for complex reflection coefficients |kappa_k| < 1.
    Returns a with x_t = sum_k a[k] x_{t-1-k} + e_t (stationary by construction)."""
    a = np.zeros(0, complex)
    for k in kappa:
        a = np.concatenate([a - k * np.conj(a[::-1]), [k]])
    return a


def arp_corr(dim, a, L=6000):
    """Unit-variance autocorrelation matrix (dim x dim) of complex AR(p) with coefficients a."""
    p = len(a); psi = np.zeros(L, complex); psi[0] = 1
    for t in range(1, L):
        k = min(p, t); psi[t] = np.dot(a[:k], psi[t - 1::-1][:k])
    g = np.array([np.sum(psi[k:] * np.conj(psi[:L - k])) for k in range(dim)])
    g /= g[0].real
    j = np.arange(dim); d = j[:, None] - j[None, :]
    return np.where(d >= 0, g[np.abs(d)], np.conj(g[np.abs(d)]))


def _npmle(X, d, V, nu, grid, em_iter):
    """Negative mean marginal log-likelihood and EM texture weights for X_i ~ CN(0, nu (c R + I))."""
    proj = np.abs(X @ np.conj(V)) ** 2
    g = nu * (np.outer(grid, d) + 1)
    ll = -(np.log(g).sum(1)[None, :] + proj @ (1 / g).T)
    mx = ll.max(1, keepdims=True); lik = np.exp(ll - mx)
    w = np.full(len(grid), 1 / len(grid))
    for _ in range(em_iter):
        post = lik * w; post /= post.sum(1, keepdims=True); w = post.mean(0)
    return -np.mean(np.log(lik @ w) + mx[:, 0]), w


class NoiseAwareINARCP(_SplitConformalDisc):
    """Clutter (AR(1) or AR(p) correlation) + white noise; see module docstring.

    cnr_grid: support of the nonparametric texture distribution in the fit and the per-episode
    CNR search grid. Fitting uses Nelder-Mead on (atanh|rho|, arg rho, log nu) for order 1 and on
    (atanh|kappa_k|, arg kappa_k, log nu) over p reflection coefficients for order p >= 2, with
    EM-profiled texture weights; it is a numerical optimizer without a global-optimality certificate.
    em_iter and maxiter default to 60/600 for order 1 and 40/1500 for order p >= 2, the settings of
    the IPIX studies. The AR(p) fit starts from least squares on the top-power fifth of episodes.
    """

    def __init__(self, alpha=0.1, cnr_grid=None, em_iter=None, order=1, maxiter=None):
        super().__init__(alpha)
        if int(order) != order or order < 1:
            raise ValueError("order must be a positive integer.")
        self.order = int(order)
        self.cnr_grid = np.logspace(-2, 5, 50) if cnr_grid is None else np.asarray(cnr_grid, float)
        self.em_iter = (60 if self.order == 1 else 40) if em_iter is None else int(em_iter)
        self.maxiter = (600 if self.order == 1 else 1500) if maxiter is None else int(maxiter)

    def fit(self, episodes):
        from scipy.optimize import minimize
        X = _complex_rows(episodes, "episodes"); p = X.shape[1]
        if p < self.order + 2:
            raise ValueError("Episodes are too short for this AR order.")
        self.m_ = p - 1
        P = np.mean(np.abs(X) ** 2, 1); q = self.order
        if q == 1:
            def corr(th): return ar1_corr(p, np.tanh(th[0]) * np.exp(1j * th[1]))
            r0 = np.sum(np.conj(X[:, :-1]) * X[:, 1:]) / np.sum(np.abs(X[:, :-1]) ** 2)
            th0 = [np.arctanh(min(abs(r0), 0.97)), np.angle(r0), np.log(np.quantile(P, 0.05))]
        else:
            def corr(th): return arp_corr(p, reflection_to_ar(np.tanh(th[:q]) * np.exp(1j * th[q:2 * q])))
            top = X[P >= np.quantile(P, 0.8)]
            kap = np.array([_fit_arp(top, j)[-1] for j in range(1, q + 1)])
            kap = np.where(abs(kap) > 0.97, 0.97 * kap / abs(kap), kap)
            th0 = np.concatenate([np.arctanh(abs(kap)), np.angle(kap), [np.log(np.quantile(P, 0.05))]])

        def profile(th, ret=False):
            d, V = np.linalg.eigh(corr(th))
            if q > 1:
                d = np.maximum(d, 1e-12)
            val, w = _npmle(X, d, V, np.exp(th[-1]), self.cnr_grid, self.em_iter)
            return (val, w) if ret else val

        res = minimize(profile, th0, method="Nelder-Mead",
                       options=dict(xatol=1e-4, fatol=1e-7, maxiter=self.maxiter))
        _, self.texture_weights_ = profile(res.x, True)
        self.R_ = corr(res.x)
        if q == 1:
            self.rho_ = complex(np.tanh(res.x[0]) * np.exp(1j * res.x[1]))
        else:
            self.reflection_ = np.tanh(res.x[:q]) * np.exp(1j * res.x[q:2 * q])
            self.coef_ = reflection_to_ar(self.reflection_)
        self.nu_ = float(np.exp(res.x[-1])); self.converged_ = bool(res.success)
        self._prepare()
        self.q_ = None
        return self

    def _prepare(self, grid=np.logspace(-3, 6, 721)):
        m = self.m_; R = self.R_
        RH, rHY = R[:m, :m], R[:m, m]
        self._d, self._U = np.linalg.eigh(RH); self._grid = grid
        W, V = [], []
        for c in grid:
            w = np.linalg.solve(c * RH + np.eye(m), c * rHY)
            W.append(np.conj(w)); V.append(float(np.real(c + 1 - np.conj(c * rHY) @ w)))
        self._W, self._V = np.array(W), np.array(V)

    def _center_scale(self, H):
        proj = np.abs(H @ np.conj(self._U)) ** 2 / self.nu_
        gd = np.outer(self._grid, np.maximum(self._d, 1e-12)) + 1; logdet = np.log(gd).sum(1)
        j = np.empty(len(H), int)
        for s in range(0, len(H), 1000):
            j[s:s + 1000] = np.argmax(-(logdet[None, :] + proj[s:s + 1000] @ (1 / gd).T), 1)
        return np.sum(self._W[j] * H, 1), np.sqrt(self.nu_ * self._V[j])


def exact_coverage(Sigma, center_coef, Q, q):
    """P(|Y - a^T H| <= q sqrt(H^H Q H / m)) for X=(H,Y) ~ CN(0, Sigma); elementary closed form."""
    Sigma = np.asarray(Sigma, complex); a = np.asarray(center_coef, complex); m = len(a)
    b = np.zeros(m + 1, complex); b[m] = 1; b[:m] = -a
    M = np.outer(np.conj(b), b); M[:m, :m] -= (q * q / m) * np.asarray(Q, complex)
    L = np.linalg.cholesky(Sigma)
    lam = np.linalg.eigvalsh(L.conj().T @ M @ L)
    lam = lam[np.abs(lam) > 1e-12 * np.abs(lam).max()]
    pos = lam[lam > 0]
    return 1.0 - float(sum(np.prod(lj / (lj - lam[lam != lj])) for lj in pos))
