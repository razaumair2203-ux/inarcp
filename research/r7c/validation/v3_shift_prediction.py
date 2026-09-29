"""Gate V3 (real data): can the exact fitted-coefficient score law PREDICT cross-session coverage?
For each ordered pair (A -> B), like0 channel, m=8, AR(1) IN-ARCP (stationary initial term, as in the
theory): fit r and calibrate q_hat on session A; observe coverage on session B's test third.
Prediction (uses only B's TRAINING third, never its test outcomes): fit B's clutter+noise model
(rho_B, nu_B, texture weights w_B) and compute  sum_g w_B[g] * G_{c_g}(q_hat; r_A)  with the exact
complex quadratic-form law. Compare with the naive prediction 1 - alpha."""
import sys, os, math, json
sys.path.insert(0, os.path.dirname(os.path.dirname(__file__)))
import numpy as np
from ipix import FILES, load, episodes
from methods import fit_ols, innovation_scale, fit_mixture_model, conformal_quantile
from cgauss import coverage, cov_matrix
from v2b_ipix_within import T, t1, t2, GAP, STRIDE

M, ALPHA = 8, 0.1
CG = np.logspace(-2, 5, 50)
S = {}
for num in FILES:
    z = load(num)["z"]["like0"]
    Xtr, _, _ = episodes(z, 0, t1 - GAP, M, STRIDE)
    Xca, _, _ = episodes(z, t1, t2 - GAP, M, STRIDE)
    Xte, _, _ = episodes(z, t2, T, M, STRIDE)
    rho, nu, w = fit_mixture_model(Xtr, CG)
    S[num] = dict(Xca=Xca, Xte=Xte, r=fit_ols(Xtr), rho=rho, nu=nu, w=w)
    print(f"file {num}: r_ols={S[num]['r']:.3f} rho_mix={rho:.3f} |rho|={abs(rho):.3f} nu={nu:.3g}", flush=True)


def score(X, r):
    return abs(X[:, -1] - r * X[:, -2]) / innovation_scale(X[:, :-1], r)


rows = []
for a in FILES:
    A = S[a]; q = conformal_quantile(score(A["Xca"], A["r"]), ALPHA)
    for b in FILES:
        B = S[b]
        obs = float(np.mean(score(B["Xte"], A["r"]) <= q))
        keep = B["w"] > 1e-6
        pred = float(sum(wg * coverage(cov_matrix(M, B["rho"], cg), M, A["r"], q)
                         for cg, wg in zip(CG[keep], B["w"][keep])) / B["w"][keep].sum())
        rows.append(dict(cal=a, test=b, observed=obs, predicted=pred, same=a == b))
json.dump(rows, open(os.path.join(os.path.dirname(__file__), "v3_results.json"), "w"), indent=1)
o = np.array([r_["observed"] for r_ in rows]); p = np.array([r_["predicted"] for r_ in rows])
cross = np.array([not r_["same"] for r_ in rows])
print(f"\ncross-session pairs: {cross.sum()} | observed coverage range {o[cross].min():.3f}-{o[cross].max():.3f}")
print(f"  MAE exact prediction  {np.mean(abs(o-p)[cross]):.4f}  | MAE naive (1-alpha) {np.mean(abs(o-0.9)[cross]):.4f}")
print(f"  corr(pred, obs) {np.corrcoef(p[cross], o[cross])[0,1]:.3f} | pairs with obs < .85: {np.sum(o[cross]<.85)}, "
      f"flagged by pred < .85: {np.sum((p<.85)&(o<.85)&cross)} (false flags {np.sum((p<.85)&(o>=.85)&cross)})")
print(f"  same-session MAE exact {np.mean(abs(o-p)[~cross]):.4f}")
