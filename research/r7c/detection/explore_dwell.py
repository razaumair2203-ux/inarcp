"""EXPLORATORY (not in a frozen protocol; defined after seeing R8-O unit-17 smoke output):
dwell-level comparison at EQUAL dwell false-alarm probability. For K looks after onset, dwell statistics:
  max_j score_j (OR rule) and sum_j score_j^2 (non-coherent integration of normalized statistics),
for IN1, NA4 and the power detector CAloc (score |z|/sqrt(P_loc)). Dwell thresholds are split-conformal quantiles
of the dwell statistic over clean calibration-third segments, so every detector has dwell Pfa <= alpha.
Targets: persistent Swerling-1, random Doppler, as in PROTOCOL_ONSET.md.
Usage: INARCP_GPU=1 python explore_dwell.py [--workers 8] -> study/results/dwell/"""
import sys, os, math, json, hashlib, argparse, time
HERE = os.path.dirname(os.path.abspath(__file__)); ROOT = os.path.dirname(HERE)
sys.path.insert(0, ROOT); sys.path.insert(0, os.path.join(ROOT, "study"))
import numpy as np
from ipix import FILES, load, episodes
from methods import conformal_quantile, fit_ols, innovation_scale, fit_mixture_arp, NoiseAwareGeneral
from run_study import texture_proxy, BLOCKS, ROT, STRIDE

M, K = 16, 8
KS = (1, 2, 4, 8)
ALPHA = 0.01
SCR_DB = np.arange(-5, 25.01, 2.5)
OUT = os.path.join(ROOT, "study", "results", "dwell")


def segments(z, blk):
    T, B = z.shape; starts = np.arange(blk[0], blk[1] - M - K, STRIDE)
    idx = starts[:, None] + np.arange(M + K)[None, :]
    seg = np.transpose(z[idx], (0, 2, 1)).reshape(-1, M + K)
    return seg, texture_proxy(z, np.repeat(starts, B), np.tile(np.arange(B), len(starts)), M + K - 1, 1024)


def look_scores(S, P, cs):
    out = {m: np.zeros((len(S), K)) for m in list(cs) + ["CAloc"]}
    for j in range(K):
        W = S[:, j:j + M + 1]; H, Y = W[:, :-1], W[:, -1]
        for m, f in cs.items():
            c, s = f(H); out[m][:, j] = abs(Y - c) / s
        out["CAloc"][:, j] = abs(S[:, M + j]) / np.sqrt(P)
    return out


def unit(args):
    num, pol, rot = args
    path = os.path.join(OUT, f"w_{num}_{pol}_rot{rot}.npz")
    if os.path.exists(path): return path
    z = load(num)["z"][pol]; tr, ca, te = (BLOCKS[b] for b in ROT[rot])
    Xtr, _, _ = episodes(z, *tr, M, STRIDE)
    r = fit_ols(Xtr); R4, nu4, _, _ = fit_mixture_arp(Xtr, 4); na4 = NoiseAwareGeneral(R4, nu4)
    cs = {"IN1": lambda H: (r * H[:, -1], innovation_scale(H, r)), "NA4": lambda H: na4.center_scale(H)[:2]}
    Sc, Pc = segments(z, ca); St, Pt = segments(z, te)
    cal = look_scores(Sc, Pc, cs); n = len(St)
    rng = np.random.default_rng(int(hashlib.sha256(f"R8W|{num}|{pol}|{rot}".encode()).hexdigest()[:8], 16))
    amp = np.sqrt(.5) * (rng.standard_normal(n) + 1j * rng.standard_normal(n)); om = rng.uniform(-np.pi, np.pi, n)
    tv = np.zeros((n, M + K), complex); tv[:, M:] = np.exp(1j * om[:, None] * np.arange(K)[None, :])
    stat = {"max": lambda X, k: X[:, :k].max(1), "sum": lambda X, k: (X[:, :k] ** 2).sum(1)}
    thr = {(m, s, k): conformal_quantile(f(cal[m], k), ALPHA) for m in cal for s, f in stat.items() for k in KS}
    res = {}
    clean = look_scores(St, Pt, cs)
    for (m, s, k), t in thr.items(): res[f"{m}|{s}|K{k}|pfa"] = float(np.mean(stat[s](clean[m], k) > t))
    for (m, s, k) in thr: res[f"{m}|{s}|K{k}|pd"] = np.zeros(len(SCR_DB))
    for i, sdb in enumerate(SCR_DB):
        sc = look_scores(St + (np.sqrt(10 ** (sdb / 10) * Pt) * amp)[:, None] * tv, Pt, cs)
        for (m, s, k), t in thr.items(): res[f"{m}|{s}|K{k}|pd"][i] = np.mean(stat[s](sc[m], k) > t)
    np.savez_compressed(path, **res, scr_db=SCR_DB, day=FILES[num][1]); return path


if __name__ == "__main__":
    ap = argparse.ArgumentParser(); ap.add_argument("--workers", type=int, default=8); a = ap.parse_args()
    os.makedirs(OUT, exist_ok=True); os.environ["OPENBLAS_NUM_THREADS"] = "2"
    from concurrent.futures import ProcessPoolExecutor
    jobs = [(f, pol, r) for f in FILES for pol in ("like0", "like1") for r in (2, 3)]
    with ProcessPoolExecutor(a.workers) as ex:
        for p in ex.map(unit, jobs): print("saved", os.path.basename(p), flush=True)
