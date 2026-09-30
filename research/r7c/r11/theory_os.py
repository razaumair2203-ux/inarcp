"""R11 theory check (pre-protocol mechanics): order-statistic innovation normalization.
Score^2 = |Y - r H_m|^2 / X_(k), X_(k) = k-th smallest of the m history innovation powers
{(1-|r|^2)|h_1|^2, |h_j - r h_{j-1}|^2}. At r = rho in pure AR(1) compound-Gaussian clutter these are iid exponential,
so P{exceed} = prod_{i=0}^{k-1} (m-i)/(m-i+T), T = q^2 (OS-CFAR law, Rohling 1983), and a Swerling-1 target in Y
only gives Pd with T/(1+S/(1-|rho|^2)). Also: robustness of the scale to up to m-k contaminated history samples."""
import numpy as np
rng = np.random.default_rng(1)
m, k, rho, n = 16, 12, 0.93 * np.exp(-0.2j), 400000
def ar1(n, L):
    e = np.sqrt(.5) * (rng.standard_normal((n, L)) + 1j * rng.standard_normal((n, L)))
    x = np.empty((n, L), complex); x[:, 0] = e[:, 0]
    for t in range(1, L): x[:, t] = rho * x[:, t - 1] + np.sqrt(1 - abs(rho) ** 2) * e[:, t]
    return x
def os_scale2(H, r, k):
    inn = np.concatenate([(1 - abs(r) ** 2) * abs(H[:, :1]) ** 2, abs(H[:, 1:] - r * H[:, :-1]) ** 2], 1)
    return np.sort(inn, 1)[:, k - 1]
law = lambda T, k=k: np.prod([(m - i) / (m - i + T) for i in range(k)])
X = ar1(n, m + 1) * np.sqrt(np.exp(rng.normal(0, 1, (n, 1))))       # lognormal texture (scale mixture)
H, Y = X[:, :m], X[:, m]
s2 = os_scale2(H, rho, k); sc2 = abs(Y - rho * H[:, -1]) ** 2 / s2
for T in (1.0, 3.0, 8.0):
    emp = np.mean(sc2 > T); se = np.sqrt(emp * (1 - emp) / n)
    print(f"Pfa T={T}: law {law(T):.5f}  MC {emp:.5f}  z={(emp - law(T)) / se:+.2f}")
T = min(np.linspace(0.1, 50, 5000), key=lambda t: abs(law(t) - 0.01))
for S in (1.0, 10.0):                                               # SCR relative to clutter power
    g = np.sqrt(.5) * (rng.standard_normal(n) + 1j * rng.standard_normal(n))
    sc = abs(Y + np.sqrt(S * np.exp(0)) * g * np.sqrt(np.mean(abs(X) ** 2, 1)) * 0 + np.sqrt(S) * g * 0 - rho * H[:, -1]) ** 2  # placeholder
Xc = ar1(n, m + 1); H, Y = Xc[:, :m], Xc[:, m]                      # unit-power clutter for Pd check
for S in (1.0, 10.0):
    g = np.sqrt(.5) * (rng.standard_normal(n) + 1j * rng.standard_normal(n))
    emp = np.mean(abs(Y + np.sqrt(S) * g - rho * H[:, -1]) ** 2 / os_scale2(H, rho, k) > T)
    pred = law(T / (1 + S / (1 - abs(rho) ** 2)))
    print(f"Pd S={S}: law {pred:.4f}  MC {emp:.4f}")
# CA (RMS) vs OS threshold multiplier loss in homogeneous clutter at Pfa 0.01: SNR (whitened) needed for Pd 0.5
from scipy.optimize import brentq
Tca = m * (0.01 ** (-1 / m) - 1)
snr = lambda f: brentq(f, 1e-3, 1e4)
ca = snr(lambda s: (1 + Tca / (m * (1 + s))) ** (-m) - 0.5); os_ = snr(lambda s: law(T / (1 + s)) - 0.5)
print(f"OS(k={k}) loss vs CA in homogeneous clutter at Pfa 0.01, Pd 0.5: {10 * np.log10(os_ / ca):.2f} dB")
# robustness: c contaminated history samples of power 1000x
for c in (0, 2, 4, 5):
    Hc = H.copy(); idx = rng.choice(m, c, replace=False) if c else []
    for j in idx: Hc[:, j] = Hc[:, j] + np.sqrt(1000) * np.sqrt(.5) * (rng.standard_normal(n) + 1j * rng.standard_normal(n))
    pf_os = np.mean(abs(Y + np.sqrt(10.) * np.sqrt(.5) * (rng.standard_normal(n) + 1j * rng.standard_normal(n)) - rho * Hc[:, -1]) ** 2 / os_scale2(Hc, rho, k) > T)
    inn = np.concatenate([(1 - abs(rho) ** 2) * abs(Hc[:, :1]) ** 2, abs(Hc[:, 1:] - rho * Hc[:, :-1]) ** 2], 1).mean(1)
    pd_ca = np.mean(abs(Y + np.sqrt(10.) * np.sqrt(.5) * (rng.standard_normal(n) + 1j * rng.standard_normal(n)) - rho * Hc[:, -1]) ** 2 / inn > Tca)
    print(f"{c} contaminated history samples (random positions): Pd at S=10  OS {pf_os:.3f}  RMS {pd_ca:.3f}")
