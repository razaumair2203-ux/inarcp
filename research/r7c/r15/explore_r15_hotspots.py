"""EXPLORATORY (post hoc, after the R15 outcomes): where do the conformal exceedances at alpha = 1e-4 of the dwell and
Doppler statistics fall on NetRAD? Recomputes the R12 Part L dwell statistics (frozen code) for chosen units and reports
exceedances by range cell and by 1-s time block of the test third. Not part of PROTOCOL_R15.
Usage: python explore_r15_hotspots.py 1450_16:3 1128_12:3 ..."""
import sys, os
HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)
import numpy as np
import run_r15_netrad as R
from run_study import STRIDE
import run_study
from ipix import episodes
from methods import fit_ols, innovation_scale

A = 1e-4
for arg in sys.argv[1:]:
    tag, rot = arg.split(":"); rot = int(rot)
    d = R.load(tag); z = d["z"]; T, B = z.shape; run_study.T = T
    BL = R.blocks(T); tr, ca, te = (BL[b] for b in R.ROT[rot])
    Xtr, _, _ = episodes(z, *tr, R.M, STRIDE)
    r = fit_ols(Xtr); a4 = R.fit_arp(Xtr, R.R12.P4); W = R.R12.steer_whitened(a4)
    Dc, stc, bc = R.R12.dense_segments(z, ca, R.M + R.K, R.M + R.K, margin=48)
    Dt, stt, btt = R.R12.dense_segments(z, te, R.M + R.K, R.M + R.K, margin=48)
    Sc = R.R12.coh_stats(Dc, a4, W, fixed=True); St = R.R12.coh_stats(Dt, a4, W, fixed=True)
    Xc, _, _ = episodes(z, *ca, R.M, R.M + 1); Xt, s1, b1 = episodes(z, *te, R.M, R.M + 1)
    in1 = lambda X: abs(X[:, -1] - r * X[:, -2]) ** 2 / innovation_scale(X[:, :-1], r) ** 2
    print(f"\n{tag} rot{rot} ({d['pol']}, hit rate {d['hit'].mean():.3f}), test pulses {te}, cells {B}")
    for name, vc, vt, st_, bi in (("D-IN4", Sc["D-IN4"], St["D-IN4"], stt, btt), ("PAMF-H(w)", Sc["PAMF-H(w)"], St["PAMF-H(w)"], stt, btt),
                                  ("P-ANMF", Sc["P-ANMF"], St["P-ANMF"], stt, btt), ("IN1", in1(Xc), in1(Xt), s1, b1)):
        q = R.R12.q_rank(vc, A); e = vt > q
        cells = np.bincount(bi[e], minlength=B); secs = np.bincount((st_[e] - te[0]) // 1000, minlength=(te[1] - te[0]) // 1000 + 1)
        top_c = np.argsort(cells)[::-1][:3]; top_s = np.argsort(secs)[::-1][:3]
        hits = d["hit"][st_[e][:, None] + np.arange(R.M + R.K)].any(1).mean() if e.any() else np.nan
        print(f"  {name:<10s} {e.sum():5d} exceedances of {len(e)} (Pfa/a {e.mean() / A:6.2f}); cells with most: "
              + ", ".join(f"{c}:{cells[c]}" for c in top_c) + f" (share {cells[top_c].sum() / max(e.sum(), 1):.2f}); 1-s blocks with most: "
              + ", ".join(f"{s}s:{secs[s]}" for s in top_s) + f" (share {secs[top_s].sum() / max(e.sum(), 1):.2f}); with a flagged hit {hits:.2f}")
