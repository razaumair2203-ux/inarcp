"""R11 Part J (PROTOCOL_R11.md): JKU 77 GHz FMCW with real mutual interference.
Fit/calibrate on the clean reference run meas_1_ref_corner (frames 0-32 / 34-65), test on its frames 67-99 and on all frames of
meas_2_int_A and meas_5_int_C. Detectors IN1, OS1_8, CA16, OS16_8, each without and with fast-time zeroing (Z).
Usage: python run_r11_jku.py --data <dir> -> study/results/r11/j_st<s>_rx<r>.npz"""
import sys, os, json, hashlib, argparse, time
HERE = os.path.dirname(os.path.abspath(__file__)); ROOT = os.path.dirname(HERE)
sys.path.insert(0, ROOT); sys.path.insert(0, os.path.join(ROOT, "study"))
import numpy as np
from scipy.io import loadmat
from scipy.ndimage import binary_dilation
from methods import conformal_quantile, fit_ols, innovation_scale

M, EP = 16, 17
RX = (0, 5, 10, 15)
BINS = np.arange(8, 248)
ALPHA = 0.01
SCR_DB = np.arange(-5, 25.01, 2.5)
STRATA = ((0, 0), (1, 2), (3, 5), (6, 16))
RUNS = {"ref": "meas_1_ref_corner.mat", "A": "meas_2_int_A.mat", "C": "meas_5_int_C.mat"}
METH = ("IN1", "OS1_8", "CA16", "OS16_8")
OUT = os.path.join(ROOT, "study", "results", "r11")
HANN = np.hanning(512)
HP = np.abs(1 - np.exp(-2j * np.pi * BINS / 512))


def frozen():
    h = open(os.path.join(HERE, "PROTOCOL_R11.sha256")).read().split()[0]
    return hashlib.sha256(open(os.path.join(HERE, "PROTOCOL_R11.md"), "rb").read()).hexdigest() == h


def profiles(xr, zero):
    """xr: raw ADC (512, 128, 100) for one Rx. Returns Z (240, 128, 100), retained Hann weight (128, 100), zeroed fraction."""
    x = np.diff(xr, axis=0, prepend=xr[:1])
    keep = np.ones(x.shape, bool)
    if zero:
        med = np.median(np.abs(x), axis=0, keepdims=True)
        mask = binary_dilation(np.abs(x) > 4 * med, structure=np.ones((9, 1, 1), bool))
        keep = ~mask; x = np.where(keep, x, 0.0)
    w = np.tensordot(HANN, keep.astype(float), axes=(0, 0)) / HANN.sum()
    Z = np.fft.fft(x * HANN[:, None, None], axis=0)[BINS] / HP[:, None, None]
    return Z, w, float(1 - keep.mean())


def episodes(Z, frames, hits, keepw):
    X, meta = [], []
    for f in frames:
        for e in range(7):
            sl = slice(EP * e, EP * e + EP)
            X.append(Z[:, sl, f])
            h = hits[sl, f]; nb = len(BINS)
            meta.append(np.stack([np.full(nb, h[:M].sum()), np.full(nb, h[M]), np.full(nb, keepw[EP * e + M, f]), np.arange(nb)], 1))
    return np.concatenate(X), np.concatenate(meta)


def inn_pow1(H, r):
    return np.concatenate([(1 - abs(r) ** 2) * abs(H[:, :1]) ** 2, abs(H[:, 1:] - r * H[:, :-1]) ** 2], 1)


def scores(X, r):
    H, Y = X[:, :-1], X[:, -1]
    kth = lambda v, k: np.partition(v, k - 1, axis=1)[:, k - 1]
    return {"IN1": abs(Y - r * H[:, -1]) / innovation_scale(H, r),
            "OS1_8": abs(Y - r * H[:, -1]) / np.sqrt(kth(inn_pow1(H, r), 8)),
            "CA16": abs(Y) / np.sqrt(np.mean(abs(H) ** 2, 1)),
            "OS16_8": abs(Y) / np.sqrt(kth(abs(H) ** 2, 8))}


def station(args):
    data, st = args
    raw = {k: loadmat(os.path.join(data, f), variable_names=[f"data_station_{st}"])[f"data_station_{st}"] for k, f in RUNS.items()}
    for rx in RX:
        path = os.path.join(OUT, f"j_st{st}_rx{rx}.npz")
        if os.path.exists(path): continue
        res = {}
        base = {k: profiles(raw[k][:, :, rx, :].astype(np.float64), False) for k in RUNS}
        medP = np.median(np.abs(base["ref"][0]) ** 2, axis=(1, 2))
        hits = {k: ((np.abs(base[k][0]) ** 2 > 10 * medP[:, None, None]).mean(0) > 0.1) for k in RUNS}   # (128, 100)
        for k in RUNS: res[f"hitrate|{k}"] = float(hits[k].mean())
        for zero in (False, True):
            tag = "Z" if zero else "N"
            prof = base if not zero else {k: profiles(raw[k][:, :, rx, :].astype(np.float64), True) for k in RUNS}
            for k in RUNS: res[f"zeroed|{tag}|{k}"] = prof[k][2]
            Zr, wr, _ = prof["ref"]
            Xtr, _ = episodes(Zr, range(0, 33), hits["ref"], wr); Xca, _ = episodes(Zr, range(34, 66), hits["ref"], wr)
            r = fit_ols(Xtr); res[f"r|{tag}"] = np.array([r.real, r.imag])
            q = {m: conformal_quantile(v, ALPHA) for m, v in scores(Xca, r).items()}
            for run, frames in (("ref", range(67, 100)), ("A", range(100)), ("C", range(100))):
                Zt, wt, _ = prof[run]
                X, meta = episodes(Zt, frames, hits[run], wt)
                hh, yh, kw, bn = meta[:, 0], meta[:, 1].astype(bool), meta[:, 2], meta[:, 3].astype(int)
                strat = np.full(len(X), -1)
                for s, (lo, hi) in enumerate(STRATA): strat[(hh >= lo) & (hh <= hi)] = s
                clean = scores(X, r)
                for s in range(len(STRATA)):
                    sel = (~yh) & (strat == s); res[f"n|{tag}|{run}|s{s}"] = int(sel.sum())
                    for m in METH: res[f"pfa|{tag}|{run}|{m}|s{s}"] = float(np.mean(clean[m][sel] > q[m])) if sel.any() else np.nan
                res[f"n|{tag}|{run}|yhit"] = int(yh.sum())
                for m in METH: res[f"pfa|{tag}|{run}|{m}|yhit"] = float(np.mean(clean[m][yh] > q[m])) if yh.any() else np.nan
                rng = np.random.default_rng(int(hashlib.sha256(f"R11J|{st}|{rx}|{run}".encode()).hexdigest()[:8], 16))
                g = np.sqrt(.5) * (rng.standard_normal(len(X)) + 1j * rng.standard_normal(len(X)))
                amp = np.sqrt(medP[bn]) * g * (kw if zero else 1.0)
                pd = {(m, s): np.zeros(len(SCR_DB)) for m in METH for s in range(len(STRATA))}
                for i, sdb in enumerate(SCR_DB):
                    Xi = X.copy(); Xi[:, -1] += np.sqrt(10 ** (sdb / 10)) * amp
                    sc = scores(Xi, r)
                    for s in range(len(STRATA)):
                        sel = (~yh) & (strat == s)
                        for m in METH: pd[(m, s)][i] = np.mean(sc[m][sel] > q[m]) if sel.any() else np.nan
                for (m, s), v in pd.items(): res[f"pd|{tag}|{run}|{m}|s{s}"] = v
        np.savez_compressed(path, **res, scr_db=SCR_DB)
        print("saved", os.path.basename(path), flush=True)
    return st


if __name__ == "__main__":
    ap = argparse.ArgumentParser(); ap.add_argument("--data", required=True); a = ap.parse_args()
    if not frozen(): sys.exit("PROTOCOL_R11.md does not match its hash.")
    os.makedirs(OUT, exist_ok=True)
    json.dump(dict(started=time.strftime("%Y-%m-%d %H:%M:%S"), protocol_sha=open(os.path.join(HERE, "PROTOCOL_R11.sha256")).read().split()[0],
                   script_sha=hashlib.sha256(open(__file__, "rb").read()).hexdigest()), open(os.path.join(OUT, f"manifest_j_{int(time.time())}.json"), "w"), indent=1)
    from concurrent.futures import ProcessPoolExecutor
    with ProcessPoolExecutor(2) as ex:
        for s in ex.map(station, [(a.data, 1), (a.data, 2)]): print("station done", s, flush=True)
