"""EXPLORATORY: exact-law prediction of IN-ARCP per-look Pd after onset of a persistent Swerling-1 target
(Corollary 2 with the rank-one target covariance S*P*v v^H, v_t = exp(j w t) on the samples after onset), averaged
over the unit's fitted texture law (NA1 NPMLE on the training third), and compared with the measured per-look Pd of
R8-O at SCR = 10 dB, alpha = 0.01. Random Doppler is averaged over 16 equispaced w. Writes onset_theory.json."""
import sys, os, glob, json, math
HERE = os.path.dirname(os.path.abspath(__file__)); ROOT = os.path.dirname(HERE)
sys.path.insert(0, ROOT); sys.path.insert(0, os.path.join(ROOT, "study"))
import numpy as np
from ipix import load, episodes
from methods import fit_mixture_model, fit_ols, innovation_scale, conformal_quantile
from cgauss import coverage, ar1_corr
from run_study import BLOCKS, ROT, STRIDE
M, K, CG, SCR = 16, 8, np.logspace(-2, 5, 50), 10 ** (10 / 10)


def unit(p):
    b = os.path.basename(p)[2:-4].split("_"); num, pol, rot = int(b[0]), b[1], int(b[2][3:])
    z = load(num)["z"][pol]; tr, ca, _ = (BLOCKS[x] for x in ROT[rot])
    Xtr, _, _ = episodes(z, *tr, M, STRIDE); Xca, _, _ = episodes(z, *ca, M, STRIDE)
    r = fit_ols(Xtr); q = conformal_quantile(abs(Xca[:, -1] - r * Xca[:, -2]) / innovation_scale(Xca[:, :-1], r), 0.01)
    rho, nu, w = fit_mixture_model(Xtr, CG); keep = w > 1e-6; R = ar1_corr(M + 1, rho)
    oms = {"random": np.linspace(-np.pi, np.pi, 16, endpoint=False), "matched": [np.angle(r)], "opposite": [np.angle(r) + np.pi]}
    out = {}
    for dop, ws in oms.items():
        pd = np.zeros(K)
        for j in range(K):
            acc = 0.0
            for om in ws:
                v = np.zeros(M + 1, complex); pos = np.arange(M - j, M + 1)          # target in last j+1 samples
                v[pos] = np.exp(1j * om * np.arange(j + 1))
                for c, wg in zip(CG[keep], w[keep]):
                    S = c * R + np.eye(M + 1) + SCR * (c + 1) * np.outer(v, np.conj(v))
                    acc += wg * (1 - coverage(S, M, r, q))
            pd[j] = acc / (len(ws) * w[keep].sum())
        out[dop] = pd.tolist()
    d = np.load(p); i10 = int(np.argmin(abs(d["scr_db"] - 10)))
    meas = {dop: d[f"IN1|0.01|{dop}|look"][i10].tolist() for dop in oms}
    return dict(unit=os.path.basename(p), pred=out, meas=meas)


if __name__ == "__main__":
    from concurrent.futures import ProcessPoolExecutor
    P = sorted(glob.glob(os.path.join(ROOT, "study", "results", "onset", "o_*.npz")))
    with ProcessPoolExecutor(12) as ex: rows = list(ex.map(unit, P))
    json.dump(rows, open(os.path.join(HERE, "onset_theory.json"), "w"))
    for dop in ("random", "matched", "opposite"):
        pr = np.mean([x["pred"][dop] for x in rows], 0); me = np.mean([x["meas"][dop] for x in rows], 0)
        mae = np.mean([np.abs(np.array(x["pred"][dop]) - np.array(x["meas"][dop])) for x in rows])
        print(f"{dop:8s} pred " + " ".join(f"{v:.3f}" for v in pr)); print(f"{'':8s} meas " + " ".join(f"{v:.3f}" for v in me) + f"  | MAE per unit x look {mae:.3f}")
