"""Analysis per PROTOCOL.md section 4. Reads results/<run>/unit_*.npz and transfer_*.npz.
Writes results/<run>/analysis.json and prints tables. Confirmatory = rotations 2, 3.
Usage: python analyze.py --run confirmatory [--boot 10000]"""
import sys, os, glob, json, argparse
HERE = os.path.dirname(os.path.abspath(__file__)); sys.path.insert(0, os.path.dirname(HERE))
import numpy as np
from ipix import FILES, load, episodes
from run_study import BLOCKS, ROT, STRIDE

METHODS = ["U", "RMS", "IN1", "G1", "IN2", "IN4", "MON", "NA1", "NA2", "NA4", "NA1G", "NA2G", "NA4G", "LS", "MLP"]
ALPHAS = (0.1, 0.01)


def unit_stats(path, window=1024, rng=None):
    d = np.load(path); tex = d[f"texture|{window}"]
    qb = np.digitize(tex, np.quantile(tex, [.2, .4, .6, .8])); counts = np.bincount(qb, minlength=5)
    out = {}
    for a in ALPHAS:
        base = d[f"IN1|{a}|radius"].mean()
        # MC-noise reference: ideal method, binomial quintile coverage at nominal
        sims = rng.binomial(counts[None, :], 1 - a, (2000, 5)) / counts[None, :]
        ref = np.abs(sims - (1 - a)).max(1).mean()
        for mth in METHODS:
            cov = d[f"{mth}|{a}|cover"]; rad = d[f"{mth}|{a}|radius"]
            by = np.array([cov[qb == b].mean() for b in range(5)])
            out[(mth, a)] = dict(cover=cov.mean(), by=by, maxdev=np.abs(by - (1 - a)).max(),
                                 ratio=rad.mean() / base, ref=ref)
    return out, json.loads(str(d["fit_record"]))


def noise_index(num, pol, rot, m, rec):
    z = load(num)["z"][pol]; tr = BLOCKS[ROT[rot][0]]
    X, _, _ = episodes(z, *tr, m, STRIDE)
    return rec["na1"]["nu"] / np.mean(np.abs(X) ** 2)


def boot(units, stat, B, rng):
    """Cluster bootstrap over days. units: list of (day, value-tuple); stat: list -> float."""
    days = sorted({u[0] for u in units}); by_day = {d: [u for u in units if u[0] == d] for d in days}
    est = stat(units); bs = []
    for _ in range(B):
        pick = rng.choice(days, len(days), replace=True)
        bs.append(stat([u for dd in pick for u in by_day[dd]]))
    lo, hi = np.percentile(bs, [2.5, 97.5])
    return float(est), float(lo), float(hi)


def main():
    ap = argparse.ArgumentParser(); ap.add_argument("--run", default="confirmatory")
    ap.add_argument("--boot", type=int, default=10000); ap.add_argument("--window", type=int, default=1024); a = ap.parse_args()
    rdir = os.path.join(HERE, "results", a.run); rng = np.random.default_rng(20260929)
    sfx = "" if a.window == 1024 else f"_w{a.window}"; cache = os.path.join(rdir, f"unit_stats_cache{sfx}.json")
    rows = []
    for p in sorted(glob.glob(os.path.join(rdir, "unit_*.npz"))):
        _, num, pol, rot, m = os.path.basename(p)[:-4].split("_")
        num, rot, m = int(num), int(rot[3:]), int(m[1:])
        st, rec = unit_stats(p, window=a.window, rng=rng)
        ni = noise_index(num, pol, rot, m, rec)
        for (mth, al), v in st.items():
            rows.append(dict(file=num, day=FILES[num][1], pol=pol, rot=rot, m=m, method=mth, alpha=al,
                             cover=float(v["cover"]), by=v["by"].tolist(), maxdev=float(v["maxdev"]),
                             ratio=float(v["ratio"]), ref=float(v["ref"]), noise_index=float(ni)))
    json.dump(rows, open(cache, "w"))
    res = {}
    for stage, rots in (("confirmatory", {2, 3}), ("development", {1})):
        for m in (8, 16):
            for al in ALPHAS:
                print(f"\n=== {stage} | m={m} | alpha={al} ===")
                print(f"{'method':6s} {'GM radius/IN1 [95% CI]':>28s} {'noisy':>7s} {'clean':>7s} {'cover':>6s} {'min':>6s} "
                      f"{'%<nom-.02':>9s} {'maxdev [CI]':>22s} {'ref':>6s}  texture-quintile curve")
                for mth in METHODS:
                    U = [r for r in rows if r["rot"] in rots and r["m"] == m and r["alpha"] == al and r["method"] == mth]
                    if not U: continue
                    items = [(u["day"], u) for u in U]
                    gm = boot(items, lambda L: np.exp(np.mean([np.log(x[1]["ratio"]) for x in L])), a.boot, rng)
                    md = boot(items, lambda L: np.mean([x[1]["maxdev"] for x in L]), a.boot, rng)
                    noisy = [u for u in U if u["noise_index"] > 0.01]; clean = [u for u in U if u["noise_index"] <= 0.01]
                    gmn = np.exp(np.mean([np.log(u["ratio"]) for u in noisy])) if noisy else np.nan
                    gmc = np.exp(np.mean([np.log(u["ratio"]) for u in clean])) if clean else np.nan
                    cov = np.array([u["cover"] for u in U]); curve = np.mean([u["by"] for u in U], 0)
                    ref = np.mean([u["ref"] for u in U])
                    print(f"{mth:6s} {gm[0]:8.3f} [{gm[1]:.3f},{gm[2]:.3f}]      {gmn:7.3f} {gmc:7.3f} {cov.mean():6.3f} {cov.min():6.3f} "
                          f"{np.mean(cov < 1 - al - 0.02):9.2f} {md[0]:.3f} [{md[1]:.3f},{md[2]:.3f}] {ref:6.3f}  {np.round(curve, 3)}")
                    res[f"{stage}|{m}|{al}|{mth}"] = dict(gm_ratio=gm, gm_noisy=float(gmn), gm_clean=float(gmc),
                                                          n_noisy=len(noisy), n_clean=len(clean), cover_mean=float(cov.mean()),
                                                          cover_min=float(cov.min()), maxdev=md, ref=float(ref), curve=curve.tolist())
    # day transfer
    for p in sorted(glob.glob(os.path.join(rdir, "transfer_*.npz"))):
        d = np.load(p); day, m = os.path.basename(p)[9:-4].rsplit("_m", 1)
        for al in ALPHAS:
            base = d[f"IN1|{al}|radius"].mean()
            res[f"transfer|{day}|{m}|{al}"] = {mth: dict(cover=float(d[f"{mth}|{al}|cover"].mean()),
                                                         ratio=float(d[f"{mth}|{al}|radius"].mean() / base)) for mth in METHODS}
    if any(k.startswith("transfer") for k in res):
        for m in ("8", "16"):
            for al in ALPHAS:
                ks = [k for k in res if k.startswith("transfer") and k.split("|")[2] == m and float(k.split("|")[3]) == al]
                if not ks: continue
                print(f"\n=== day transfer | m={m} | alpha={al} | {len(ks)} held-out days: mean cover (min) | mean radius/IN1")
                for mth in METHODS:
                    c = [res[k][mth]["cover"] for k in ks]; r = [res[k][mth]["ratio"] for k in ks]
                    print(f"  {mth:6s} {np.mean(c):.3f} ({np.min(c):.3f}) | {np.exp(np.mean(np.log(r))):.3f}")
    json.dump(res, open(os.path.join(rdir, f"analysis{sfx}.json"), "w"), indent=1)


if __name__ == "__main__":
    main()
