"""R10 macros for the manuscript from saved outcomes (repo research/r7c/r10): audit_existing.json, r10_summary.json,
theory_ramps.json, na4_convergence.json, and the JKU per-unit files. Writes ../manuscript/generated/r10_macros.tex."""
import os, json, glob
import numpy as np
HERE = os.path.dirname(os.path.abspath(__file__))
R7C = os.path.join(HERE, "..", "..", "02_paper_repo_inarcp", "research", "r7c"); R10 = os.path.join(R7C, "r10")
au = json.load(open(os.path.join(R10, "audit_existing.json"))); rs = json.load(open(os.path.join(R10, "r10_summary.json")))
th = json.load(open(os.path.join(R10, "theory_ramps.json")))
f1 = lambda x: f"{x:.1f}"; f2 = lambda x: f"{x:.2f}"; f3 = lambda x: f"{x:.3f}"
M = {}
# fit diagnostics and audit
M["FitClampBinding"] = str(au["fit"]["clamp_binding"]); M["FitNAFourConv"] = str(au["fit"]["na4_conv"])
M["DepLagOne"] = f"${au['dep']['lag1']:.3f}$"; M["DepCross"] = f3(au["dep"]["crossbin"])
M["MaxdevShiftIN"] = f3(au["maxdev|IN1"]["shift"]); M["MaxdevShiftU"] = f3(au["maxdev|U"]["shift"])
M["LodoLocLo"] = f1(au["lodo|det|IN1 vs CAloc|0.5"][1]); M["LodoLocHi"] = f1(au["lodo|det|IN1 vs CAloc|0.5"][2])
M["LodoSameLo"] = f3(au["lodo|same_order_ratio"][1]); M["LodoSameHi"] = f3(au["lodo|same_order_ratio"][2])
M["NAvsINFourHalf"] = f1(au["lodo|det|NA4 vs IN4|0.5"][0]); M["NAvsINFourNinety"] = f1(au["lodo|det|NA4 vs IN4|0.9"][0])
# per-day single-pulse gain IN1 vs CAloc (from audit text line)
line = [l for l in open(os.path.join(R10, "audit_existing.txt")) if "per-day values" in l][0]
vals = [float(t.split()[-1]) for t in line.split(":", 1)[1].split(",")]
M["DayGainMin"] = f1(min(vals)); M["DayGainMax"] = f1(max(vals))
# JKU false-alarm ratios by class
j = au["jku|IN1|0.01"]["ratio"]; units = au["jku|IN1|0.01"]["units"]
M["JPfaRatioLow"], M["JPfaRatioB"], M["JPfaRatioC"], M["JPfaRatioD"], M["JPfaRatioHigh"] = (f2(x) for x in j[:5])
M["JLawRatioHigh"] = f2(au["jku|law|0.01"][4])
M["JNFiveClassEp"] = f"{721095 + 265416 + 229845 + 68556 + 31870:,}".replace(",", "{,}"); M["JTopEp"] = "338"; M["JTopUnits"] = str(units[5])
jk = [l for l in open(os.path.join(R7C, "jku", "jku_summary.txt")) if "G_IN(c) dB" in l][0].split()
M["JMatchLow"] = f1(float(jk[2])); M["JMatchHigh"] = f1(float(jk[-1]))
# Part C
sc = lambda d, k, dop="random": rs[f"C|scr|{d}|K{k}|0.01|{dop}"]
cell = lambda d, k: f"{sc(d, k)[0]:.1f} / {sc(d, k)[1]:.1f}"
M["ClScrINOne"], M["ClScrINEight"] = cell("IN1sum", 1), cell("IN1sum", 8)
M["ClScrNAOne"], M["ClScrNAEight"] = cell("NA4sum", 1), cell("NA4sum", 8)
M["ClScrPAMFOne"], M["ClScrPAMFEight"] = cell("PAMFH", 1), cell("PAMFH", 8)
M["ClScrMTDEight"] = cell("MTDhann", 8); M["ClScrLocOne"], M["ClScrLocEight"] = cell("CAlocsum", 1), cell("CAlocsum", 8)
g = lambda a, b, k, l: rs[f"C|gain|{a}-{b}|K{k}|{l}"]
x = g("IN1sum", "PAMFH", 8, 0.5); M["ClPAMFvsIN"], M["ClPAMFvsINLo"], M["ClPAMFvsINHi"] = f1(-x[0]), f1(-x[2]), f1(-x[1])
M["ClPAMFvsINNinety"] = f1(-g("IN1sum", "PAMFH", 8, 0.9)[0])
x = g("NA4sum", "PAMFH", 8, 0.5); M["ClNAvsPAMF"], M["ClNAvsPAMFLo"], M["ClNAvsPAMFHi"] = f1(x[0]), f1(x[1]), f1(x[2])
M["ClNAvsPAMFNinety"] = f1(g("NA4sum", "PAMFH", 8, 0.9)[0])
M["ClMTDvsLoc"] = f1(g("MTDhann", "CAlocsum", 8, 0.5)[0]); M["ClINvsMTD"] = f1(g("IN1sum", "MTDhann", 8, 0.5)[0])
M["ClPAMFMatched"] = f1(rs["C4"])
pf = [l for l in open(os.path.join(R10, "r10_summary.txt"))]
i0 = next(i for i, l in enumerate(pf) if "measured dwell Pfa" in l and "alpha = 0.01 (" in l)
nums = [float(t) for l in pf[i0 + 1:i0 + 8] for t in l.split()[1:] if t != "nan"]
M["ClPfaMin"], M["ClPfaMax"] = f"{min(nums):.4f}", f"{max(nums):.4f}"
# Part R (ramp pre, L = 16 dwell column; single-look gains)
rd = lambda d: [l for l in pf if l.strip().startswith("L=16") and "IN1sum" in l][0]   # first match = placement pre
row = rd(None).split(); kv = {row[i]: row[i + 1] for i in range(1, len(row) - 1, 2)}
fmt = lambda v: "n.r." if v == "nan" else v
M["ClRampIN"], M["ClRampNA"], M["ClRampPAMF"], M["ClRampMTD"], M["ClRampLoc"] = (fmt(kv[k]) for k in ("IN1sum", "NA4sum", "PAMFH", "MTDhann", "CAlocsum"))
M["RampPAMFLoss"] = f1(float(kv["PAMFH"]) - sc("PAMFH", 8)[0])
M["RampGainOne"], M["RampGainFour"], M["RampGainEight"] = (f1(rs[f"R|gain_look0|pre|L{L}"][0]) for L in (1, 4, 8))
M["RampPdSixteen"] = [l for l in pf if l.strip().startswith("L=16 IN1") and "look0" not in l][0].split()[2]
errs = {k: np.mean([np.abs(np.array(r["res"][k]["pred"]) - np.array(r["res"][k]["meas"])) for r in th]) for k in th[0]["res"]}
M["RampMae"] = f3(float(np.mean(list(errs.values())))); M["RampMaeWorst"] = f3(max(errs.values()))
# Part A
a = lambda arm: rs[f"A|0.05|{arm}"]
M["AciNaivePfa"] = f2(a("naive0.02")[0] / .01); M["AciNaivePd"] = f2(a("naive0.02")[1]); M["AciSplitPd"] = f2(a("split")[1])
M["AciGatedPfa"] = f2(a("gated0.02")[0] / .01); M["AciGatedPd"] = f2(a("gated0.02")[1])
# NA-AR(4) convergence sensitivity
p = os.path.join(R10, "na4_convergence.json")
if os.path.exists(p):
    nc = json.load(open(p)); rr = np.array([r["long|0.1|radius"] / r["orig|0.1|radius"] for r in nc])
    cv = abs(np.mean([r["long|0.1|cover"] - r["orig|0.1|cover"] for r in nc]))
    ok = abs(np.log(np.exp(np.mean(np.log(rr))))) < 0.01 and cv < 0.002
    M["FitNAFourSentence"] = (f"restarting it changes the radius by a factor "
                              f"{np.exp(np.mean(np.log(rr))):.3f} (range {rr.min():.3f}--{rr.max():.3f}) and the mean coverage by {cv:.4f}, " +
                              ("so the results do not depend on full convergence." if ok else "so the results are sensitive to the optimizer and are reported at the pre-specified cap."))
else:
    M["FitNAFourSentence"] = "[convergence sensitivity pending]"
out = os.path.join(HERE, "..", "manuscript", "generated", "r10_macros.tex")
open(out, "w").write("% Generated by analysis_provenance/make_r10_macros.py from the saved R10 outcomes. Do not edit.\n" +
                     "".join(f"\\newcommand{{\\{k}}}{{{v}}}\n" for k, v in sorted(M.items())))
print(open(out).read())
