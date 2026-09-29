"""Endpoints of PROTOCOL_BASELINES.md. Writes baselines_summary.txt/.json."""
import os, glob, json
import numpy as np
HERE = os.path.dirname(os.path.abspath(__file__)); RES = os.path.join(os.path.dirname(HERE), "study", "results", "baselines")
U = [np.load(p) for p in sorted(glob.glob(os.path.join(RES, "b_*.npz")))]; days = [str(d["day"]) for d in U]
T = {os.path.basename(p)[2:-4]: np.load(p) for p in sorted(glob.glob(os.path.join(RES, "t_*.npz")))}
rng = np.random.default_rng(20260930); lines = []; out = {}
log = lambda s: (print(s), lines.append(s))


def gm_boot(vals):
    vals = np.log(np.asarray(vals)); ud = sorted(set(days)); by = {u: vals[[d == u for d in days]] for u in ud}
    bs = [np.exp(np.mean(np.concatenate([by[u] for u in rng.choice(ud, len(ud))]))) for _ in range(10000)]
    return float(np.exp(vals.mean())), *map(float, np.percentile(bs, [2.5, 97.5]))


log(f"B1/B2 within-session units: {len(U)}; transfer days: {len(T)}")
for a in (0.1, 0.01):
    log(f"\n=== 1-alpha = {1-a:g} ===")
    r = gm_boot([d[f"NA4K|{a}|radius"].mean() / d[f"NA4|{a}|radius"].mean() for d in U])
    out[f"B1|{a}"] = dict(ratio=r, cover_NA4=float(np.mean([d[f'NA4|{a}|cover'].mean() for d in U])),
                          cover_NA4K=float(np.mean([d[f'NA4K|{a}|cover'].mean() for d in U])),
                          maxdev_NA4=float(np.mean([d[f'NA4|{a}|maxdev'] for d in U])), maxdev_NA4K=float(np.mean([d[f'NA4K|{a}|maxdev'] for d in U])))
    o = out[f"B1|{a}"]
    log(f"B1 NA4-K / NA4 radius (GM): {r[0]:.4f} [{r[1]:.4f}, {r[2]:.4f}] | coverage NA4 {o['cover_NA4']:.4f} NA4-K {o['cover_NA4K']:.4f} "
        f"| max dev NA4 {o['maxdev_NA4']:.3f} NA4-K {o['maxdev_NA4K']:.3f}")
    for g in ("0.005", "0.02"):
        cov = np.mean([d[f"ACI{g}|{a}|cover"].mean() for d in U]); spl = np.mean([d[f"IN1|{a}|cover"].mean() for d in U])
        rr = gm_boot([np.nanmean(d[f"ACI{g}|{a}|radius"]) / d[f"IN1|{a}|radius"].mean() for d in U])
        inf = np.mean([float(d[f"ACI{g}|{a}|inf_frac"]) for d in U])
        md = (np.mean([d[f"ACI{g}|{a}|maxdev"] for d in U]), np.mean([d[f"IN1|{a}|maxdev"] for d in U]))
        out[f"B2in|{g}|{a}"] = dict(cover=float(cov), split=float(spl), radius_ratio=rr, inf_frac=float(inf), maxdev=md)
        log(f"B2 within ACI g={g}: coverage {cov:.4f} vs split {spl:.4f} | radius ratio (finite) {rr[0]:.3f} [{rr[1]:.3f},{rr[2]:.3f}] "
            f"| infinite-region fraction {inf:.4f} | max dev {md[0]:.3f} vs {md[1]:.3f}")
    for k in ("IN1", "ACI0.005", "ACI0.02"):
        covs = {d: float(t[f"{k}|{a}|cover"].mean()) for d, t in T.items()}
        rad = [float(np.nanmean(t[f"{k}|{a}|radius"]) / t[f"IN1|{a}|radius"].mean()) for t in T.values()]
        md = np.mean([float(t[f"{k}|{a}|maxdev"]) for t in T.values()])
        out[f"B2tr|{k}|{a}"] = dict(per_day=covs, mean=float(np.mean(list(covs.values()))), worst=float(min(covs.values())),
                                    radius_ratio_mean=float(np.mean(rad)), maxdev=float(md))
        log(f"B2 transfer {k:9s}: mean coverage {np.mean(list(covs.values())):.4f} worst day {min(covs.values()):.4f} "
            f"| radius vs split {np.mean(rad):.3f} | max dev {md:.3f} | per day " + " ".join(f"{v:.3f}" for v in covs.values()))
json.dump(out, open(os.path.join(HERE, "baselines_summary.json"), "w"), indent=1)
open(os.path.join(HERE, "baselines_summary.txt"), "w").write("\n".join(lines) + "\n")
