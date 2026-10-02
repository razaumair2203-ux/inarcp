"""R17 (PROTOCOL_R17.md): a real target with real onsets. A pedestrian walks through the range bins of the JKU 77 GHz
Station 1 under interference scenario A; each arrival of its return in a bin is a real onset in that bin's
frame-to-frame sequence (one chirp per frame, frames 200 ms apart).

Ground truth: Station 1's own range-Doppler map over all 128 chirps and 16 receivers (moving-energy ratio MER and its
confident peaks; Station 1 sees the person twice, monostatic and bistatic about 100 bins farther, so up to two peaks
per frame are kept). The four detectors under test (IN1, CA-CM, OS-CM, Range-CA) see one chirp per frame. Thresholds
are split-conformal on null episodes of even bins; false alarms are measured on null episodes of odd bins.

Usage:
  python run_r17_jku.py --hash                  write PROTOCOL_R17.sha256 (protocol, this script, two helpers)
  python run_r17_jku.py --mechanics <dir>       mechanics check on meas_2_int_A.mat with a synthetic walker
                                                (monostatic and bistatic copies) -> r17/MECHANICS_R17.txt
  python run_r17_jku.py --data <dir>            protocol run on meas_3_int_A_pedestrian.mat -> study/results/r17/
"""
import sys, os, json, hashlib, argparse, time
HERE = os.path.dirname(os.path.abspath(__file__)); ROOT = os.path.dirname(HERE)
sys.path.insert(0, ROOT); sys.path.insert(0, os.path.join(ROOT, "r12"))
import numpy as np
from scipy.io import loadmat, whosmat
from methods import conformal_quantile, fit_ols
from run_r12_jku import hpdiff, zero_mask, range_profiles, BINS, NB

FILE, FILE_MD5 = "meas_3_int_A_pedestrian.mat", "52d257c47741b0f64433da2ddecad67d"
MECH_FILE = "meas_2_int_A.mat"
OUT = os.path.join(ROOT, "study", "results", "r17")
HASHED = ("r17/PROTOCOL_R17.md", "r17/run_r17_jku.py", "methods.py", "r12/run_r12_jku.py")   # relative to research/r7c
RX = (0, 5, 10, 15)
CHIRPS = (0, 32, 64, 96)
M, NF = 16, 100
ALPHAS = (1e-2, 1e-3)
DETS = ("IN1", "CA-CM", "OS-CM", "Range-CA")
TAGS = ("Z", "Z-sum16", "N", "N-sum16")             # mitigation x looks (per receiver | 16-channel sum)
MER_MOVE, MER_PEAK = 10.0, 13.0       # dB: moving cell; confident peak
PEAK_SEP, W_ATTR, G_NULL, W_NULL, PEAK_WIN = 20, 3, 6, 8, 2
MIN_PAIRS, MIN_PEAK_FRAMES = 8, 20
NI_MARGIN, INFORMATIVE = -0.05, 0.10
NBOOT, BLOCK, SEED, MIN_BLOCKS, MIN_EVENTS = 10000, 5, 17, 8, 20
T_REP, F_C, K_RAMP, FS, C0 = 34e-6, 76.5e9, 1e9 / 25.6e-6, 20e6, 3e8


# ---------------------------------------------------------------- freeze: LF-normalised SHA-256 of the four files
def sha_lf(path):
    return hashlib.sha256(open(path, "rb").read().replace(b"\r\n", b"\n")).hexdigest()


def write_hashes():
    lines = [f"{sha_lf(os.path.join(ROOT, p))}  {p}" for p in HASHED]
    open(os.path.join(HERE, "PROTOCOL_R17.sha256"), "w", newline="\n").write("\n".join(lines) + "\n")
    print("\n".join(lines))


def frozen():
    f = os.path.join(HERE, "PROTOCOL_R17.sha256")
    if not os.path.exists(f): return False, {}
    want = {}
    for line in open(f, encoding="utf8"):
        tok = line.split()
        if len(tok) == 2: want[tok[1].lstrip("*")] = tok[0]
    have = {p: sha_lf(os.path.join(ROOT, p)) for p in HASHED}
    return set(want) == set(HASHED) and all(want[p] == have[p] for p in HASHED), have


def md5(path):
    d = hashlib.md5()
    with open(path, "rb") as f:
        for blk in iter(lambda: f.read(1 << 24), b""): d.update(blk)
    return d.hexdigest()


def load_station(path, st):
    v = f"data_station_{st}"
    info = {n: s for n, s, t in whosmat(path)}
    assert info[v] == (512, 128, 16, 100), info[v]
    return np.asarray(loadmat(path, variable_names=[v])[v], dtype=np.float64)


# ---------------------------------------------------------------- per-frame processing (R11/R12 chain)
def frame_profiles(raw, mit):
    """raw: (512, n_chirp, n_rx) one frame. Returns range profiles (NB, n_chirp, n_rx), complex."""
    x = hpdiff(raw)
    if mit == "Z":
        x = np.where(zero_mask(x), 0.0, x)
    return range_profiles(x)


def reference_power(data):
    """Range-Doppler power summed over the 16 receivers per frame (mitigation Z): (NF, NB, 128), Doppler fftshifted."""
    win = np.hanning(128)[None, :, None]
    P = np.empty((NF, NB, 128))
    for t in range(NF):
        rd = np.fft.fftshift(np.fft.fft(frame_profiles(data[:, :, :, t], "Z") * win, axis=1), axes=1)
        P[t] = (np.abs(rd) ** 2).sum(2)
    return P


def ground_truth(P):
    """MER (NF, NB) in dB and up to two confident peaks per frame (NF, 2), -1 where none."""
    k = np.arange(128) - 64
    Q = P[:, :, np.abs(k) >= 2].max(2)
    mer = 10 * np.log10(Q / np.median(Q, axis=0, keepdims=True))
    peaks = np.full((NF, 2), -1)
    for t in range(NF):
        if mer[t].max() >= MER_PEAK:
            p1 = int(mer[t].argmax()); peaks[t, 0] = p1
            far = np.abs(np.arange(NB) - p1) > PEAK_SEP
            if far.any() and mer[t, far].max() >= MER_PEAK:
                peaks[t, 1] = int(np.nonzero(far)[0][mer[t, far].argmax()])
    return mer, peaks


def near_peak(peaks, frames, w):
    """(NB,) bool: some confident peak in the given frames lies within w bins."""
    out = np.zeros(NB, bool)
    b = np.arange(NB)
    for p in peaks[frames].ravel():
        if p >= 0: out |= np.abs(b - p) <= w
    return out


def clean_frames(mer, peaks):
    """clean[b, t]: single-frame null rule. No moving cell within +-G_NULL bins (inside bins 8-247) and no confident
    peak within +-W_NULL bins in frames t-2..t+2."""
    mov = mer >= MER_MOVE
    clean = np.ones((NB, NF), bool)
    for t in range(NF):
        m = mov[t]
        near = np.zeros(NB, bool)
        for d in range(-G_NULL, G_NULL + 1):
            lo, hi = max(0, -d), min(NB, NB - d)
            near[lo:hi] |= m[lo + d:hi + d]
        fr = np.arange(max(0, t - PEAK_WIN), min(NF, t + PEAK_WIN + 1))
        clean[:, t] = ~near & ~near_peak(peaks, fr, W_NULL)
    return clean


def events(mer, peaks):
    """(b, t0), t0 = M..NF-3: (a) MER >= 10 dB at t0; (b) MER < 10 dB in t0-16..t0-1. Primary also (c): a confident peak
    within +-3 bins in t0..t0+2. Secondary: (a) and (b), primary included."""
    prim, sec = [], []
    mov = mer >= MER_MOVE
    for t0 in range(M, NF - 2):
        att = near_peak(peaks, np.arange(t0, t0 + 3), W_ATTR)
        for b in np.nonzero(mov[t0] & ~mov[t0 - M:t0].any(0))[0]:
            sec.append((b, t0))
            if att[b]: prim.append((b, t0))
    return np.array(prim, int).reshape(-1, 2), np.array(sec, int).reshape(-1, 2)


# ---------------------------------------------------------------- detectors on frame slow time
def slow_time(data, mit):
    """One chirp per frame: per-receiver looks X[(rx, ch), b, t] and 16-channel-sum looks X[ch, b, t]."""
    Xr = np.empty((len(RX) * len(CHIRPS), NB, NF), complex)
    Xs = np.empty((len(CHIRPS), NB, NF), complex)
    for t in range(NF):
        rp = frame_profiles(data[:, :, :, t][:, list(CHIRPS), :], mit)      # (NB, 4 chirps, 16 rx)
        Xr[:, :, t] = rp[:, :, list(RX)].transpose(2, 1, 0).reshape(-1, NB)
        Xs[:, :, t] = rp.sum(2).T
    return Xr, Xs


def fit_r(X, clean):
    """AR(1) per (look, bin) on consecutive clean frame pairs (fit_ols, clamp 0.98); r = 0 with < MIN_PAIRS pairs."""
    r = np.zeros(X.shape[:2], complex)
    ok = clean[:, 1:] & clean[:, :-1]
    for b in range(X.shape[1]):
        idx = np.nonzero(ok[b])[0]
        if len(idx) < MIN_PAIRS: continue
        for l in range(X.shape[0]):
            r[l, b] = fit_ols(np.stack([X[l, b, idx], X[l, b, idx + 1]], 1))
    return r


def innov_scale(H, r):
    """methods.innovation_scale with one AR(1) coefficient per row: H (n, m), r (n,)."""
    e = (1 - np.abs(r) ** 2) * np.abs(H[:, 0]) ** 2 + np.sum(np.abs(H[:, 1:] - r[:, None] * H[:, :-1]) ** 2, 1)
    return np.sqrt(e / H.shape[1])


def scores(X, r):
    """Scores of every episode t = M..NF-1: det -> (looks, NB, NF-M)."""
    L_, B_, _ = X.shape
    S = {d: np.empty((L_, B_, NF - M)) for d in DETS}
    pw = np.abs(X) ** 2
    with np.errstate(divide="ignore", invalid="ignore"):
        for j, t in enumerate(range(M, NF)):
            H, Y, Hp = X[:, :, t - M:t], X[:, :, t], pw[:, :, t - M:t]
            for l in range(L_):
                S["IN1"][l, :, j] = np.abs(Y[l] - r[l] * H[l, :, -1]) / innov_scale(H[l], r[l])
            S["CA-CM"][:, :, j] = pw[:, :, t] / Hp.mean(2)
            S["OS-CM"][:, :, j] = pw[:, :, t] / np.partition(Hp, 7, axis=2)[:, :, 7]
            ref = np.zeros((L_, B_)); cnt = np.zeros(B_)
            for d in list(range(-10, -2)) + list(range(3, 11)):
                lo, hi = max(0, -d), min(B_, B_ - d)
                ref[:, lo:hi] += pw[:, lo + d:hi + d, t]; cnt[lo:hi] += 1
            S["Range-CA"][:, :, j] = pw[:, :, t] / (ref / cnt)
    return S


def static_snr(X, clean):
    """Per (look, bin), dB: median |x|^2 over clean frames / (0.5 median |x_t - x_t-1|^2 over clean pairs).
    NaN with fewer than MIN_PAIRS clean frames or pairs."""
    out = np.full(X.shape[:2], np.nan)
    ok = clean[:, 1:] & clean[:, :-1]
    for b in range(X.shape[1]):
        f, p = np.nonzero(clean[b])[0], np.nonzero(ok[b])[0]
        if len(f) < MIN_PAIRS or len(p) < MIN_PAIRS: continue
        num = np.median(np.abs(X[:, b, f]) ** 2, axis=1)
        den = 0.5 * np.median(np.abs(X[:, b, p + 1] - X[:, b, p]) ** 2, axis=1)
        out[:, b] = 10 * np.log10(num / den)
    return out


def evaluate(X, mer, peaks, ev_p, ev_s, tag):
    clean = clean_frames(mer, peaks)
    r = fit_r(X, clean)
    S = scores(X, r)
    nullep = np.stack([clean[:, t - M:t + 1].all(1) for t in range(M, NF)], 1)        # (NB, NF-M)
    even = (BINS % 2 == 0)[:, None] & nullep
    odd = (BINS % 2 == 1)[:, None] & nullep
    odd3 = odd[:, :-2] & odd[:, 1:-1] & odd[:, 2:]                                     # three consecutive null episodes
    res = {f"{tag}|n_null_cal": int(even.sum()) * X.shape[0], f"{tag}|n_null_test": int(odd.sum()) * X.shape[0]}
    for d in DETS:
        res[f"{tag}|nonfinite|{d}"] = int((~np.isfinite(S[d])).sum())
        cal = S[d][:, even]; cal = cal[np.isfinite(cal)]          # non-finite: dropped from calibration
        for a in ALPHAS:
            q = conformal_quantile(cal, a)
            E = S[d] > q                                          # NaN -> no alarm, +inf -> alarm
            res[f"{tag}|pfa|{d}|{a:g}"] = float(E[:, odd].mean())
            E3 = E[:, :, :-2] | E[:, :, 1:-1] | E[:, :, 2:]
            res[f"{tag}|floor3|{d}|{a:g}"] = float(E3[:, odd3].mean())
            for name, ev in (("prim", ev_p), ("sec", ev_s)):
                if len(ev) == 0:
                    res[f"{tag}|pd0|{name}|{d}|{a:g}"] = []; res[f"{tag}|pd3|{name}|{d}|{a:g}"] = []; continue
                j0 = ev[:, 1] - M
                res[f"{tag}|pd0|{name}|{d}|{a:g}"] = E[:, ev[:, 0], j0].mean(0).tolist()
                res[f"{tag}|pd3|{name}|{d}|{a:g}"] = (E[:, ev[:, 0], j0] | E[:, ev[:, 0], j0 + 1]
                                                      | E[:, ev[:, 0], j0 + 2]).mean(0).tolist()
    snr = static_snr(X, clean)
    res[f"{tag}|snr_prim"] = [float(np.nanmean(snr[:, b])) if np.isfinite(snr[:, b]).any() else None for b in ev_p[:, 0]]
    nz = np.abs(r[r != 0])
    res[f"{tag}|r_abs_median"] = float(np.median(nz)) if len(nz) else 0.0
    sb = np.nanmean(snr, 0) if np.isfinite(snr).any() else np.full(NB, np.nan)
    top = np.isfinite(sb) & (sb >= np.nanpercentile(sb, 90)) if np.isfinite(sb).any() else np.zeros(NB, bool)
    res[f"{tag}|r_abs_median_top10_static"] = float(np.median(np.abs(r[:, top]))) if top.any() else None
    return res


def bootstrap(x, t0, seed=SEED):
    """Block bootstrap of mean(x) over onset frames (non-overlapping blocks of BLOCK frames): mean, 2.5th, 97.5th pct."""
    x = np.asarray(x, float)
    blk = (np.asarray(t0) - M) // BLOCK
    groups = [np.nonzero(blk == u)[0] for u in np.unique(blk)]
    rng = np.random.default_rng(seed)
    bs = np.empty(NBOOT)
    for i in range(NBOOT):
        idx = np.concatenate([groups[p] for p in rng.integers(0, len(groups), len(groups))])
        bs[i] = x[idx].mean()
    return float(x.mean()), float(np.percentile(bs, 2.5)), float(np.percentile(bs, 97.5))


# ---------------------------------------------------------------- one file
def run_file(path, inject=None):
    v1 = load_station(path, 1)
    if inject is not None: v1 = inject(v1)
    mer, peaks = ground_truth(reference_power(v1))
    ev_p, ev_s = events(mer, peaks)
    out = dict(peaks=peaks.tolist(), n_peak_frames=int((peaks[:, 0] >= 0).sum()),
               events_prim=ev_p.tolist(), events_sec=ev_s.tolist())
    for mit in ("Z", "N"):
        Xr, Xs = slow_time(v1, mit)
        out.update(evaluate(Xr, mer, peaks, ev_p, ev_s, mit))
        out.update(evaluate(Xs, mer, peaks, ev_p, ev_s, mit + "-sum16"))
        del Xr, Xs
    return out


def summary(out, lines):
    ev = np.array(out["events_prim"]).reshape(-1, 2)
    nblk = len(np.unique((ev[:, 1] - M) // BLOCK)) if len(ev) else 0
    lines.append(f"frames with a confident peak {out['n_peak_frames']} of {NF}; primary events {len(ev)} in {nblk} "
                 f"blocks; secondary events {len(out['events_sec'])} (primary included)")
    if len(ev):
        b = ev[:, 0] + BINS[0]
        lines.append(f"  primary events: bins {b.min()}-{b.max()} ({b.min() * 0.15:.1f}-{b.max() * 0.15:.1f} m), onset "
                     f"frames {ev[:, 1].min()}-{ev[:, 1].max()}")
    for tag in TAGS:
        top = out[f"{tag}|r_abs_median_top10_static"]
        lines.append(f"{tag}: median |r| {out[f'{tag}|r_abs_median']:.3f} (top-10% static bins "
                     f"{'-' if top is None else f'{top:.3f}'}); null episodes cal {out[f'{tag}|n_null_cal']}, test "
                     f"{out[f'{tag}|n_null_test']}; non-finite scores " + ", ".join(
                         f"{d} {out[f'{tag}|nonfinite|{d}']}" for d in DETS))
        for a in ALPHAS:
            lines.append(f"  alpha {a:g}: Pfa/alpha " + ", ".join(f"{d} {out[f'{tag}|pfa|{d}|{a:g}'] / a:.2f}" for d in DETS)
                         + "; 3-frame null floor " + ", ".join(f"{d} {out[f'{tag}|floor3|{d}|{a:g}']:.4f}" for d in DETS))
            for name in ("prim", "sec"):
                for k, lab in (("pd3", "Pd within 3 frames"), ("pd0", "Pd at onset frame")):
                    v = [out[f"{tag}|{k}|{name}|{d}|{a:g}"] for d in DETS]
                    if len(v[0]):
                        lines.append(f"    {name} {lab}: " + ", ".join(f"{d} {np.mean(x):.3f}" for d, x in zip(DETS, v)))
    return lines


def verdicts(out, lines):
    ev = np.array(out["events_prim"]).reshape(-1, 2)
    nblk = len(np.unique((ev[:, 1] - M) // BLOCK)) if len(ev) else 0
    feas = out["n_peak_frames"] >= MIN_PEAK_FRAMES
    lines.append(f"Feasibility (>= {MIN_PEAK_FRAMES} frames with a confident peak): {out['n_peak_frames']} -> "
                 f"{'feasible' if feas else 'NOT FEASIBLE'}")
    E1 = feas and len(ev) >= MIN_EVENTS and nblk >= MIN_BLOCKS
    lines.append(f"E1 (>= {MIN_EVENTS} primary events in >= {MIN_BLOCKS} blocks): {len(ev)} events, {nblk} blocks -> "
                 f"{'MET' if E1 else 'NOT MET (all below descriptive only)'}")
    tag = lambda ok: ("MET" if ok else "NOT MET") if E1 else "descriptive only (E1 not met)"
    pf = {d: out[f"Z|pfa|{d}|0.01"] / 0.01 for d in DETS}
    E2 = {d: 0.5 <= v <= 2 for d, v in pf.items()}
    lines.append("E2 (Z, per receiver, alpha 1e-2: Pfa/alpha in [0.5, 2]): " + ", ".join(
        f"{d} {v:.2f}{'' if E2[d] else ' (false-alarm rate not controlled)'}" for d, v in pf.items())
        + f" -> {tag(all(E2.values()))}")
    if not len(ev): return lines
    pd = {d: np.array(out[f"Z|pd3|prim|{d}|0.01"]) for d in DETS}
    t0 = ev[:, 1]
    for d in DETS:
        m, lo, hi = bootstrap(pd[d], t0)
        lines.append(f"  event-mean Pd within 3 frames, {d}: {m:.3f} [{lo:.3f}, {hi:.3f}]")
    inf = pd["CA-CM"].mean() >= INFORMATIVE
    m3, lo3, hi3 = bootstrap(pd["IN1"] - pd["CA-CM"], t0)
    if inf:
        lines.append(f"E3 (IN1 - CA-CM, 2.5th pct > {NI_MARGIN}): {m3:.3f} [{lo3:.3f}, {hi3:.3f}] -> {tag(lo3 > NI_MARGIN)}; "
                     f"superiority (not expected): {'yes' if lo3 > 0 else 'no'}")
    else:
        lines.append(f"E3: not informative (CA-CM event-mean Pd {pd['CA-CM'].mean():.3f} < {INFORMATIVE}); "
                     f"IN1 - CA-CM {m3:.3f} [{lo3:.3f}, {hi3:.3f}]")
    e4 = []
    for d in ("OS-CM", "Range-CA"):
        m4, lo4, hi4 = bootstrap(pd["IN1"] - pd[d], t0)
        e4.append(lo4 > 0)
        lines.append(f"E4 (IN1 - {d}, 2.5th pct > 0): {m4:.3f} [{lo4:.3f}, {hi4:.3f}]")
    lines.append(f"E4 -> {tag(all(e4))}")
    snr = np.array([np.nan if s is None else s for s in out["Z|snr_prim"]], float)
    ok = np.isfinite(snr)
    dif = pd["IN1"] - pd["CA-CM"]
    if ok.sum() >= 2:
        med = np.median(snr[ok]); hi = ok & (snr > med); lo = ok & (snr <= med)
        if hi.any() and lo.any():
            dd = np.where(hi, dif, 0.0) / hi.mean() - np.where(lo, dif, 0.0) / lo.mean()
            mh, lh, uh = bootstrap(dd, t0)
            lines.append(f"E5 (IN1 - CA-CM larger in the high static-to-noise half; split at {med:.1f} dB, "
                         f"{(~ok).sum()} events without a ratio left out): high {dif[hi].mean():.3f} (n={hi.sum()}), "
                         f"low {dif[lo].mean():.3f} (n={lo.sum()}); high - low {dif[hi].mean() - dif[lo].mean():.3f} "
                         f"[descriptive {lh:.3f}, {uh:.3f}] -> {tag(dif[hi].mean() > dif[lo].mean())}")
        else:
            lines.append("E5: not evaluable (a half is empty)")
    else:
        lines.append("E5: not evaluable (fewer than 2 events with a ratio)")
    return lines


# ---------------------------------------------------------------- mechanics: synthetic walker in meas_2_int_A
def walker(v1, scale=0.05):
    """Walker 3 -> 18 m over frames 10..90 in every Station 1 receiver (raw ADC beat tones with Doppler), with a
    bistatic copy 15 m farther (the Station 2 offset of about 100 bins)."""
    rng = np.random.default_rng(1)
    n = np.arange(512)[:, None]; ch = np.arange(128)[None, :]
    amp = scale * np.median(np.std(v1[:, :, 0, :], axis=0))
    out = v1.copy()
    v = 15 / 80 / 0.2
    for t in range(10, 91):
        R = 3 + 15 * (t - 10) / 80
        for Rc in (R, R + 15.0):
            ph = 2 * np.pi * (2 * K_RAMP * Rc / C0 * n / FS + 2 * v * F_C / C0 * ch * T_REP) + rng.uniform(0, 2 * np.pi)
            out[:, :, :, t] += (amp * np.cos(ph))[:, :, None]
    return out


if __name__ == "__main__":
    ap = argparse.ArgumentParser()
    g = ap.add_mutually_exclusive_group(required=True)
    g.add_argument("--data"); g.add_argument("--mechanics"); g.add_argument("--hash", action="store_true")
    a = ap.parse_args()
    if a.hash:
        write_hashes(); sys.exit(0)
    if a.mechanics:
        ok, _ = frozen()
        out = run_file(os.path.join(a.mechanics, MECH_FILE), inject=walker)
        pk = np.array(out["peaks"])
        truth = (3 + 15 * (np.arange(NF) - 10) / 80) / 0.15 - BINS[0]
        fr = np.arange(12, 89)
        err = np.array([np.min(np.abs(pk[t][pk[t] >= 0] - truth[t])) if (pk[t] >= 0).any() else np.nan for t in fr])
        err2 = np.array([np.min(np.abs(pk[t][pk[t] >= 0] - truth[t] - 100)) if (pk[t] >= 0).any() else np.nan for t in fr])
        lines = [f"R17 MECHANICS on {MECH_FILE} with a synthetic walker (monostatic and bistatic copies); protocol frozen: {ok}",
                 "Used for the design (peaks, event count, |r|); the detector numbers below were also seen before the "
                 "expectations were written.",
                 f"peaks: monostatic copy found on {np.isfinite(err).sum()} of {len(fr)} frames 12-88, |peak - truth| "
                 f"median {np.nanmedian(err):.2f} bins; nearest peak to the bistatic copy median |diff| {np.nanmedian(err2):.2f} bins"]
        lines = summary(out, lines)
        txt = "\n".join(lines)
        open(os.path.join(HERE, "MECHANICS_R17.txt"), "w", encoding="utf8", newline="\n").write(txt + "\n")
        print(txt)
        sys.exit(0)
    ok, have = frozen()
    if not ok: sys.exit("PROTOCOL_R17.sha256 does not match the protocol, this script and its helpers.")
    path = os.path.join(a.data, FILE)
    h = md5(path)
    if h != FILE_MD5: sys.exit(f"MD5 mismatch: {h}")
    os.makedirs(OUT, exist_ok=True)
    started = time.strftime("%Y-%m-%d %H:%M:%S"); t_start = time.time()
    out = run_file(path)
    out["meta"] = dict(started=started, runtime_s=time.time() - t_start, md5=h, hashes=have)
    jpath = os.path.join(OUT, "r17_outcomes.json")
    json.dump(out, open(jpath, "w"))
    open(jpath + ".sha256", "w").write(f"{sha_lf(jpath)}  r17_outcomes.json\n")
    lines = summary(out, ["R17 outcomes (Station 1, meas_3_int_A_pedestrian)"])
    lines = verdicts(out, lines + ["", "Pre-stated expectations (PROTOCOL_R17.md, section 4)"])
    txt = "\n".join(lines)
    open(os.path.join(OUT, "r17_summary.txt"), "w", encoding="utf8", newline="\n").write(txt + "\n")
    print(txt)
