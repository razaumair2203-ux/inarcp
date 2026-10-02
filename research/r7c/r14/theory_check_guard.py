"""Independent Monte Carlo check of the guarded post-onset law (Prop. 4 with l replaced by l - Delta), written from scratch
(does not import laws.py or the study code). AR(1) compound-Gaussian clutter at the true coefficient, no thermal noise,
lognormal texture, m = 16, Pfa = 0.01, persistent Swerling-1 target from the onset pulse.
Output: theory_check_guard_output.txt"""
import os
import numpy as np

rng = np.random.default_rng(2026)
M, ALPHA, NEP = 16, 0.01, 400_000
rho = 0.93 * np.exp(-0.2j)
Q2 = M * (ALPHA ** (-1.0 / M) - 1.0)          # CA-law threshold on |eps_Y|^2 / s^2
BETA = Q2 / M
LOOKS = 13


def law(S, l, d2, guard):
    Sw = S / (1 - abs(rho) ** 2)
    if l == 0:
        E0, EH = Sw, 0.0
    else:
        E0 = Sw * d2
        n_in = l - guard
        EH = 0.0 if n_in <= 0 else Sw * (1 + (n_in - 1) * d2)
    b = 1 + E0 - BETA - BETA * EH; c = BETA * (1 + E0 + EH)
    lp, lm = (b + np.sqrt(b * b + 4 * c)) / 2, (b - np.sqrt(b * b + 4 * c)) / 2
    return lp / (lp - lm) * (1 + BETA / lp) ** (-(M - 1))


def cn(*shape):
    return np.sqrt(0.5) * (rng.standard_normal(shape) + 1j * rng.standard_normal(shape))


def simulate(S_db, omega, guard):
    T_ON = guard + M + 1
    L = T_ON + LOOKS
    e = cn(NEP, L); x = np.empty((NEP, L), complex); x[:, 0] = e[:, 0]
    for t in range(1, L):
        x[:, t] = rho * x[:, t - 1] + np.sqrt(1 - abs(rho) ** 2) * e[:, t]
    tex = np.exp(rng.normal(0, 1, (NEP, 1)))            # texture: scales clutter and target alike (SCR relative to local power)
    S = 10 ** (S_db / 10)
    t = np.arange(L)
    tgt = np.sqrt(S) * cn(NEP, 1) * np.where(t >= T_ON, np.exp(1j * omega * t), 0)[None, :]
    z = np.sqrt(tex) * (x + tgt)
    pd = []
    for l in range(LOOKS):
        ty = T_ON + l
        num = abs(z[:, ty] - rho * z[:, ty - 1]) ** 2
        h = z[:, ty - guard - M:ty - guard]
        inn = np.concatenate([np.sqrt(1 - abs(rho) ** 2) * h[:, :1], h[:, 1:] - rho * h[:, :-1]], 1)
        s2 = np.mean(abs(inn) ** 2, 1)
        pd.append(np.mean(num > Q2 * s2))
    return np.array(pd)


out = [f"Guarded post-onset law vs Monte Carlo ({NEP} episodes per point; m={M}, Pfa={ALPHA}, rho={rho:.3f})"]
worst = 0.0
for guard in (0, 8):
    for S_db, omega, name in ((10.0, np.angle(rho) + np.pi, "opposite"), (0.0, np.angle(rho) + np.pi, "opposite"), (10.0, np.angle(rho) + np.pi / 2, "quadrature")):
        d2 = abs(1 - rho * np.exp(-1j * omega)) ** 2
        mc = simulate(S_db, omega, guard)
        th = np.array([law(10 ** (S_db / 10), l, d2, guard) for l in range(LOOKS)])
        se = np.sqrt(np.maximum(th * (1 - th), 1e-12) / NEP)
        z = (mc - th) / se
        worst = max(worst, np.max(abs(z)))
        out.append(f"guard {guard:2d}, SCR {S_db:4.0f} dB, {name:<10s} looks 0-{LOOKS - 1}: MC " + " ".join(f"{v:.3f}" for v in mc))
        out.append(f"{'':38s} law " + " ".join(f"{v:.3f}" for v in th) + f"   max |z| {np.max(abs(z)):.2f}")
out.append(f"{'ALL CHECKS PASSED' if worst < 4 else 'CHECK FAILED'} (max |z| = {worst:.2f})")
txt = "\n".join(out); print(txt)
open(os.path.join(os.path.dirname(os.path.abspath(__file__)), "theory_check_guard_output.txt"), "w", encoding="utf8").write(txt + "\n")
