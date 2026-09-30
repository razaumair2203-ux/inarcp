"""R10 Part R, endpoint R2 (secondary, pre-specified): exact-law prediction of IN-ARCP's per-look Pd for ramped targets
(Corollary 2 with signature v_t = g_t e^{jw(t - t0)} on the look window), averaged over the unit's fitted texture law
(NA1 NPMLE on the training third) and 16 equispaced Dopplers, from the training and calibration thirds only.
Compared with the measured per-look Pd at SCR = 10 dB. Writes r10/theory_ramps.json/.txt."""
import sys, os, glob, json
HERE = os.path.dirname(os.path.abspath(__file__)); ROOT = os.path.dirname(HERE)
sys.path.insert(0, ROOT); sys.path.insert(0, os.path.join(ROOT, "study")); sys.path.insert(0, HERE)
import numpy as np
from ipix import load, episodes
from methods import fit_mixture_model, fit_ols, innovation_scale, conformal_quantile
from cgauss import coverage, ar1_corr
from run_study import BLOCKS, ROT, STRIDE
from run_r10 import ramp_profile, M, K
CG, SCR, OMS = np.logspace(-2, 5, 50), 10.0, np.linspace(-np.pi, np.pi, 16, endpoint=False)


def unit(p):
    b = os.path.basename(p)[2:-4].split("_"); num, pol, rot = int(b[0]), b[1], int(b[2][3:])
    z = load(num)["z"][pol]; tr, ca, _ = (BLOCKS[x] for x in ROT[rot])
    Xtr, _, _ = episodes(z, *tr, M, STRIDE); Xca, _, _ = episodes(z, *ca, M, STRIDE)
    r = fit_ols(Xtr); q = conformal_quantile(abs(Xca[:, -1] - r * Xca[:, -2]) / innovation_scale(Xca[:, :-1], r), 0.01)
    rho, nu, w = fit_mixture_model(Xtr, CG); keep = w > 1e-6; R = ar1_corr(M + 1, rho)
    d = np.load(p); out = {}
    for place in ("pre", "in"):
        for L in (1, 4, 8, 16):
            g, t0 = ramp_profile(L, place); pd = np.zeros(K)
            for j in range(K):
                pos = np.arange(j, j + M + 1); acc = 0.0
                for om in OMS:
                    v = g[pos] * np.exp(1j * om * (pos - t0))
                    for c, wg in zip(CG[keep], w[keep]):
                        S = c * R + np.eye(M + 1) + SCR * (c + 1) * np.outer(v, np.conj(v))
                        acc += wg * (1 - coverage(S, M, r, q))
                pd[j] = acc / (len(OMS) * w[keep].sum())
            i10 = int(np.argmin(abs(d["scr_db"] - 10)))
            out[f"{place}|L{L}"] = dict(pred=pd.tolist(), meas=d[f"R|{place}|L{L}|IN1|look"][i10].tolist())
    return dict(unit=os.path.basename(p), res=out)


if __name__ == "__main__":
    from concurrent.futures import ProcessPoolExecutor
    P = sorted(glob.glob(os.path.join(ROOT, "study", "results", "r10", "x_*.npz")))
    with ProcessPoolExecutor(12) as ex: rows = list(ex.map(unit, P))
    json.dump(rows, open(os.path.join(HERE, "theory_ramps.json"), "w"))
    L_, errs = [], []
    for key in rows[0]["res"]:
        pr = np.mean([x["res"][key]["pred"] for x in rows], 0); me = np.mean([x["res"][key]["meas"] for x in rows], 0)
        e = [np.abs(np.array(x["res"][key]["pred"]) - np.array(x["res"][key]["meas"])) for x in rows]; errs += e
        L_.append(f"{key:8s} pred " + " ".join(f"{v:.3f}" for v in pr)); L_.append(f"{'':8s} meas " + " ".join(f"{v:.3f}" for v in me) + f" | MAE {np.mean(e):.3f}")
    mae = float(np.mean(errs)); L_.append(f"R2: exact-law MAE per unit x look x L x placement = {mae:.3f} (expectation <= 0.03): {'OK' if mae <= 0.03 else 'FAILED'}")
    print("\n".join(L_)); open(os.path.join(HERE, "theory_ramps.txt"), "w").write("\n".join(L_) + "\n")
