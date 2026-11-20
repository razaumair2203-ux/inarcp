"""Gaussian known-coefficient mean and local large-sample efficiency terms."""
import math
from scipy.special import gammaln
from scipy.stats import t
import numpy as np
from scipy.linalg import eigh_tridiagonal
from scipy.integrate import quad
from scipy.special import betaincc


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


def beta_quadrature(a, b, points=128):
    """Normalized Gauss-Jacobi rule for Beta(a,b), avoiding huge raw weights.

    Nodes lie in (0,1). The eigenvector weights sum to one, even for large
    calibration sizes for which unnormalized Jacobi weights can overflow.
    This numerical integration rule is not an error bound.
    """
    if not (math.isfinite(a) and math.isfinite(b) and a > 0 and b > 0):
        raise ValueError("Beta parameters must be finite and positive.")
    if isinstance(points, bool) or int(points) != points or points < 2:
        raise ValueError("points must be an integer >= 2.")
    aa, bb = b-1, a-1
    j = np.arange(points, dtype=float)
    diagonal = np.empty(points)
    diagonal[0] = (bb-aa)/(aa+bb+2)
    diagonal[1:] = ((bb-aa)*(bb+aa) /
                    ((2*j[1:]+aa+bb)*(2*j[1:]+aa+bb+2)))
    j = np.arange(1, points, dtype=float)
    # The j=1 removable singularity at a+b=1 is evaluated after cancelling.
    off = np.empty(points-1)
    off[0] = math.sqrt(4*a*b/((a+b)**2*(a+b+1)))
    if points > 2:
        jj = j[1:]
        off[1:] = np.sqrt(4*jj*(jj+aa)*(jj+bb)*(jj+aa+bb) /
                          ((2*jj+aa+bb)**2*((2*jj+aa+bb)**2-1)))
    nodes, vectors = eigh_tridiagonal(diagonal, off)
    weights = vectors[0]**2
    weights /= weights.sum()
    return (nodes+1)/2, weights


def finite_calibration_mean_length(m, rho, calibration, alpha=0.1,
                                   sigma=1.0, points=128, method="adaptive"):
    """Numerically integrate the known-rho finite-calibration mean length.

    The identity is exact under the Gaussian episode model; this quadrature
    evaluation has numerical error. Adaptive tail integration is the default;
    optional method='jacobi' uses `points` and needs refinement, especially at
    the extreme finite rank k=n. It includes no coefficient-fitting cost.
    """
    oracle = oracle_mean_length(m, rho, alpha, sigma)
    if isinstance(calibration, bool) or int(calibration) != calibration or calibration < 1:
        raise ValueError("calibration must be a positive integer.")
    k = math.ceil((calibration+1)*(1-alpha))
    if k > calibration:
        return math.inf
    if method == "adaptive":
        # E Q = integral P(Q>x) dx, Q = G^-1(B). No endpoint inverse-CDF singularity.
        def survival(x):
            return betaincc(k, calibration+1-k, 1-2*t.sf(x,m))
        meanq, error = quad(survival, 0, np.inf, epsabs=1e-8, epsrel=1e-8, limit=300)
        if error > 1e-6*max(1,abs(meanq)):
            raise ArithmeticError("Finite-calibration integration did not meet tolerance.")
    elif method == "jacobi":
        u, w = beta_quadrature(k, calibration+1-k, points)
        meanq = float(w @ t.isf((1-u)/2, m))
    else:
        raise ValueError("method must be 'adaptive' or 'jacobi'.")
    return oracle * meanq / t.ppf(1-alpha/2, m)


def recommend_split(total, m, rho, kappa=1.0, alpha=0.1,
                    min_training=20, min_calibration=19):
    """Minimize the published leading approximation over integer splits.

    Use prespecified planning values, never calibration/test outcome tuning.
    Returns a planning candidate, not a finite-sample optimality guarantee.
    Assumes fixed m/alpha, sufficient scale moments and rho interior to clip.
    """
    for value in (total, min_training, min_calibration):
        if isinstance(value, bool) or int(value) != value or value < 1:
            raise ValueError("Episode counts must be positive integers.")
    candidates = []
    for n in range(min_calibration, total-min_training+1):
        if math.ceil((n+1)*(1-alpha)) > n:
            continue
        terms = efficiency_terms(m, rho, total-n, n, kappa, alpha)
        candidates.append(dict(training=total-n, calibration=n,
                               excess=sum(terms.values()), terms=terms))
    if not candidates:
        raise ValueError("No feasible finite-rank split meets the minimum sizes.")
    return min(candidates, key=lambda item: item['excess'])
