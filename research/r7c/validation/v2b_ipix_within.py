"""Gate V2b (real data, all 14 IPIX sessions x 2 like-pol channels): within-session evaluation.
Time thirds (train | cal | test) with 2 s gaps. Texture proxy for evaluation only: mean power in
the same range bin over +/-1024 pulses around the episode, excluding the episode's own pulses."""
import sys, os, math, json
sys.path.insert(0, os.path.dirname(os.path.dirname(__file__)))
import numpy as np
from ipix import FILES, load, episodes
from methods import (fit_ols, innovation_scale, fit_mixture_model, NoiseAware, conformal_quantile)

M, STRIDE, GAP, HALF = 8, 256, 2000, 1024
T = 131072; t1, t2 = T // 3, 2 * T // 3


def texture_proxy(z, starts, bins):
    P = np.abs(z) ** 2
    cs = np.vstack([np.zeros((1, P.shape[1])), np.cumsum(P, 0)])
    lo = np.clip(starts - HALF, 0, T); hi = np.clip(starts + M + 1 + HALF, 0, T)
    tot = cs[hi, bins] - cs[lo, bins] - (cs[starts + M + 1, bins] - cs[starts, bins])
    return tot / (hi - lo - (M + 1))


def run(alpha):
    rows = []
    for num in FILES:
        d = load(num)
        for pol, z in d["z"].items():
            Xtr, _, _ = episodes(z, 0, t1 - GAP, M, STRIDE)
            Xca, _, _ = episodes(z, t1, t2 - GAP, M, STRIDE)
            Xte, st, bt = episodes(z, t2, T, M, STRIDE)
            tex = texture_proxy(z, st, bt)
            qb = np.digitize(tex, np.quantile(tex, [.2, .4, .6, .8]))
            r = fit_ols(Xtr)
            rho_n, nu_n, _ = fit_mixture_model(Xtr)
            res = {}
            # IN-ARCP and its closed-form Gaussian plug-in (F(2,2m))
            s_c = innovation_scale(Xca[:, :-1], r); s_t = innovation_scale(Xte[:, :-1], r)
            sc_c = abs(Xca[:, -1] - r * Xca[:, -2]) / s_c; sc_t = abs(Xte[:, -1] - r * Xte[:, -2]) / s_t
            q = conformal_quantile(sc_c, alpha)
            res["IN-ARCP"] = (sc_t <= q, q * s_t)
            qg = math.sqrt(M * (alpha ** (-1 / M) - 1))
            res["Gauss plug-in (IN)"] = (sc_t <= qg, qg * s_t)
            # Mondrian IN-ARCP on history-scale quintiles
            e = np.quantile(s_c, [.2, .4, .6, .8]); qm = [conformal_quantile(sc_c[np.digitize(s_c, e) == b], alpha) for b in range(5)]
            qq = np.array(qm)[np.digitize(s_t, e)]; res["IN-ARCP Mondrian"] = (sc_t <= qq, qq * s_t)
            # noise-aware
            na = NoiseAware(M, rho_n, nu_n)
            cc, scc, _ = na.center_scale(Xca[:, :-1]); ct, sct, _ = na.center_scale(Xte[:, :-1])
            nc = abs(Xca[:, -1] - cc) / scc; nt = abs(Xte[:, -1] - ct) / sct
            qn = conformal_quantile(nc, alpha); res["NA-IN-ARCP"] = (nt <= qn, qn * sct)
            qe = math.sqrt(-math.log(alpha)); res["NA Gauss plug-in"] = (nt <= qe, qe * sct)
            # weak baselines
            ru = abs(Xca[:, -1] - r * Xca[:, -2]); rt = abs(Xte[:, -1] - r * Xte[:, -2])
            qu = conformal_quantile(ru, alpha); res["unnormalized CP"] = (rt <= qu, np.full(len(rt), qu))
            for name, (cov, rad) in res.items():
                by = [float(cov[qb == b].mean()) for b in range(5)]
                rows.append(dict(file=num, pol=pol, method=name, alpha=alpha, cover=float(cov.mean()),
                                 by_texture=by, radius=float(rad.mean()),
                                 rho_ols=[r.real, r.imag], rho_mix=[rho_n.real, rho_n.imag], nu=nu_n))
        print(f"done file {num}", flush=True)
    return rows


if __name__ == "__main__":
    out = []
    for a in (0.1, 0.01):
        out += run(a)
    path = os.path.join(os.path.dirname(__file__), "v2b_results.json")
    json.dump(out, open(path, "w"), indent=1)
    import collections
    for a in (0.1, 0.01):
        print(f"\n=== alpha={a}: averages over 28 session-channels ===")
        g = collections.defaultdict(list)
        for r_ in out:
            if r_["alpha"] == a: g[r_["method"]].append(r_)
        base = {(r_["file"], r_["pol"]): r_["radius"] for r_ in g["IN-ARCP"]}
        for name, rs in g.items():
            by = np.array([x["by_texture"] for x in rs]); cov = np.array([x["cover"] for x in rs])
            spread = by.max(1) - by.min(1); worst = np.abs(by - (1 - a)).max(1)
            rel = np.array([x["radius"] / base[(x["file"], x["pol"])] for x in rs])
            print(f"  {name:20s} marginal {cov.mean():.3f} (min {cov.min():.3f}) | by texture quintile {np.round(by.mean(0),3)}"
                  f" | spread mean {spread.mean():.3f} | worst dev mean {worst.mean():.3f} | radius/IN-ARCP {np.exp(np.log(rel).mean()):.3f}")
