"""R11 Part O (PROTOCOL_R11.md): order-statistic innovation normalization on the 56 IPIX units.
Same segments, thresholds, seeds and target draws as R10 (run_r10.py). Usage: INARCP_GPU=1 python run_r11_ipix.py [--workers 12]
Output: study/results/r11/o_<file>_<pol>_rot<k>.npz"""
import sys, os, math, json, hashlib, argparse, time
HERE = os.path.dirname(os.path.abspath(__file__)); ROOT = os.path.dirname(HERE)
sys.path.insert(0, ROOT); sys.path.insert(0, os.path.join(ROOT, "study")); sys.path.insert(0, os.path.join(ROOT, "r10"))
import numpy as np
from ipix import FILES, load, episodes
from methods import conformal_quantile, fit_ols, innovation_scale, fit_mixture_arp, NoiseAwareGeneral
from run_study import fit_arp, arp_cs, BLOCKS, ROT, STRIDE
from run_r10 import segments, ramp_profile, steer_whitened, innovations, M, K, P4, SCR_DB, I10, LS

KS = (1, 2, 4, 8)
LOOK = ("IN1", "OS1_8", "OS1_12", "IN4", "OS4", "NA4", "CAloc")
DWELL = ("IN1sum", "OS1_8sum", "PAMFH", "PAMFOS", "CAlocsum")
ALPHAS = (0.1, 0.01)
OUT = os.path.join(ROOT, "study", "results", "r11")


def frozen():
    h = open(os.path.join(HERE, "PROTOCOL_R11.sha256")).read().split()[0]
    return hashlib.sha256(open(os.path.join(HERE, "PROTOCOL_R11.md"), "rb").read()).hexdigest() == h


def inn_pow1(H, r):
    return np.concatenate([(1 - abs(r) ** 2) * abs(H[:, :1]) ** 2, abs(H[:, 1:] - r * H[:, :-1]) ** 2], 1)


def inn_pow4(H, a):
    p = len(a); m = H.shape[1]
    res = H[:, p:] - sum(a[k] * H[:, p - 1 - k:m - 1 - k] for k in range(p))
    return abs(res) ** 2


def kth(v, k):
    return np.partition(v, k - 1, axis=1)[:, k - 1]


def os_law(q2, m, k):
    return 1 - np.prod([(m - i) / (m - i + q2) for i in range(k)])


def look_scores(S, P, cs):
    out = {m: np.zeros((len(S), K)) for m in LOOK}
    for j in range(K):
        W = S[:, j:j + M + 1]; H, Y = W[:, :-1], W[:, -1]
        for m, f in cs.items():
            c, s = f(H); out[m][:, j] = abs(Y - c) / s
        out["CAloc"][:, j] = abs(S[:, M + j]) / np.sqrt(P)
    return out


def pamf(S, a, W):
    E = innovations(S, a); hist = E[:, :M - P4]; dw = E[:, M - P4:]
    out = {}
    for k in KS:
        num = np.max(abs(dw[:, :k] @ np.conj(W[:, :k]).T) ** 2 / np.sum(abs(W[:, :k]) ** 2, 1)[None, :], 1)
        out[("PAMFH", k)] = num / np.mean(abs(hist) ** 2, 1)
        out[("PAMFOS", k)] = num / np.median(abs(hist) ** 2, 1)
    return out


def all_stats(S, P, cs, a4, W):
    L = look_scores(S, P, cs); D = {}
    for k in KS:
        D[("IN1sum", k)] = (L["IN1"][:, :k] ** 2).sum(1)
        D[("OS1_8sum", k)] = (L["OS1_8"][:, :k] ** 2).sum(1)
        D[("CAlocsum", k)] = (L["CAloc"][:, :k] ** 2).sum(1)
    D.update(pamf(S, a4, W)); return L, D


def run_unit(z, blocks, seed):
    tr, ca, te = blocks
    Xtr, _, _ = episodes(z, *tr, M, STRIDE)
    r = fit_ols(Xtr); a4 = fit_arp(Xtr, P4); R4, nu4, _, _ = fit_mixture_arp(Xtr, P4); na4 = NoiseAwareGeneral(R4, nu4)
    cs = {"IN1": lambda H: (r * H[:, -1], innovation_scale(H, r)),
          "OS1_8": lambda H: (r * H[:, -1], np.sqrt(kth(inn_pow1(H, r), 8))),
          "OS1_12": lambda H: (r * H[:, -1], np.sqrt(kth(inn_pow1(H, r), 12))),
          "IN4": lambda H: arp_cs(H, a4),
          "OS4": lambda H: (arp_cs(H, a4)[0], np.sqrt(kth(inn_pow4(H, a4), 6))),
          "NA4": lambda H: na4.center_scale(H)[:2]}
    W = steer_whitened(a4)
    Sc, Pc, _ = segments(z, ca); St, Pt, _ = segments(z, te); n = len(St)
    Lc, Dc = all_stats(Sc, Pc, cs, a4, W)
    qL = {(m, a): conformal_quantile(Lc[m][:, 0], a) for m in LOOK for a in ALPHAS}
    qD = {(d, k): conformal_quantile(v, 0.01) for (d, k), v in Dc.items()}
    res = dict(n=n, r=np.array([r.real, r.imag]))
    Lt, Dt = all_stats(St, Pt, cs, a4, W)
    qb = np.digitize(Pt, np.quantile(Pt, [.2, .4, .6, .8]))
    for m in LOOK:
        for a in ALPHAS:
            e = Lt[m][:, 0] > qL[(m, a)]
            res[f"L|{m}|{a}|pfa"] = float(e.mean()); res[f"L|{m}|{a}|qpfa"] = np.array([e[qb == b].mean() for b in range(5)])
    for m, kk in (("OS1_8", 8), ("OS1_12", 12)):
        for a in ALPHAS:
            res[f"law|{m}|{a}"] = np.array([os_law(qL[(m, a)] ** 2, M, kk), float(np.mean(Lt[m][:, 0] <= qL[(m, a)]))])
    res["law|OS4|0.1"] = np.array([os_law(qL[("OS4", 0.1)] ** 2, M - P4, 6), float(np.mean(Lt["OS4"][:, 0] <= qL[("OS4", 0.1)]))])
    res["law|OS4|0.01"] = np.array([os_law(qL[("OS4", 0.01)] ** 2, M - P4, 6), float(np.mean(Lt["OS4"][:, 0] <= qL[("OS4", 0.01)]))])
    for (d, k), v in Dt.items(): res[f"D|{d}|K{k}|pfa"] = float(np.mean(v > qD[(d, k)]))
    rng = np.random.default_rng(seed)                                     # identical draws to R10
    amp = np.sqrt(.5) * (rng.standard_normal(n) + 1j * rng.standard_normal(n)); om = rng.uniform(-np.pi, np.pi, n)
    tpos = np.arange(M + K)
    for place in ("pre", "in"):
        for L in LS:
            g, t0 = ramp_profile(L, place)
            tv = g[None, :] * np.exp(1j * om[:, None] * (tpos[None, :] - t0))
            look = {m: np.zeros((len(SCR_DB), K)) for m in LOOK}; cum = {m: np.zeros(len(SCR_DB)) for m in LOOK}
            dw = {d: np.zeros(len(SCR_DB)) for d in DWELL}; dw9 = {}
            for i, sdb in enumerate(SCR_DB):
                Ls, D = all_stats(St + (np.sqrt(10 ** (sdb / 10) * Pt) * amp)[:, None] * tv, Pt, cs, a4, W)
                for m in LOOK:
                    dec = Ls[m] > qL[(m, 0.01)]; look[m][i] = dec.mean(0); cum[m][i] = dec.any(1).mean()
                for d in DWELL: dw[d][i] = np.mean(D[(d, 8)] > qD[(d, 8)])
            for m in LOOK: res[f"R|{place}|L{L}|{m}|look"] = look[m]; res[f"R|{place}|L{L}|{m}|cum"] = cum[m]
            for d in DWELL: res[f"R|{place}|L{L}|{d}|dwell"] = dw[d]
    return res


def unit(args):
    num, pol, rot = args
    path = os.path.join(OUT, f"o_{num}_{pol}_rot{rot}.npz")
    if os.path.exists(path): return path
    t0 = time.time(); z = load(num)["z"][pol]
    seed = int(hashlib.sha256(f"R10|{num}|{pol}|{rot}".encode()).hexdigest()[:8], 16)
    res = run_unit(z, tuple(BLOCKS[b] for b in ROT[rot]), seed)
    tmp = path + ".tmp.npz"; np.savez_compressed(tmp, **res, scr_db=SCR_DB, day=FILES[num][1], seconds=time.time() - t0)
    os.replace(tmp, path); return path


if __name__ == "__main__":
    ap = argparse.ArgumentParser(); ap.add_argument("--workers", type=int, default=12); a = ap.parse_args()
    if not frozen(): sys.exit("PROTOCOL_R11.md does not match its hash.")
    os.makedirs(OUT, exist_ok=True); os.environ["OPENBLAS_NUM_THREADS"] = "2"
    json.dump(dict(started=time.strftime("%Y-%m-%d %H:%M:%S"), protocol_sha=open(os.path.join(HERE, "PROTOCOL_R11.sha256")).read().split()[0],
                   script_sha=hashlib.sha256(open(__file__, "rb").read()).hexdigest()), open(os.path.join(OUT, f"manifest_o_{int(time.time())}.json"), "w"), indent=1)
    from concurrent.futures import ProcessPoolExecutor
    jobs = [(f, pol, r) for f in FILES for pol in ("like0", "like1") for r in (2, 3)]
    with ProcessPoolExecutor(a.workers) as ex:
        for p in ex.map(unit, jobs): print("saved", os.path.basename(p), flush=True)
