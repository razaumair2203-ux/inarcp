"""R15: the frozen R12 parts L/A/I and R14 parts G/K/T/X/B, plus Part W (real interference), on NetRAD node-3 sea clutter
(PROTOCOL_R15.md, frozen before outcomes). 28 units = 14 recordings x rotations 2, 3.
Usage: INARCP_GPU=1 python run_r15_netrad.py [--workers 12] [--synthetic]  ->  study/results/r15/n_<tag>_rot<k>.npz
--synthetic runs the mechanics on AR(1)+texture+noise data with injected whole-pulse hits (not NetRAD)."""
import sys, os, json, hashlib, argparse, time
HERE = os.path.dirname(os.path.abspath(__file__)); ROOT = os.path.dirname(HERE)
for p in (ROOT, os.path.join(ROOT, "study"), os.path.join(ROOT, "r10"), os.path.join(ROOT, "r12"), os.path.join(ROOT, "r14"), HERE):
    sys.path.insert(0, p)
import numpy as np
from ipix import episodes
from methods import fit_ols, fit_mixture_arp, NoiseAwareGeneral
from run_study import fit_arp, GAP, STRIDE
import run_study
import run_r12_ipix as R12
import run_r14_ipix as R14
import laws as L
from netrad import FILES, load

M, K, KH = 16, 8, 8
SCR_DB = R14.SCR_DB
ALPHAS = (1e-2, 1e-3)
KAPPAS_W = (6.0, 9.0)
W_MIN_RATE = 0.005
OUT = os.path.join(ROOT, "study", "results", "r15")
ROT = {2: ("B", "C", "A"), 3: ("C", "A", "B")}


def frozen():
    h = open(os.path.join(HERE, "PROTOCOL_R15.sha256")).read().split()[0]
    return hashlib.sha256(open(os.path.join(HERE, "PROTOCOL_R15.md"), "rb").read()).hexdigest() == h


def blocks(T):
    B1, B2 = T // 3, 2 * T // 3
    return {"A": (0, B1 - GAP), "B": (B1, B2 - GAP), "C": (B2, T)}


def secondary_near(z, st, bi, bins, off, N, hit_fn=None):
    """R12 secondary(), restricted to cells two to four cells away (PROTOCOL_R15 Section 1): 20-30 vectors, as on IPIX."""
    T, B = z.shape; ob = np.array(bins); out = []
    for b in range(B):
        rows = np.where(bi == b)[0]
        if len(rows) == 0:
            continue
        d = abs(ob - ob[b]); refs = np.where((d > 1) & (d <= 4))[0]
        ws = np.clip(st[rows][:, None] + off + R12.SHIFTS[None, :], 0, T - N)
        idx = ws[:, :, None] + np.arange(N)[None, None, :]
        W = z[idx][..., refs]
        W = np.transpose(W, (0, 1, 3, 2)).reshape(len(rows), -1, N)
        if hit_fn is not None:
            W = hit_fn(W)
        out.append((rows, W))
    return out


R12.secondary = secondary_near


# ================================================================ Part W: real interference
def seg_at(z, starts, Lseg):
    idx = starts[:, None] + np.arange(Lseg)[None, :]
    B = z.shape[1]
    S = np.transpose(z[idx], (0, 2, 1)).reshape(-1, Lseg)
    P = run_study.texture_proxy(z, np.repeat(starts, B), np.tile(np.arange(B), len(starts)), Lseg - 1, 1024)
    return S, P


def runs_mean(h):
    d = np.diff(np.concatenate([[0], h.astype(int), [0]]))
    lens = np.flatnonzero(d == -1) - np.flatnonzero(d == 1)
    return float(lens.mean()) if len(lens) else 0.0


def part_w(z, hit, ca, te, r, seed):
    res = {"W|hit_rate": float(hit.mean()), "W|run_mean": runs_mean(hit)}
    res["W|eligible"] = float(hit.mean() >= W_MIN_RATE)
    if not res["W|eligible"]:
        return res
    rng = np.random.default_rng(seed)
    Lseg = M + K; B = z.shape[1]
    sc = np.arange(ca[0], ca[1] - Lseg, Lseg); stt = np.arange(te[0], te[1] - Lseg, Lseg)
    clean_c = ~hit[sc[:, None] + np.arange(Lseg)].any(1)
    Sc, _ = seg_at(z, sc[clean_c], Lseg); St, Pt = seg_at(z, stt, Lseg)
    nh = np.repeat(hit[stt[:, None] + np.arange(Lseg)].sum(1), B)
    ec = R14.inn_pow(Sc, r)
    # empirical hit model: real calibration-third hit masks as random 24-pulse blocks
    u = rng.integers(ca[0], ca[1] - Lseg, len(Sc))
    cor = L.corrupted_innovations(hit[u[:, None] + np.arange(Lseg)])
    q = {}
    din_c = R12.int_stats(Sc, r)["D-IN1"]
    bl_c = R14.blank_stat(ec, extra=cor)
    for a in ALPHAS:
        q[("D-IN1", "clean", a)] = R12.q_rank(din_c, a)
        q[("blank", "mask", a)] = R12.q_rank(bl_c, a)
        for k in KAPPAS_W:
            q[(f"clip{k:g}", "clean", a)] = R12.q_rank(L.robust_stat(ec[:, :M], ec[:, M:], KH, "clip", c=k), a)
            q[(f"clip{k:g}", "cert", a)] = R12.q_rank(L.worst_case(ec[:, :M], ec[:, M:], cor[:, :M], cor[:, M:], KH, "clip", c=k), a)
    amp = R14.cn(rng, len(St)); om = rng.uniform(-np.pi, np.pi, len(St)); tpos = np.arange(Lseg)
    base = (np.sqrt(Pt) * amp)[:, None] * np.where(tpos >= M, np.exp(1j * om[:, None] * (tpos[None, :] - M)), 0)
    strata = {"s0": nh == 0, "s12": (nh >= 1) & (nh <= 2), "s3": nh >= 3, "all": np.ones(len(St), bool)}
    for j in range(1 + len(SCR_DB)):
        Sx = St if j == 0 else St + np.sqrt(10 ** (SCR_DB[j - 1] / 10)) * base
        e = R14.inn_pow(Sx, r)
        stat = {"D-IN1": R12.int_stats(Sx, r)["D-IN1"], "blank": R14.blank_stat(e)}
        for k in KAPPAS_W:
            stat[f"clip{k:g}"] = L.robust_stat(e[:, :M], e[:, M:], KH, "clip", c=k)
        for (nm, rule, a), thr in q.items():
            dec = stat[nm] > thr
            for sname, sm in strata.items():
                res.setdefault(f"W|{nm}|{rule}|{a}|{sname}", np.zeros(1 + len(SCR_DB)))[j] = dec[sm].mean() if sm.any() else np.nan
    res["W|n"] = np.array([len(Sc), len(St)] + [int(v.sum()) for v in strata.values()])
    return res


# ================================================================ unit
def run_unit(tag, rot, data=None):
    d = load(tag) if data is None else data
    z, bins, hit = d["z"], d["bins"], d["hit"]
    T = z.shape[0]; run_study.T = T
    BL = blocks(T); tr, ca, te = (BL[b] for b in ROT[rot])
    Xtr, _, _ = episodes(z, *tr, M, STRIDE)
    r = fit_ols(Xtr); a4 = fit_arp(Xtr, R12.P4)
    R4, nu4, _, _ = fit_mixture_arp(Xtr, R12.P4); na4 = NoiseAwareGeneral(R4, nu4)
    sd = lambda part: int(hashlib.sha256(f"R15|{part}|{tag}|{rot}".encode()).hexdigest()[:8], 16)
    res = dict(r=np.array([r.real, r.imag]), a4=a4, nu4=nu4, T=T, B=z.shape[1])
    t0 = time.time()
    rl, _ = R12.part_l(z, bins, ca, te, r, a4, na4, Xtr, np.random.default_rng(sd("L"))); res.update(rl)
    res["sec_L"] = time.time() - t0; t0 = time.time()
    res.update(R12.part_ai(z, bins, ca, te, r, a4, sd("A10"), sd("I")))
    res["sec_AI"] = time.time() - t0; t0 = time.time()
    res.update(R14.part_g(z, None, ca, te, r, sd("G")))
    res["sec_G"] = time.time() - t0; t0 = time.time()
    res.update(R14.part_ktxb(z, ca, te, r, sd("KTXB")))
    res["sec_KTXB"] = time.time() - t0; t0 = time.time()
    res.update(part_w(z, hit, ca, te, r, sd("W")))
    res["sec_W"] = time.time() - t0
    return res


def unit(args):
    tag, rot = args
    path = os.path.join(OUT, f"n_{tag}_rot{rot}.npz")
    if os.path.exists(path):
        return path
    t0 = time.time(); res = run_unit(tag, rot)
    tmp = path + ".tmp.npz"
    np.savez_compressed(tmp, **res, scr_db=SCR_DB, pol=FILES[tag][0], seconds=time.time() - t0)
    os.replace(tmp, path)
    return path


def synthetic():
    rng = np.random.default_rng(0); T, B = 130000, 16; rho = 0.97 * np.exp(-0.1j)
    e = R14.cn(rng, T, B); x = np.zeros((T, B), complex)
    for t in range(1, T):
        x[t] = rho * x[t - 1] + np.sqrt(1 - abs(rho) ** 2) * e[t]
    tex = np.exp(rng.normal(0, 1, (T // 2048 + 1, B))).repeat(2048, 0)[:T]
    z = np.sqrt(30 * tex) * x + R14.cn(rng, T, B)
    hit = rng.random(T) < 0.01
    z = z + np.where(hit[:, None], np.sqrt(1000.0) * R14.cn(rng, T, B), 0)          # whole-pulse hits, 30 dB above noise
    z = (z - z.mean(0)) / np.sqrt(np.mean(abs(z - z.mean(0)) ** 2, 0))
    t0 = time.time(); res = run_unit("synthetic", 2, dict(z=z, bins=list(range(300, 300 + B)), hit=hit))
    print(f"synthetic unit {time.time() - t0:.0f} s; " + ", ".join(f"{k} {res[k]:.0f}" for k in res if k.startswith("sec_")))
    for a in (1e-2, 1e-3, 1e-4):
        print(f"L a={a:g}: " + "; ".join(f"{m} conf {res[f'L|{m}|conf|{a}'][0] / res[f'L|{m}|conf|{a}'][1] / a:.2f}"
                                         for m in ("IN1", "IN4", "OS1_8", "NA4", "CA16", "D-IN4", "PAMF-H(w)", "P-ANMF", "ANMF-FP(w)", "Clip-OS1")))
    print("A Pd@10dB:", {m: round(float(res[f'A|{m}|0.01|pd'][R14.I10]), 2) for m in ("PAMF-H", "D-IN1", "Clip-OS1", "ANMF-FP", "IN1look", "OSraw")})
    print("G g=0/8 look Pd@10dB:", [np.round(res[f"G|abrupt|random|{g}|look"][R14.I10], 2).tolist() for g in (0, 8)])
    print("I 0.05/30 Pfa/a: D-IN1 %.2f, Clip-cert %.2f" % (res["I|0.05|30|D-IN1|0.01"][0] / .01, res["I|0.05|30|Clip-OS1-cert|0.01"][0] / .01))
    print("W hit rate %.4f run %.2f eligible %d n %s" % (res["W|hit_rate"], res["W|run_mean"], res["W|eligible"], res["W|n"].tolist()))
    for k in sorted(k for k in res if k.startswith("W|") and k.endswith("|all") and "|0.01|" in k):
        v = res[k]; s1 = res[k.replace("|all", "|s12")]
        print(f"{k:<28s} Pfa/a {v[0] / .01:5.2f} (1-2 hits {s1[0] / .01:5.2f})  Pd@10dB {v[1 + R14.I10]:.2f}")


if __name__ == "__main__":
    ap = argparse.ArgumentParser(); ap.add_argument("--workers", type=int, default=12); ap.add_argument("--synthetic", action="store_true")
    ap.add_argument("--tags", nargs="*", help="restrict to these recordings (job selection only)")
    a = ap.parse_args()
    if a.synthetic:
        synthetic(); sys.exit()
    if not frozen():
        sys.exit("PROTOCOL_R15.md does not match its hash.")
    os.makedirs(OUT, exist_ok=True)
    src = lambda p: hashlib.sha256(open(p, "rb").read()).hexdigest()
    json.dump(dict(started=time.strftime("%Y-%m-%d %H:%M:%S"), protocol_sha=open(os.path.join(HERE, "PROTOCOL_R15.sha256")).read().split()[0],
                   script_sha=src(__file__), loader_sha=src(os.path.join(HERE, "netrad.py")),
                   r12_sha=src(os.path.join(ROOT, "r12", "run_r12_ipix.py")), r14_sha=src(os.path.join(ROOT, "r14", "run_r14_ipix.py")),
                   laws_sha=src(os.path.join(ROOT, "r12", "laws.py"))),
              open(os.path.join(OUT, f"manifest_{int(time.time())}.json"), "w"), indent=1)
    jobs = [(tag, rot) for tag in (a.tags or FILES) for rot in (2, 3)]
    from concurrent.futures import ProcessPoolExecutor
    with ProcessPoolExecutor(a.workers) as ex:
        for pth in ex.map(unit, jobs):
            print("saved", os.path.basename(pth), flush=True)
