"""Development gate D1: does noise-aware + AR(p) clutter (NA-AR(p)) combine the C3 and C4 gains?
(0) synthetic unit check: reflection->AR->correlation vs simulated AR(2) autocorrelation.
(1) IPIX, m=16, alpha in {.1,.01}: AR(p) conditional-innovation IN (best of V2c) vs NA-AR(p), p in {1,2,4}."""
import sys, os, math, json
sys.path.insert(0, os.path.dirname(os.path.dirname(__file__)))
import numpy as np
from methods import reflection_to_ar, arp_corr, fit_mixture_arp, NoiseAwareGeneral, conformal_quantile

rng = np.random.default_rng(5)
a = reflection_to_ar(np.array([0.9 * np.exp(0.4j), -0.5 * np.exp(-0.2j)]))
x = np.zeros(400000, complex); e = (rng.standard_normal(400000) + 1j * rng.standard_normal(400000)) / np.sqrt(2)
for t in range(2, len(x)): x[t] = a[0] * x[t - 1] + a[1] * x[t - 2] + e[t]
x = x[1000:]; emp = np.array([np.mean(x[k:] * np.conj(x[:len(x) - k])) for k in range(4)]); emp /= emp[0]
print("(0) AR(2) corr lags 0-3 theory:", np.round(arp_corr(4, a)[:, 0], 3), " simulated:", np.round(emp, 3))

from ipix import FILES, load, episodes
from v2b_ipix_within import texture_proxy, T, t1, t2, GAP, STRIDE
from v2c_arp_diagnosis import fit_arp, center_scale

m = 16
rows = []
for num in FILES:
    d = load(num)
    for pol, z in d["z"].items():
        import v2b_ipix_within as v2b; v2b.M = m
        Xtr, _, _ = episodes(z, 0, t1 - GAP, m, STRIDE); Xca, _, _ = episodes(z, t1, t2 - GAP, m, STRIDE)
        Xte, st, bt = episodes(z, t2, T, m, STRIDE)
        tex = texture_proxy(z, st, bt); qb = np.digitize(tex, np.quantile(tex, [.2, .4, .6, .8]))
        for p in (1, 2, 4):
            ap = fit_arp(Xtr, p); c1, s1 = center_scale(Xca, ap); c2, s2 = center_scale(Xte, ap)
            R, nu, w, res = fit_mixture_arp(Xtr, p)
            na = NoiseAwareGeneral(R, nu); n1, t1s, _ = na.center_scale(Xca[:, :-1]); n2, t2s, _ = na.center_scale(Xte[:, :-1])
            for alpha in (0.1, 0.01):
                for name, cc, sc, ct, stt in (("AR-IN", c1, s1, c2, s2), ("NA-AR", n1, t1s, n2, t2s)):
                    q = conformal_quantile(abs(Xca[:, -1] - cc) / sc, alpha)
                    cov = abs(Xte[:, -1] - ct) <= q * stt
                    rows.append(dict(file=num, pol=pol, p=p, alpha=alpha, method=name, cover=float(cov.mean()),
                                     by=[float(cov[qb == b].mean()) for b in range(5)], radius=float((q * stt).mean()),
                                     nu=nu, converged=bool(res.success)))
    print("done", num, flush=True)
json.dump(rows, open(os.path.join(os.path.dirname(__file__), "d1_results.json"), "w"), indent=1)
base = {(r["file"], r["pol"], r["alpha"]): r["radius"] for r in rows if r["method"] == "AR-IN" and r["p"] == 1}
for alpha in (0.1, 0.01):
    print(f"\nalpha={alpha} (radius relative to AR(1)-IN, geometric mean over 28 session-channels)")
    for p in (1, 2, 4):
        for meth in ("AR-IN", "NA-AR"):
            rs = [r for r in rows if r["alpha"] == alpha and r["p"] == p and r["method"] == meth]
            rel = np.array([r["radius"] / base[(r["file"], r["pol"], alpha)] for r in rs])
            by = np.array([r["by"] for r in rs])
            print(f"  p={p} {meth}: marginal {np.mean([r['cover'] for r in rs]):.3f} (min {min(r['cover'] for r in rs):.3f}) | "
                  f"by texture {np.round(by.mean(0),3)} | radius {np.exp(np.log(rel).mean()):.3f} "
                  f"(best {rel.min():.3f}, worst {rel.max():.3f}) | nonconverged {sum(not r['converged'] for r in rs)}")
