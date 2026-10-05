"""Complex-valued prediction-region methods for episodes X = (H_1..H_m, Y).

All regions are discs {y : |y - center(H)| <= q * scale(H)}; q is a split-conformal quantile
(or a closed-form Gaussian constant for plug-in methods).
"""
import math
import numpy as np


def conformal_quantile(scores, alpha):
    n = len(scores); k = math.ceil((n + 1) * (1 - alpha))
    return math.inf if k > n else float(np.partition(scores, k - 1)[k - 1])


# ---------- AR(1) fitting ----------
def fit_ols(X, a=0.98):
    r = np.sum(np.conj(X[:, :-1]) * X[:, 1:]) / np.sum(abs(X[:, :-1]) ** 2)
    return r if abs(r) <= a else a * r / abs(r)


def innovation_scale(H, r):
    m = H.shape[1]
    e = (1 - abs(r) ** 2) * abs(H[:, 0]) ** 2 + np.sum(abs(H[:, 1:] - r * H[:, :-1]) ** 2, 1)
    return np.sqrt(e / m)


# ---------- clutter + noise model ----------
def ar1_corr(p, rho):
    j = np.arange(p); d = j[:, None] - j[None, :]
    return np.where(d >= 0, rho ** np.abs(d), np.conj(rho) ** np.abs(d)).astype(complex)


def fit_noise_model(X):
    """Moment fit of E[x_{j+1} conj(x_j) | episode power P] = rho (P - nu), weighted by 1/P^2.
    Returns (rho, nu) with nu >= 0 (noise power, same units as the data)."""
    P = np.mean(abs(X) ** 2, 1)
    z = np.mean(X[:, 1:] * np.conj(X[:, :-1]), 1)
    w = 1 / P ** 2
    A = np.column_stack([P, np.ones_like(P)]) * np.sqrt(w)[:, None]
    coef, *_ = np.linalg.lstsq(A.astype(complex), z * np.sqrt(w), rcond=None)
    rho = coef[0]
    nu = float(max(np.real(-coef[1] / rho), 0.0))
    if abs(rho) > 0.98: rho = 0.98 * rho / abs(rho)
    return rho, nu


def _backend():
    """Array module for the likelihood fits: CuPy (GPU, float64) if INARCP_GPU=1, else NumPy.
    Same operations in the same order on both; results agree to floating-point tolerance."""
    import os
    if os.environ.get("INARCP_GPU") == "1":
        import cupy
        return cupy
    return np


def _npmle_value(Xd, d, V, nu, cgrid, em_iter, xp):
    """Negative mean marginal log-likelihood (up to a constant) and EM texture weights for
    X_i ~ CN(0, nu (c R + I)), c on cgrid, with R = V diag(d) V^H. Xd lives on the backend."""
    proj = xp.abs(Xd @ xp.asarray(np.conj(V))) ** 2                         # (n, p)
    g = nu * (xp.outer(xp.asarray(cgrid), xp.asarray(d)) + 1)             # (G, p)
    ll = -(xp.log(g).sum(1)[None, :] + proj @ (1 / g).T)                   # (n, G)
    mx = ll.max(1, keepdims=True); lik = xp.exp(ll - mx)
    w = xp.full(len(cgrid), 1 / len(cgrid))
    for _ in range(em_iter):
        post = lik * w; post /= post.sum(1, keepdims=True); w = post.mean(0)
    val = -xp.mean(xp.log(lik @ w) + mx[:, 0])
    return float(val), (w.get() if xp is not np else w)


def fit_mixture_model(X, cgrid=np.logspace(-2, 5, 50), em_iter=60, start=None):
    """Marginal-likelihood fit of X_i ~ CN(0, nu (c_i R_rho + I)), c_i ~ discrete NPMLE on cgrid.
    Profile: for each (rho, nu), mixture weights by EM; outer Nelder-Mead over
    (atanh|rho|, arg rho, log nu). Returns rho, nu, weights."""
    from scipy.optimize import minimize
    p = X.shape[1]; xp = _backend(); Xd = xp.asarray(X)

    def profile(th, return_w=False):
        rho = np.tanh(th[0]) * np.exp(1j * th[1]); nu = np.exp(th[2])
        d, V = np.linalg.eigh(ar1_corr(p, rho))
        val, w = _npmle_value(Xd, d, V, nu, cgrid, em_iter, xp)
        return (val, w) if return_w else val

    if start is None:
        r0, n0 = fit_noise_model(X)
        start = [np.arctanh(min(abs(r0), 0.97)), np.angle(r0), np.log(max(n0, 1e-3 * np.mean(abs(X) ** 2)))]
    res = minimize(profile, start, method="Nelder-Mead", options=dict(xatol=1e-4, fatol=1e-7, maxiter=600))
    val, w = profile(res.x, True)
    rho = np.tanh(res.x[0]) * np.exp(1j * res.x[1])
    return rho, float(np.exp(res.x[2])), w


# ---------- general AR(p) clutter correlation via reflection coefficients ----------
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


def theta_to_corr(th, dim, p):
    kappa = np.tanh(th[:p]) * np.exp(1j * th[p:2 * p])
    return arp_corr(dim, reflection_to_ar(kappa))


def fit_mixture_arp(X, p, cgrid=np.logspace(-2, 5, 50), em_iter=40, maxiter=1500):
    """Clutter+noise NPMLE with AR(p) clutter correlation. Params: p reflection magnitudes (atanh),
    p phases, log nu. Start: AR(p) LS on the top-power fifth of episodes (clutter-dominated)."""
    from scipy.optimize import minimize
    dim = X.shape[1]
    P = np.mean(abs(X) ** 2, 1); top = X[P >= np.quantile(P, 0.8)]
    # start: reflection coefficients from Burg-like LS fits of increasing order
    kap = []
    for q in range(1, p + 1):
        Y = top[:, q:].reshape(-1)
        Z = np.stack([top[:, q - k:dim - k] for k in range(1, q + 1)], -1).reshape(-1, q)
        aq, *_ = np.linalg.lstsq(Z, Y, rcond=None); kap.append(aq[-1])
    kap = np.array(kap); kap = np.where(abs(kap) > 0.97, 0.97 * kap / abs(kap), kap)
    th0 = np.concatenate([np.arctanh(abs(kap)), np.angle(kap), [np.log(np.quantile(P, 0.05))]])

    xp = _backend(); Xd = xp.asarray(X)

    def profile(th, ret=False):
        R = theta_to_corr(th, dim, p); nu = np.exp(th[-1])
        d, V = np.linalg.eigh(R)
        val, w = _npmle_value(Xd, np.maximum(d, 1e-12), V, nu, cgrid, em_iter, xp)
        return (val, w, R, nu) if ret else val

    res = minimize(profile, th0, method="Nelder-Mead", options=dict(maxiter=maxiter, xatol=1e-4, fatol=1e-7))
    val, w, R, nu = profile(res.x, True)
    return R, nu, w, res


class NoiseAwareGeneral:
    """NA predictive with a general clutter correlation R ((m+1)x(m+1)); per-episode CNR by
    history likelihood on a grid; conformal calibration done by the caller."""

    def __init__(self, R, nu, grid=np.logspace(-3, 6, 721)):
        m = R.shape[0] - 1; self.m, self.nu, self.grid = m, nu, grid
        RH, rHY = R[:m, :m], R[:m, m]
        self.d, self.U = np.linalg.eigh(RH)
        W, V = [], []
        for c in grid:
            w_ = np.linalg.solve(c * RH + np.eye(m), c * rHY)
            W.append(np.conj(w_)); V.append(float(np.real(c + 1 - np.conj(c * rHY) @ w_)))
        self.W, self.V = np.array(W), np.array(V)

    def center_scale(self, H):
        proj = abs(H @ np.conj(self.U)) ** 2 / self.nu
        gd = np.outer(self.grid, np.maximum(self.d, 1e-12)) + 1; logdet = np.log(gd).sum(1)
        j = np.empty(len(H), int)
        for s in range(0, len(H), 1000):
            j[s:s + 1000] = np.argmax(-(logdet[None, :] + proj[s:s + 1000] @ (1 / gd).T), 1)
        return np.sum(self.W[j] * H, 1), np.sqrt(self.nu * self.V[j]), j


class EmpiricalBayes:
    """Predictive mean / sd of Y | H under X ~ CN(0, nu (c R + I)), c ~ fitted discrete prior w on
    cgrid (texture integrated out, not plugged in). Disc: center = predictive mean,
    scale = predictive sd; calibrated conformally."""

    def __init__(self, m, rho, nu, cgrid, w, tol=1e-12):
        keep = w > tol
        self.c, self.w, self.nu, self.m = cgrid[keep], w[keep], nu, m
        R = ar1_corr(m + 1, rho); RH, rHY = R[:m, :m], R[:m, m]
        self.d, self.U = np.linalg.eigh(RH)
        W, V = [], []
        for c in self.c:
            SHH = c * RH + np.eye(m); w_ = np.linalg.solve(SHH, c * rHY)
            W.append(np.conj(w_)); V.append(float(np.real(c + 1 - np.conj(c * rHY) @ w_)))
        self.W, self.V = np.array(W), np.array(V)             # (G, m), (G,)

    def center_scale(self, H):
        proj = abs(H @ np.conj(self.U)) ** 2 / self.nu
        gd = np.outer(self.c, self.d) + 1
        ll = -(np.log(gd).sum(1)[None, :] + proj @ (1 / gd).T) + np.log(self.w)[None, :]
        ll -= ll.max(1, keepdims=True); post = np.exp(ll); post /= post.sum(1, keepdims=True)
        mu = H @ self.W.T                                         # (n, G) component means
        mbar = np.sum(post * mu, 1)
        var = np.sum(post * (self.nu * self.V[None, :] + abs(mu - mbar[:, None]) ** 2), 1)
        return mbar, np.sqrt(var), post @ np.log(self.c)          # last: posterior mean log-CNR


class NoiseAware:
    """Gaussian predictive for X | c ~ CN(0, nu (c R_rho + I)); c estimated per episode by the
    history-only likelihood. nu = 0 reduces exactly to IN-ARCP (innovation-normalized AR(1))."""

    def __init__(self, m, rho, nu, grid=np.logspace(-3, 6, 721)):
        self.m, self.rho, self.nu, self.grid = m, rho, nu, grid
        R = ar1_corr(m + 1, rho)
        RH, rHY = R[:m, :m], R[:m, m]
        d, U = np.linalg.eigh(RH)
        self.d, self.U = d, U
        # predictive weights and variance on the CNR grid (units of nu)
        W, V = [], []
        for c in grid:
            SHH = c * RH + np.eye(m); sHY = c * rHY
            w = np.linalg.solve(SHH, sHY)      # E[Y|H] = w^H H  (Hermitian convention below)
            W.append(np.conj(w)); V.append(float(np.real(c + 1 - np.conj(sHY) @ w)))
        self.W, self.V = np.array(W), np.array(V)

    def cnr_hat(self, H):
        if self.nu == 0:
            return None
        proj = abs(H @ np.conj(self.U)) ** 2 / self.nu            # |u_k^H h|^2 / nu
        gd = np.outer(self.grid, self.d) + 1                       # (G, m)
        logdet = np.log(gd).sum(1)
        out = np.empty(len(H), int)
        for s in range(0, len(H), 1000):
            ll = -(logdet[None, :] + proj[s:s + 1000] @ (1 / gd).T)
            out[s:s + 1000] = np.argmax(ll, 1)
        return out

    def center_scale(self, H):
        if self.nu == 0:
            return self.rho * H[:, -1], innovation_scale(H, self.rho), None
        j = self.cnr_hat(H)
        center = np.sum(self.W[j] * H, 1)
        scale = np.sqrt(self.nu * self.V[j])
        return center, scale, j
