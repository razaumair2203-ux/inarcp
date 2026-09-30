"""Same-order comparison of noise-aware (NA) vs innovation-normalized (IN) discs, confirmatory rotations 2-3.
Run from 02_paper_repo_inarcp/research/r7c/study:  python <path>/na_vs_in.py
Uses the repo day-cluster bootstrap (analyze.boot), 10,000 resamples, seed 20260929. Reads unit_*.npz only; writes nothing.
Check: IN4/IN1 at m=16, 0.90 reproduces Table 1 (0.845 [0.805, 0.905])."""
import sys, os, glob
sys.path.insert(0, os.getcwd()); sys.path.insert(0, os.path.dirname(os.getcwd()))
import numpy as np
from ipix import FILES
from analyze import boot
rng = np.random.default_rng(20260929)
units = {}
for p in sorted(glob.glob("results/confirmatory/unit_*.npz")):
    _, num, pol, rot, m = os.path.basename(p)[:-4].split("_"); num=int(num); m=int(m[1:])
    if int(rot[3:]) not in (2, 3): continue
    d = np.load(p)
    for a in (0.1, 0.01):
        for num_m, den_m in (("NA4","IN4"),("NA2","IN2"),("NA1","IN1"),("IN4","IN1")):
            r = d[f"{num_m}|{a}|radius"].mean()/d[f"{den_m}|{a}|radius"].mean()
            units.setdefault((m,a,num_m,den_m), []).append((FILES[num][1], r))
for k, L in sorted(units.items()):
    est, lo, hi = boot(L, lambda U: float(np.exp(np.mean(np.log([u[1] for u in U])))), 10000, rng)
    print(f"m={k[0]:2d} 1-a={1-k[1]:.2f} {k[2]}/{k[3]}: {est:.3f} [{lo:.3f}, {hi:.3f}]  n={len(L)}")
