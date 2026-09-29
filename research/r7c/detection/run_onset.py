"""R8-O: onset detection of persistent targets in real IPIX clutter (PROTOCOL_ONSET.md).
Usage: INARCP_GPU=1 python run_onset.py [--workers 8]. Output: study/results/onset/o_<file>_<pol>_rot<k>.npz"""
import sys, os, math, json, hashlib, argparse, time
HERE = os.path.dirname(os.path.abspath(__file__)); ROOT = os.path.dirname(HERE)
sys.path.insert(0, ROOT); sys.path.insert(0, os.path.join(ROOT, "study"))
import numpy as np
from ipix import FILES, load, episodes
from methods import conformal_quantile, fit_ols, innovation_scale, fit_mixture_arp, NoiseAwareGeneral
from run_study import fit_arp, arp_cs, texture_proxy, BLOCKS, ROT, STRIDE

M, K = 16, 8
ALPHAS = (0.01, 0.001)
SCR_DB = np.arange(-5, 25.01, 2.5)
KS = (1, 2, 4, 8)
DOPPLER = ("random", "matched", "opposite")
OUT = os.path.join(ROOT, "study", "results", "onset")


def frozen():
    h = open(os.path.join(HERE, "PROTOCOL_ONSET.sha256")).read().split()[0]
    return hashlib.sha256(open(os.path.join(HERE, "PROTOCOL_ONSET.md"), "rb").read()).hexdigest() == h


def unit(args):
    num, pol, rot = args
    path = os.path.join(OUT, f"o_{num}_{pol}_rot{rot}.npz")
    if os.path.exists(path): return path
    t0 = time.time(); z = load(num)["z"][pol]; T, B = z.shape
    tr, ca, te = (BLOCKS[b] for b in ROT[rot])
    Xtr, _, _ = episodes(z, *tr, M, STRIDE); Xca, sca, bca = episodes(z, *ca, M, STRIDE)
    r = fit_ols(Xtr); a4 = fit_arp(Xtr, 4); R4, nu4, _, _ = fit_mixture_arp(Xtr, 4); na4 = NoiseAwareGeneral(R4, nu4)
    cs = {"IN1": lambda H: (r * H[:, -1], innovation_scale(H, r)),
          "IN4": lambda H: arp_cs(H, a4),
          "NA4": lambda H: na4.center_scale(H)[:2],
          "CA16": lambda H: (np.zeros(len(H), complex), np.sqrt(np.mean(abs(H) ** 2, 1)))}
    q = {}
    for mth, f in cs.items():
        c, s = f(Xca[:, :-1]); sc = abs(Xca[:, -1] - c) / s
        for a in ALPHAS: q[(mth, a)] = conformal_quantile(sc, a)
    for a in ALPHAS: q[("G1", a)] = math.sqrt(M * (a ** (-1 / M) - 1))
    Pca = texture_proxy(z, sca, bca, M, 1024)
    sloc = abs(Xca[:, -1]) / np.sqrt(Pca)
    for a in ALPHAS: q[("CAloc", a)] = conformal_quantile(sloc, a)
    # test segments of length M+K; onset at segment position M
    starts = np.arange(te[0], te[1] - M - K, STRIDE)
    idx = starts[:, None] + np.arange(M + K)[None, :]
    seg = np.transpose(z[idx], (0, 2, 1)).reshape(-1, M + K)                      # (n, M+K)
    st = np.repeat(starts, B); bt = np.tile(np.arange(B), len(starts)); n = len(seg)
    Ploc = texture_proxy(z, st, bt, M + K - 1, 1024)
    rng = np.random.default_rng(int(hashlib.sha256(f"R8O|{num}|{pol}|{rot}".encode()).hexdigest()[:8], 16))
    amp0 = np.sqrt(.5) * (rng.standard_normal(n) + 1j * rng.standard_normal(n))
    om = {"random": rng.uniform(-np.pi, np.pi, n), "matched": np.full(n, np.angle(r)), "opposite": np.full(n, np.angle(r) + np.pi)}
    methods = ("IN1", "G1", "IN4", "NA4", "CA16", "CAloc")
    res = {}

    def decide(S):                       # S: (n, M+K) segment -> dict method -> (n, K) bool decisions per look
        out = {m: {a: np.zeros((n, K), bool) for a in ALPHAS} for m in methods}
        for j in range(K):
            W = S[:, j:j + M + 1]; H, Y = W[:, :-1], W[:, -1]
            for mth, f in cs.items():
                c, s = f(H); sc = abs(Y - c) / s
                for a in ALPHAS:
                    out[mth][a][:, j] = sc > q[(mth, a)]
                    if mth == "IN1": out["G1"][a][:, j] = sc > q[("G1", a)]
            sl = abs(S[:, M + j]) / np.sqrt(Ploc)
            for a in ALPHAS: out["CAloc"][a][:, j] = sl > q[("CAloc", a)]
        return out

    clean = decide(seg)
    for mth in methods:
        for a in ALPHAS:
            d = clean[mth][a]; res[f"{mth}|{a}|pfa_cum"] = np.array([d[:, :k].any(1).mean() for k in KS])
            res[f"{mth}|{a}|pfa_look"] = d.mean(0)
    for dop in DOPPLER:
        tv = np.zeros((n, M + K), complex); tv[:, M:] = np.exp(1j * om[dop][:, None] * np.arange(K)[None, :])
        look = {(m, a): np.zeros((len(SCR_DB), K)) for m in methods for a in ALPHAS}
        cum = {(m, a): np.zeros((len(SCR_DB), len(KS))) for m in methods for a in ALPHAS}
        for i, sdb in enumerate(SCR_DB):
            S = seg + (np.sqrt(10 ** (sdb / 10) * Ploc) * amp0)[:, None] * tv
            dd = decide(S)
            for m in methods:
                for a in ALPHAS:
                    look[(m, a)][i] = dd[m][a].mean(0)
                    cum[(m, a)][i] = [dd[m][a][:, :k].any(1).mean() for k in KS]
        for (m, a), v in look.items(): res[f"{m}|{a}|{dop}|look"] = v
        for (m, a), v in cum.items(): res[f"{m}|{a}|{dop}|cum"] = v
    tmp = path + ".tmp.npz"
    np.savez_compressed(tmp, **res, scr_db=SCR_DB, day=FILES[num][1], n=n, r=[r.real, r.imag], seconds=time.time() - t0)
    os.replace(tmp, path); return path


if __name__ == "__main__":
    ap = argparse.ArgumentParser(); ap.add_argument("--workers", type=int, default=8); a = ap.parse_args()
    if not frozen(): sys.exit("PROTOCOL_ONSET.md does not match its hash.")
    os.makedirs(OUT, exist_ok=True); os.environ["OPENBLAS_NUM_THREADS"] = "2"
    json.dump(dict(started=time.strftime("%Y-%m-%d %H:%M:%S"), gpu=os.environ.get("INARCP_GPU"),
                   protocol_sha=open(os.path.join(HERE, "PROTOCOL_ONSET.sha256")).read().split()[0],
                   script_sha=hashlib.sha256(open(__file__, "rb").read()).hexdigest()),
              open(os.path.join(OUT, f"manifest_{int(time.time())}.json"), "w"), indent=1)
    from concurrent.futures import ProcessPoolExecutor
    jobs = [(f, pol, r) for f in FILES for pol in ("like0", "like1") for r in (2, 3)]
    with ProcessPoolExecutor(a.workers) as ex:
        for p in ex.map(unit, jobs): print("saved", os.path.basename(p), flush=True)
