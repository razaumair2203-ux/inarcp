"""EXPLORATORY (R10 audit, after seeing that NA-AR(4) Nelder-Mead reached its 1500-iteration cap in 40 of 56 units):
does convergence matter? For every confirmatory unit, refit NA-AR(4) exactly as in the study (maxiter 1500), then restart
Nelder-Mead from that solution for up to 4500 further iterations. Report the log-likelihood gain per training episode and
the change in split-conformal radius and coverage (1-alpha = 0.90, 0.99) on the same test episodes.
Usage: INARCP_GPU=1 python explore_na4_convergence.py [--workers 6] -> r10/na4_convergence.json/.txt"""
import sys, os, json, glob, argparse
HERE = os.path.dirname(os.path.abspath(__file__)); ROOT = os.path.dirname(HERE)
sys.path.insert(0, ROOT); sys.path.insert(0, os.path.join(ROOT, "study"))
import numpy as np
from ipix import FILES, load, episodes
import methods
from methods import conformal_quantile, fit_mixture_arp, NoiseAwareGeneral
from run_study import BLOCKS, ROT, STRIDE
M = 16


def unit(args):
    num, pol, rot = args
    z = load(num)["z"][pol]; tr, ca, te = (BLOCKS[b] for b in ROT[rot])
    Xtr, _, _ = episodes(z, *tr, M, STRIDE); Xca, _, _ = episodes(z, *ca, M, STRIDE); Xte, _, _ = episodes(z, *te, M, STRIDE)
    R1, nu1, _, res1 = fit_mixture_arp(Xtr, 4)
    # restart from res1.x: temporarily wrap minimize so the start is res1.x
    from scipy import optimize
    orig = optimize.minimize

    def restart(fun, x0, **kw):
        kw["options"] = dict(kw["options"], maxiter=4500); return orig(fun, res1.x, **kw)
    optimize.minimize = restart
    try:
        R2, nu2, _, res2 = fit_mixture_arp(Xtr, 4)
    finally:
        optimize.minimize = orig
    out = dict(unit=f"{num}_{pol}_rot{rot}", day=FILES[num][1], conv1=bool(res1.success), conv2=bool(res2.success),
               nit2=int(res2.nit), dll_per_ep=float((res1.fun - res2.fun) / len(Xtr)))
    for tag, (R, nu) in (("orig", (R1, nu1)), ("long", (R2, nu2))):
        na = NoiseAwareGeneral(R, nu)
        cc, sc = na.center_scale(Xca[:, :-1])[:2]; ct, st = na.center_scale(Xte[:, :-1])[:2]
        s_cal = abs(Xca[:, -1] - cc) / sc; s_te = abs(Xte[:, -1] - ct) / st
        for a in (0.1, 0.01):
            q = conformal_quantile(s_cal, a); out[f"{tag}|{a}|radius"] = float(np.mean(q * st)); out[f"{tag}|{a}|cover"] = float(np.mean(s_te <= q))
    return out


if __name__ == "__main__":
    ap = argparse.ArgumentParser(); ap.add_argument("--workers", type=int, default=6); a = ap.parse_args()
    from concurrent.futures import ProcessPoolExecutor
    jobs = [(f, pol, r) for f in FILES for pol in ("like0", "like1") for r in (2, 3)]
    with ProcessPoolExecutor(a.workers) as ex: rows = list(ex.map(unit, jobs))
    json.dump(rows, open(os.path.join(HERE, "na4_convergence.json"), "w"), indent=1)
    L = []
    c1 = sum(r["conv1"] for r in rows); c2 = sum(r["conv2"] for r in rows)
    L.append(f"units {len(rows)}; converged at cap 1500: {c1}; converged after restart (+4500): {c2}")
    d = np.array([r["dll_per_ep"] for r in rows]); L.append(f"log-likelihood gain per training episode: median {np.median(d):.2e}, max {d.max():.2e}")
    for al in (0.1, 0.01):
        rr = np.array([r[f"long|{al}|radius"] / r[f"orig|{al}|radius"] for r in rows])
        L.append(f"1-alpha={1 - al:g}: radius ratio long/orig geo-mean {np.exp(np.mean(np.log(rr))):.4f} (range {rr.min():.4f}..{rr.max():.4f}); "
                 f"coverage orig {np.mean([r[f'orig|{al}|cover'] for r in rows]):.4f} long {np.mean([r[f'long|{al}|cover'] for r in rows]):.4f}")
    print("\n".join(L)); open(os.path.join(HERE, "na4_convergence.txt"), "w").write("\n".join(L) + "\n")
