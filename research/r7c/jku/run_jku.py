"""R8-J: second radar (77 GHz FMCW, JKU open dataset) per PROTOCOL_JKU.md.
Usage: INARCP_GPU=1 python run_jku.py --data <dir with meas_0_ref.mat, meas_5_int_C.mat> [--workers 6]"""
import sys, os, math, json, hashlib, argparse, time
HERE = os.path.dirname(os.path.abspath(__file__)); ROOT = os.path.dirname(HERE)
sys.path.insert(0, ROOT); sys.path.insert(0, os.path.join(ROOT, "study"))
import numpy as np
from methods import (conformal_quantile, fit_ols, innovation_scale, fit_mixture_model, NoiseAware,
                     fit_mixture_arp, NoiseAwareGeneral)
from run_study import fit_arp, arp_cs
from cgauss import coverage, cov_matrix

M, EP = 16, 17
ALPHAS = (0.1, 0.01)
RX = (0, 5, 10, 15)
BINS = np.arange(8, 248)
THIRDS = {"A": range(0, 33), "B": range(34, 66), "C": range(67, 100)}
ROT = {1: ("A", "B", "C"), 2: ("B", "C", "A"), 3: ("C", "A", "B")}
CLS = [-np.inf, -5, 0, 5, 10, 20, np.inf]
SCR_DB = np.arange(-5, 25.01, 2.5)
OUT = os.path.join(ROOT, "study", "results", "jku")


def frozen():
    h = open(os.path.join(HERE, "PROTOCOL_JKU.sha256")).read().split()[0]
    return hashlib.sha256(open(os.path.join(HERE, "PROTOCOL_JKU.md"), "rb").read()).hexdigest() == h


def profiles(path, station, rx):
    """complex range profiles Z[bin, chirp, frame] for one station/Rx, noise-floor equalized."""
    from scipy.io import loadmat
    x = loadmat(path, variable_names=[f"data_station_{station}"])[f"data_station_{station}"][:, :, rx, :].astype(np.float64)
    x = np.diff(x, axis=0, prepend=x[:1])                                    # dataset high-pass [1,-1]
    Z = np.fft.fft(x * np.hanning(512)[:, None, None], axis=0)[BINS]         # (240, 128, 100)
    h = np.abs(1 - np.exp(-2j * np.pi * BINS / 512))                          # known high-pass magnitude
    return Z / h[:, None, None]


def episodes(Z, frames):
    """X (n, 17), P_loc (n,), frame and bin index of each episode."""
    Xs, Ps, fr, bn = [], [], [], []
    P = np.abs(Z) ** 2
    for f in frames:
        tot = P[:, :, f].sum(1)
        for e in range(7):
            sl = slice(EP * e, EP * e + EP)
            Xs.append(Z[:, sl, f]); Ps.append((tot - P[:, sl, f].sum(1)) / (128 - EP))
            fr.append(np.full(len(BINS), f)); bn.append(np.arange(len(BINS)))
    return np.concatenate(Xs), np.concatenate(Ps), np.concatenate(fr), np.concatenate(bn)


def fits_for(Xtr):
    f = {}; r = fit_ols(Xtr)
    f["U"] = lambda H: (r * H[:, -1], np.ones(len(H)))
    f["RMS"] = lambda H: (r * H[:, -1], np.sqrt(np.mean(abs(H) ** 2, 1)))
    f["IN1"] = lambda H: (r * H[:, -1], innovation_scale(H, r))
    a4 = fit_arp(Xtr, 4); f["IN4"] = lambda H: arp_cs(H, a4)
    rho1, nu1, w1 = fit_mixture_model(Xtr); na1 = NoiseAware(M, rho1, nu1); f["NA1"] = lambda H: na1.center_scale(H)[:2]
    R4, nu4, _, res4 = fit_mixture_arp(Xtr, 4); na4 = NoiseAwareGeneral(R4, nu4); f["NA4"] = lambda H: na4.center_scale(H)[:2]
    f["CA16"] = lambda H: (np.zeros(len(H), complex), np.sqrt(np.mean(abs(H) ** 2, 1)))
    return f, dict(r=r, rho1=rho1, nu1=nu1, nu4=nu4, na4_conv=bool(res4.success))


def unit(args):
    data, station, rx, rot = args
    path = os.path.join(OUT, f"j_s{station}_rx{rx}_rot{rot}.npz")
    if os.path.exists(path): return path
    t0 = time.time(); Z = profiles(os.path.join(data, "meas_0_ref.mat"), station, rx)
    tr, ca, te = (THIRDS[b] for b in ROT[rot])
    Xtr, _, _, _ = episodes(Z, tr); Xca, Pca, _, _ = episodes(Z, ca); Xte, Pte, fte, bte = episodes(Z, te)
    rng = np.random.default_rng(int(hashlib.sha256(f"R8J|{station}|{rx}|{rot}".encode()).hexdigest()[:8], 16))
    Xtr = Xtr[rng.choice(len(Xtr), 20000, replace=False)]
    f, rec = fits_for(Xtr)
    f["CAloc"] = None
    cnr = np.maximum(Pte / rec["nu1"] - 1, 1e-3); cls = np.digitize(10 * np.log10(cnr), CLS[1:-1])
    g = np.sqrt(.5) * (rng.standard_normal(len(Xte)) + 1j * rng.standard_normal(len(Xte)))
    amp = np.sqrt(10 ** (SCR_DB / 10)[:, None] * Pte[None, :]); Y = Xte[:, -1]; res = {}
    for name, fn in f.items():
        if name == "CAloc":
            cc, sc, ct, stt = np.zeros(len(Xca)), np.sqrt(Pca), np.zeros(len(Xte)), np.sqrt(Pte)
        else:
            (cc, sc), (ct, stt) = fn(Xca[:, :-1]), fn(Xte[:, :-1])
        s_cal = abs(Xca[:, -1] - cc) / sc; s_te = abs(Y - ct) / stt
        qs = {a: conformal_quantile(s_cal, a) for a in ALPHAS}
        if name == "IN1": qs_g1 = {a: math.sqrt(M * (a ** (-1 / M) - 1)) for a in ALPHAS}; q_in1 = qs
        if name == "NA4": qs_g = {a: math.sqrt(-math.log(a)) for a in ALPHAS}
        variants = [(name, qs)] + ([("G1", qs_g1)] if name == "IN1" else []) + ([("NA4G", qs_g)] if name == "NA4" else [])
        for vn, qd in variants:
            for a, q in qd.items():
                cov = s_te <= q; res[f"{vn}|{a}|cover"] = float(cov.mean()); res[f"{vn}|{a}|radius"] = float(np.mean(q * stt))
                res[f"{vn}|{a}|cls_cover"] = np.array([cov[cls == k].mean() if np.any(cls == k) else np.nan for k in range(6)])
            s_det = abs(Y[None, :] + amp * g[None, :] - ct[None, :]) / stt[None, :]
            q = qd[0.01]
            res[f"{vn}|0.01|pd_cls"] = np.array([[np.mean(s_det[i, cls == k] > q) if np.any(cls == k) else np.nan for k in range(6)]
                                                  for i in range(len(SCR_DB))])
    # exact law per CNR class for IN1 (J2)
    r, rho = rec["r"], rec["rho1"]
    for a in ALPHAS:
        pred = []
        for k in range(6):
            sel = cls == k
            pred.append(np.nan if not np.any(sel) else coverage(cov_matrix(M, rho, float(np.mean(cnr[sel]))), M, r, q_in1[a]))
        res[f"IN1|{a}|cls_pred"] = np.array(pred)
    res["cls_n"] = np.bincount(cls, minlength=6); res["cls_mean_cnr_db"] = np.array([10 * np.log10(np.mean(cnr[cls == k])) if np.any(cls == k) else np.nan for k in range(6)])
    res["G_IN_db"] = np.array([10 * np.log10((1 + c) / (1 + abs(r) ** 2 + c * (1 - abs(r) ** 2))) if np.isfinite(c) else np.nan
                               for c in 10 ** (res["cls_mean_cnr_db"] / 10)])
    tmp = path + ".tmp.npz"
    np.savez_compressed(tmp, **res, rec=json.dumps({k: (str(v) if isinstance(v, complex) else v) for k, v in rec.items()}),
                        scr_db=SCR_DB, seconds=time.time() - t0)
    os.replace(tmp, path); return path


def j4(data):
    """Descriptive: models from meas_0 (rotation-1 splits, station 1, Rx 0); test on meas_5_int_C frames 67-99."""
    path = os.path.join(OUT, "j4_interference.npz")
    if os.path.exists(path): return path
    Z0 = profiles(os.path.join(data, "meas_0_ref.mat"), 1, 0); Z5 = profiles(os.path.join(data, "meas_5_int_C.mat"), 1, 0)
    Xtr, _, _, _ = episodes(Z0, THIRDS["A"]); Xca, _, _, _ = episodes(Z0, THIRDS["B"])
    Xtr = Xtr[np.random.default_rng(4).choice(len(Xtr), 20000, replace=False)]
    f, rec = fits_for(Xtr)
    Xte, _, fte, _ = episodes(Z5, THIRDS["C"])
    P5 = np.abs(Z5) ** 2; tot = P5[12:243].sum(0)                                        # bins 20-250 of original indexing
    hit = tot > 2 * np.median(tot, axis=0, keepdims=True)                                  # (chirp, frame)
    ychirp = np.concatenate([np.full(len(BINS), EP * e + EP - 1) for f_ in THIRDS["C"] for e in range(7)])
    yhit = hit[ychirp, fte]; res = {"hit_rate": float(hit[:, list(THIRDS["C"])].mean())}
    for name in ("IN1", "NA1", "NA4", "U", "CA16"):
        (cc, sc), (ct, stt) = f[name](Xca[:, :-1]), f[name](Xte[:, :-1])
        s_cal = abs(Xca[:, -1] - cc) / sc; s_te = abs(Xte[:, -1] - ct) / stt
        for a in ALPHAS:
            cov = s_te <= conformal_quantile(s_cal, a)
            res[f"{name}|{a}|clean"] = float(cov[~yhit].mean()); res[f"{name}|{a}|hit"] = float(cov[yhit].mean())
    np.savez_compressed(path, **res, n_hit=int(yhit.sum()), n_clean=int((~yhit).sum())); return path


if __name__ == "__main__":
    ap = argparse.ArgumentParser(); ap.add_argument("--data", required=True); ap.add_argument("--workers", type=int, default=6)
    a = ap.parse_args()
    if not frozen(): sys.exit("PROTOCOL_JKU.md does not match its hash.")
    os.makedirs(OUT, exist_ok=True); os.environ["OPENBLAS_NUM_THREADS"] = "4"
    json.dump(dict(started=time.strftime("%Y-%m-%d %H:%M:%S"), protocol_sha=open(os.path.join(HERE, "PROTOCOL_JKU.sha256")).read().split()[0],
                   script_sha=hashlib.sha256(open(__file__, "rb").read()).hexdigest(), gpu=os.environ.get("INARCP_GPU")),
              open(os.path.join(OUT, f"manifest_{int(time.time())}.json"), "w"), indent=1)
    from concurrent.futures import ProcessPoolExecutor
    jobs = [(a.data, s, rx, rot) for s in (1, 2) for rx in RX for rot in (1, 2, 3)]
    with ProcessPoolExecutor(a.workers) as ex:
        futs = [ex.submit(j4, a.data)] + [ex.submit(unit, j) for j in jobs]
        for fu in futs: print("saved", os.path.basename(fu.result()), flush=True)
