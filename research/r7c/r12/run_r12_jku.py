"""R12 Part J (PROTOCOL_R12.md, "Common definitions" and "Part J"): JKU 77 GHz FMCW with real mutual interference.
Certified dwell integration with fast-time mitigation N (none), Z (R11 zeroing) and ZAR (zeroing + AR(8) gap filling).

Fit (AR(1) r) on meas_1_ref_corner frames 0-32, calibrate on frames 34-65 (alpha = 0.01), test on frames 50-99 of
meas_2_int_A and meas_5_int_C and, as a clean check, on reference frames 67-99. Segments: 24 chirps (16 history + 8
dwell), 5 per frame (chirps 0-119), bins 8-247. Targets: persistent Swerling-1 beat tones injected in the raw ADC
domain on the dwell chirps, before the fast-time diff, zeroing/reconstruction and range FFT. The zeroing mask and the
ZAR AR(8) coefficients are those of the data without targets, so the chain is linear: each CUT's target is propagated
alone (exact lone-tone response per chirp and bin), which avoids the leakage between targets that zeroing gaps cause
for any comb of simultaneous targets (the comb leakage is still measured and reported as a diagnostic).

Usage:
  python run_r12_jku.py --data <dir>       protocol run -> study/results/r12/j_st<s>_rx<r>.npz + manifest
  python run_r12_jku.py --mechanics <dir>  mechanics check on meas_0_ref.mat only (used by no outcome): all three
                                           runs are meas_0_ref, synthetic Bernoulli(0.05) hit masks, synthetic
                                           interference bursts in run "A"; station 1, rx 0; prints a summary.
"""
import sys, os, io, json, math, hashlib, argparse, time
HERE = os.path.dirname(os.path.abspath(__file__)); ROOT = os.path.dirname(HERE)
sys.path.insert(0, ROOT); sys.path.insert(0, HERE)
import numpy as np
from numpy.lib.stride_tricks import sliding_window_view
from scipy.io import loadmat
from scipy.ndimage import binary_dilation
from scipy.sparse import csr_matrix
from methods import conformal_quantile, fit_ols
import laws

# ---------------------------------------------------------------- conventions (R11 run_r11_jku.py)
RX = (0, 5, 10, 15)
STATIONS = (1, 2)
BINS = np.arange(8, 248); NB = len(BINS)
HANN = np.hanning(512)
HP = np.abs(1 - np.exp(-2j * np.pi * BINS / 512))
RUNS = {"ref": "meas_1_ref_corner.mat", "A": "meas_2_int_A.mat", "C": "meas_5_int_C.mat"}
MECH_FILE = "meas_0_ref.mat"
OUT = os.path.join(ROOT, "study", "results", "r12")

# ---------------------------------------------------------------- R12 Part J design
ALPHA = 0.01
M, K, L = 16, 8, 24                    # history, dwell, segment length (chirps)
NSEG, NCH = 5, 120                     # segments per frame, chirps used per frame
KH, CLIP, ETA = 8, 6.0, 6.0            # OS history rank, clip level, binary per-look threshold
SCR_DB = np.arange(-5, 25.01, 2.5)
F_TRAIN, F_CAL = np.arange(0, 33), np.arange(34, 66)
F_TEST = {"ref": np.arange(67, 100), "A": np.arange(50, 100), "C": np.arange(50, 100)}
F_HITMODEL, START_MAX = 50, 104        # hit model: frames 0..49 of the test run, block starts 0..104
STRATA = (("s0", 0, 0), ("s1", 1, 2), ("s2", 3, 5), ("s3", 6, L))
STRATA_LABELS = ("0", "1-2", "3-5", ">=6", "all")
MITS = ("N", "Z", "ZAR")
DETS = ("IN1", "OS1_8", "D-IN1", "Clip-OS1", "Bin-OS1", "Clip-OS1-cert", "Bin-OS1-cert")
P_AR, MIN_KEEP = 8, 32                 # ZAR: AR order, minimum unmasked samples per chirp
COMB = 8                               # leakage diagnostic: targets 8 bins away (a comb of every 16th bin)
DWELL_C = (np.arange(NSEG)[:, None] * L + np.arange(M, L)).ravel()   # the 40 dwell chirps of a frame
MECH_P, MECH_LEN, MECH_JNR = 0.05, 60, 30.0                            # mechanics: hit rate, burst length, burst RMS ratio


def frozen():
    h = open(os.path.join(HERE, "PROTOCOL_R12.sha256")).read().split()[0]
    return hashlib.sha256(open(os.path.join(HERE, "PROTOCOL_R12.md"), "rb").read()).hexdigest() == h


def seed(*parts):
    return int(hashlib.sha256("|".join(("R12", "J") + tuple(map(str, parts))).encode()).hexdigest()[:16], 16)


def db(x):
    return float(10 * np.log10(x)) if x > 0 else -np.inf


def rate(x):
    return float(np.mean(x)) if len(x) else np.nan


# ---------------------------------------------------------------- fast-time processing (R11 profiles(), split up)
def load_rx(path, st, rx):
    v = f"data_station_{st}"
    d = loadmat(path, variable_names=[v])[v]
    x = np.ascontiguousarray(d[:, :, rx, :], dtype=np.float64)          # (512, 128, 100)
    del d
    return x


def hpdiff(x):
    """R11 [1, -1] fast-time high-pass along axis 0 (first sample 0)."""
    return np.diff(x, axis=0, prepend=x[:1])


def zero_mask(x):
    """R11 zeroing mask on the high-passed chirps (512, ...): |x| > 4 median|x| of the chirp, +-4 samples."""
    med = np.median(np.abs(x), axis=0, keepdims=True)
    return binary_dilation(np.abs(x) > 4 * med, structure=np.ones((9,) + (1,) * (x.ndim - 1), bool))


def range_profiles(x):
    """R11 range profiles of high-passed (and mitigated) chirps (512, ...): Hann, FFT, bins 8-247, / |HP|."""
    sh = (-1,) + (1,) * (x.ndim - 1)
    return np.fft.fft(x * HANN.reshape(sh), axis=0)[BINS] / HP.reshape(sh)


# ---------------------------------------------------------------- ZAR: AR(8) gap reconstruction
def ar_fit(x, keep):
    """Real AR(8), x_t = sum_k a_k x_{t-k}, by least squares on the forward and backward equations stacked, over the
    9-sample windows that lie entirely inside unmasked runs. x, keep: (n, 512). Sample 0 (the artificial zero of the
    diff) is never used. Returns a (n, 8) and the number of windows per chirp."""
    v = keep.copy(); v[:, 0] = False
    W = sliding_window_view(x, P_AR + 1, axis=1)                       # (n, 504, 9): x[t-8..t]
    ok = sliding_window_view(v, P_AR + 1, axis=1).all(2)
    C = np.empty((len(x), P_AR + 1, P_AR + 1))
    for i in range(0, len(x), 1024):
        Wi = W[i:i + 1024]
        C[i:i + 1024] = np.matmul((Wi * ok[i:i + 1024, :, None]).transpose(0, 2, 1), Wi)
    k = np.arange(1, P_AR + 1)
    R = C[:, P_AR - k[:, None], P_AR - k[None, :]] + C[:, k[:, None], k[None, :]]   # forward + backward normal matrix
    rhs = C[:, P_AR - k, P_AR] + C[:, k, 0]
    a = np.einsum("nij,nj->ni", np.linalg.pinv(R), rhs)
    return a, ok.sum(1)


def pole_radius(a):
    Cm = np.zeros((len(a), P_AR, P_AR)); Cm[:, 0, :] = a; Cm[:, np.arange(1, P_AR), np.arange(P_AR - 1)] = 1.0
    return np.abs(np.linalg.eigvals(Cm)).max(1) if len(a) else np.zeros(0)


def gap_plan(keep, a):
    """Zeroed gaps (maximal masked runs) of every chirp with >= 32 unmasked samples, with the availability of 8
    unmasked context samples on each side. Chirps with fewer unmasked samples stay zeroed."""
    n = len(keep)
    v = keep.copy(); v[:, 0] = False
    fill = ~keep & (keep.sum(1) >= MIN_KEEP)[:, None]
    e = np.zeros((n, 1), np.int8)
    d = np.diff(np.concatenate([e, fill.astype(np.int8), e], 1), axis=1)
    c, g0 = np.nonzero(d == 1); _, g1 = np.nonzero(d == -1)             # row-major: starts and ends pair up
    Lg = g1 - g0
    cv = np.concatenate([np.zeros((n, 1), np.int64), np.cumsum(v, 1)], 1)   # valid samples in [0, t)
    left = (g0 >= P_AR) & (cv[c, g0] - cv[c, np.maximum(g0 - P_AR, 0)] == P_AR)
    right = (g1 + P_AR <= 512) & (cv[c, np.minimum(g1 + P_AR, 512)] - cv[c, g1] == P_AR)
    o = np.argsort(-Lg, kind="stable")
    filled = int(Lg[left | right].sum())
    return dict(keep=keep, c=c[o], g0=g0[o], L=Lg[o], left=left[o], right=right[o], a=a[c[o]],
                unfilled=int((~keep).sum()) - filled, chirps=np.unique(c))


def _zar_gen(plan, ctx, ch, budget=2 ** 23):
    """Gap filling core. ctx(chirps (g,), positions (g, 8)) -> context samples (g, 8, ch). Yields, per chunk of gaps,
    (chirp index, sample index, fill value (nsamp, ch)) for every gap sample: the AR(8) forward prediction from the left
    context and the backward prediction from the right context, crossfaded linearly (forward weight (L - i) / (L + 1)
    at gap sample i, i.e. 1 -> 0 across the gap); one side only if only that side has 8 unmasked context samples; zero
    if neither. For a fixed plan (mask and coefficients) the fill is linear in the signal."""
    c, g0, Lg, left, right, a = (plan[k] for k in ("c", "g0", "L", "left", "right", "a"))
    G = len(c); j = np.arange(P_AR)
    i0 = 0
    while i0 < G:
        Lmax = int(Lg[i0]); sl = slice(i0, min(G, i0 + max(1, budget // ((P_AR + Lmax) * ch)))); i0 = sl.stop
        cc, s0, LL, lf, rt = c[sl], g0[sl], Lg[sl], left[sl], right[sl]
        arev = a[sl][:, ::-1]                                           # (a_8 .. a_1)
        F = np.zeros((len(cc), P_AR + Lmax, ch)); B = np.zeros_like(F)
        F[:, :P_AR] = ctx(cc, np.clip(s0[:, None] - P_AR + j, 0, 511)) * lf[:, None, None]             # x[g0-8 .. g0-1]
        B[:, :P_AR] = ctx(cc, np.clip((s0 + LL)[:, None] + P_AR - 1 - j, 0, 511)) * rt[:, None, None]  # x[g1+7 .. g1]
        nact = np.searchsorted(-LL, -np.arange(Lmax), side="left")      # number of gaps longer than i
        for i in range(Lmax):
            na = nact[i]
            F[:na, P_AR + i] = np.einsum("gk,gkc->gc", arev[:na], F[:na, i:i + P_AR])
            B[:na, P_AR + i] = np.einsum("gk,gkc->gc", arev[:na], B[:na, i:i + P_AR])
        rep = np.repeat(np.arange(len(cc)), LL); off = np.arange(len(rep)) - np.repeat(np.cumsum(LL) - LL, LL)
        Lr = LL[rep]
        f, b = F[rep, P_AR + off], B[rep, P_AR + Lr - 1 - off]
        wf = ((Lr - off) / (Lr + 1.0))[:, None]
        lr, rr = lf[rep][:, None], rt[rep][:, None]
        yield cc[rep], s0[rep] + off, np.where(lr & rr, wf * f + (1 - wf) * b, np.where(lr, f, np.where(rr, b, 0.0)))


def zar_fill(x, plan):
    """x: (n, 512, ch) high-passed chirps -> keep * x with every gap filled (see _zar_gen)."""
    out = x * plan["keep"][:, :, None]
    for ci, pi, y in _zar_gen(plan, lambda cc, pos: x[cc[:, None], pos], x.shape[2]):
        out[ci, pi] = y
    return out


def zar_selftest():
    """Mechanics only: a sum of three sinusoids (an AR(6) process) plus 1e-6 noise must be reconstructed almost exactly
    in a 40-sample gap (both contexts), a gap at the chirp end (left context only) and one at the start (right only)."""
    n = np.arange(512)
    x = hpdiff(sum(np.cos(2 * np.pi * f * n / 512 + p) for f, p in ((37.3, .4), (81.7, 1.9), (140.2, -2.2)))
               + 1e-6 * np.random.default_rng(seed("zar-selftest")).standard_normal(512))
    out = {}
    for lab, (a0, a1) in (("both sides", (200, 240)), ("left only", (490, 512)), ("right only", (1, 30))):
        keep = np.ones((1, 512), bool); keep[0, a0:a1] = False
        a, _ = ar_fit(x[None], keep)
        y = zar_fill(x[None, :, None], gap_plan(keep, a))[0, :, 0]
        out[lab] = float(np.sum((y - x)[a0:a1] ** 2) / np.sum(x[a0:a1] ** 2))
    return out


# ---------------------------------------------------------------- targets
NN =np.arange(512)[:, None]; TH = 2 * np.pi * BINS / 512
BASIS = hpdiff(np.concatenate([np.cos(NN * TH), np.sin(NN * TH)], 1))       # (512, 2 NB): high-passed unit raw tones
KER = np.tile(HANN[:, None] * np.exp(-1j * NN * TH) / HP, 2)                  # (512, 2 NB): profile kernel at each tone's bin


def tone_response(keep, plan):
    """Exact response, at its own bin, of a lone unit raw-ADC tone cos(2 pi b n / 512) (columns :NB) or sin (columns
    NB:) at every bin b, per chirp, through diff -> mitigation -> Hann FFT -> / |HP|. keep (n, 512): the data's zeroing
    mask; plan: the data's ZAR plan (mask and AR coefficients fixed, so the chain is linear). Each bin's target is
    thereby processed alone: no leakage between targets. Returns {mitigation: (n, 2 NB) complex}."""
    KB = KER * BASIS
    rZ = keep.astype(float) @ KB
    rF = np.zeros(rZ.shape, complex)
    for ci, pi, y in _zar_gen(plan, lambda cc, pos: BASIS[pos], BASIS.shape[1]):
        rF += csr_matrix((np.ones(len(ci)), (ci, np.arange(len(ci)))), shape=(len(keep), len(ci))) @ (KER[pi] * y)
    return {"N": np.broadcast_to(KB.sum(0), rZ.shape), "Z": rZ, "ZAR": rZ + rF}


def target_amplitudes(medP, g, w):
    """G = A_b g e^{j w t} on the dwell chirps (t = 16..23 in the segment), A_b = 2 sqrt(medP_b) / sum(HANN) (unit SCR),
    so that s[n] = Re{G e^{j 2 pi b n / 512}} has range-profile power |g|^2 medP_b at bin b. g, w: (NB, nf, NSEG).
    Returns (NB, NSEG * K, nf): dwell chirp index s * 8 + (t - 16)."""
    A = 2 * np.sqrt(medP) / HANN.sum()
    G = A[:, None, None, None] * g[..., None] * np.exp(1j * w[..., None] * np.arange(M, L))   # (NB, nf, NSEG, K)
    return G.transpose(0, 2, 3, 1).reshape(NB, NSEG * K, g.shape[1])


def subcomb_signal(G):
    """Reference diagnostic only (not used for Pd): raw signal of a comb of targets on every 16th bin,
    (b - 8) % 16 == 0, to measure the leakage into the empty slots 8 bins away. Returns (512, 40, nf)."""
    sel = np.arange(NB) % (2 * COMB) == 0
    Gs = G[sel].reshape(sel.sum(), -1)
    return (np.cos(NN * TH[sel]) @ Gs.real - np.sin(NN * TH[sel]) @ Gs.imag).reshape(512, *G.shape[1:])


# ---------------------------------------------------------------- segments, innovations, detectors
def segments(P, frames):
    """Profiles (240, 128, 100) -> segment rows (bin, frame, segment) x 24 chirps."""
    X = P[:, :NCH, frames].reshape(NB, NSEG, L, len(frames)).transpose(0, 3, 1, 2)
    return X.reshape(-1, L)


def seg_hitcount(h, frames):
    c = h[:NCH, frames].reshape(NSEG, L, len(frames)).sum(1).T                # (nf, NSEG)
    return np.broadcast_to(c, (NB,) + c.shape).ravel()


def innov(X, r):
    e = np.empty_like(X)
    e[:, 0] = np.sqrt(1 - abs(r) ** 2) * X[:, 0]
    e[:, 1:] = X[:, 1:] - r * X[:, :-1]
    return e


def statistics(P):
    """P: AR(1) innovation powers (n, 24). IN1 / OS1_8 as R11 scores() at the first dwell chirp (history 0..15)."""
    H, D = P[:, :M], P[:, M:]
    with np.errstate(divide="ignore", invalid="ignore"):
        mh = H.mean(1); s8 = np.partition(H, KH - 1, 1)[:, KH - 1]
        s = {"IN1": np.sqrt(D[:, 0] / mh), "OS1_8": np.sqrt(D[:, 0] / s8), "D-IN1": D.sum(1) / mh,
             "Clip-OS1": laws.robust_stat(H, D, KH, "clip", c=CLIP), "Bin-OS1": laws.robust_stat(H, D, KH, "bin", eta=ETA)}
    s["Clip-OS1-cert"], s["Bin-OS1-cert"] = s["Clip-OS1"], s["Bin-OS1"]
    return s


def cert_q(W):
    n = len(W); k = laws.conformal_rank(n, ALPHA)
    return math.inf if k > n else float(np.partition(W, k - 1)[k - 1])


# ---------------------------------------------------------------- mechanics-only synthetic interference
def add_interference(xr, hits, rng):
    """On hit chirps: Gaussian noise with 30x the chirp's raw (AC) RMS on a random contiguous block of 60 samples."""
    x = xr.copy()
    c, f = np.nonzero(hits)
    rms = xr.std(axis=0)[c, f]
    idx = rng.integers(0, 512 - MECH_LEN + 1, len(c))[:, None] + np.arange(MECH_LEN)
    x[idx, c[:, None], f[:, None]] += MECH_JNR * rms[:, None] * rng.standard_normal((len(c), MECH_LEN))
    return x


# ---------------------------------------------------------------- one (station, rx) unit
def unit(data, st, rx, mech=False):
    t0 = time.time(); res, chk = {}, {}
    if mech:
        base = load_rx(os.path.join(data, MECH_FILE), st, rx)
        files = {k: f"mechanics:{k}:{MECH_FILE}" for k in RUNS}
        hits, raw = {}, {}
        for k in RUNS:
            hits[k] = np.random.default_rng(seed(files[k], st, rx, "hits")).random((128, 100)) < MECH_P
            raw[k] = add_interference(base, hits[k], np.random.default_rng(seed(files[k], st, rx, "interference"))) if k == "A" else base
    else:
        files = dict(RUNS)
        raw = {k: load_rx(os.path.join(data, f), st, rx) for k, f in RUNS.items()}
    res["t_load_s"] = time.time() - t0

    # fast-time processing; the zeroing mask is computed on the data without targets
    D = {k: hpdiff(v) for k, v in raw.items()}
    KEEP = {k: ~zero_mask(v) for k, v in D.items()}
    prof = {"N": {k: range_profiles(D[k]) for k in RUNS}, "Z": {k: range_profiles(D[k] * KEEP[k]) for k in RUNS}}
    medP = np.median(np.abs(prof["N"]["ref"]) ** 2, axis=(1, 2))
    if not mech:
        hits = {k: (np.abs(prof["N"][k]) ** 2 > 10 * medP[:, None, None]).mean(0) > 0.1 for k in RUNS}
    for k in RUNS:
        res[f"hitrate|{k}"] = float(hits[k].mean())
        res[f"hitrate_test|{k}"] = float(hits[k][:NCH, F_TEST[k]].mean())
        res[f"zeroed|{k}"] = float(1 - KEEP[k].mean())
        res[f"zeroed_test|{k}"] = float(1 - KEEP[k][:, :NCH, F_TEST[k]].mean())
    res["medP"] = medP

    # ZAR on the frames each run needs (ref: train + cal + test; A, C: test)
    prof["ZAR"], AR = {}, {}
    for k in RUNS:
        fr = np.union1d(np.union1d(F_TRAIN, F_CAL), F_TEST[k]) if k == "ref" else F_TEST[k]
        xc = D[k][:, :NCH, fr].transpose(2, 1, 0).reshape(-1, 512)
        kc = KEEP[k][:, :NCH, fr].transpose(2, 1, 0).reshape(-1, 512)
        a, _ = ar_fit(xc, kc)
        plan = gap_plan(kc, a)
        y = zar_fill(xc[:, :, None], plan)[:, :, 0].reshape(len(fr), NCH, 512).transpose(2, 1, 0)
        P = np.full((NB, 128, 100), np.nan + 0j); P[:, :NCH, fr] = range_profiles(y)
        prof["ZAR"][k] = P; AR[k] = (fr, a)
        if mech and k == "A":                                                # clean truth known: meas_0_ref without bursts
            gapm = ~KEEP[k][:, :NCH, fr]; xt = D["ref"][:, :NCH, fr]; hc = np.broadcast_to(hits[k][:NCH, fr], gapm.shape)
            for lab, sel in (("hit chirps", gapm & hc), ("other chirps", gapm & ~hc)):
                chk[f"ZAR fill error / clean signal energy in zeroed samples, {lab} (Z: 1)"] = float(np.sum((y - xt)[sel] ** 2) / np.sum(xt[sel] ** 2))
        res[f"zar_unfilled|{k}"] = plan["unfilled"] / kc.size
        res[f"zar_unstable|{k}"] = float(np.mean(pole_radius(a[plan["chirps"]]) > 1)) if len(plan["chirps"]) else 0.0
        res[f"zar_finite|{k}"] = bool(np.isfinite(P[:, :NCH, fr]).all())

    # certified hit model: random contiguous 24-chirp blocks of the detected masks of frames 0..49 of the run
    ncal = NB * len(F_CAL) * NSEG
    bad = {}
    for k in RUNS:
        rng = np.random.default_rng(seed(files[k], st, rx, "certmask"))
        fi = rng.integers(0, F_HITMODEL, ncal); s0 = rng.integers(0, START_MAX + 1, ncal)
        mk = hits[k][s0[:, None] + np.arange(L), fi[:, None]]
        bad[k] = laws.corrupted_innovations(mk, p=1)
        res[f"cert_hitfrac|{k}"] = float(mk.mean())

    # targets: a lone raw-ADC beat tone per CUT on the dwell chirps, through the data's zeroing mask and ZAR plan
    # (mask and AR coefficients fixed -> linear chain); unit SCR, scaled by sqrt(SCR) below
    TS = {m: {} for m in MITS}
    vict = np.arange(NB) % (2 * COMB) == COMB                                # diagnostic: empty slots 8 bins from the sub-comb
    for k in RUNS:
        fr = F_TEST[k]; nf = len(fr); nd = len(DWELL_C)
        rng = np.random.default_rng(seed(files[k], st, rx, "target"))
        g = np.sqrt(.5) * (rng.standard_normal((NB, nf, NSEG)) + 1j * rng.standard_normal((NB, nf, NSEG)))
        w = rng.uniform(-np.pi, np.pi, (NB, nf, NSEG))
        G = target_amplitudes(medP, g, w)                                    # (NB, 40, nf)
        keep_d = KEEP[k][:, DWELL_C][:, :, fr]                               # (512, 40, nf)
        kd = keep_d.transpose(2, 1, 0).reshape(-1, 512)                      # rows: frame * 40 + dwell chirp
        zfr, a = AR[k]; pos = np.searchsorted(zfr, fr); assert np.array_equal(zfr[pos], fr)
        a_d = a[(pos[:, None] * NCH + DWELL_C[None, :]).ravel()]
        plan_d = gap_plan(kd, a_d)
        Rt = tone_response(kd, plan_d)                                       # {m: (nf * 40, 2 NB)}
        Gr = G.transpose(2, 1, 0).reshape(-1, NB)                            # rows as kd
        gd = g.transpose(0, 2, 1)[:, np.arange(nd) // K, :]                  # (NB, 40, nf)
        hd = hits[k][np.ix_(DWELL_C, fr)]                                    # (40, nf)
        dS = hpdiff(subcomb_signal(G))                                       # reference diagnostic (comb leakage)
        ys = zar_fill(dS.transpose(2, 1, 0).reshape(-1, 512)[:, :, None], plan_d)[:, :, 0]
        comb = {"N": range_profiles(dS), "Z": range_profiles(dS * keep_d),
                "ZAR": range_profiles(ys.reshape(nf, nd, 512).transpose(2, 1, 0))}
        del dS, ys
        for m in MITS:
            T = (Gr.real * Rt[m][:, :NB] - Gr.imag * Rt[m][:, NB:]).reshape(nf, nd, NB).transpose(2, 1, 0)   # (NB, 40, nf)
            e0 = np.abs(gd) ** 2 * medP[:, None, None]                       # nominal target power
            res[f"tgain|{m}|{k}"] = db(np.sum(np.abs(T) ** 2) / np.sum(e0))
            res[f"tgainhit|{m}|{k}"] = db(np.sum(np.abs(T) ** 2 * hd) / np.sum(e0 * hd)) if hd.any() else np.nan
            res[f"tfinite|{m}|{k}"] = bool(np.isfinite(T).all())
            lp = np.abs(comb[m][vict]) ** 2                                  # power at the empty slots / nominal target power there
            res[f"combleak|{m}|{k}"] = db(lp.sum() / (medP[vict].sum() * nd * nf))
            res[f"combleakmax|{m}|{k}"] = db((lp.mean((1, 2)) / medP[vict]).max())
            res[f"combleakhit|{m}|{k}"] = db((lp * hd).sum() / (medP[vict].sum() * hd.sum())) if hd.any() else np.nan
            Tseg = np.zeros((NB, nf, NSEG, L), complex)
            Tseg[..., M:] = T.reshape(NB, NSEG, K, nf).transpose(0, 3, 1, 2)
            TS[m][k] = Tseg.reshape(-1, L)
        if mech and k == "A":                                                # exact response vs brute-force raw injection
            rb = np.random.default_rng(seed(files[k], st, rx, "bruteforce"))
            hr = hd.T.ravel(); gap = (~kd).any(1)
            rows = np.concatenate([rb.choice(np.nonzero(hr)[0], 32, replace=False), rb.choice(np.nonzero(~hr & gap)[0], 32, replace=False)])
            err = {m: 0.0 for m in MITS}
            for rw in rows:
                bi = rb.integers(NB); gt = rb.standard_normal() + 1j * rb.standard_normal()
                x = hpdiff(np.real(gt * np.exp(1j * TH[bi] * np.arange(512))))
                y = {"N": x, "Z": x * kd[rw], "ZAR": zar_fill(x[None, :, None], gap_plan(kd[rw:rw + 1], a_d[rw:rw + 1]))[0, :, 0]}
                for m in MITS:
                    bf = range_profiles(y[m])[bi]
                    err[m] = max(err[m], abs(gt.real * Rt[m][rw, bi] - gt.imag * Rt[m][rw, NB + bi] - bf) / abs(bf))
            for m in MITS: chk[f"lone-tone response {m} vs brute-force raw injection (64 chirps, run A), max rel err"] = err[m]
        del Rt, comb

    # detection
    for m in MITS:
        r = fit_ols(segments(prof[m]["ref"], F_TRAIN)); res[f"r|{m}"] = np.array([r.real, r.imag])
        Pc = np.abs(innov(segments(prof[m]["ref"], F_CAL), r)) ** 2
        sc = statistics(Pc)
        q0 = {d: conformal_quantile(sc[d], ALPHA) for d in DETS if not d.endswith("-cert")}
        for k in RUNS:
            q = dict(q0)
            q["Clip-OS1-cert"] = cert_q(laws.worst_case(Pc[:, :M], Pc[:, M:], bad[k][:, :M], bad[k][:, M:], KH, "clip", c=CLIP))
            q["Bin-OS1-cert"] = cert_q(laws.worst_case(Pc[:, :M], Pc[:, M:], bad[k][:, :M], bad[k][:, M:], KH, "bin", eta=ETA))
            for d in DETS: res[f"q|{m}|{k}|{d}"] = q[d]
            fr = F_TEST[k]
            ed = innov(segments(prof[m][k], fr), r); eT = innov(TS[m][k], r)
            hc = seg_hitcount(hits[k], fr)
            sel = {s: (hc >= lo) & (hc <= hi) for s, lo, hi in STRATA}; sel["all"] = np.ones(len(hc), bool)
            s0 = statistics(np.abs(ed) ** 2)
            for s, ms in sel.items():
                res[f"n|{m}|{k}|{s}"] = int(ms.sum())
                for d in DETS: res[f"pfa|{m}|{k}|{d}|{s}"] = rate(s0[d][ms] > q[d])
            for d in DETS: res[f"nan|{m}|{k}|{d}"] = int(np.isnan(s0[d]).sum())
            pd = {(d, s): np.full(len(SCR_DB), np.nan) for d in DETS for s in sel}
            for i, sdb in enumerate(SCR_DB):
                s1 = statistics(np.abs(ed + np.sqrt(10 ** (sdb / 10)) * eT) ** 2)
                for d in DETS:
                    ex = s1[d] > q[d]
                    for s, ms in sel.items(): pd[(d, s)][i] = rate(ex[ms])
            for (d, s), v in pd.items(): res[f"pd|{m}|{k}|{d}|{s}"] = v

    if mech:                                                                 # consistency with the R11 template
        for lab, v in zar_selftest().items(): chk[f"ZAR self-test (3 sinusoids), fill error / energy, gap {lab}"] = v
        sys.path.insert(0, os.path.join(ROOT, "r11")); import run_r11_jku as r11
        for zero, m in ((False, "N"), (True, "Z")):
            Zr = r11.profiles(raw["A"], zero)[0]
            chk[f"profiles {m} vs R11 profiles() (run A), max rel diff"] = float(np.max(np.abs(Zr - prof[m]["A"])) / np.max(np.abs(Zr)))
        X = segments(prof["N"]["ref"], F_CAL); r = fit_ols(segments(prof["N"]["ref"], F_TRAIN))
        s11 = r11.scores(X[:, :M + 1], r); s12 = statistics(np.abs(innov(X, r)) ** 2)
        for d in ("IN1", "OS1_8"):
            chk[f"{d} vs R11 scores(), max rel diff"] = float(np.max(np.abs(s11[d] - s12[d]) / s11[d]))

    res.update(scr_db=SCR_DB, strata=np.array([s for s, _, _ in STRATA] + ["all"]), strata_labels=np.array(STRATA_LABELS),
               detectors=np.array(DETS), mitigations=np.array(MITS), alpha=ALPHA, n_cal=ncal, station=st, rx=rx,
               mechanics=mech, runtime_s=time.time() - t0)
    return res, chk


def task(args):
    data, st, rx = args
    path = os.path.join(OUT, f"j_st{st}_rx{rx}.npz")
    if os.path.exists(path): return st, rx, 0.0
    t = time.time(); res, _ = unit(data, st, rx)
    np.savez_compressed(path, **res)
    return st, rx, time.time() - t


# ---------------------------------------------------------------- mechanics summary
def scr50(pd):
    i = np.nonzero(pd >= 0.5)[0]
    if len(i) == 0: return np.nan
    i = i[0]
    if i == 0: return float(SCR_DB[0])
    return float(SCR_DB[i - 1] + (0.5 - pd[i - 1]) / (pd[i] - pd[i - 1]) * (SCR_DB[i] - SCR_DB[i - 1]))


def summary(res, chk):
    R = list(RUNS)
    print(f"\n== R12 Part J mechanics: {MECH_FILE} for all runs, station {res['station']}, rx {res['rx']} ==")
    print(f"runtime: load {res['t_load_s']:.1f} s, total {res['runtime_s']:.1f} s")
    for k, v in chk.items(): print(f"  {k}: {v:.2e}")
    for k in R:
        print(f"run {k:>3}: hit rate {res[f'hitrate|{k}']:.3f} (test {res[f'hitrate_test|{k}']:.3f}); zeroed {res[f'zeroed|{k}']:.4f}; "
              f"ZAR left zero {res[f'zar_unfilled|{k}']:.5f}, unstable AR {res[f'zar_unstable|{k}']:.3f}, finite {res[f'zar_finite|{k}']}; "
              f"cert hit-model rate {res[f'cert_hitfrac|{k}']:.3f}")
    print("AR(1) r: " + ", ".join(f"{m} {complex(*res[f'r|{m}']):.3f}" for m in MITS))
    cols = [(m, k) for m in MITS for k in R]
    hdr = "".join(f"{m + '/' + k:>9}" for m, k in cols)
    print("\nthresholds q\n" + f"{'':14}" + hdr)
    for d in DETS: print(f"{d:14}" + "".join(f"{res[f'q|{m}|{k}|{d}']:9.3f}" for m, k in cols))
    print("\ntarget power at its CUT / nominal SCR x medP (dB), all dwell chirps and hit dwell chirps; and, for reference only,")
    print("the leakage a comb of targets would cause (comb of every 16th bin: power at the empty slots 8 bins away /")
    print("nominal target power there; pooled, worst bin, hit chirps). Pd uses lone-tone responses: no inter-target leakage.")
    print(f"{'':14}" + hdr)
    for lab, key in (("gain", "tgain"), ("gain hit ch.", "tgainhit"), ("comb pooled", "combleak"),
                     ("comb worst", "combleakmax"), ("comb hit ch.", "combleakhit")):
        print(f"{lab:14}" + "".join(f"{res[f'{key}|{m}|{k}']:9.1f}" for m, k in cols))
    print("\nPfa (stratum all)\n" + f"{'':14}" + hdr)
    for d in DETS: print(f"{d:14}" + "".join(f"{res[f'pfa|{m}|{k}|{d}|all']:9.4f}" for m, k in cols))
    print("\nPfa by stratum, run A (n per stratum: " + ", ".join(f"{lab} {res[f'n|N|A|{s}']}" for s, lab in zip(res['strata'], STRATA_LABELS)) + ")")
    print(f"{'':14}" + "".join(f"{m + ':' + lab:>9}" for m in MITS for lab in STRATA_LABELS[:4]))
    for d in DETS: print(f"{d:14}" + "".join(f"{res[f'pfa|{m}|A|{d}|{s}']:9.4f}" for m in MITS for s, _, _ in STRATA))
    print("\nSCR (dB) for Pd = 0.5 (stratum all)\n" + f"{'':14}" + hdr)
    for d in DETS: print(f"{d:14}" + "".join(f"{scr50(res[f'pd|{m}|{k}|{d}|all']):9.1f}" for m, k in cols))
    i10 = int(np.argmin(abs(SCR_DB - 10)))
    print("\nPd at 10 dB (stratum all)\n" + f"{'':14}" + hdr)
    for d in DETS: print(f"{d:14}" + "".join(f"{res[f'pd|{m}|{k}|{d}|all'][i10]:9.3f}" for m, k in cols))
    print("\nPd curve, IN1 and Clip-OS1-cert, run A (SCR " + " ".join(f"{s:g}" for s in SCR_DB) + ")")
    for m in MITS:
        for d in ("IN1", "Clip-OS1-cert"): print(f"  {m:3} {d:14}" + " ".join(f"{v:.2f}" for v in res[f"pd|{m}|A|{d}|all"]))

    print("\nsanity checks")
    ok_all = True
    def check(name, ok, detail):
        nonlocal ok_all; ok_all &= bool(ok); print(f"  [{'PASS' if ok else 'FAIL'}] {name}: {detail}")
    cont = ("IN1", "OS1_8", "D-IN1", "Clip-OS1")
    v = {(m, d): res[f"pfa|{m}|ref|{d}|all"] for m in MITS for d in DETS}
    check("clean check (ref frames 67-99), continuous detectors Pfa in [0.007, 0.013]",
          all(0.007 <= v[(m, d)] <= 0.013 for m in MITS for d in cont),
          ", ".join(f"{m}/{d} {v[(m, d)]:.4f}" for m in MITS for d in cont))
    check("clean check, Bin-OS1 (discrete) and cert detectors Pfa <= 0.013 (conservative by construction)",
          all(v[(m, d)] <= 0.013 for m in MITS for d in DETS if d not in cont),
          ", ".join(f"{m}/{d} {v[(m, d)]:.4f}" for m in MITS for d in DETS if d not in cont))
    check("Clip-OS1-cert Pfa <= 0.01 on the synthetic-interference run A",
          all(res[f"pfa|{m}|A|Clip-OS1-cert|all"] <= 0.01 for m in MITS),
          ", ".join(f"{m} {res[f'pfa|{m}|A|Clip-OS1-cert|all']:.4f} (n {res[f'n|{m}|A|all']})" for m in MITS))
    dips = [(m, k, d, float(np.min(np.diff(res[f"pd|{m}|{k}|{d}|all"])))) for m in MITS for k in R for d in DETS]
    bad = [x for x in dips if x[3] < -0.002]
    flat = [(m, k, d) for m, k, d, _ in dips if res[f"pd|{m}|{k}|{d}|all"][-1] <= res[f"pd|{m}|{k}|{d}|all"][0]]
    check("Pd non-decreasing in SCR (tolerance 0.002) and Pd(25 dB) > Pd(-5 dB), stratum all",
          not bad and not flat, f"largest decrease {min(x[3] for x in dips):+.4f}; violations {bad + flat}")
    nans = {(m, k): sum(res[f"nan|{m}|{k}|{d}"] for d in DETS) for m in MITS for k in R}
    check("ZAR without NaN (profiles, target responses, statistics)",
          all(res[f"zar_finite|{k}"] and res[f"tfinite|ZAR|{k}"] and nans[("ZAR", k)] == 0 for k in R),
          ", ".join(f"{k}: profiles {res[f'zar_finite|{k}']}, targets {res[f'tfinite|ZAR|{k}']}, NaN stats {nans[('ZAR', k)]}" for k in R))
    zs = {k.split("gap ")[1]: v for k, v in chk.items() if k.startswith("ZAR self-test")}
    check("ZAR self-test: sinusoidal (AR(6)) chirp reconstructed in its gaps, error / energy < 1e-6",
          bool(zs) and max(zs.values()) < 1e-6, ", ".join(f"{k} {v:.1e}" for k, v in zs.items()))
    bf = {k: v for k, v in chk.items() if k.startswith("lone-tone")}
    check("targets processed alone (exact lone-tone responses, no leakage between targets): agreement with brute-force "
          "raw injection < 1e-9", bool(bf) and max(bf.values()) < 1e-9, ", ".join(f"{k.split()[2]} {v:.1e}" for k, v in bf.items()))
    check("window leakage from a target 8 bins away < -40 dB (N, comb reference, pooled and worst bin)",
          all(res[f"combleak|N|{k}"] < -40 and res[f"combleakmax|N|{k}"] < -40 for k in R),
          ", ".join(f"{k}: {res[f'combleak|N|{k}']:.1f} / {res[f'combleakmax|N|{k}']:.1f}" for k in R))
    for m in ("Z", "ZAR"):
        print(f"  [info] a comb of every 8th bin would leak under {m}: " + ", ".join(
            f"{k}: pooled {res[f'combleak|{m}|{k}']:.1f}, worst bin {res[f'combleakmax|{m}|{k}']:.1f}, hit chirps "
            f"{res[f'combleakhit|{m}|{k}']:.1f} dB" for k in R) + " (not used)")
    buf = io.BytesIO(); np.savez_compressed(buf, **res)
    print(f"  npz serialisation (in memory, not written): {len(res)} keys, {buf.tell() / 1e6:.2f} MB")
    print("all checks passed" if ok_all else "SOME CHECKS FAILED")


if __name__ == "__main__":
    ap = argparse.ArgumentParser()
    grp = ap.add_mutually_exclusive_group(required=True)
    grp.add_argument("--data", help="protocol run on meas_1_ref_corner, meas_2_int_A, meas_5_int_C")
    grp.add_argument("--mechanics", help="mechanics check on meas_0_ref.mat only")
    ap.add_argument("--workers", type=int, default=4)
    a = ap.parse_args()
    if a.mechanics:
        print("protocol hash matches:", frozen(), flush=True)
        res, chk = unit(a.mechanics, 1, 0, mech=True)
        summary(res, chk)
        sys.exit(0)
    if not frozen(): sys.exit("PROTOCOL_R12.md does not match its hash.")
    missing = [f for f in RUNS.values() if not os.path.exists(os.path.join(a.data, f))]
    if missing: sys.exit(f"missing data files: {missing}")
    os.makedirs(OUT, exist_ok=True)
    json.dump(dict(started=time.strftime("%Y-%m-%d %H:%M:%S"), protocol_sha=open(os.path.join(HERE, "PROTOCOL_R12.sha256")).read().split()[0],
                   script_sha=hashlib.sha256(open(__file__, "rb").read()).hexdigest(), files=RUNS),
              open(os.path.join(OUT, f"manifest_j_{int(time.time())}.json"), "w"), indent=1)
    from concurrent.futures import ProcessPoolExecutor
    jobs = [(a.data, s, r) for s in STATIONS for r in RX]
    with ProcessPoolExecutor(max(1, min(4, a.workers))) as ex:
        for s, r, dt in ex.map(task, jobs): print(f"saved j_st{s}_rx{r}.npz ({dt:.0f} s)", flush=True)
