"""Summarize synthetic_results.json: coverage by true-CNR bin (mean over replications, MC se),
IN1 simulated vs exact (Corollary 1), radius ratios."""
import json, os
import numpy as np
HERE = os.path.dirname(os.path.abspath(__file__))
rows = json.load(open(os.path.join(HERE, "synthetic_results.json")))
bins = ["<0", "0-5", "5-10", "10-15", "15-20", ">20"]
for arm in ("sirv", "noise"):
    for m in (8, 16):
        rs = [r for r in rows if r["arm"] == arm and r["m"] == m]
        print(f"\n== arm={arm} m={m} ({len(rs)} reps) | true-CNR bins (dB) {bins}")
        for k in ("IN1", "MON", "NA1", "NA1G"):
            if k not in rs[0]: continue
            by = np.array([r[k]["by"] for r in rs]); cov = np.array([r[k]["cover"] for r in rs])
            rad = np.array([r[k]["radius"] / r["IN1"]["radius"] for r in rs])
            print(f"  {k:5s} marginal {cov.mean():.4f}+-{cov.std()/np.sqrt(len(cov)):.4f} | by bin {np.round(by.mean(0),3)}"
                  f" (se<= {by.std(0).max()/np.sqrt(len(rs)):.4f}) | radius/IN1 {rad.mean():.3f}")
        ex = np.array([r["IN1_exact_by"] for r in rs]); sim = np.array([r["IN1"]["by"] for r in rs])
        d = sim - ex
        print(f"  IN1 exact  by bin {np.round(ex.mean(0),3)} | sim-exact mean {np.round(d.mean(0),4)} "
              f"| |t| max {np.max(abs(d.mean(0))/(d.std(0)/np.sqrt(len(rs)))):.2f}")
        if arm == "noise":
            f = np.array([r["na_fit"] for r in rs])
            print(f"  NA fit: |rho| {np.mean(np.hypot(f[:,0],f[:,1])):.4f} (true {abs(0.93):.2f}), nu {f[:,2].mean():.4f} (sd {f[:,2].std():.4f})")
