"""R12 IPIX parts L (low-Pfa control), A (ANMF baselines), T (real targets) and I (injected pulsed interference)
on the 56 confirmatory units (PROTOCOL_R12.md, frozen before outcomes).
Usage: INARCP_GPU=1 python run_r12_ipix.py [--workers 14] [--synthetic]  ->  study/results/r12/i_<file>_<pol>_rot<k>.npz
--synthetic runs the mechanics on AR(1)+texture+noise data (not IPIX)."""
import sys, os, math, json, hashlib, argparse, time
HERE = os.path.dirname(os.path.abspath(__file__)); ROOT = os.path.dirname(HERE)
for p in (ROOT, os.path.join(ROOT, "study"), os.path.join(ROOT, "r10"), HERE):
    sys.path.insert(0, p)
import numpy as np
from ipix import FILES, load, episodes
from methods import conformal_quantile, fit_ols, innovation_scale, fit_mixture_arp, NoiseAwareGeneral
from run_study import fit_arp, arp_cs, texture_proxy, BLOCKS, ROT, STRIDE
import run_study
from run_r10 import segments, steer_whitened, innovations, pamf, ramp_profile, M, K, P4, SCR_DB, NDOP, OMEGA
import laws as L

ALPHAS_L = (1e-2, 1e-3, 1e-4)
ALPHAS_A = (1e-2, 1e-3)
KH, CLIP, ETA = 8, 6.0, 6.0
W_FIX = 48                                   # OMEGA[48] = pi/2
SHIFTS = np.array([0, 24, -24, 48, -48])
NT = (8, 16, 32, 64, 128, 256, 512, 1024)
PS, JNRS = (0.02, 0.05), (10.0, 30.0)
NSIM = 1_000_000
OUT = os.path.join(ROOT, "study", "results", "r12")


def frozen():
    h = open(os.path.join(HERE, "PROTOCOL_R12.sha256")).read().split()[0]
    return hashlib.sha256(open(os.path.join(HERE, "PROTOCOL_R12.md"), "rb").read()).hexdigest() == h


def cn(rng, *shape):
    return np.sqrt(.5) * (rng.standard_normal(shape) + 1j * rng.standard_normal(shape))


def kth(v, k):
    return np.partition(v, k - 1, axis=1)[:, k - 1]


def inn_pow1(S, r):
    return np.concatenate([(1 - abs(r) ** 2) * abs(S[:, :1]) ** 2, abs(S[:, 1:] - r * S[:, :-1]) ** 2], 1)


def q_rank(v, a):
    return conformal_quantile(np.asarray(v), a)


# ---------------------------------------------------------------- data windows
def dense_segments(z, blk, L_, stride, margin=0):
    T, B = z.shape
    starts = np.arange(blk[0] + margin, blk[1] - L_ - margin, stride)
    idx = starts[:, None] + np.arange(L_)[None, :]
    seg = np.transpose(z[idx], (0, 2, 1)).reshape(-1, L_)
    st = np.repeat(starts, B); bi = np.tile(np.arange(B), len(starts))
    return seg, st, bi


def secondary(z, st, bi, bins, off, N, hit_fn=None):
    """ANMF secondary windows grouped by CUT bin: list of (row indices, (n_b, Ks_b, N))."""
    T, B = z.shape; ob = np.array(bins); out = []
    for b in range(B):
        rows = np.where(bi == b)[0]
        if len(rows) == 0:
            continue
        refs = np.where(abs(ob - ob[b]) > 1)[0]
        ws = np.clip(st[rows][:, None] + off + SHIFTS[None, :], 0, T - N)            # (n, 5)
        idx = ws[:, :, None] + np.arange(N)[None, None, :]                            # (n, 5, N)
        W = z[idx][..., refs]                                                          # (n, 5, N, R)
        W = np.transpose(W, (0, 1, 3, 2)).reshape(len(rows), -1, N)
        if hit_fn is not None:
            W = hit_fn(W)
        out.append((rows, W))
    return out


def tyler(Sec, iters=30):
    n, Ks, N = Sec.shape
    R = np.broadcast_to(np.eye(N, dtype=complex), (n, N, N)).copy()
    for _ in range(iters):
        q = np.real(np.einsum("nki,nij,nkj->nk", np.conj(Sec), np.linalg.inv(R), Sec))
        R = (N / Ks) * np.einsum("nki,nkj->nij", Sec / np.maximum(q, 1e-300)[..., None], np.conj(Sec))
        R *= N / np.real(np.trace(R, axis1=1, axis2=2))[:, None, None]
    return R


def anmf_inverse(sec_groups, fp):
    """Per group: inverse scatter (SCM or Tyler) and Ks."""
    out = []
    for rows, W in sec_groups:
        R = tyler(W) if fp else np.einsum("nki,nkj->nij", W, np.conj(W)) / W.shape[1]
        out.append((rows, np.linalg.inv(R), W.shape[1]))
    return out


def anmf_stat(x, inv_groups, steer):
    """x (n, N) CUT vectors; steer (G, N); returns (n, G) cos^2 statistics and per-row Ks."""
    n = len(x); out = np.zeros((n, len(steer))); ks = np.zeros(n)
    for rows, Ri, Ks in inv_groups:
        xr = x[rows]
        xRx = np.real(np.einsum("ni,nij,nj->n", np.conj(xr), Ri, xr))
        sRs = np.real(np.einsum("gi,nij,gj->ng", np.conj(steer), Ri, steer))
        sRx = np.einsum("gi,nij,nj->ng", np.conj(steer), Ri, xr)
        out[rows] = abs(sRx) ** 2 / (sRs * xRx[:, None]); ks[rows] = Ks
    return out, ks


STEER8 = np.exp(1j * OMEGA[:, None] * np.arange(K)[None, :])                           # (64, 8)


# ---------------------------------------------------------------- statistics
def look_stats(X, r, a4, na4):
    H, Y = X[:, :-1], X[:, -1]
    c4, s4 = arp_cs(H, a4)
    out = {"IN1": abs(Y - r * H[:, -1]) ** 2 / innovation_scale(H, r) ** 2,
           "IN4": abs(Y - c4) ** 2 / s4 ** 2,
           "OS1_8": abs(Y - r * H[:, -1]) ** 2 / kth(inn_pow1(H, r), 8),
           "CA16": abs(Y) ** 2 / np.mean(abs(H) ** 2, 1),
           "OSraw": abs(Y) ** 2 / kth(abs(H) ** 2, 8)}
    if na4 is not None:
        c, s = na4.center_scale(H)[:2]; out["NA4"] = abs(Y - c) ** 2 / s ** 2
    return out


def int_stats(S, r):
    """AR(1) dwell integrators on 24-pulse segments (16 history + 8 dwell innovations)."""
    e = inn_pow1(S, r); h, d = e[:, :M], e[:, M:]
    return {"D-IN1": d.sum(1) / h.mean(1),
            "Clip-OS1": L.robust_stat(h, d, KH, "clip", c=CLIP),
            "Bin-OS1": L.robust_stat(h, d, KH, "bin", eta=ETA)}


def excision_din(S, r):
    e = inn_pow1(S, r); med = np.median(e, 1, keepdims=True); keep = e <= 10 * med
    h, d = np.where(keep[:, :M], e[:, :M], 0), np.where(keep[:, M:], e[:, M:], 0)
    kh, kd = keep[:, :M].sum(1), keep[:, M:].sum(1)
    with np.errstate(invalid="ignore", divide="ignore"):
        v = np.where(kd > 0, d.sum(1) / np.maximum(kd, 1) * K, 0.0) / (h.sum(1) / np.maximum(kh, 1))
    return np.nan_to_num(v, nan=0.0, posinf=1e300)


def whitened_dwell(S, a4):
    E = innovations(S, a4); return E[:, :M - P4], E[:, M - P4:]


def coh_stats(S, a4, W, inv_scm=None, inv_fp=None, fixed=False):
    """PAMF-H, P-ANMF and ANMF statistics on 24-pulse segments."""
    hist, dw = whitened_dwell(S, a4); out = {}
    if fixed:
        w = W[W_FIX]
        out["PAMF-H(w)"] = abs(dw @ np.conj(w)) ** 2 / np.sum(abs(w) ** 2) / np.mean(abs(hist) ** 2, 1)
        F = abs(np.fft.fft(dw, axis=1)) ** 2 / (K * np.sum(abs(dw) ** 2, 1, keepdims=True))
        out["P-ANMF(bin)"] = F[:, 2]; out["P-ANMF"] = F.max(1)
        out["D-IN4"] = np.sum(abs(dw) ** 2, 1) / np.mean(abs(hist) ** 2, 1)
        steer = STEER8[W_FIX:W_FIX + 1]
    else:
        out["PAMF-H"] = pamf(S, a4, W)[("PAMFH", K)]
        F = abs(np.fft.fft(dw, NDOP, axis=1)) ** 2 / (K * np.sum(abs(dw) ** 2, 1, keepdims=True))
        out["P-ANMF"] = F.max(1)
        out["D-IN4"] = np.sum(abs(dw) ** 2, 1) / np.mean(abs(hist) ** 2, 1)
        steer = STEER8
    x = S[:, M:M + K]
    for nm, inv in (("ANMF-SCM", inv_scm), ("ANMF-FP", inv_fp)):
        if inv is not None:
            t, ks = anmf_stat(x, inv, steer)
            out[nm + ("(w)" if fixed else "")] = t[:, 0] if fixed else t.max(1)
            out["_Ks"] = ks
    return out


# ---------------------------------------------------------------- Part L
def gaussian_sim_thresholds(rng, alphas):
    """Gaussian-model thresholds of Clip-OS1 (i.i.d. CN innovations)."""
    e = abs(cn(rng, NSIM, M + K)) ** 2
    v = L.robust_stat(e[:, :M], e[:, M:], KH, "clip", c=CLIP)
    return {a: float(np.quantile(v, 1 - a)) for a in alphas}


def bootstrap_threshold(Xtr, r, rng, alphas):
    e = np.sqrt(inn_pow1(Xtr, r)); e = e / np.sqrt(np.mean(e ** 2, 1, keepdims=True))
    pool = e.reshape(-1) ** 2
    d = pool[rng.integers(0, len(pool), (NSIM, M + 1))]
    v = d[:, -1] / d[:, :-1].mean(1)
    return {a: float(np.quantile(v, 1 - a)) for a in alphas}


def analytic_look(a):
    return {"IN1": L.q2_in(a, 16), "IN4": L.q2_in(a, 12), "OS1_8": L.q2_os(a, 16, 8), "CA16": L.q2_in(a, 16),
            "OSraw": L.q2_os(a, 16, 8), "NA4": -math.log(a)}


def analytic_dwell(a):
    return {"D-IN4": L.t_dwell(a, 12, K), "PAMF-H(w)": L.q2_in(a, 12), "P-ANMF(bin)": 1 - a ** (1 / (K - 1)),
            "P-ANMF": L.t_snd_max(a, K)}


def part_l(z, bins, ca, te, r, a4, na4, Xtr, rng):
    res = {}; T, B = z.shape
    # per-look, non-overlapping episodes
    Xc, _, _ = episodes(z, *ca, M, M + 1); Xt, st, bt = episodes(z, *te, M, M + 1)
    Pt = texture_proxy(z, st, bt, M, 1024); qe = np.quantile(Pt, [.2, .4, .6, .8]); qb = np.digitize(Pt, qe)
    Sc, St = look_stats(Xc, r, a4, na4), look_stats(Xt, r, a4, na4)
    boot = bootstrap_threshold(Xtr, r, rng, ALPHAS_L)
    res["L|nlook"] = np.array([len(Xc), len(Xt)])
    for a in ALPHAS_L:
        an = analytic_look(a)
        for m, v in St.items():
            rules = {"conf": q_rank(Sc[m], a), "anal": an[m]}
            if m == "IN1": rules["boot"] = boot[a]
            for rule, q in rules.items():
                e = v > q
                res[f"L|{m}|{rule}|{a}"] = np.array([e.sum(), len(e)] + [e[qb == k].sum() for k in range(5)] + [(qb == k).sum() for k in range(5)])
    # dwell, non-overlapping 24-pulse segments with room for the secondary shifts
    W = steer_whitened(a4)
    Dc, stc, bc = dense_segments(z, ca, M + K, M + K, margin=48)
    Dt, stt, btt = dense_segments(z, te, M + K, M + K, margin=48)
    Pd_ = texture_proxy(z, stt, btt, M + K - 1, 1024); qbd = np.digitize(Pd_, np.quantile(Pd_, [.2, .4, .6, .8]))
    stats = {}
    for tag, S, s_, b_ in (("c", Dc, stc, bc), ("t", Dt, stt, btt)):
        sec = secondary(z, s_, b_, bins, M, K)
        cs = coh_stats(S, a4, W, anmf_inverse(sec, False), anmf_inverse(sec, True), fixed=True)
        cs["Clip-OS1"] = int_stats(S, r)["Clip-OS1"]; stats[tag] = cs
    gs = gaussian_sim_thresholds(rng, ALPHAS_L)
    res["L|ndwell"] = np.array([len(Dc), len(Dt)])
    ks = stats["t"]["_Ks"]
    for a in ALPHAS_L:
        an = analytic_dwell(a); an["Clip-OS1"] = gs[a]
        for m, v in stats["t"].items():
            if m.startswith("_"): continue
            rules = {"conf": np.full(len(v), q_rank(stats["c"][m], a))}
            if m in an:
                rules["anal"] = np.full(len(v), an[m])
            elif m.startswith("ANMF"):
                fp = m.startswith("ANMF-FP")
                thr = {k_: L.t_anmf(a, K, int(k_), fp=fp) for k_ in np.unique(ks)}
                rules["anal"] = np.array([thr[k_] for k_ in ks])
            for rule, q in rules.items():
                e = v > q
                res[f"L|{m}|{rule}|{a}"] = np.array([e.sum(), len(e)] + [e[qbd == k].sum() for k in range(5)] + [(qbd == k).sum() for k in range(5)])
    return res, stats


# ---------------------------------------------------------------- Parts A and I
def r10_targets(n, r, seed_r10):
    rng = np.random.default_rng(seed_r10)
    amp = np.sqrt(.5) * (rng.standard_normal(n) + 1j * rng.standard_normal(n))
    om = rng.uniform(-np.pi, np.pi, n)
    return amp, om


def ai_stats(S, st, bi, z, bins, r, a4, W, sec_hit=None):
    sec = secondary(z, st, bi, bins, M, K, sec_hit)
    out = coh_stats(S, a4, W, anmf_inverse(sec, False), anmf_inverse(sec, True))
    out.update(int_stats(S, r))
    Xl = S[:, :M + 1]
    out["IN1look"] = abs(Xl[:, -1] - r * Xl[:, -2]) ** 2 / innovation_scale(Xl[:, :-1], r) ** 2
    out["OSraw"] = abs(Xl[:, -1]) ** 2 / kth(abs(Xl[:, :-1]) ** 2, 8)
    out["Exc-D-IN1"] = excision_din(S, r)
    out.pop("_Ks", None)
    return out, sec


def part_ai(z, bins, ca, te, r, a4, seed_r10, seed):
    res = {}; T, B = z.shape
    W = steer_whitened(a4)
    Sc, Pc, stc = segments(z, ca); St, Pt, stt = segments(z, te)
    bc = np.tile(np.arange(B), len(Sc) // B); bt = np.tile(np.arange(B), len(St) // B)
    n = len(St)
    Qc, _ = ai_stats(Sc, stc, bc, z, bins, r, a4, W)
    q = {(m, a): q_rank(v, a) for m, v in Qc.items() for a in ALPHAS_A}
    amp, om = r10_targets(n, r, seed_r10)
    g1, t01 = ramp_profile(1, "in"); tpos = np.arange(M + K)
    tv = g1[None, :] * np.exp(1j * om[:, None] * (tpos[None, :] - t01))
    base = (np.sqrt(Pt) * amp)[:, None] * tv
    # Part A: clean test segments (secondary windows fixed; the target is in the CUT only)
    Qt, sec_t = ai_stats(St, stt, bt, z, bins, r, a4, W)
    inv_s, inv_f = anmf_inverse(sec_t, False), anmf_inverse(sec_t, True)
    for m, v in Qt.items():
        for a in ALPHAS_A: res[f"A|{m}|{a}|pfa"] = float(np.mean(v > q[(m, a)]))
    pd = {}
    for i, sdb in enumerate(SCR_DB):
        Si = St + np.sqrt(10 ** (sdb / 10)) * base
        Q = coh_stats(Si, a4, W, inv_s, inv_f); Q.update(int_stats(Si, r)); Q.pop("_Ks", None)
        Xl = Si[:, :M + 1]
        Q["IN1look"] = abs(Xl[:, -1] - r * Xl[:, -2]) ** 2 / innovation_scale(Xl[:, :-1], r) ** 2
        Q["OSraw"] = abs(Xl[:, -1]) ** 2 / kth(abs(Xl[:, :-1]) ** 2, 8)
        Q["Exc-D-IN1"] = excision_din(Si, r)
        for m, v in Q.items():
            for a in ALPHAS_A: pd.setdefault((m, a), np.zeros(len(SCR_DB)))[i] = np.mean(v > q[(m, a)])
    for (m, a), v in pd.items(): res[f"A|{m}|{a}|pd"] = v
    # Part I: interference on test segments and on the secondary windows
    rng = np.random.default_rng(seed)
    ecal = inn_pow1(Sc, r)
    for p in PS:
        hc = L.corrupted_innovations(rng.random((len(Sc), M + K)) < p)
        for stat, kw in (("Clip-OS1", dict(c=CLIP)), ("Bin-OS1", dict(eta=ETA))):
            wc = L.worst_case(ecal[:, :M], ecal[:, M:], hc[:, :M], hc[:, M:], KH, stat.split("-")[0].lower(), **kw)
            for a in ALPHAS_A: q[(stat + "-cert", p, a)] = q_rank(wc, a)
        for jnr in JNRS:
            hit = rng.random((n, M + K)) < p
            ia = np.where(hit, np.sqrt(10 ** (jnr / 10) * Pt)[:, None] * cn(rng, n, M + K), 0)

            def sec_hit(Wn, rng=rng, p=p, jnr=jnr):
                h = rng.random(Wn.shape) < p
                return Wn + np.where(h, np.sqrt(10 ** (jnr / 10) * np.mean(abs(Wn) ** 2, (1, 2), keepdims=True)) * cn(rng, *Wn.shape), 0)

            Si0 = St + ia
            sec_i = secondary(z, stt, bt, bins, M, K, sec_hit)
            inv_f = anmf_inverse(sec_i, True)
            tag = f"I|{p}|{int(jnr)}"
            for lab, Sx in (("pfa", Si0), ) + tuple((f"pd{i}", Si0 + np.sqrt(10 ** (sdb / 10)) * base) for i, sdb in enumerate(SCR_DB)):
                Q = coh_stats(Sx, a4, W, None, inv_f); Q.update(int_stats(Sx, r)); Q.pop("_Ks", None)
                Q["Exc-D-IN1"] = excision_din(Sx, r)
                for m, v in Q.items():
                    for a in ALPHAS_A:
                        res.setdefault(f"{tag}|{m}|{a}", np.zeros(1 + len(SCR_DB)))[0 if lab == "pfa" else 1 + int(lab[2:])] = np.mean(v > q[(m, a)])
                for stat in ("Clip-OS1", "Bin-OS1"):
                    for a in ALPHAS_A:
                        res.setdefault(f"{tag}|{stat}-cert|{a}", np.zeros(1 + len(SCR_DB)))[0 if lab == "pfa" else 1 + int(lab[2:])] = np.mean(Q[stat] > q[(stat + "-cert", p, a)])
    res["A|n"] = n
    return res


# ---------------------------------------------------------------- Part T
def windows(z, blk, N, stride):
    starts = np.arange(blk[0], blk[1] - N - P4, stride)
    idx = starts[:, None] + np.arange(N + P4)[None, :]
    return np.transpose(z[idx], (0, 2, 1)), starts                                     # (S, B, N+4)


def white(Wn, a4):
    """AR(4) conditional innovations of each (N+4)-sample window -> N innovations."""
    x = Wn; Lw = x.shape[-1]
    return x[..., P4:] - sum(a4[i - 1] * x[..., P4 - i:Lw - i] for i in range(1, P4 + 1))


def panmf(e):
    N = e.shape[-1]
    F = abs(np.fft.fft(e, axis=-1)) ** 2
    return F.max(-1) / (N * np.sum(abs(e) ** 2, -1))


def part_t(zc, zt, bins, ca, te, r, a4, qlook, qclip):
    res = {}; ob = np.array(bins); B = zc.shape[1]
    refm = (abs(ob[:, None] - ob[None, :]) > 1)
    for N in NT:
        stride = N // 2 if N <= 32 else N // 4
        Wc, _ = windows(zc, ca, N, stride); Wt, _ = windows(zc, te, N, stride); Wg, _ = windows(zt, te, N, stride)
        pc, pt, pg = panmf(white(Wc, a4)), panmf(white(Wt, a4)), panmf(white(Wg, a4))
        # CA-NCI in range: power of the CUT window / mean power of reference clutter bins
        def canci(Wx, Wref, cut_is_clutter):
            P = np.sum(abs(Wx[..., P4:]) ** 2, -1); Pr = np.sum(abs(Wref[..., P4:]) ** 2, -1)
            if cut_is_clutter:
                return P / ((Pr @ refm.T) / refm.sum(1))[..., :]
            return P[:, 0] / Pr.mean(1)
        cc, ct, cg = canci(Wc, Wc, True), canci(Wt, Wt, True), canci(Wg, Wt, False)
        for a in (1e-3, 1e-2):
            qc = q_rank(pc.reshape(-1), a); qa = L.t_snd_max(a, N); qn = q_rank(cc.reshape(-1), a)
            res[f"T|P-ANMF|conf|N{N}|{a}"] = np.array([np.mean(pg > qc), np.mean(pt > qc), len(pg)])
            res[f"T|P-ANMF|anal|N{N}|{a}"] = np.array([np.mean(pg > qa), np.mean(pt > qa), len(pg)])
            res[f"T|CA-NCI|conf|N{N}|{a}"] = np.array([np.mean(cg > qn), np.mean(ct > qn), len(cg)])
        if N in (8, 16):
            steer = np.exp(1j * OMEGA[:, None] * np.arange(N)[None, :])
            stat = {}
            for tag, Wx, blk in (("c", Wc, ca), ("t", Wt, te)):
                S_, B_ = Wx.shape[0], Wx.shape[1]
                starts = np.arange(blk[0], blk[1] - N - P4, stride)
                st = np.repeat(starts, B_); bi = np.tile(np.arange(B_), S_)
                x = Wx[..., P4:].reshape(-1, N)
                sec = secondary(zc, st, bi, bins, P4, N)
                stat[tag] = anmf_stat(x, anmf_inverse(sec, True), steer)[0].max(1)
            starts = np.arange(te[0], te[1] - N - P4, stride)
            T_, _ = zc.shape
            ws = np.clip(starts[:, None] + P4 + SHIFTS[None, :], 0, T_ - N)
            idx = ws[:, :, None] + np.arange(N)[None, None, :]
            Wsec = np.transpose(zc[idx], (0, 1, 3, 2)).reshape(len(starts), -1, N)
            Ri = np.linalg.inv(tyler(Wsec))
            xg = Wg[:, 0, P4:]
            sg = anmf_stat(xg, [(np.arange(len(xg)), Ri, Wsec.shape[1])], steer)[0].max(1)
            for a in (1e-3, 1e-2):
                qf = q_rank(stat["c"], a)
                res[f"T|ANMF-FP|conf|N{N}|{a}"] = np.array([np.mean(sg > qf), np.mean(stat["t"] > qf), len(sg)])
    # history-normalized detectors on the target cell (consecutive 24-pulse segments of the test third)
    Sg, _, _ = dense_segments(zt, te, M + K, M + K)
    Xl = Sg[:, :M + 1]
    il = abs(Xl[:, -1] - r * Xl[:, -2]) ** 2 / innovation_scale(Xl[:, :-1], r) ** 2
    cl = int_stats(Sg, r)["Clip-OS1"]
    for a in (1e-3, 1e-2):
        res[f"T|IN1|conf|look|{a}"] = np.array([np.mean(il > qlook[a]), np.nan, len(il)])
        res[f"T|Clip-OS1|conf|dwell|{a}"] = np.array([np.mean(cl > qclip[a]), np.nan, len(cl)])
    return res


# ---------------------------------------------------------------- unit
def run_unit(num, pol, rot, synthetic_data=None):
    tr, ca, te = tuple(BLOCKS[b] for b in ROT[rot])
    if synthetic_data is None:
        d = load(num); z = d["z"][pol]; bins = d["bins"]; zt = load(num, keep="target")["z"][pol]
    else:
        z, bins, zt = synthetic_data
    Xtr, _, _ = episodes(z, *tr, M, STRIDE)
    r = fit_ols(Xtr); a4 = fit_arp(Xtr, P4)
    R4, nu4, _, _ = fit_mixture_arp(Xtr, P4); na4 = NoiseAwareGeneral(R4, nu4)
    seed = int(hashlib.sha256(f"R12|L|{num}|{pol}|{rot}".encode()).hexdigest()[:8], 16)
    seed_r10 = int(hashlib.sha256(f"R10|{num}|{pol}|{rot}".encode()).hexdigest()[:8], 16)
    seed_i = int(hashlib.sha256(f"R12|I|{num}|{pol}|{rot}".encode()).hexdigest()[:8], 16)
    res = dict(r=np.array([r.real, r.imag]), a4=a4, nu4=nu4)
    t0 = time.time()
    rl, dstats = part_l(z, bins, ca, te, r, a4, na4, Xtr, np.random.default_rng(seed)); res.update(rl)
    res["sec_L"] = time.time() - t0; t0 = time.time()
    res.update(part_ai(z, bins, ca, te, r, a4, seed_r10, seed_i))
    res["sec_AI"] = time.time() - t0; t0 = time.time()
    # thresholds of the history-normalized detectors for Part T: from Part L's calibration statistics
    Xc, _, _ = episodes(z, *ca, M, M + 1)
    lc = abs(Xc[:, -1] - r * Xc[:, -2]) ** 2 / innovation_scale(Xc[:, :-1], r) ** 2
    qlook = {a: q_rank(lc, a) for a in (1e-3, 1e-2)}
    qclip = {a: q_rank(dstats["c"]["Clip-OS1"], a) for a in (1e-3, 1e-2)}
    res.update(part_t(z, zt, bins, ca, te, r, a4, qlook, qclip))
    res["sec_T"] = time.time() - t0
    return res


def unit(args):
    num, pol, rot = args
    path = os.path.join(OUT, f"i_{num}_{pol}_rot{rot}.npz")
    if os.path.exists(path): return path
    t0 = time.time(); res = run_unit(num, pol, rot)
    tmp = path + ".tmp.npz"
    np.savez_compressed(tmp, **res, scr_db=SCR_DB, day=FILES[num][1], seconds=time.time() - t0)
    os.replace(tmp, path); return path


def synthetic():
    rng = np.random.default_rng(0); T, B = 131072, 9; rho = 0.93 * np.exp(-0.2j)
    run_study.T = T
    def ar(nb):
        e = cn(rng, T, nb); x = np.zeros((T, nb), complex)
        for t in range(1, T): x[t] = rho * x[t - 1] + np.sqrt(1 - abs(rho) ** 2) * e[t]
        return x
    x = ar(B + 1)
    tex = np.exp(rng.normal(0, 1, (T // 2048 + 1, B + 1))).repeat(2048, 0)[:T]
    zz = np.sqrt(10 * tex) * x + cn(rng, T, B + 1)
    tgt = 0.8 * np.sqrt(10) * np.exp(1j * (0.9 * np.arange(T) + 0.3 * np.cumsum(rng.standard_normal(T)) * 0.05))
    zt = (zz[:, -1] + tgt)[:, None]
    t0 = time.time(); res = run_unit(0, "like0", 2, (zz[:, :B], list(range(0, B)), zt))
    print(f"synthetic unit seconds {time.time() - t0:.0f}  (L {res['sec_L']:.0f}, AI {res['sec_AI']:.0f}, T {res['sec_T']:.0f})")
    for a in ALPHAS_L:
        row = []
        for m in ("IN1", "IN4", "OS1_8", "NA4", "CA16", "OSraw", "D-IN4", "PAMF-H(w)", "P-ANMF(bin)", "P-ANMF", "ANMF-SCM(w)", "ANMF-FP(w)", "Clip-OS1"):
            for rule in ("conf", "anal"):
                k_ = f"L|{m}|{rule}|{a}"
                if k_ in res: row.append(f"{m}/{rule} {res[k_][0] / res[k_][1] / a:.2f}")
        print(f"Part L alpha={a:g}: Pfa/alpha  " + "; ".join(row))
    print("Part L IN1 boot 1e-4:", res["L|IN1|boot|0.0001"][0] / res["L|IN1|boot|0.0001"][1] / 1e-4)
    i10 = int(np.argmin(abs(SCR_DB - 10)))
    for m in ("PAMF-H", "P-ANMF", "ANMF-SCM", "ANMF-FP", "D-IN1", "D-IN4", "Clip-OS1", "Bin-OS1", "IN1look", "OSraw", "Exc-D-IN1"):
        print(f"Part A {m:<10s} Pfa {res[f'A|{m}|0.01|pfa']:.4f}  Pd@0dB {res[f'A|{m}|0.01|pd'][4]:.3f}  Pd@10dB {res[f'A|{m}|0.01|pd'][i10]:.3f}")
    for p in PS:
        for jnr in JNRS:
            tag = f"I|{p}|{int(jnr)}"
            print(tag, "; ".join(f"{m} Pfa {res[f'{tag}|{m}|0.01'][0]:.4f} Pd10 {res[f'{tag}|{m}|0.01'][1 + i10]:.3f}"
                                   for m in ("D-IN1", "PAMF-H", "P-ANMF", "ANMF-FP", "Clip-OS1", "Clip-OS1-cert", "Bin-OS1-cert", "Exc-D-IN1")))
    for N in NT:
        v = res[f"T|P-ANMF|conf|N{N}|0.001"]; c = res[f"T|CA-NCI|conf|N{N}|0.001"]
        extra = f"; ANMF-FP Pd {res[f'T|ANMF-FP|conf|N{N}|0.001'][0]:.3f}" if N in (8, 16) else ""
        print(f"Part T N={N}: P-ANMF Pd {v[0]:.3f} Pfa {v[1]:.4f}; anal Pd {res[f'T|P-ANMF|anal|N{N}|0.001'][0]:.3f} Pfa {res[f'T|P-ANMF|anal|N{N}|0.001'][1]:.4f}; CA-NCI Pd {c[0]:.3f}{extra}")
    print("Part T IN1 look Pd", res["T|IN1|conf|look|0.001"][0], " Clip-OS1 Pd", res["T|Clip-OS1|conf|dwell|0.001"][0])


if __name__ == "__main__":
    ap = argparse.ArgumentParser(); ap.add_argument("--workers", type=int, default=14); ap.add_argument("--synthetic", action="store_true")
    a = ap.parse_args()
    if a.synthetic:
        synthetic(); sys.exit()
    if not frozen(): sys.exit("PROTOCOL_R12.md does not match its hash.")
    os.makedirs(OUT, exist_ok=True)
    json.dump(dict(started=time.strftime("%Y-%m-%d %H:%M:%S"), protocol_sha=open(os.path.join(HERE, "PROTOCOL_R12.sha256")).read().split()[0],
                   script_sha=hashlib.sha256(open(__file__, "rb").read()).hexdigest(), laws_sha=hashlib.sha256(open(os.path.join(HERE, "laws.py"), "rb").read()).hexdigest()),
              open(os.path.join(OUT, f"manifest_i_{int(time.time())}.json"), "w"), indent=1)
    jobs = [(num, pol, rot) for num in FILES for pol in ("like0", "like1") for rot in (2, 3)]
    from concurrent.futures import ProcessPoolExecutor
    with ProcessPoolExecutor(a.workers) as ex:
        for p in ex.map(unit, jobs): print("saved", os.path.basename(p), flush=True)
