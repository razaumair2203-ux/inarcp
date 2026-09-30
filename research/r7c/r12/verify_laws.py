"""Monte Carlo verification of every closed form in laws.py (R12, part S). Synthetic only.
Usage: python verify_laws.py [--reps 400000] -> verify_laws_output.txt, verify_laws.json"""
import os, sys, json, math, argparse, time
HERE = os.path.dirname(os.path.abspath(__file__)); sys.path.insert(0, HERE)
import numpy as np
import laws as L

RHO = 0.93 * np.exp(-0.2j)
OUT = []


def log(s=""):
    print(s, flush=True); OUT.append(s)


def cn(rng, *shape):
    return (rng.standard_normal(shape) + 1j * rng.standard_normal(shape)) / math.sqrt(2)


def ar1(rng, n, T, rho, spread=1.5):
    x = np.empty((n, T), complex); x[:, 0] = cn(rng, n)
    e = cn(rng, n, T) * math.sqrt(1 - abs(rho) ** 2)
    for t in range(1, T):
        x[:, t] = rho * x[:, t - 1] + e[:, t]
    return np.exp(rng.normal(0, spread, n) / 2)[:, None] * x          # texture: lognormal power


def innov(x, rho):
    return np.concatenate([math.sqrt(1 - abs(rho) ** 2) * x[:, :1], x[:, 1:] - rho * x[:, :-1]], 1)


def tyler(Sec, iters=30):
    """Fixed-point (Tyler) scatter estimate, trace-normalized, batched over the first axis."""
    n, Ks, N = Sec.shape
    R = np.broadcast_to(np.eye(N, dtype=complex), (n, N, N)).copy()
    for _ in range(iters):
        q = np.real(np.einsum("nki,nij,nkj->nk", np.conj(Sec), np.linalg.inv(R), Sec))
        R = (N / Ks) * np.einsum("nki,nkj->nij", Sec / q[..., None], np.conj(Sec))
        R *= N / np.real(np.trace(R, axis1=1, axis2=2))[:, None, None]
    return R


def se(p, n):
    return math.sqrt(max(p * (1 - p), 1e-12) / n)


def check(name, th, mc, n, res):
    z = (mc - th) / max(se(th, n), 1e-12)
    res.append(dict(check=name, theory=float(th), mc=float(mc), z=float(z)))
    log(f"  {name:<46s} theory {th:.5f}  MC {mc:.5f}  z {z:+.2f}")


def main(reps):
    rng = np.random.default_rng(20261001); res = []
    m = 16; alpha = 0.01; q2 = L.q2_in(alpha, m)

    log("V1-V3  IN-ARCP per-look score: onset, post-onset rank-one law, visibility horizon")
    for wname, w in (("clutter", np.angle(RHO)), ("opposite", np.angle(RHO) + np.pi)):
        for Sdb in (10, 25):
            S = 10 ** (Sdb / 10)
            n = reps // 4; T = m + 9
            tex = np.exp(rng.normal(0, 1.5, n) / 2)
            base = ar1(rng, n, T, RHO, spread=0.0) * tex[:, None]
            g = cn(rng, n); t = np.arange(T); t0 = m
            tg = np.sqrt(S) * tex[:, None] * g[:, None] * np.where(t >= t0, np.exp(1j * w * t), 0)
            X = base + tg
            for look in (0, 1, 2, 4, 8):
                win = X[:, look:look + m + 1]
                e = innov(win[:, :-1], RHO)
                s2 = np.mean(abs(e) ** 2, 1)
                y = abs(win[:, -1] - RHO * win[:, -2]) ** 2
                mc = np.mean(y > q2 * s2)
                th = L.pd_onset(q2, m, S, RHO, w, look)
                check(f"Pd {wname} Doppler, SCR {Sdb} dB, look {look}", th, mc, n, res)
            d2 = float(L.d2_of(RHO, w))
            log(f"  visibility horizon ({wname}): l* = {L.visibility_horizon(q2, m, d2):.2f}")
    log("  random Doppler (closed form averaged over w) at 10 dB:")
    n = reps // 2; T = m + 9
    tex = np.exp(rng.normal(0, 1.5, n) / 2); base = ar1(rng, n, T, RHO, spread=0.0) * tex[:, None]
    w = rng.uniform(-np.pi, np.pi, n); g = cn(rng, n); t = np.arange(T)
    X = base + math.sqrt(10) * tex[:, None] * g[:, None] * np.where(t >= m, np.exp(1j * np.outer(w, t)), 0)
    for look in (0, 1, 2, 4, 8):
        win = X[:, look:look + m + 1]; e = innov(win[:, :-1], RHO)
        mc = np.mean(abs(win[:, -1] - RHO * win[:, -2]) ** 2 > q2 * np.mean(abs(e) ** 2, 1))
        check(f"Pd random Doppler, 10 dB, look {look}", L.pd_onset_random_doppler(q2, m, 10, RHO, look), mc, n, res)

    log("\nV4  order-statistic score (k = 8, m = 16): Pfa law and post-onset law")
    k = 8; q2o = L.q2_os(alpha, m, k)
    n = reps; x = ar1(rng, n, m + 1, RHO); e = innov(x, RHO)
    mc = np.mean(abs(e[:, -1]) ** 2 > q2o * np.partition(abs(e[:, :-1]) ** 2, k - 1, 1)[:, k - 1])
    check("Pfa OS (k=8)", alpha, mc, n, res)
    for Sdb in (10, 25):
        S = 10 ** (Sdb / 10); Sw = S / (1 - abs(RHO) ** 2)
        n = reps // 4; T = m + 9; w = np.angle(RHO) + np.pi / 2
        tex = np.exp(rng.normal(0, 1.5, n) / 2); base = ar1(rng, n, T, RHO, spread=0.0) * tex[:, None]
        g = cn(rng, n); t = np.arange(T)
        X = base + math.sqrt(S) * tex[:, None] * g[:, None] * np.where(t >= m, np.exp(1j * w * t), 0)
        d2 = float(L.d2_of(RHO, w))
        for look in (0, 2, 6, 8, 9):
            win = X[:, look:look + m + 1]; e = innov(win, RHO)
            mc = np.mean(abs(e[:, -1]) ** 2 > q2o * np.partition(abs(e[:, :-1]) ** 2, k - 1, 1)[:, k - 1])
            sig = np.zeros(m)
            if look >= 1:
                sig[m - look] = Sw; sig[m - look + 1:] = Sw * d2
            a = Sw if look == 0 else Sw * d2
            th = L.pd_os_exact(q2o, m, k, sig, a)
            check(f"Pd OS exact, quarter Doppler, {Sdb} dB, look {look}", th, mc, n, res)
            if look >= 1:
                log(f"      strong-target limit: {L.pd_os_strong(q2o, m, k, a, look):.4f}")

    log("\nV5  dwell integration with a shared history (m = 16): Pfa and Pd laws")
    for K in (2, 4, 8):
        tK = L.t_dwell(alpha, m, K)
        n = reps // 2; x = ar1(rng, n, m + K, RHO); e = innov(x, RHO)
        mc = np.mean(np.sum(abs(e[:, m:]) ** 2, 1) > tK * np.mean(abs(e[:, :m]) ** 2, 1))
        check(f"Pfa dwell K={K}", alpha, mc, n, res)
        for Sdb in (0, 10):
            S = 10 ** (Sdb / 10); Sw = S / (1 - abs(RHO) ** 2); w = np.angle(RHO) + np.pi / 2
            tex = np.exp(rng.normal(0, 1.5, n) / 2); base = ar1(rng, n, m + K, RHO, spread=0.0) * tex[:, None]
            g = cn(rng, n); t = np.arange(m + K)
            X = base + math.sqrt(S) * tex[:, None] * g[:, None] * np.where(t >= m, np.exp(1j * w * t), 0)
            e = innov(X, RHO)
            mc = np.mean(np.sum(abs(e[:, m:]) ** 2, 1) > tK * np.mean(abs(e[:, :m]) ** 2, 1))
            th = L.pd_dwell(tK, m, K, L.dwell_energy(Sw, float(L.d2_of(RHO, w)), K))
            check(f"Pd dwell K={K}, {Sdb} dB, quarter Doppler", th, mc, n, res)
    lam, keff = L.power_nci_eigs(RHO, 8)
    log(f"  power integration over 8 pulses at |rho| = {abs(RHO):.2f}: effective looks K_eff = {keff:.2f}")

    log("\nV6  self-normalized whitened Doppler (P-ANMF): Fisher's g and the NMF law")
    for K in (8, 16, 64):
        n = reps // 4 if K < 64 else reps // 16
        x = ar1(rng, n, K + 1, RHO); e = innov(x, RHO)[:, 1:]                     # dwell innovations
        I = abs(np.fft.fft(e, axis=1)) ** 2; Ttot = K * np.sum(abs(e) ** 2, 1)
        tb = 1 - alpha ** (1 / (K - 1)); tm = L.t_snd_max(alpha, K)
        check(f"Pfa known bin K={K}", alpha, np.mean(I[:, 3] / Ttot > tb), n, res)
        check(f"Pfa max (Fisher g) K={K}", alpha, np.mean(I.max(1) / Ttot > tm), n, res)
        for Sdb in (-10, 0):
            S = 10 ** (Sdb / 10); Sw = S / (1 - abs(RHO) ** 2); w = 2 * np.pi * 3 / K
            tex = np.exp(rng.normal(0, 1.5, n) / 2); base = ar1(rng, n, K + 1, RHO, spread=0.0) * tex[:, None]
            g = cn(rng, n); t = np.arange(K + 1)
            X = base + math.sqrt(S) * tex[:, None] * g[:, None] * np.exp(1j * w * t)
            e = innov(X, RHO)[:, 1:]; I = abs(np.fft.fft(e, axis=1)) ** 2; Ttot = K * np.sum(abs(e) ** 2, 1)
            d2 = float(L.d2_of(RHO, w))
            check(f"Pd known bin K={K}, {Sdb} dB", L.pd_snd_bin(tb, K, Sw, d2), np.mean(I[:, 3] / Ttot > tb), n, res)
            check(f"Pd max K={K}, {Sdb} dB", L.pd_snd_max(tm, K, Sw, d2), np.mean(I.max(1) / Ttot > tm), n, res)

    log("\nV7  ANMF with the sample covariance (Kraut-Scharf law), Gaussian and compound-Gaussian data")
    for N, Ks in ((8, 24), (8, 40)):
        n = reps // 20; t = L.t_anmf(alpha, N, Ks)
        for spread in (0.0, 1.5):
            Z = ar1(rng, n * (Ks + 1), N, RHO, spread=spread).reshape(n, Ks + 1, N)
            x = Z[:, 0]; Sec = Z[:, 1:]
            Sc = np.einsum("nki,nkj->nij", Sec, np.conj(Sec))
            s = np.exp(1j * 0.7 * np.arange(N))
            Si = np.linalg.inv(Sc)
            num = abs(np.einsum("i,nij,nj->n", np.conj(s), Si, x)) ** 2
            den = np.real(np.einsum("i,nij,j->n", np.conj(s), Si, s)) * np.real(np.einsum("ni,nij,nj->n", np.conj(x), Si, x))
            lab = "CG secondary+test" if spread else "Gaussian"
            check(f"Pfa ANMF-SCM N={N}, Ks={Ks}, {lab}" + (" [law assumes Gaussian]" if spread else ""), alpha, np.mean(num / den > t), n, res)
            Rf = tyler(Sec)
            Ri = np.linalg.inv(Rf); tf = L.t_anmf(alpha, N, Ks, fp=True)
            num = abs(np.einsum("i,nij,nj->n", np.conj(s), Ri, x)) ** 2
            den = np.real(np.einsum("i,nij,j->n", np.conj(s), Ri, s)) * np.real(np.einsum("ni,nij,nj->n", np.conj(x), Ri, x))
            check(f"Pfa ANMF-FP N={N}, Ks={Ks}, {lab} [asymptotic law]", alpha, np.mean(num / den > tf), n, res)

    log("\nV8  conformal calibration: conditional Pfa ~ Beta(n+1-k, k); expected Pd")
    for n_cal, a in ((1000, 0.01), (2000, 0.001)):
        B = L.pfa_conditional_law(n_cal, a); R = 20000
        u = np.sort(rng.random((R, n_cal)), 1)[:, L.conformal_rank(n_cal, a) - 1]
        cond = 1 - u
        log(f"  n={n_cal}, alpha={a}: mean Pfa theory {B.mean():.5f} MC {cond.mean():.5f}; "
            f"P(Pfa > 2 alpha) theory {B.sf(2 * a):.4f} MC {np.mean(cond > 2 * a):.4f}")
        res.append(dict(check=f"Beta law n={n_cal} a={a}", theory=float(B.mean()), mc=float(cond.mean()), z=0.0))
        gam = 1 / (1 + 10.0)
        log(f"    E[Pd] at SNR 10 dB (Pd = Pfa^(1/(1+SNR))): theory {L.mean_pd_conformal(n_cal, a, gam):.5f} MC {np.mean(cond ** gam):.5f}")
    for a in (1e-2, 1e-3, 1e-4):
        log(f"  calibration size for P(Pfa > 2 alpha) <= 0.05 at alpha = {a:g}: n >= {L.n_required(a)}")

    log("\nV9  certified integration under pulsed interference (m = 16, K = 8, median history, AR(1))")
    log("    q: conformal quantile of the worst case over amplitudes, on clean episodes with hit positions drawn at")
    log("    the design rate p. Test hits at rate p with Gaussian amplitudes (JNR re local power) or exact cancellation.")
    m, K, kH = 16, 8, 8; Lp = m + K
    n_cal, n_te = 20000, 200000
    S = 10 ** (10 / 10); w0 = np.angle(RHO) + np.pi / 2
    tca = L.t_dwell(alpha, m, K)
    for stat, kw in (("clip", dict(c=6.0)), ("trim", dict(t=2)), ("bin", dict(eta=6.0))):
        for p in (0.0, 0.02, 0.05):
            xc = ar1(rng, n_cal, Lp, RHO); ec = abs(innov(xc, RHO)) ** 2
            bad = L.corrupted_innovations(rng.random((n_cal, Lp)) < p)
            Wc = L.worst_case(ec[:, :m], ec[:, m:], bad[:, :m], bad[:, m:], kH, stat, **kw)
            q = np.sort(Wc)[L.conformal_rank(n_cal, alpha) - 1]
            q0 = np.sort(L.robust_stat(ec[:, :m], ec[:, m:], kH, stat, **kw))[L.conformal_rank(n_cal, alpha) - 1]
            for jnr, mode in ((1e3, "gauss"), (1e1, "gauss"), (None, "cancel")):
                if p == 0 and (mode != "gauss" or jnr != 1e3):
                    continue
                xt = ar1(rng, n_te, Lp, RHO); hit = rng.random((n_te, Lp)) < p
                if mode == "gauss":
                    amp = np.sqrt(jnr * np.mean(abs(xt) ** 2, 1, keepdims=True)) * cn(rng, n_te, Lp)
                    xi = xt + np.where(hit, amp, 0)
                else:
                    xi = np.where(hit, 0.0, xt)
                ei = abs(innov(xi, RHO)) ** 2
                T = L.robust_stat(ei[:, :m], ei[:, m:], kH, stat, **kw)
                e0 = abs(innov(xt, RHO)) ** 2; bt = L.corrupted_innovations(hit)
                Wt = L.worst_case(e0[:, :m], e0[:, m:], bt[:, :m], bt[:, m:], kH, stat, **kw)
                viol = np.mean(T > Wt + 1e-9)
                ca = np.mean(ei[:, m:].sum(1) > tca * ei[:, :m].mean(1))
                tex = np.sqrt(np.mean(abs(xt) ** 2, 1)); g = cn(rng, n_te); t = np.arange(Lp)
                xs = xi + math.sqrt(S) * tex[:, None] * g[:, None] * np.where(t >= m, np.exp(1j * w0 * t), 0)
                es = abs(innov(xs, RHO)) ** 2; Ts = L.robust_stat(es[:, :m], es[:, m:], kH, stat, **kw)
                lab = f"JNR {10 * np.log10(jnr):.0f} dB" if mode == "gauss" else "cancelling"
                log(f"  {stat:<4s} p={p:<4} {lab:<11s}: violations {viol:.0e}; Pfa certified {np.mean(T > q):.4f}, "
                    f"clean-thr {np.mean(T > q0):.4f}, CA-NCI {ca:.4f}; Pd(10 dB) certified {np.mean(Ts > q):.3f}, clean-thr {np.mean(Ts > q0):.3f}")
                res.append(dict(check=f"cert {stat} p={p} {lab}", theory=alpha, mc=float(np.mean(T > q)), z=float(viol)))
    return res


if __name__ == "__main__":
    ap = argparse.ArgumentParser(); ap.add_argument("--reps", type=int, default=400000); a = ap.parse_args()
    t = time.time(); res = main(a.reps)
    zs = np.array([r["z"] for r in res if not r["check"].startswith(("cert", "Beta")) and "[" not in r["check"]])
    log(f"\nSummary: {len(zs)} probability checks, max |z| = {np.max(abs(zs)):.2f}, "
        f"{np.sum(abs(zs) > 3)} with |z| > 3; runtime {time.time() - t:.0f} s")
    open(os.path.join(HERE, "verify_laws_output.txt"), "w").write("\n".join(OUT) + "\n")
    json.dump(res, open(os.path.join(HERE, "verify_laws.json"), "w"), indent=1)
