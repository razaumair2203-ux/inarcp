"""Gate V2c: is the residual texture-conditional drift on IPIX due to AR(1) misspecification?
Complex AR(p) innovation-normalized conformal (conditional innovations over history positions
p+1..m), p in {1,2,4}, m in {8,16}; texture proxy as in v2b. alpha = 0.1."""
import sys, os, math
sys.path.insert(0, os.path.dirname(os.path.dirname(__file__)))
import numpy as np
from ipix import FILES, load, episodes
from methods import conformal_quantile
from v2b_ipix_within import texture_proxy, T, t1, t2, GAP, STRIDE

ALPHA = 0.1


def lagmat(X, p):
    """rows: predict X[:, t] from X[:, t-1..t-p] for t = p..L-1; returns (targets, regressors)."""
    L = X.shape[1]
    Y = X[:, p:].reshape(-1)
    Z = np.stack([X[:, p - k:L - k] for k in range(1, p + 1)], -1).reshape(-1, p)
    return Y, Z


def fit_arp(X, p):
    Y, Z = lagmat(X, p)
    a, *_ = np.linalg.lstsq(Z, Y, rcond=None)
    return a


def center_scale(X, a):
    p = len(a); H = X[:, :-1]; m = H.shape[1]
    center = sum(a[k] * H[:, m - 1 - k] for k in range(p))
    res = H[:, p:] - sum(a[k] * H[:, p - 1 - k:m - 1 - k] for k in range(p))
    return center, np.sqrt(np.mean(abs(res) ** 2, 1))


for m in (8, 16):
    import v2b_ipix_within as v2b; v2b.M = m
    acc = {p: [] for p in (1, 2, 4)}
    for num in FILES:
        d = load(num)
        for pol, z in d["z"].items():
            Xtr, _, _ = episodes(z, 0, t1 - GAP, m, STRIDE)
            Xca, _, _ = episodes(z, t1, t2 - GAP, m, STRIDE)
            Xte, st, bt = episodes(z, t2, T, m, STRIDE)
            tex = texture_proxy(z, st, bt); qb = np.digitize(tex, np.quantile(tex, [.2, .4, .6, .8]))
            for p in (1, 2, 4):
                a = fit_arp(Xtr, p)
                cc, sc = center_scale(Xca, a); ct, stt = center_scale(Xte, a)
                q = conformal_quantile(abs(Xca[:, -1] - cc) / sc, ALPHA)
                cov = abs(Xte[:, -1] - ct) <= q * stt
                acc[p].append(([cov[qb == b].mean() for b in range(5)], cov.mean(), (q * stt).mean()))
    print(f"\nm={m}:")
    base = np.array([x[2] for x in acc[1]])
    for p in (1, 2, 4):
        by = np.array([x[0] for x in acc[p]]); rad = np.array([x[2] for x in acc[p]])
        print(f"  AR({p}) marginal {np.mean([x[1] for x in acc[p]]):.3f} | by texture {np.round(by.mean(0),3)} | "
              f"spread {np.mean(by.max(1)-by.min(1)):.3f} | radius/AR(1) {np.exp(np.mean(np.log(rad/base))):.3f}")
