"""EXPLORATORY (post hoc, after the R15 outcomes and the claim audit): attribution of the NetRAD 1e-4 conformal excess.
For every unit: flagged-pulse fraction in its calibration and test thirds, and the unit's Pfa/alpha at 1e-4 for each statistic;
then the pooled ratio with and without the units whose excess coincides with interference absent from their calibration third.
Not part of PROTOCOL_R15. Output: explore_r15_attribution_output.txt"""
import os, sys, glob
HERE = os.path.dirname(os.path.abspath(__file__)); ROOT = os.path.dirname(HERE)
sys.path.insert(0, HERE)
import numpy as np
from run_r15_netrad import blocks, ROT
from netrad import load

A = 1e-4
STATS = ("IN1", "IN4", "OS1_8", "NA4", "CA16", "OSraw", "D-IN4", "PAMF-H(w)", "P-ANMF(bin)", "P-ANMF", "ANMF-SCM(w)", "ANMF-FP(w)", "Clip-OS1")
out = []
U = {}
for f in sorted(glob.glob(os.path.join(ROOT, "study", "results", "r15", "n_*.npz"))):
    k = os.path.basename(f)[2:-4]; tag, rot = k[:7], int(k[-1])
    u = dict(np.load(f, allow_pickle=True)); h = load(tag)["hit"]
    BL = blocks(len(h)); tr, ca, te = (BL[b] for b in ROT[rot])
    u["fc"], u["ft"] = h[ca[0]:ca[1]].mean(), h[te[0]:te[1]].mean(); U[k] = u
out.append("EXPLORATORY. Per unit: flagged fraction in calibration / test third; Pfa/alpha at 1e-4 (conformal)")
out.append("unit          pol  cal%   test%  " + " ".join(f"{s[:10]:>10s}" for s in STATS))
for k, u in U.items():
    out.append(f"{k:<13s} {str(u['pol'])}  {100 * u['fc']:5.2f}  {100 * u['ft']:5.2f}  "
               + " ".join(f"{u[f'L|{s}|conf|{A}'][0] / u[f'L|{s}|conf|{A}'][1] / A:10.2f}" for s in STATS))


def pooled(keys, s):
    e = sum(U[k][f"L|{s}|conf|{A}"][0] for k in keys); n = sum(U[k][f"L|{s}|conf|{A}"][1] for k in keys)
    return e / n / A


allk = list(U)
clean_cal_bursty = [k for k, u in U.items() if u["fc"] == 0 and u["ft"] > 0]
out.append("")
out.append(f"units whose calibration third has no flagged pulse but whose test third has some: {clean_cal_bursty}")
for drop in (["1450_16_rot3", "1501_53_rot3"], ["1450_16_rot3", "1501_53_rot3", "1128_12_rot3"]):
    keep = [k for k in allk if k not in drop]
    out.append(f"pooled Pfa/alpha at 1e-4, all units vs without {drop}:")
    for s in STATS:
        out.append(f"  {s:<12s} {pooled(allk, s):6.2f} -> {pooled(keep, s):6.2f}")
txt = "\n".join(out)
print(txt)
open(os.path.join(HERE, "explore_r15_attribution_output.txt"), "w", encoding="utf8").write(txt + "\n")
