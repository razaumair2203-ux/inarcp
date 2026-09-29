"""Q4 / C5 on the confirmatory day-transfer units: exact prediction of IN1 coverage on each held-out day.
Pooled other-day fit r and calibration threshold q_hat are recomputed deterministically exactly as in
run_study.transfer_unit (block A train, block B calibration). Prediction uses ONLY the held-out day's
training thirds (block A): per session-channel clutter+noise NPMLE fit (rho, nu, texture weights), then
sum_g w_g G_{c_g R + I}(q_hat; r), averaged over session-channels weighted by test-episode counts.
Observed coverage comes from the saved transfer_*.npz (block C of the held-out day)."""
import sys, os, json
HERE = os.path.dirname(os.path.abspath(__file__)); sys.path.insert(0, os.path.dirname(HERE))
import numpy as np
from ipix import FILES, load, episodes
from methods import innovation_scale, conformal_quantile, fit_mixture_model
from cgauss import coverage, cov_matrix
from run_study import BLOCKS, STRIDE

CG = np.logspace(-2, 5, 50)
data = {n: load(n)["z"] for n in FILES}
days = sorted({d for _, d, _, _ in FILES.values()})
rows = []
for m in (8, 16):
    # per session-channel model from block A (training third), fitted once per m
    models = {}
    for n in FILES:
        for pol, z in data[n].items():
            Xa, _, _ = episodes(z, *BLOCKS["A"], m, STRIDE)
            rho, nu, w = fit_mixture_model(Xa, CG)
            models[(n, pol)] = (rho, w, len(episodes(z, *BLOCKS["C"], m, STRIDE)[0]))
    for day in days:
        d = np.load(os.path.join(HERE, "results", "confirmatory", f"transfer_{day}_m{m}.npz"))
        r = complex(*json.loads(str(d["fit_record"]))["r_ols"])
        ca = np.concatenate([episodes(z, *BLOCKS["B"], m, STRIDE)[0]
                             for n, (_, dd, _, _) in FILES.items() if dd != day for z in data[n].values()])
        sc = abs(ca[:, -1] - r * ca[:, -2]) / innovation_scale(ca[:, :-1], r)
        for a in (0.1, 0.01):
            q = conformal_quantile(sc, a)
            preds, wts = [], []
            for (n, pol), (rho, w, nt) in models.items():
                if FILES[n][1] != day: continue
                k = w > 1e-6
                preds.append(sum(wg * coverage(cov_matrix(m, rho, cg), m, r, q) for cg, wg in zip(CG[k], w[k])) / w[k].sum())
                wts.append(nt)
            pred = float(np.average(preds, weights=wts)); obs = float(d[f"IN1|{a}|cover"].mean())
            rows.append(dict(m=m, day=day, alpha=a, predicted=pred, observed=obs))
            print(f"m={m:2d} {day} alpha={a}: predicted {pred:.4f} observed {obs:.4f}", flush=True)
json.dump(rows, open(os.path.join(HERE, "results", "confirmatory", "c5_transfer.json"), "w"), indent=1)
for a in (0.1, 0.01):
    R = [r for r in rows if r["alpha"] == a]; p = np.array([r["predicted"] for r in R]); o = np.array([r["observed"] for r in R])
    print(f"alpha={a}: MAE exact {np.mean(abs(p-o)):.4f} | MAE naive {np.mean(abs(o-(1-a))):.4f} | corr {np.corrcoef(p,o)[0,1]:.3f} | n={len(R)}")
