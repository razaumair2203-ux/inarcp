"""Figure: closed-form laws (lines) against Monte Carlo (markers), synthetic AR(1) compound-Gaussian clutter.
Usage: python fig_theory.py -> paper/r12/manuscript/figures/fig_theory.pdf and fig_theory.json (plotted values)."""
import os, sys, json, math
HERE = os.path.dirname(os.path.abspath(__file__)); sys.path.insert(0, HERE)
import numpy as np
import matplotlib; matplotlib.use("Agg"); import matplotlib.pyplot as plt
import laws as L
from verify_laws import ar1, innov, cn

OUT = os.path.join(HERE, "..", "..", "..", "paper", "r12", "manuscript", "figures")
plt.rcParams.update({"font.size": 7.5, "axes.edgecolor": "#c3c2b7", "axes.labelcolor": "#52514e", "legend.frameon": False})
BLUE, ORANGE, GREEN, PINK, PURPLE, DARK, GREY = "#2a78d6", "#eb6834", "#1baf7a", "#e87ba4", "#7a4fd6", "#52514e", "#898781"
RHO = 0.93 * np.exp(-0.2j); m, alpha = 16, 0.01
rng = np.random.default_rng(20261002); N_MC = 100000
rec = {}


def target_rows(n, T, t0, w, S):
    tex = np.exp(rng.normal(0, 1.5, n) / 2); base = ar1(rng, n, T, RHO, spread=0.0) * tex[:, None]
    g = cn(rng, n); t = np.arange(T); w = np.broadcast_to(np.asarray(w, float), (n,))
    return base + math.sqrt(S) * tex[:, None] * g[:, None] * np.where(t >= t0, np.exp(1j * np.outer(w, t)), 0)


fig, axs = plt.subplots(2, 3, figsize=(7.16, 4.3)); axs = axs.ravel()

# (a) post-onset decay of the IN-ARCP score
ax = axs[0]; q2 = L.q2_in(alpha, m); looks = np.arange(9); S = 10.0
for nm, w, c in (("clutter Doppler", np.angle(RHO), PINK), ("quarter", np.angle(RHO) + np.pi / 2, BLUE), ("opposite", np.angle(RHO) + np.pi, GREEN)):
    th = [float(L.pd_onset(q2, m, S, RHO, w, l)) for l in looks]
    X = target_rows(N_MC, m + 9, m, w, S); mc = []
    for l in looks:
        win = X[:, l:l + m + 1]; e = innov(win[:, :-1], RHO)
        mc.append(float(np.mean(abs(win[:, -1] - RHO * win[:, -2]) ** 2 > q2 * np.mean(abs(e) ** 2, 1))))
    ax.plot(looks, th, "-", color=c, lw=1.4, label=nm); ax.plot(looks, mc, "o", color=c, ms=3, mfc="white")
    rec[f"a|{nm}"] = dict(theory=th, mc=mc, horizon=float(L.visibility_horizon(q2, m, float(L.d2_of(RHO, w)))))
ax.set_xlabel("Look after onset $\\ell$"); ax.set_ylabel("$P_{\\rm d}$"); ax.set_title("(a) IN-ARCP after onset, SCR 10 dB", fontsize=7.5)
ax.legend(fontsize=6, loc="upper right"); ax.grid(alpha=.3)

# (b) visibility horizon: Pd at look l versus SCR, opposite Doppler
ax = axs[1]; w = np.angle(RHO) + np.pi; scr = np.arange(-5, 41, 1.0); d2 = float(L.d2_of(RHO, w))
lstar = L.visibility_horizon(q2, m, d2)
for l, c in zip((1, 2, 3, 4, 5), (BLUE, GREEN, ORANGE, PINK, PURPLE)):
    th = [float(L.pd_onset(q2, m, 10 ** (s / 10), RHO, w, l)) for s in scr]
    ax.plot(scr, th, "-", color=c, lw=1.3, label=f"$\\ell={l}$")
    mcx = []
    for s in (0, 10, 20, 30, 40):
        X = target_rows(N_MC // 2, m + 9, m, w, 10 ** (s / 10)); win = X[:, l:l + m + 1]; e = innov(win[:, :-1], RHO)
        mcx.append(float(np.mean(abs(win[:, -1] - RHO * win[:, -2]) ** 2 > q2 * np.mean(abs(e) ** 2, 1))))
    ax.plot((0, 10, 20, 30, 40), mcx, "o", color=c, ms=3, mfc="white"); rec[f"b|{l}"] = dict(theory=th, mc=mcx)
ax.set_xlabel("SCR (dB)"); ax.set_ylabel("$P_{\\rm d}$ at look $\\ell$")
ax.set_title(f"(b) Visibility horizon $\\ell^*={lstar:.2f}$ (opposite Doppler)", fontsize=7.5); ax.legend(fontsize=6, ncol=2); ax.grid(alpha=.3)
rec["b|lstar"] = float(lstar)

# (c) order-statistic score after onset (exact law by quadrature)
ax = axs[2]; w = np.angle(RHO) + np.pi / 2; d2 = float(L.d2_of(RHO, w)); Sw = S / (1 - abs(RHO) ** 2)
X = target_rows(N_MC, m + 13, m, w, S)
for k, c in ((8, PURPLE), (12, ORANGE)):
    q2o = L.q2_os(alpha, m, k); th, mc = [], []
    for l in range(0, 11):
        sig = np.zeros(m)
        if l >= 1: sig[m - l] = Sw; sig[m - l + 1:] = Sw * d2
        th.append(L.pd_os_exact(q2o, m, k, sig, Sw if l == 0 else Sw * d2, ng=200, nx=3000))
        win = X[:, l:l + m + 1]; e = innov(win, RHO)
        mc.append(float(np.mean(abs(e[:, -1]) ** 2 > q2o * np.partition(abs(e[:, :-1]) ** 2, k - 1, 1)[:, k - 1])))
    ax.plot(range(11), th, "-", color=c, lw=1.4, label=f"$k={k}$ ($m-k={m - k}$)"); ax.plot(range(11), mc, "D", color=c, ms=2.8, mfc="white")
    rec[f"c|{k}"] = dict(theory=th, mc=mc)
th = [float(L.pd_onset(q2, m, S, RHO, w, l)) for l in range(11)]
ax.plot(range(11), th, "-", color=BLUE, lw=1.0, alpha=.7, label="RMS scale (IN-ARCP)")
ax.set_xticks(range(0, 11, 2)); ax.set_xlabel("Look after onset $\\ell$"); ax.set_ylabel("$P_{\\rm d}$"); ax.set_title("(c) Order-statistic scale, SCR 10 dB", fontsize=7.5)
ax.legend(fontsize=6, loc="lower left"); ax.grid(alpha=.3)

# (d) non-coherent integration of whitened innovations with a shared history
ax = axs[3]; scr = np.arange(-15, 21, 1.0); w = np.angle(RHO) + np.pi / 2; d2 = float(L.d2_of(RHO, w))
for Kd, c in ((1, DARK), (2, BLUE), (4, GREEN), (8, ORANGE)):
    t = L.t_dwell(alpha, m, Kd)
    th = [L.pd_dwell(t, m, Kd, L.dwell_energy(10 ** (s / 10) / (1 - abs(RHO) ** 2), d2, Kd)) for s in scr]
    ax.plot(scr, th, "-", color=c, lw=1.4, label=f"$K={Kd}$")
    mcx = []
    for s in (-10, -5, 0, 5):
        X = target_rows(N_MC // 2, m + Kd, m, w, 10 ** (s / 10)); e = abs(innov(X, RHO)) ** 2
        mcx.append(float(np.mean(e[:, m:].sum(1) > t * e[:, :m].mean(1))))
    ax.plot((-10, -5, 0, 5), mcx, "o", color=c, ms=3, mfc="white"); rec[f"d|{Kd}"] = dict(theory=th, mc=mcx)
_, keff = L.power_nci_eigs(RHO, 8)
ax.text(0.03, 0.97, f"power integration, 8 pulses:\n$K_{{\\rm eff}}={keff:.2f}$ looks", transform=ax.transAxes, va="top", fontsize=6, color=DARK)
ax.set_xlabel("SCR (dB)"); ax.set_ylabel("$P_{\\rm d}$"); ax.set_title("(d) Whitened non-coherent integration", fontsize=7.5)
ax.legend(fontsize=6, loc="lower right"); ax.grid(alpha=.3); rec["d|keff"] = float(keff)

# (e) self-normalized whitened Doppler (P-ANMF), unknown Doppler
ax = axs[4]; scr = np.arange(-25, 6, 1.0)
for Kd, c in ((8, BLUE), (16, GREEN), (64, ORANGE)):
    t = L.t_snd_max(alpha, Kd); w = 2 * np.pi * (Kd // 4) / Kd; d2 = float(L.d2_of(RHO, w))
    th = [L.pd_snd_max(t, Kd, 10 ** (s / 10) / (1 - abs(RHO) ** 2), d2) for s in scr]
    ax.plot(scr, th, "-", color=c, lw=1.4, label=f"$N={Kd}$")
    mcx = []
    for s in (-20, -15, -10, -5, 0):
        n = N_MC // 4 if Kd < 64 else N_MC // 10
        tex = np.exp(rng.normal(0, 1.5, n) / 2); base = ar1(rng, n, Kd + 1, RHO, spread=0.0) * tex[:, None]
        X = base + math.sqrt(10 ** (s / 10)) * tex[:, None] * cn(rng, n)[:, None] * np.exp(1j * w * np.arange(Kd + 1))
        e = innov(X, RHO)[:, 1:]; I = abs(np.fft.fft(e, axis=1)) ** 2
        mcx.append(float(np.mean(I.max(1) / (Kd * np.sum(abs(e) ** 2, 1)) > t)))
    ax.plot((-20, -15, -10, -5, 0), mcx, "o", color=c, ms=3, mfc="white"); rec[f"e|{Kd}"] = dict(theory=th, mc=mcx)
ax.set_xlabel("SCR (dB)"); ax.set_ylabel("$P_{\\rm d}$"); ax.set_title("(e) Self-normalized whitened Doppler, $\\omega=\\pi/2$", fontsize=7.5)
ax.legend(fontsize=6, loc="lower right"); ax.grid(alpha=.3)

# (f) certified integration under pulsed interference (JNR 30 dB), Pfa versus hit rate
ax = axs[5]; ps = np.array([0.0, 0.01, 0.02, 0.03, 0.05, 0.08]); Lp = m + 8; kH = 8
res = {k: [] for k in ("ca", "clip0", "cert", "bin_cert")}
t_ca = L.t_dwell(alpha, m, 8)
xc = ar1(rng, 20000, Lp, RHO); ec = abs(innov(xc, RHO)) ** 2
q0 = np.sort(L.robust_stat(ec[:, :m], ec[:, m:], kH, "clip", c=6.0))[L.conformal_rank(20000, alpha) - 1]
for p in ps:
    bad = L.corrupted_innovations(rng.random((20000, Lp)) < p)
    qc = np.sort(L.worst_case(ec[:, :m], ec[:, m:], bad[:, :m], bad[:, m:], kH, "clip", c=6.0))[L.conformal_rank(20000, alpha) - 1]
    qb = np.sort(L.worst_case(ec[:, :m], ec[:, m:], bad[:, :m], bad[:, m:], kH, "bin", eta=6.0))[L.conformal_rank(20000, alpha) - 1]
    xt = ar1(rng, N_MC, Lp, RHO); hit = rng.random((N_MC, Lp)) < p
    xi = xt + np.where(hit, np.sqrt(1e3 * np.mean(abs(xt) ** 2, 1, keepdims=True)) * cn(rng, N_MC, Lp), 0)
    ei = abs(innov(xi, RHO)) ** 2
    res["ca"].append(float(np.mean(ei[:, m:].sum(1) > t_ca * ei[:, :m].mean(1))))
    cl = L.robust_stat(ei[:, :m], ei[:, m:], kH, "clip", c=6.0); res["clip0"].append(float(np.mean(cl > q0)))
    res["cert"].append(float(np.mean(cl > qc)))
    res["bin_cert"].append(float(np.mean(L.robust_stat(ei[:, :m], ei[:, m:], kH, "bin", eta=6.0) > qb)))
for k_, c, ls, lab in (("ca", DARK, ":", "CA integration"), ("clip0", ORANGE, "--", "clipped, clean threshold"),
                      ("cert", BLUE, "-", "clipped, certified"), ("bin_cert", GREEN, "-.", "binary, certified")):
    ax.semilogy(100 * ps, np.maximum(res[k_], 1e-5), ls, marker="o", ms=3, color=c, lw=1.3, label=lab)
ax.axhline(alpha, color=GREY, lw=1); ax.text(6.0, alpha * 1.25, "design $\\alpha$", fontsize=6, color=GREY)
ax.set_xlabel("Hit rate per pulse (%)"); ax.set_ylabel("$P_{\\rm fa}$ (JNR 30 dB)"); ax.set_title("(f) Certified integration, pulsed interference", fontsize=7.5)
ax.legend(fontsize=6, loc="lower right"); ax.grid(alpha=.3, which="both"); rec["f"] = dict(p=ps.tolist(), **res)

fig.tight_layout(); os.makedirs(OUT, exist_ok=True)
fig.savefig(os.path.join(OUT, "fig_theory.pdf"), bbox_inches="tight"); fig.savefig(os.path.join(HERE, "fig_theory.png"), dpi=160, bbox_inches="tight")
json.dump(rec, open(os.path.join(HERE, "fig_theory.json"), "w"), indent=1)
print("saved; horizon opposite", lstar)
