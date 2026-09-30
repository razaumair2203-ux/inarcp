"""R10: classical correlation-aware detectors (Part C), gradual onset (Part R) and ACI under target contamination
(Part A) on the 56 confirmatory IPIX units (PROTOCOL_R10.md, frozen before outcomes).
Usage: INARCP_GPU=1 python run_r10.py [--workers 8] [--synthetic]  ->  study/results/r10/x_<file>_<pol>_rot<k>.npz
--synthetic runs the mechanics check on AR(1)+noise data (allowed before the freeze; not IPIX)."""
import sys, os, math, json, hashlib, argparse, time
HERE = os.path.dirname(os.path.abspath(__file__)); ROOT = os.path.dirname(HERE)
sys.path.insert(0, ROOT); sys.path.insert(0, os.path.join(ROOT, "study"))
import numpy as np
from ipix import FILES, load, episodes
from methods import conformal_quantile, fit_ols, innovation_scale, fit_mixture_arp, NoiseAwareGeneral
from run_study import fit_arp, arp_cs, texture_proxy, BLOCKS, ROT, STRIDE

M, K, P4 = 16, 8, 4
KS = (1, 2, 4, 8)
ALPHAS = (0.01, 0.001)
SCR_DB = np.arange(-5, 25.01, 2.5)
I10 = int(np.argmin(abs(SCR_DB - 10)))
NDOP = 64
OMEGA = 2 * np.pi * np.arange(NDOP) / NDOP - np.pi
LS = (1, 4, 8, 16)
PIS = (0.0, 0.01, 0.05)
GAMMAS = (0.005, 0.02)
OUT = os.path.join(ROOT, "study", "results", "r10")
LOOK = ("IN1", "IN4", "NA4", "CA16", "CAloc")
DWELL = ("IN1sum", "NA4sum", "CAlocsum", "PAMFH", "NPAMF", "MTDhann", "MTDrect")


def frozen():
    h = open(os.path.join(HERE, "PROTOCOL_R10.sha256")).read().split()[0]
    return hashlib.sha256(open(os.path.join(HERE, "PROTOCOL_R10.md"), "rb").read()).hexdigest() == h


# ---------------------------------------------------------------- dwell statistics
def steer_whitened(a):
    """W[w, k] = whitened steering at dwell position k = 0..K-1 for Doppler OMEGA[w] (target on t >= M)."""
    s = np.exp(1j * OMEGA[:, None] * np.arange(K)[None, :])                         # s_{M+k}
    W = s.copy()
    for i in range(1, P4 + 1):
        W[:, i:] -= a[i - 1] * s[:, :-i]                                              # s_{M+k-i} = 0 for k < i
    return W


def innovations(S, a):
    """eps_t for t = P4..M+K-1 (index 0 <-> t = P4)."""
    L = S.shape[1]
    return S[:, P4:] - sum(a[i - 1] * S[:, P4 - i:L - i] for i in range(1, P4 + 1))


def pamf(S, a, W):
    """PAMF-H and NPAMF statistics for K' in KS: dict (name, K') -> (n,)."""
    E = innovations(S, a); hist = E[:, :M - P4]; dw = E[:, M - P4:]
    s2h = np.mean(abs(hist) ** 2, 1)
    out = {}
    for k in KS:
        num = abs(dw[:, :k] @ np.conj(W[:, :k]).T) ** 2                               # (n, NDOP)
        den = np.sum(abs(W[:, :k]) ** 2, 1)[None, :]
        t = np.max(num / den, 1)
        out[("PAMFH", k)] = t / s2h
        out[("NPAMF", k)] = t / np.mean(abs(E[:, :M - P4 + k]) ** 2, 1)
    return out


def doppler_power(S, k, win):
    h = np.hanning(k + 2)[1:-1] if win == "hann" else np.ones(k)
    return abs(np.fft.fft(S[:, M:M + k] * h[None, :], NDOP, axis=1)) ** 2              # (n, NDOP)


def mtd(S_cut, S_clean, B, refmask):
    """MTD-CA: CUT Doppler power / mean over reference bins (clean) at the same start and Doppler; max over Doppler.
    Rows are ordered start-major (row = start*B + bin)."""
    out = {}
    for win, name in (("hann", "MTDhann"), ("rect", "MTDrect")):
        for k in KS:
            if k < 2: continue
            Fc = doppler_power(S_clean, k, win).reshape(-1, B, NDOP)
            Fref = np.einsum("sbf,cb->scf", Fc, refmask) / refmask.sum(1)[None, :, None]
            Fcut = doppler_power(S_cut, k, win).reshape(-1, B, NDOP)
            out[(name, k)] = np.max(Fcut / Fref, 2).reshape(-1)
    return out


def look_scores(S, P, cs):
    """Per-look scores on sliding windows: dict name -> (n, K)."""
    out = {m: np.zeros((len(S), K)) for m in LOOK}
    for j in range(K):
        W = S[:, j:j + M + 1]; H, Y = W[:, :-1], W[:, -1]
        for m, f in cs.items():
            c, s = f(H); out[m][:, j] = abs(Y - c) / s
        out["CAloc"][:, j] = abs(S[:, M + j]) / np.sqrt(P)
    return out


def all_stats(S, S_clean, P, cs, a4, W, B, refmask):
    L = look_scores(S, P, cs)
    D = {}
    for k in KS:
        D[("IN1sum", k)] = (L["IN1"][:, :k] ** 2).sum(1)
        D[("NA4sum", k)] = (L["NA4"][:, :k] ** 2).sum(1)
        D[("CAlocsum", k)] = (L["CAloc"][:, :k] ** 2).sum(1)
    D.update(pamf(S, a4, W)); D.update(mtd(S, S_clean, B, refmask))
    return L, D


# ---------------------------------------------------------------- data access
def segments(z, blk):
    T, B = z.shape; starts = np.arange(blk[0], blk[1] - M - K, STRIDE)
    idx = starts[:, None] + np.arange(M + K)[None, :]
    seg = np.transpose(z[idx], (0, 2, 1)).reshape(-1, M + K)
    P = texture_proxy(z, np.repeat(starts, B), np.tile(np.arange(B), len(starts)), M + K - 1, 1024)
    return seg, P, np.repeat(starts, B)


def ramp_profile(L, place):
    """g_t / a on the segment positions 0..M+K-1 before the Doppler factor, and t0."""
    t0 = M - L + 1 if place == "pre" else M
    t = np.arange(M + K); g = np.where(t >= t0, np.minimum(1.0, (t - t0 + 1) / L), 0.0)
    return g, t0


# ---------------------------------------------------------------- Part A: ACI with contaminated feedback
def aci_stream(s_cal_sorted, s_te, starts, a, gamma, gated, qg):
    n = len(s_cal_sorted); at = a; ag = a / 10 if gated else 0.0
    exceed = np.empty(len(s_te), bool); alev = []
    for t in np.unique(starts):
        idx = np.where(starts == t)[0]
        k = math.ceil((n + 1) * (1 - at))
        q = math.inf if k > n else (0.0 if k < 1 else s_cal_sorted[k - 1])
        e = s_te[idx] > q; exceed[idx] = e; alev.append(at)
        if gated:
            keep = s_te[idx] <= qg
            err = float(np.mean(e[keep])) if keep.any() else a - ag
            at = at + gamma * ((a - ag) - err)
        else:
            at = at + gamma * (a - float(np.mean(e)))
    return exceed, float(np.mean(alev))


def part_a(z, ca, te, r, rng):
    Xca, _, _ = episodes(z, *ca, M, STRIDE); Xte, st, bt = episodes(z, *te, M, STRIDE)
    sc = lambda X: abs(X[:, -1] - r * X[:, -2]) / innovation_scale(X[:, :-1], r)
    s_cal = np.sort(sc(Xca)); Pte = texture_proxy(z, st, bt, M, 1024)
    steps = np.unique(st); res = {}
    amp = np.sqrt(.5) * (rng.standard_normal(len(Xte)) + 1j * rng.standard_normal(len(Xte)))
    for pi in PIS:
        hit = np.isin(st, rng.choice(steps, int(round(pi * len(steps))), replace=False)) if pi > 0 else np.zeros(len(st), bool)
        X = Xte.copy(); X[hit, -1] += np.sqrt(10.0 * Pte[hit]) * amp[hit]
        s = sc(X)
        for a in (0.01,):
            q = conformal_quantile(s_cal, a); qg = conformal_quantile(s_cal, a / 10)
            e = s > q
            res[f"A|{pi}|split|pfa"] = float(e[~hit].mean()); res[f"A|{pi}|split|pd"] = float(e[hit].mean()) if hit.any() else np.nan
            for g in GAMMAS:
                for gated, nm in ((False, "naive"), (True, "gated")):
                    ex, am = aci_stream(s_cal, s, st, a, g, gated, qg)
                    res[f"A|{pi}|{nm}{g}|pfa"] = float(ex[~hit].mean())
                    res[f"A|{pi}|{nm}{g}|pd"] = float(ex[hit].mean()) if hit.any() else np.nan
                    res[f"A|{pi}|{nm}{g}|alev"] = am
    return res


# ---------------------------------------------------------------- unit
def run_unit(z, bins, blocks, seed, need_na=True):
    tr, ca, te = blocks
    T, B = z.shape
    Xtr, _, _ = episodes(z, *tr, M, STRIDE)
    r = fit_ols(Xtr); a4 = fit_arp(Xtr, P4)
    R4, nu4, _, _ = fit_mixture_arp(Xtr, P4); na4 = NoiseAwareGeneral(R4, nu4)
    cs = {"IN1": lambda H: (r * H[:, -1], innovation_scale(H, r)),
          "IN4": lambda H: arp_cs(H, a4),
          "NA4": lambda H: na4.center_scale(H)[:2],
          "CA16": lambda H: (np.zeros(len(H), complex), np.sqrt(np.mean(abs(H) ** 2, 1)))}
    W = steer_whitened(a4)
    ob = np.array(bins); refmask = (abs(ob[:, None] - ob[None, :]) > 1).astype(float)
    Sc, Pc, _ = segments(z, ca); St, Pt, _ = segments(z, te); n = len(St)
    # thresholds: per-look (window at look 0 on clean calibration segments) and dwell
    Lc, Dc = all_stats(Sc, Sc, Pc, cs, a4, W, B, refmask)
    qL = {(m, a): conformal_quantile(Lc[m][:, 0], a) for m in LOOK for a in ALPHAS}
    qD = {(d, k, a): conformal_quantile(v, a) for (d, k), v in Dc.items() for a in ALPHAS}
    res = dict(r=np.array([r.real, r.imag]), a4=a4, nu4=nu4, n=n, B=B)
    Lt, Dt = all_stats(St, St, Pt, cs, a4, W, B, refmask)
    for (d, k), v in Dt.items():
        for a in ALPHAS: res[f"C|{d}|K{k}|{a}|pfa"] = float(np.mean(v > qD[(d, k, a)]))
    for m in LOOK:
        for a in ALPHAS:
            res[f"L|{m}|{a}|pfa_look"] = (Lt[m] > qL[(m, a)]).mean(0)
            res[f"L|{m}|{a}|pfa_cum"] = np.array([(Lt[m][:, :k] > qL[(m, a)]).any(1).mean() for k in KS])
    rng = np.random.default_rng(seed)
    amp = np.sqrt(.5) * (rng.standard_normal(n) + 1j * rng.standard_normal(n))
    om = {"random": rng.uniform(-np.pi, np.pi, n), "matched": np.full(n, np.angle(r)), "opposite": np.full(n, np.angle(r) + np.pi)}
    tpos = np.arange(M + K)

    def inject(prof, t0, dop, sdb):
        tv = prof[None, :] * np.exp(1j * om[dop][:, None] * (tpos[None, :] - t0))
        return St + (np.sqrt(10 ** (sdb / 10) * Pt) * amp)[:, None] * tv

    # Part C: abrupt persistent target, all Doppler relations
    g1, t01 = ramp_profile(1, "in")
    for dop in om:
        pd = {}
        for i, sdb in enumerate(SCR_DB):
            _, D = all_stats(inject(g1, t01, dop, sdb), St, Pt, cs, a4, W, B, refmask)
            for (d, k), v in D.items():
                for a in ALPHAS:
                    pd.setdefault((d, k, a), np.zeros(len(SCR_DB)))[i] = np.mean(v > qD[(d, k, a)])
        for (d, k, a), v in pd.items(): res[f"C|{d}|K{k}|{a}|{dop}|pd"] = v
    # Part R: ramps (random Doppler, alpha = 0.01)
    a = 0.01
    for place in ("pre", "in"):
        for L in LS:
            g, t0 = ramp_profile(L, place)
            look = {m: np.zeros((len(SCR_DB), K)) for m in LOOK}; cum = {m: np.zeros(len(SCR_DB)) for m in LOOK}
            first = {}; dw = {d: np.zeros(len(SCR_DB)) for d in DWELL}
            for i, sdb in enumerate(SCR_DB):
                Ls, D = all_stats(inject(g, t0, "random", sdb), St, Pt, cs, a4, W, B, refmask)
                for m in LOOK:
                    dec = Ls[m] > qL[(m, a)]; look[m][i] = dec.mean(0); anyd = dec.any(1); cum[m][i] = anyd.mean()
                    if i == I10: first[m] = float(np.argmax(dec[anyd], 1).mean()) if anyd.any() else np.nan
                for d in DWELL: dw[d][i] = np.mean(D[(d, 8)] > qD[(d, 8, a)])
            for m in LOOK:
                res[f"R|{place}|L{L}|{m}|look"] = look[m]; res[f"R|{place}|L{L}|{m}|cum"] = cum[m]; res[f"R|{place}|L{L}|{m}|first10"] = first[m]
            for d in DWELL: res[f"R|{place}|L{L}|{d}|dwell"] = dw[d]
    # Part A
    res.update(part_a(z, ca, te, r, np.random.default_rng(seed + 1)))
    return res


def unit(args):
    num, pol, rot = args
    path = os.path.join(OUT, f"x_{num}_{pol}_rot{rot}.npz")
    if os.path.exists(path): return path
    t0 = time.time(); d = load(num); z = d["z"][pol]
    seed = int(hashlib.sha256(f"R10|{num}|{pol}|{rot}".encode()).hexdigest()[:8], 16)
    res = run_unit(z, d["bins"], tuple(BLOCKS[b] for b in ROT[rot]), seed)
    tmp = path + ".tmp.npz"
    np.savez_compressed(tmp, **res, scr_db=SCR_DB, day=FILES[num][1], seconds=time.time() - t0)
    os.replace(tmp, path); return path


def synthetic():
    """Mechanics check on AR(1)+noise (not IPIX): PAMF-H(K'=1) must equal IN4^2; dwell Pfa near alpha."""
    rng = np.random.default_rng(0); T, B = 60000, 9; rho = 0.93 * np.exp(-0.2j)
    e = np.sqrt(.5) * (rng.standard_normal((T, B)) + 1j * rng.standard_normal((T, B)))
    x = np.zeros((T, B), complex)
    for t in range(1, T): x[t] = rho * x[t - 1] + np.sqrt(1 - abs(rho) ** 2) * e[t]
    tex = np.exp(rng.normal(0, 1, (T // 2048 + 1, B))).repeat(2048, 0)[:T]
    z = np.sqrt(10 * tex) * x + np.sqrt(.5) * (rng.standard_normal((T, B)) + 1j * rng.standard_normal((T, B)))
    blocks = ((0, 18000), (20000, 38000), (40000, 60000))
    import run_study; run_study.T = T
    Xtr, _, _ = episodes(z, *blocks[0], M, STRIDE); a4 = fit_arp(Xtr, P4); W = steer_whitened(a4)
    St, Pt, _ = segments(z, blocks[2])
    D = pamf(St, a4, W); c, s = arp_cs(St[:, :M], a4); in4 = (abs(St[:, M] - c) / s) ** 2
    print("C1 mechanics: max |PAMF-H(K'=1) - IN4^2| =", float(np.max(abs(D[("PAMFH", 1)] - in4))))
    t0 = time.time(); res = run_unit(z, list(range(B)), blocks, 1)
    print(f"unit seconds {time.time() - t0:.0f}")
    for d in DWELL + ("PAMFH",):
        k = [f"C|{d}|K8|0.01|pfa"]
        print(d, "dwell Pfa K8:", [round(res[x], 4) for x in k], "Pd@10dB random:", round(res[f"C|{d}|K8|0.01|random|pd"][I10], 3))
    print("per-look IN1 Pfa:", np.round(res["L|IN1|0.01|pfa_look"], 4))
    print("ramp pre L16 IN1 look Pd@10:", np.round(res["R|pre|L16|IN1|look"][I10], 3))
    print("A:", {k: round(v, 4) for k, v in res.items() if k.startswith("A|0.05")})


if __name__ == "__main__":
    ap = argparse.ArgumentParser(); ap.add_argument("--workers", type=int, default=8); ap.add_argument("--synthetic", action="store_true")
    a = ap.parse_args()
    if a.synthetic: synthetic(); sys.exit()
    if not frozen(): sys.exit("PROTOCOL_R10.md does not match its hash.")
    os.makedirs(OUT, exist_ok=True); os.environ["OPENBLAS_NUM_THREADS"] = "2"
    json.dump(dict(started=time.strftime("%Y-%m-%d %H:%M:%S"), gpu=os.environ.get("INARCP_GPU"),
                   protocol_sha=open(os.path.join(HERE, "PROTOCOL_R10.sha256")).read().split()[0],
                   script_sha=hashlib.sha256(open(__file__, "rb").read()).hexdigest()),
              open(os.path.join(OUT, f"manifest_{int(time.time())}.json"), "w"), indent=1)
    from concurrent.futures import ProcessPoolExecutor
    jobs = [(f, pol, r) for f in FILES for pol in ("like0", "like1") for r in (2, 3)]
    with ProcessPoolExecutor(a.workers) as ex:
        for p in ex.map(unit, jobs): print("saved", os.path.basename(p), flush=True)
