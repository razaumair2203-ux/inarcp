"""Gaussian known-coefficient mean and local large-sample efficiency terms."""
import math
from scipy.special import gammaln
from scipy.stats import t


def _validate(m, rho, alpha):
    if isinstance(m, bool) or int(m) != m or m < 2:
        raise ValueError("m must be an integer >= 2.")
    if not math.isfinite(rho) or abs(rho) >= 1 or not 0 < alpha < 1:
        raise ValueError("Require abs(rho)<1 and 0<alpha<1.")


def oracle_mean_length(m, rho, alpha=0.1, sigma=1.0):
    """Mean length of the known-rho scale-equivariant Student interval."""
    _validate(m, rho, alpha)
    if not math.isfinite(sigma) or sigma <= 0:
        raise ValueError("sigma must be finite and positive.")
    radial = math.sqrt(2/m)*math.exp(gammaln((m+1)/2)-gammaln(m/2))
    return 2*t.ppf(1-alpha/2,m)*sigma*math.sqrt(1-rho*rho)*radial


def efficiency_terms(m, rho, training, calibration, kappa=1.0, alpha=0.1):
    """Leading relative excess lengths, not finite-sample error bounds.

    kappa = E[sigma**4] / E[sigma**2]**2. Requires a common Gaussian AR
    coefficient interior to the fitting clip, fixed m/alpha, and the scale
    moments specified in the manuscript. It does not include a remainder bound.
    """
    _validate(m,rho,alpha)
    for size in (training,calibration):
        if isinstance(size,bool) or int(size)!=size or size<1:
            raise ValueError("Sample sizes must be positive integers.")
    if not math.isfinite(kappa) or kappa<1:
        raise ValueError("kappa must be finite and >=1.")
    p=1-alpha
    k=math.ceil((calibration+1)*p)
    if k>calibration:
        raise ValueError("Calibration rank gives an infinite interval; expansion is inapplicable.")
    c=t.ppf(1-alpha/2,m); f=t.pdf(c,m); d=1-rho*rho
    vu=((m-1)-(m-3+2/m)*rho*rho)/(m*(m+2)*d*d)
    curvature=(m+1)/(2*(m+c*c))*(c*c*vu+1/d)
    return dict(fitting=curvature*d*kappa/(m*training),
                calibration=p*(1-p)*(m+1)/(8*(m+c*c)*f*f*(calibration+2)),
                rounding=(k-(calibration+1)*p)/(2*c*f*(calibration+1)))
