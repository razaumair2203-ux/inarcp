"""Check that the inarcp package reproduces the research code behind the paper's R7-R11 numbers:
the order-statistic scales OS1_8, OS1_12, OS4 (research/r7c/r11/run_r11_ipix.py) and the AR(4)
noise-aware model (research/r7c/methods.py fit_mixture_arp + NoiseAwareGeneral).
CPU only (INARCP_GPU is cleared). Usage: python reproducibility/check_package_equivalence.py"""
import os, sys, math
os.environ.pop("INARCP_GPU", None)
ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, ROOT); sys.path.insert(0, os.path.join(ROOT, "research", "r7c"))
import numpy as np
from inarcp.clutter import ComplexINARCP, NoiseAwareINARCP, ar1_corr
from methods import fit_mixture_arp, NoiseAwareGeneral, arp_corr, reflection_to_ar


def cn(rng, *shape):
    return (rng.standard_normal(shape) + 1j * rng.standard_normal(shape)) / math.sqrt(2)


def kth(v, k):                                            # run_r11_ipix.py
    return np.partition(v, k - 1, axis=1)[:, k - 1]


def inn_pow1(H, r):
    return np.concatenate([(1 - abs(r) ** 2) * abs(H[:, :1]) ** 2, abs(H[:, 1:] - r * H[:, :-1]) ** 2], 1)


def inn_pow4(H, a):
    p = len(a); m = H.shape[1]
    return abs(H[:, p:] - sum(a[k] * H[:, p - 1 - k:m - 1 - k] for k in range(p))) ** 2


rng = np.random.default_rng(20260930); m = 16
a_true = reflection_to_ar(np.array([0.9 * np.exp(0.3j), -0.5, 0.2j, 0.1]))
L = np.linalg.cholesky(arp_corr(m + 1, a_true) + 1e-12 * np.eye(m + 1))
tex = np.exp(rng.normal(0, 1.5, 3000))
X = np.sqrt(tex)[:, None] * (cn(rng, 3000, m + 1) @ L.T) + 0.3 * cn(rng, 3000, m + 1)
H = X[:, :-1]
worst = 0.0

for k in (8, 12):
    mod = ComplexINARCP(order=1, os_rank=k).fit(X)
    r = mod.coef_[0]
    d = np.max(abs(mod._center_scale(H)[1] - np.sqrt(kth(inn_pow1(H, r), k))))
    print(f"OS1_{k}: max |scale difference| = {d:.2e}"); worst = max(worst, d)
mod = ComplexINARCP(order=4, os_rank=6).fit(X)
d = np.max(abs(mod._center_scale(H)[1] - np.sqrt(kth(inn_pow4(H, mod.coef_), 6))))
print(f"OS4 (k=6): max |scale difference| = {d:.2e}"); worst = max(worst, d)

R, nu, w, res = fit_mixture_arp(X[:2000], 4)
na = NoiseAwareINARCP(order=4).fit(X[:2000])
ref = NoiseAwareGeneral(R, nu); c0, s0, _ = ref.center_scale(H[2000:]); c1, s1 = na._center_scale(H[2000:])
print(f"NA-AR(4): |dnu|/nu = {abs(na.nu_ - nu) / nu:.2e}, max|dR| = {np.max(abs(na.R_ - R)):.2e}, "
      f"max|dcenter| = {np.max(abs(c1 - c0)):.2e}, max|dscale| = {np.max(abs(s1 - s0)):.2e}, "
      f"converged = {na.converged_} ({res.nit} iterations)")
worst = max(worst, abs(na.nu_ - nu) / nu, np.max(abs(na.R_ - R)), np.max(abs(c1 - c0)), np.max(abs(s1 - s0)))
print("PASS" if worst < 1e-8 else f"FAIL (worst difference {worst:.2e})")
sys.exit(0 if worst < 1e-8 else 1)
