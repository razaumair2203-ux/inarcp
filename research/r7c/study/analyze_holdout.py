"""Hold-out summary (#269 hi, #287 lo; one VV bin each): per method, geometric-mean radius ratio to IN1,
mean/min marginal coverage over 2 sessions x 3 rotations, per m and alpha. Small test sets (~165 episodes
per unit): binomial se of a 0.9 coverage estimate is ~0.023; treat as a directional check only."""
import os, glob, json
import numpy as np
from analyze import unit_stats, METHODS, ALPHAS

HERE = os.path.dirname(os.path.abspath(__file__))
rng = np.random.default_rng(1)
rows = []
for p in sorted(glob.glob(os.path.join(HERE, "results", "holdout", "unit_*.npz"))):
    _, name, _, rot, m = os.path.basename(p)[:-4].split("_")
    st, rec = unit_stats(p, rng=rng)
    for (mth, a), v in st.items():
        rows.append(dict(session=name, rot=int(rot[3:]), m=int(m[1:]), method=mth, alpha=a,
                         cover=float(v["cover"]), ratio=float(v["ratio"])))
json.dump(rows, open(os.path.join(HERE, "results", "holdout", "holdout_summary.json"), "w"), indent=1)
for m in (8, 16):
    for a in ALPHAS:
        print(f"\n== hold-out m={m} alpha={a} (6 units: 2 sessions x 3 rotations) ==")
        for mth in METHODS:
            U = [r for r in rows if r["m"] == m and r["alpha"] == a and r["method"] == mth]
            c = np.array([u["cover"] for u in U]); r = np.array([u["ratio"] for u in U])
            per = {s: np.exp(np.mean(np.log([u["ratio"] for u in U if u["session"] == s]))) for s in ("hi", "lo")}
            print(f"  {mth:5s} radius/IN1 {np.exp(np.log(r).mean()):.3f} (hi {per['hi']:.3f}, lo {per['lo']:.3f}) | cover {c.mean():.3f} (min {c.min():.3f})")
