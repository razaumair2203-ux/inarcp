"""Texture-invariant conformal prediction discs for complex (I/Q) autoregressive episodes.

Each row of the input arrays is one independent episode of complex samples. The history is
the first m columns; the response is the next sample. Regions are discs
    {y : |y - center(h)| <= q * scale(h)}.

ComplexINARCP  : AR(p) centre, conditional-innovation RMS scale (texture-equivariant).
NoiseAwareINARCP: clutter + white-noise model X | c ~ CN(0, nu (c R + I)) fitted by marginal
                  likelihood with a nonparametric texture distribution; per-episode CNR by history
                  likelihood; Gaussian predictive centre/scale. nu -> 0 recovers the IN-ARCP score.
exact_coverage : elementary exact P(score <= q) for X ~ CN(0, Sigma) and a linear normalized score.

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


def _arp_center_scale(H, a):
    p, m = len(a), H.shape[1]
    center = sum(a[k] * H[:, m - 1 - k] for k in range(p))
    res = H[:, p:] - sum(a[k] * H[:, p - 1 - k:m - 1 - k] for k in range(p))
    scale = np.sqrt(np.mean(np.abs(res) ** 2, 1))
    if np.any(scale <= 0):
        raise ValueError("A history has zero innovation energy; its normalized score is undefined.")
    return center, scale


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
    """AR(p) centre fitted by pooled least squares on training episodes (all transitions)."""

    def __init__(self, order=1, alpha=0.1):
        super().__init__(alpha)
        if int(order) != order or order < 1:
            raise ValueError("order must be a positive integer.")
        self.order = int(order)

    def fit(self, episodes):
        X = _complex_rows(episodes, "episodes")
        if X.shape[1] < self.order + 2:
            raise ValueError("Episodes are too short for this AR order.")
        self.m_ = X.shape[1] - 1
        self.coef_ = _fit_arp(X, self.order)
        self.q_ = None
        return self

    def _center_scale(self, H):
        return _arp_center_scale(H, self.coef_)


def ar1_corr(dim, rho):
    j = np.arange(dim); d = j[:, None] - j[None, :]
    return np.where(d >= 0, rho ** np.abs(d), np.conj(rho) ** np.abs(d)).astype(complex)


class NoiseAwareINARCP(_SplitConformalDisc):
    """Clutter (AR(1) correlation) + white noise; see module docstring.

    cnr_grid: support of the nonparametric texture distribution in the fit and the per-episode
    CNR search grid. Fitting uses Nelder-Mead on (atanh|rho|, arg rho, log nu) with EM-profiled
    texture weights; it is a numerical optimizer without a global-optimality certificate.
    """

    def __init__(self, alpha=0.1, cnr_grid=None, em_iter=60):
        super().__init__(alpha)
        self.cnr_grid = np.logspace(-2, 5, 50) if cnr_grid is None else np.asarray(cnr_grid, float)
        self.em_iter = int(em_iter)

    def fit(self, episodes):
        from scipy.optimize import minimize
        X = _complex_rows(episodes, "episodes"); p = X.shape[1]
        self.m_ = p - 1
        g_ = self.cnr_grid

        def profile(th, ret=False):
            rho = np.tanh(th[0]) * np.exp(1j * th[1]); nu = np.exp(th[2])
            d, V = np.linalg.eigh(ar1_corr(p, rho))
            proj = np.abs(X @ np.conj(V)) ** 2
            g = nu * (np.outer(g_, d) + 1)
            ll = -(np.log(g).sum(1)[None, :] + proj @ (1 / g).T)
            mx = ll.max(1, keepdims=True); lik = np.exp(ll - mx)
            w = np.full(len(g_), 1 / len(g_))
            for _ in range(self.em_iter):
                post = lik * w; post /= post.sum(1, keepdims=True); w = post.mean(0)
            val = -np.mean(np.log(lik @ w) + mx[:, 0])
            return (val, w) if ret else val

        r0 = np.sum(np.conj(X[:, :-1]) * X[:, 1:]) / np.sum(np.abs(X[:, :-1]) ** 2)
        P = np.mean(np.abs(X) ** 2, 1)
        th0 = [np.arctanh(min(abs(r0), 0.97)), np.angle(r0), np.log(np.quantile(P, 0.05))]
        res = minimize(profile, th0, method="Nelder-Mead",
                       options=dict(xatol=1e-4, fatol=1e-7, maxiter=600))
        _, self.texture_weights_ = profile(res.x, True)
        self.rho_ = complex(np.tanh(res.x[0]) * np.exp(1j * res.x[1]))
        self.nu_ = float(np.exp(res.x[2])); self.converged_ = bool(res.success)
        self._prepare()
        self.q_ = None
        return self

    def _prepare(self, grid=np.logspace(-3, 6, 721)):
        m = self.m_; R = ar1_corr(m + 1, self.rho_)
        RH, rHY = R[:m, :m], R[:m, m]
        self._d, self._U = np.linalg.eigh(RH); self._grid = grid
        W, V = [], []
        for c in grid:
            w = np.linalg.solve(c * RH + np.eye(m), c * rHY)
            W.append(np.conj(w)); V.append(float(np.real(c + 1 - np.conj(c * rHY) @ w)))
        self._W, self._V = np.array(W), np.array(V)

    def _center_scale(self, H):
        proj = np.abs(H @ np.conj(self._U)) ** 2 / self.nu_
        gd = np.outer(self._grid, self._d) + 1; logdet = np.log(gd).sum(1)
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
