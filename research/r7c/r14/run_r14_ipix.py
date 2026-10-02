"""R14 IPIX parts G (guarded scale), K (clip level), T (certified trimmed sum), X (blanking with mask-matched
calibration) and B (bursty interference) on the 56 evaluation units (PROTOCOL_R14.md, frozen before outcomes).
Usage: python run_r14_ipix.py [--workers 26] [--synthetic]   ->  study/results/r14/u_<file>_<pol>_rot<k>.npz
--synthetic runs the mechanics on AR(1)+texture+noise data (not IPIX)."""
import sys, os, math, json, hashlib, argparse, time
HERE = os.path.dirname(os.path.abspath(__file__)); ROOT = os.path.dirname(HERE)
for p in (ROOT, os.path.join(ROOT, "study"), os.path.join(ROOT, "r12"), HERE):
    sys.path.insert(0, p)
import numpy as np
from ipix import FILES, load, episodes
from methods import conformal_quantile, fit_ols, innovation_scale
from run_study import texture_proxy, BLOCKS, ROT, STRIDE
import run_study
import laws as L

M, K, KH = 16, 8, 8
SCR_DB = np.arange(-5, 25.01, 2.5)
I10 = int(np.argmin(abs(SCR_DB - 10)))
ALPHAS = (1e-2, 1e-3)
GUARDS, GMAX, LOOKS = (0, 8, 16), 16, 9
RAMPS = (8, 16)
KAPPAS = (4.0, 6.0, 9.0, 12.0, 18.0)
PS, JNRS = (0.02, 0.05), (10.0, 30.0)
LAM_ABS, LAM_REL, BURST = 10.0, 4.0, 8
OUT = os.path.join(ROOT, "study", "results", "r14")


def frozen():
    h = open(os.path.join(HERE, "PROTOCOL_R14.sha256")).read().split()[0]
    return hashlib.sha256(open(os.path.join(HERE, "PROTOCOL_R14.md"), "rb").read()).hexdigest() == h


def cn(rng, *shape):
    return np.sqrt(.5) * (rng.standard_normal(shape) + 1j * rng.standard_normal(shape))


def segs(z, blk, Lseg, stride=STRIDE):
    T, B = z.shape
    starts = np.arange(blk[0], blk[1] - Lseg, stride)
    idx = starts[:, None] + np.arange(Lseg)[None, :]
    seg = np.transpose(z[idx], (0, 2, 1)).reshape(-1, Lseg)
    P = texture_proxy(z, np.repeat(starts, B), np.tile(np.arange(B), len(starts)), Lseg - 1, 1024)
    return seg, P


def q_rank(v, a):
    return conformal_quantile(np.asarray(v), a)


def quint(P):
    return np.digitize(P, np.quantile(P, [.2, .4, .6, .8]))


# ================================================================ Part G: guarded scale
T_ON = GMAX + M


def g_scores(S, r):
    out = {}
    for g in GUARDS:
        sc = np.empty((len(S), LOOKS))
        for l in range(LOOKS):
            t = T_ON + l
            sc[:, l] = abs(S[:, t] - r * S[:, t - 1]) ** 2 / innovation_scale(S[:, t - g - M:t - g], r) ** 2
        out[g] = sc
    return out


def guarded_law(S_lin, l, d2, g, absr, beta):
    """Prop. 4 with the guard: the scale contains the target from look g+1 on (exploratory, AR(1), no noise)."""
    Sw = S_lin / (1 - absr ** 2)
    if l == 0:
        E0, EH = Sw, 0.0
    else:
        E0 = Sw * d2
        n_in = l - g                                   # target innovations inside the scale window
        EH = 0.0 if n_in <= 0 else Sw * (1 + (n_in - 1) * d2)
    B_ = 1 + E0 - beta - beta * EH; C = beta * (1 + E0 + EH)
    lp = (B_ + np.sqrt(B_ * B_ + 4 * C)) / 2; lm = (B_ - np.sqrt(B_ * B_ + 4 * C)) / 2
    return lp / (lp - lm) * (1 + beta / lp) ** (-(M - 1))


def part_g(z, zt, ca, te, r, seed):
    res = {}
    Lseg = GMAX + M + LOOKS
    Sc, Pc = segs(z, ca, Lseg, stride=Lseg); St, Pt = segs(z, te, Lseg, stride=Lseg)
    Gc, Gt = g_scores(Sc, r), g_scores(St, r)
    q = {(g, a): q_rank(Gc[g][:, 0], a) for g in GUARDS for a in ALPHAS}
    qb = quint(Pt)
    for g in GUARDS:
        for a in ALPHAS:
            e = Gt[g][:, 0] > q[(g, a)]
            res[f"G|clean|{g}|{a}"] = np.array([e.sum(), len(e)] + [e[qb == k].sum() for k in range(5)] + [(qb == k).sum() for k in range(5)])
            res[f"G|clean_cum8|{g}|{a}"] = np.array([(Gt[g][:, :8] > q[(g, a)]).any(1).sum(), len(e)])
    rng = np.random.default_rng(seed)
    n = len(St); amp = cn(rng, n)
    om = {"random": rng.uniform(-np.pi, np.pi, n), "matched": np.full(n, np.angle(r)), "opposite": np.full(n, np.angle(r) + np.pi)}
    tpos = np.arange(Lseg)
    a = 0.01

    def run(prof, dop, tag):
        look = {g: np.zeros((len(SCR_DB), LOOKS)) for g in GUARDS}; cum = {g: np.zeros(len(SCR_DB)) for g in GUARDS}
        for i, sdb in enumerate(SCR_DB):
            tv = prof[None, :] * np.exp(1j * om[dop][:, None] * (tpos[None, :] - T_ON))
            Si = St + (np.sqrt(10 ** (sdb / 10) * Pt) * amp)[:, None] * tv
            Gi = g_scores(Si, r)
            for g in GUARDS:
                dec = Gi[g] > q[(g, a)]
                look[g][i] = dec.mean(0); cum[g][i] = dec[:, :8].any(1).mean()
        for g in GUARDS:
            res[f"G|{tag}|{dop}|{g}|look"] = look[g]; res[f"G|{tag}|{dop}|{g}|cum8"] = cum[g]

    abrupt = (tpos >= T_ON).astype(float)
    for dop in om:
        run(abrupt, dop, "abrupt")
    for Lr in RAMPS:
        t0 = T_ON - Lr + 1
        run(np.where(tpos >= t0, np.minimum(1.0, (tpos - t0 + 1) / Lr), 0.0), "random", f"ramp{Lr}")
    # exploratory law at the fitted |r| (AR(1), no noise), random Doppler averaged over the test draws
    beta = L.q2_in(a, M) / M
    w = om["random"][:2000]
    d2 = abs(1 - r * np.exp(-1j * w)) ** 2
    for g in GUARDS:
        res[f"G|law|random|{g}"] = np.array([[np.mean(guarded_law(10 ** (s / 10), l, d2, g, abs(r), beta)) for l in range(LOOKS)] for s in SCR_DB])
    # real target cell: look-0 exceedance (dense windows over the test third)
    if zt is not None:
        Sg, _ = segs(zt, te, Lseg, stride=32)
        Gg = g_scores(Sg, r)
        for g in GUARDS:
            for a_ in ALPHAS:
                res[f"G|target|{g}|{a_}"] = np.array([(Gg[g][:, 0] > q[(g, a_)]).sum(), len(Sg)])
    return res


# ================================================================ Parts K, T, X, B: dwell integration
def inn_pow(S, r):
    return np.concatenate([(1 - abs(r) ** 2) * abs(S[:, :1]) ** 2, abs(S[:, 1:] - r * S[:, :-1]) ** 2], 1)


def hits_bern(rng, n, p):
    return rng.random((n, M + K)) < p


def hits_burst(rng, n, p):
    starts = rng.random((n, M + K + BURST)) < p / BURST
    out = np.zeros((n, M + K + BURST), bool)
    for j in range(BURST):
        out[:, j:] |= starts[:, :M + K + BURST - j]
    return out[:, BURST:]                         # bursts may start before the segment


def trim_rule(rng, p, a, model):
    hits = (hits_bern if model == "bern" else hits_burst)(rng, 400_000, p)
    cnt = L.corrupted_innovations(hits)[:, M:].sum(1)
    for t in range(K):
        if np.mean(cnt > t) <= a / 5:
            return t
    return None


def blank_stat(e, extra=None):
    """Pulse blanking of isolated spikes: a normalized power is blanked when it exceeds LAM_ABS and LAM_REL times
    a robust level of its own block (history: median; dwell: third-smallest, robust to five corrupted terms), so a persistent target, which raises the whole dwell, is kept;
    the innovation after each blanked one is blanked too (a hit pulse corrupts two AR(1) innovations); extra masks
    are added in calibration. Scale: median of the kept history; statistic: K x mean of the kept dwell."""
    s0 = np.partition(e[:, :M], KH - 1, 1)[:, KH - 1]
    z0 = e / s0[:, None]
    medd = np.partition(z0[:, M:], 2, 1)[:, 2:3]; medh = np.median(z0[:, :M], 1, keepdims=True)   # 3rd-smallest dwell: robust to 5 corrupted
    rel = np.concatenate([np.repeat(medh, M, 1), np.repeat(medd, K, 1)], 1)
    fl = (z0 > LAM_ABS) & (z0 > LAM_REL * rel)
    if extra is not None:                      # calibration masks go through the same rule as detected spikes
        fl |= extra
    fl[:, 1:] |= fl[:, :-1]
    h = np.where(fl[:, :M], np.inf, e[:, :M])
    nk = (~fl[:, :M]).sum(1)
    hs = np.sort(h, 1)
    kidx = np.clip((nk - 1) // 2, 0, M - 1)
    s = hs[np.arange(len(e)), kidx]
    s = np.where(np.isfinite(s) & (s > 0), s, np.nan)
    zd = e[:, M:] / s[:, None]
    keep = ~fl[:, M:]
    kd = keep.sum(1)
    v = K * np.where(keep, zd, 0).sum(1) / np.maximum(kd, 1)
    return np.nan_to_num(np.where(kd > 0, v, 0.0), nan=0.0)


def dwell_stats(e, tr):
    h, d = e[:, :M], e[:, M:]
    out = {f"clip{k:g}": L.robust_stat(h, d, KH, "clip", c=k) for k in KAPPAS}
    for key, t in tr.items():
        if t is not None:
            out[f"trim|{key}"] = L.robust_stat(h, d, KH, "trim", t=t)
    out["blank"] = blank_stat(e)
    return out


def part_ktxb(z, ca, te, r, seed):
    res = {}
    rng = np.random.default_rng(seed)
    Sc, Pc = segs(z, ca, M + K, stride=M + K); St, Pt = segs(z, te, M + K, stride=M + K)
    ec, et = inn_pow(Sc, r), inn_pow(St, r)
    n, nc = len(St), len(Sc)
    # trim levels per (p, alpha, model), from the hit model only
    tr = {f"{p}|{a}|{mdl}": trim_rule(np.random.default_rng(int(1e6 * p) + int(1e4 * a) + (mdl == "burst")), p, a, mdl)
          for p in PS for a in ALPHAS for mdl in ("bern", "burst")}
    res["trim_levels"] = np.array([[float(k.split("|")[0]), float(k.split("|")[1]), float(k.split("|")[2] == "burst"), -1 if t is None else t] for k, t in tr.items()])
    Dc = dwell_stats(ec, tr)
    # clean thresholds (no hit model) and kappa rule
    q = {}
    for nm, v in Dc.items():
        for a in ALPHAS:
            q[("clean", nm, a)] = q_rank(v, a)
    for a in ALPHAS:
        rule = [k for k in KAPPAS if np.mean(Dc[f"clip{k:g}"] >= K * k - 1e-9) <= a / 10]
        res[f"K|rule|{a}"] = rule[0] if rule else -1.0
    # certified thresholds: worst case over amplitudes with hits from the model
    hc = {}
    for p in PS:
        for mdl, fn in (("bern", hits_bern), ("burst", hits_burst)):
            cor = L.corrupted_innovations(fn(rng, nc, p)); hc[(p, mdl)] = cor
            for k in KAPPAS:
                wc = L.worst_case(ec[:, :M], ec[:, M:], cor[:, :M], cor[:, M:], KH, "clip", c=k)
                for a in ALPHAS:
                    q[(f"cert-{mdl}", f"clip{k:g}", p, a)] = q_rank(wc, a)
            for a in ALPHAS:
                t = tr[f"{p}|{a}|{mdl}"]
                if t is not None:
                    wc = L.worst_case(ec[:, :M], ec[:, M:], cor[:, :M], cor[:, M:], KH, "trim", t=t)
                    q[(f"cert-{mdl}", f"trim|{p}|{a}|{mdl}", p, a)] = q_rank(wc, a)
                bm = blank_stat(ec, extra=cor)
                q[(f"mask-{mdl}", "blank", p, a)] = q_rank(bm, a)
    # targets: persistent, random Doppler, from the first dwell pulse
    amp = cn(rng, n); om = rng.uniform(-np.pi, np.pi, n); tpos = np.arange(M + K)
    base = (np.sqrt(Pt) * amp)[:, None] * np.where(tpos >= M, np.exp(1j * om[:, None] * (tpos[None, :] - M)), 0)

    def evaluate(Sx_fn, rules, tag):
        """Pfa (index 0) and Pd over SCR (1..) for each (rule, stat, p, a) threshold key."""
        out = {key: np.zeros(1 + len(SCR_DB)) for key in rules}
        for j in range(1 + len(SCR_DB)):
            Sx = Sx_fn(None if j == 0 else SCR_DB[j - 1])
            D = dwell_stats(inn_pow(Sx, r), tr)
            for key in rules:
                stat = key[1]
                if stat in D:
                    out[key][j] = np.mean(D[stat] > q[key])
        for key, v in out.items():
            res[f"{tag}|{'|'.join(map(str, key))}"] = v

    # clean test
    clean_keys = [k for k in q if k[0] == "clean"]
    evaluate(lambda s: St if s is None else St + np.sqrt(10 ** (s / 10)) * base, clean_keys, "clean")
    # interference: Bernoulli at 10 and 30 dB; bursts at 30 dB
    for p in PS:
        conds = [("bern", j) for j in JNRS] + [("burst", 30.0)]
        for mdl, jnr in conds:
            hit = (hits_bern if mdl == "bern" else hits_burst)(rng, n, p)
            ia = np.where(hit, np.sqrt(10 ** (jnr / 10) * Pt)[:, None] * cn(rng, n, M + K), 0)
            keys = [k for k in q if k[0] != "clean" and k[2] == p]
            keys += [("clean", f"clip{k:g}", a) for k in (6.0,) for a in ALPHAS]          # clean-threshold clipping
            evaluate(lambda s, ia=ia: St + ia if s is None else St + ia + np.sqrt(10 ** (s / 10)) * base, keys, f"I|{mdl}|{p}|{int(jnr)}")
    res["n_dwell"] = np.array([nc, n])
    return res


# ================================================================ unit
def run_unit(num, pol, rot, synthetic_data=None):
    tr_, ca, te = tuple(BLOCKS[b] for b in ROT[rot])
    if synthetic_data is None:
        d = load(num); z = d["z"][pol]; zt = load(num, keep="target")["z"][pol]
    else:
        z, zt = synthetic_data
    Xtr, _, _ = episodes(z, *tr_, M, STRIDE)
    r = fit_ols(Xtr)
    sd = lambda part: int(hashlib.sha256(f"R14|{part}|{num}|{pol}|{rot}".encode()).hexdigest()[:8], 16)
    res = dict(r=np.array([r.real, r.imag]))
    t0 = time.time(); res.update(part_g(z, zt, ca, te, r, sd("G"))); res["sec_G"] = time.time() - t0
    t0 = time.time(); res.update(part_ktxb(z, ca, te, r, sd("KTXB"))); res["sec_KTXB"] = time.time() - t0
    return res


def unit(args):
    num, pol, rot = args
    path = os.path.join(OUT, f"u_{num}_{pol}_rot{rot}.npz")
    if os.path.exists(path):
        return path
    t0 = time.time(); res = run_unit(num, pol, rot)
    tmp = path + ".tmp.npz"
    np.savez_compressed(tmp, **res, scr_db=SCR_DB, day=FILES[num][1], seconds=time.time() - t0)
    os.replace(tmp, path)
    return path


def synthetic():
    rng = np.random.default_rng(0); T, B = 131072, 9; rho = 0.93 * np.exp(-0.2j)
    run_study.T = T
    e = cn(rng, T, B + 1); x = np.zeros((T, B + 1), complex)
    for t in range(1, T):
        x[t] = rho * x[t - 1] + np.sqrt(1 - abs(rho) ** 2) * e[t]
    tex = np.exp(rng.normal(0, 1, (T // 2048 + 1, B + 1))).repeat(2048, 0)[:T]
    zz = np.sqrt(10 * tex) * x + cn(rng, T, B + 1)
    t0 = time.time(); res = run_unit(0, "like0", 2, (zz[:, :B], zz[:, B:]))
    print(f"synthetic unit {time.time() - t0:.0f} s (G {res['sec_G']:.0f}, KTXB {res['sec_KTXB']:.0f})")
    for g in GUARDS:
        c = res[f"G|clean|{g}|0.01"]
        print(f"G g={g:2d}: clean Pfa/a {c[0] / c[1] / 0.01:.2f}; abrupt random look Pd@10dB "
              + " ".join(f"{v:.2f}" for v in res[f"G|abrupt|random|{g}|look"][I10])
              + f"; law " + " ".join(f"{v:.2f}" for v in res[f"G|law|random|{g}"][I10])
              + f"; ramp16 cum8@10 {res[f'G|ramp16|random|{g}|cum8'][I10]:.2f}; target exc 1e-3 {res[f'G|target|{g}|0.001'][0] / res[f'G|target|{g}|0.001'][1]:.4f}")
    print("trim levels (p, a, burst, t):", res["trim_levels"].tolist())
    print("kappa rule:", {a: res[f"K|rule|{a}"] for a in ALPHAS})
    for k in res:
        if k.startswith("I|") and ("clip6|" in k or "trim" in k or "blank" in k) and k.endswith("0.01"):
            v = res[k]; print(f"{k:<46s} Pfa/a {v[0] / 0.01:5.2f}  Pd@0dB {v[1 + 2]:.2f}  Pd@10dB {v[1 + I10]:.2f}")


if __name__ == "__main__":
    ap = argparse.ArgumentParser(); ap.add_argument("--workers", type=int, default=26); ap.add_argument("--synthetic", action="store_true")
    a = ap.parse_args()
    if a.synthetic:
        synthetic(); sys.exit()
    if not frozen():
        sys.exit("PROTOCOL_R14.md does not match its hash.")
    os.makedirs(OUT, exist_ok=True)
    json.dump(dict(started=time.strftime("%Y-%m-%d %H:%M:%S"), protocol_sha=open(os.path.join(HERE, "PROTOCOL_R14.sha256")).read().split()[0],
                   script_sha=hashlib.sha256(open(__file__, "rb").read()).hexdigest(),
                   laws_sha=hashlib.sha256(open(os.path.join(ROOT, "r12", "laws.py"), "rb").read()).hexdigest()),
              open(os.path.join(OUT, f"manifest_{int(time.time())}.json"), "w"), indent=1)
    jobs = [(num, pol, rot) for num in FILES for pol in ("like0", "like1") for rot in (2, 3)]
    from concurrent.futures import ProcessPoolExecutor
    with ProcessPoolExecutor(a.workers) as ex:
        for pth in ex.map(unit, jobs):
            print("saved", os.path.basename(pth), flush=True)
