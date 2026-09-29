"""Quick look at unit files of a run (development inspection only)."""
import sys, glob, json
import numpy as np
run = sys.argv[1]; a = sys.argv[2] if len(sys.argv) > 2 else "0.1"
for f in sorted(glob.glob(f"results/{run}/unit_*.npz")):
    d = np.load(f); base = d[f"IN1|{a}|radius"].mean()
    print(f, "seconds", round(float(d["seconds"]), 1), "n", d["n"])
    for k in sorted(k for k in d.files if k.endswith(f"|{a}|cover")):
        nm = k.split("|")[0]
        print(f"   {nm:5s} cover {d[k].mean():.3f} radius/IN1 {d[nm + '|' + a + '|radius'].mean() / base:.3f}")
    print("  ", json.loads(str(d["fit_record"]))["na1"])
