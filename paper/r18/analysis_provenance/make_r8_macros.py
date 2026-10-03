"""Generate manuscript/generated/r8_macros.tex from the saved R8 results (detection, baselines, JKU).
Run with the repo venv from this folder: python make_r8_macros.py <repo>/research/r7c"""
import sys, os, json, glob
import numpy as np
R7C = sys.argv[1]; sys.path.insert(0, os.path.join(R7C, "detection"))
det = json.load(open(os.path.join(R7C, "detection", "detection_summary.json")))
bas = json.load(open(os.path.join(R7C, "baselines", "baselines_summary.json")))
jku = json.load(open(os.path.join(R7C, "jku", "jku_summary.json")))
M = {}
f2 = lambda x: f"{x:.2f}"; f1 = lambda x: f"{x:.1f}"; f3 = lambda x: f"{x:.3f}"; f4 = lambda x: f"{x:.4f}"
for m, key in (("IN", "IN1"), ("INFour", "IN4"), ("NAFour", "NA4")):
    for lev, tag in ((0.5, "Half"), (0.9, "Ninety")):
        g = det[f"gain|{key}|0.01|{lev}"]
        M[f"Det{m}Scr{tag}"] = f1(g["scr_mean"])
        M[f"Det{m}GainCA{tag}"] = f1(g["vsCA16"][0]); M[f"Det{m}GainCALo{tag}"] = f1(g["vsCA16"][1]); M[f"Det{m}GainCAHi{tag}"] = f1(g["vsCA16"][2])
        M[f"Det{m}GainLoc{tag}"] = f1(g["vsCAloc"][0]); M[f"Det{m}GainLocLo{tag}"] = f1(g["vsCAloc"][1]); M[f"Det{m}GainLocHi{tag}"] = f1(g["vsCAloc"][2])
for m, tag in (("IN1", "INOne"), ("NA4", "NAFour"), ("CA16", "CASixteen"), ("CAloc", "CAloc"), ("NA4G", "NAFourG")):
    M[f"DetPfa{tag}"] = f4(det[f"{m}|0.01|pfa"])
M["DetPfaNAFourGmilli"] = f4(det["NA4G|0.001|pfa"])
M["DetMae"] = f3(det["exact_mae|0.01"]); M["DetMaePooled"] = f3(det["exact_mae|0.01"] and json.load(open(os.path.join(R7C, "detection", "detection_summary.json")))["exact_mae|0.01"]) if False else f3(det["exact_mae|0.01"])
# per-unit exact-law SCR error and naive whitening gain (as in RESULTS_DETECTION.md)
from analyze_detection import D, scr_at   # re-runs analysis deterministically (same seed)
err = [scr_at(d["IN1|0.01|sw1"], .5) - scr_at(d["IN1|0.01|pred"], .5) for d in D]
wg = [10 * np.log10(1 / (1 - abs(complex(*d["rho"])) ** 2)) for d in D]
M["DetScrErrAbs"] = f1(np.nanmean(np.abs(err))); M["DetNaiveGain"] = f1(np.mean(wg))
M["DetNTest"] = f"{sum(int(d['n_test']) for d in D):,}".replace(",", "{,}")
pooled = np.mean([d["IN1|0.01|sw1"] for d in D], 0); predp = np.mean([d["IN1|0.01|pred"] for d in D], 0)
M["DetMaePooled"] = f3(float(np.mean(np.abs(predp - pooled))))
# baselines
b1 = bas["B1|0.1"]; M["BOneRatio"] = f3(b1["ratio"][0]); M["BOneRatioLo"] = f3(b1["ratio"][1]); M["BOneRatioHi"] = f3(b1["ratio"][2])
tr_s, tr_a = bas["B2tr|IN1|0.1"], bas["B2tr|ACI0.02|0.1"]
M["ACIWorstSplit"] = f3(tr_s["worst"]); M["ACIWorst"] = f3(tr_a["worst"]); M["ACIRadius"] = f3(tr_a["radius_ratio_mean"])
M["ACIDevSplit"] = f3(tr_s["maxdev"]); M["ACIDev"] = f3(tr_a["maxdev"])
M["ACIWithin"] = f4(bas["B2in|0.02|0.1"]["cover"]); M["ACIWithinSplit"] = f4(bas["B2in|0.02|0.1"]["split"])
# JKU
M["JMae"] = f3(jku["J2_mae|0.1"]); M["JMaeB"] = f3(jku["J2_mae|0.01"])
ci, pi, cu, cn4 = jku["IN1|0.1|cls"], jku["IN1|0.1|pred"], jku["U|0.1|cls"], jku["NA4|0.1|cls"]
M["JInLow"] = f3(ci[0]); M["JInHigh"] = f3(ci[4]); M["JPredHigh"] = f3(pi[4]); M["JULow"] = f3(cu[0]); M["JUHigh"] = f3(cu[5])
M["JDevIN"] = f3(jku["IN1|0.1|maxdev"]); M["JDevNAFour"] = f3(jku["NA4|0.1|maxdev"]); M["JDevNAOne"] = f3(jku["NA1|0.1|maxdev"])
for m, tag in (("IN1", "IN"), ("NA4", "NAFour")):
    M[f"J{tag}GainLow"] = f2(jku[f"J3|{m}|0"][0]); M[f"J{tag}GainMid"] = f2(jku[f"J3|{m}|2"][0]); M[f"J{tag}GainHigh"] = f2(jku[f"J3|{m}|4"][0])
d4 = np.load(os.path.join(R7C, "study", "results", "jku", "j4_interference.npz"))
M["JFourIN"] = f3(float(d4["IN1|0.1|clean"])); M["JFourNAFour"] = f3(float(d4["NA4|0.1|clean"])); M["JFourNAOne"] = f3(float(d4["NA1|0.1|clean"]))
M["JFourHit"] = f3(float(d4["IN1|0.1|hit"])); M["JFourRate"] = f1(100 * float(d4["hit_rate"]))
nj = sum(int(np.load(p)["cls_n"].sum()) for p in glob.glob(os.path.join(R7C, "study", "results", "jku", "j_s*.npz")))
M["JNTest"] = f"{nj/1e6:.2f}"
# ---- R9 additions: onset (frozen), dwell and onset theory (exploratory), texture Pfa spread, JKU general form ----
ons = json.load(open(os.path.join(R7C, "detection", "onset_summary.json")))
dwl = json.load(open(os.path.join(R7C, "detection", "dwell_summary.json")))
oth = json.load(open(os.path.join(R7C, "detection", "onset_theory.json")))
lk = ons["look10|IN1|0.01|random"]
for j, tag in enumerate(("Zero", "One", "Two", "Three", "Four")): M[f"OnLook{tag}"] = f3(lk[j])
M["OnMatchedOne"] = f3(ons["look10|IN1|0.01|matched"][1]); M["OnOppOne"] = f3(ons["look10|IN1|0.01|opposite"][1])
M["OnNALookFour"] = f3(ons["look10|NA4|0.01|random"][4]); M["OnCAloc"] = f2(ons["look10|CAloc|0.01|random"][0])
for m, tag in (("IN1", "IN"), ("NA4", "NAFour")):
    g = ons[f"gain|{m}|0.01|random|0.5|K8"]; M[f"OnGain{tag}"] = f1(g[0]); M[f"OnGain{tag}Lo"] = f1(g[1]); M[f"OnGain{tag}Hi"] = f1(g[2])
    g1 = ons[f"gain|{m}|0.01|random|0.5|K1"]; M[f"OnGainOne{tag}"] = f1(g1[0])
    dg = dwl[f"gain|{m}|sum|K8|0.5"]; M[f"Dw{tag}"] = f1(dg[0]); M[f"Dw{tag}Lo"] = f1(dg[1]); M[f"Dw{tag}Hi"] = f1(dg[2])
    dg9 = dwl[f"gain|{m}|sum|K8|0.9"]; M[f"Dw{tag}Ninety"] = f1(dg9[0])
M["DwCAlocOne"] = f1(dwl["CAloc|sum|K1"]["scr50"]); M["DwCAlocEight"] = f1(dwl["CAloc|sum|K8"]["scr50"])
M["OnCumPfaIN"] = f3(ons["pfa_cum|IN1|0.01"][3]); M["OnCumPfaCAloc"] = f3(ons["pfa_cum|CAloc|0.01"][3])
for dop, tag in (("random", "Rand"), ("matched", "Match"), ("opposite", "Opp")):
    M[f"OnTheoryMae{tag}"] = f3(float(np.mean([np.abs(np.array(x["pred"][dop]) - np.array(x["meas"][dop])) for x in oth])))
# texture-quintile Pfa at alpha = 0.01 on IPIX confirmatory units
Pc = [p for p in glob.glob(os.path.join(R7C, "study", "results", "confirmatory", "unit_*_m16.npz")) if "_rot1_" not in p]
def qpfa(m):
    qs = []
    for p in Pc:
        d = np.load(p); tex = d["texture|1024"]; qb = np.digitize(tex, np.quantile(tex, [.2, .4, .6, .8])); c = d[f"{m}|0.01|cover"]
        qs.append([1 - c[qb == b].mean() for b in range(5)])
    return np.mean(qs, 0)
for m, tag in (("IN1", "IN"), ("NA4", "NAFour"), ("U", "U"), ("RMS", "RMS"), ("MLP", "MLP")):
    q = qpfa(m); M[f"QPfa{tag}Min"] = f4(q.min()); M[f"QPfa{tag}Max"] = f4(q.max()); M[f"QPfa{tag}Spread"] = f1(q.max() / q.min())
# JKU general closed form with fitted r and rho (exploratory)
Gs = []
for p in glob.glob(os.path.join(R7C, "study", "results", "jku", "j_s*.npz")):
    d = np.load(p); rec = json.loads(str(d["rec"])); r_ = complex(rec["r"]); rho_ = complex(rec["rho1"]); c = 10 ** (d["cls_mean_cnr_db"] / 10)
    Gs.append(10 * np.log10((1 + c) / (c * (1 + abs(r_) ** 2 - 2 * (np.conj(r_) * rho_).real) + 1 + abs(r_) ** 2)))
Gm = np.nanmean(Gs, 0); M["JGenLow"] = f1(Gm[0]); M["JGenHigh"] = f1(Gm[5]); M["JGenMid"] = f1(Gm[4])
M["JMeasTop"] = f1(jku["J3|IN1|5"][0])
out = os.path.join(os.path.dirname(os.path.abspath(__file__)), "..", "manuscript", "generated", "r8_macros.tex")
open(out, "w").write("% Generated by analysis_provenance/make_r8_macros.py from the saved R8 results. Do not edit.\n" +
                     "".join(f"\\newcommand{{\\{k}}}{{{v}}}\n" for k, v in sorted(M.items())))
print(open(out).read())
