"""History-only normalization with disjoint training and calibration episodes.

Each array row is an independent episode; columns are ordered observations.
Overlapping windows from one record do not automatically satisfy this premise.
"""
import math
import numpy as np


def _history(values, width=None):
    h = np.asarray(values, dtype=float)
    if h.ndim != 2 or not len(h) or h.shape[1] < 2:
        raise ValueError("History must be a nonempty (episodes, m) array with m >= 2.")
    if width is not None and h.shape[1] != width:
        raise ValueError("History length differs from the fitted history length.")
    if not np.isfinite(h).all():
        raise ValueError("History must contain finite observations.")
    return h


def _response(values, n):
    y = np.asarray(values, dtype=float)
    if y.shape != (n,) or not np.isfinite(y).all():
        raise ValueError("Response must be a finite vector with one value per episode.")
    return y


def history_scale(history, rho):
    """RMS of the fitted innovations, including the stationary initial term.

    Zero histories are rejected: the paper assumes a positive history scale.
    An arbitrary epsilon floor would destroy exact homogeneity near zero.
    """
    h = _history(history)
    if not np.isfinite(rho) or abs(rho) >= 1:
        raise ValueError("rho must lie strictly between -1 and 1.")
    magnitude = np.max(np.abs(h), axis=1)
    if np.any(magnitude == 0):
        raise ValueError("Zero histories have undefined normalized scores.")
    z = h / magnitude[:, None]
    energy = (1-rho*rho)*z[:, 0]**2 + np.sum((z[:, 1:]-rho*z[:, :-1])**2, axis=1)
    scale = magnitude*np.sqrt(energy/h.shape[1])
    if not np.isfinite(scale).all() or np.any(scale <= 0):
        raise ValueError("History scale is outside the supported floating-point range.")
    return scale


class INARCP:
    """Fit a common zero-intercept AR(1) center, then calibrate on separate rows.

    Parameters
    ----------
    alpha : float
        Nominal miscoverage, strictly between zero and one.
    clip : float
        Symmetric coefficient clipping limit, strictly between zero and one.

    The caller must enforce disjoint training/calibration/test episodes. The
    software cannot infer independence from arrays or guarantee it by checking
    row equality. Calibration must be repeated whenever the center is refitted.
    """
    def __init__(self, alpha=0.1, clip=0.98):
        if not np.isfinite(alpha) or not 0 < alpha < 1:
            raise ValueError("alpha must lie strictly between zero and one.")
        if not np.isfinite(clip) or not 0 < clip < 1:
            raise ValueError("clip must lie strictly between zero and one.")
        self.alpha, self.clip = float(alpha), float(clip)

    def fit(self, history, response):
        """Estimate the pooled coefficient using all observed training transitions."""
        h = _history(history)
        y = _response(response, len(h))
        x = np.column_stack((h, y))
        magnitude = np.max(np.abs(x))
        if magnitude == 0:
            raise ValueError("Training transition energy is zero.")
        z = x/magnitude
        denominator = np.sum(z[:, :-1]**2)
        if denominator <= 0:
            raise ValueError("Training transition energy is zero or numerically singular.")
        estimate = np.sum(z[:, :-1]*z[:, 1:])/denominator
        if not np.isfinite(estimate):
            raise ValueError("The pooled estimate is not finite.")
        self.rho_ = float(np.clip(estimate, -self.clip, self.clip))
        self.n_features_in_ = h.shape[1]
        self.q_ = None
        self.calibration_size_ = None
        self.rank_ = None
        return self

    def _fitted_history(self, history):
        if not hasattr(self, "rho_"):
            raise RuntimeError("Call fit before calibration or prediction.")
        return _history(history, self.n_features_in_)

    def calibrate(self, history, response):
        """Use the ceil((n+1)*(1-alpha))-th normalized residual, without interpolation."""
        h = self._fitted_history(history)
        y = _response(response, len(h))
        scale = history_scale(h, self.rho_)
        scores = np.abs(y-self.rho_*h[:, -1])/scale
        if not np.isfinite(scores).all():
            raise ValueError("Calibration scores exceed the floating-point range.")
        k = math.ceil((len(h)+1)*(1-self.alpha))
        self.q_ = float(np.partition(scores, k-1)[k-1]) if k <= len(h) else math.inf
        self.calibration_size_, self.rank_ = len(h), k
        return self

    def predict_interval(self, history):
        """Return lower/upper endpoints as an (episodes, 2) array."""
        h = self._fitted_history(history)
        if self.q_ is None:
            raise RuntimeError("Call calibrate after fitting and before prediction.")
        scale = history_scale(h, self.rho_)
        if math.isinf(self.q_):
            return np.column_stack((np.full(len(h), -np.inf), np.full(len(h), np.inf)))
        center = self.rho_*h[:, -1]
        radius = self.q_*scale
        bounds = np.column_stack((center-radius, center+radius))
        if not np.isfinite(bounds).all():
            raise ValueError("Interval endpoints exceed the floating-point range.")
        return bounds
