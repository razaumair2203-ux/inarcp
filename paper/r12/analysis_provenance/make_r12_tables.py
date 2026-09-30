"""Tables and macros of the R12 results for the manuscript, from the frozen-protocol summaries (no refitting).
Usage: python make_r12_tables.py <repo>/research/r7c [summary.json]  ->  ../manuscript/generated/{r12_macros,tab_lowpfa,tab_dwell,tab_target,tab_interf}.tex"""
import sys, os, json
import numpy as np
R7C = sys.argv[1]; R12 = os.path.join(R7C, "r12")
S = json.load(open(sys.argv[2] if len(sys.argv) > 2 else os.path.join(R12, "r12_summary.json")))
J = json.load(open(os.path.join(R12, "r12_jku_summary.json")))
TH = json.load(open(os.path.join(R12, "fig_theory.json")))
OUT = os.path.join(os.path.dirname(os.path.abspath(__file__)), "..", "manuscript", "generated")
mac = []


def m(name, val, fmt="{:.2f}"):
    mac.append(f"\\newcommand{{\\{name}}}{{{fmt.format(val) if not isinstance(val, str) else val}}}")


def f2(x, bold_hi=2.0, two_sided=True):
    if x is None or not np.isfinite(x): return "--"
    s = f"{x:.1f}" if x >= 10 else f"{x:.2f}"
    return f"\\textbf{{{s}}}" if (x > bold_hi or (two_sided and x < 1 / bold_hi)) else s


def scr(x):
    if x is None or not np.isfinite(x): return "n.r."
    return "$\\le-5$" if x <= -4.999 else f"{x:.1f}"


L = S["L"]
# ------------------------------------------------ Part L table
rows = [("\\emph{Per look}", None, None),
        ("IN-ARCP (CA law)", "IN1", "anal"), ("\\quad residual bootstrap", "IN1", "boot"), ("IN-AR(4) (CA law)", "IN4", "anal"),
        ("OS scale, $k=8$ (OS law)", "OS1_8", "anal"), ("NA-AR(4) (Gaussian)", "NA4", "anal"),
        ("Power, CA (white law)", "CA16", "anal"), ("Power, OS (white law)", "OSraw", "anal"),
        ("\\emph{Eight-pulse dwell}", None, None),
        ("Integration (law \\eqref{eq:dwellpfa})", "D-IN4", "anal"), ("PAMF-H, one Doppler (CA law)", "PAMF-H(w)", "anal"),
        ("P-ANMF, one bin (Beta)", "P-ANMF(bin)", "anal"), ("P-ANMF, max (Fisher's $g$)", "P-ANMF", "anal"),
        ("ANMF-SCM (Kraut--Scharf)", "ANMF-SCM(w)", "anal"), ("ANMF-Tyler (FP law)", "ANMF-FP(w)", "anal"),
        ("Clipped, OS scale (Gaussian sim.)", "Clip-OS1", "anal")]
lines = []
for lab, k, rule in rows:
    if k is None:
        lines.append(f"{lab} &&&&&&\\\\"); continue
    conf = [L.get(f"{k}|conf|{a}", [np.nan])[0] for a in (0.01, 0.001, 0.0001)] if rule != "boot" else [np.nan] * 3
    mod = [L[f"{k}|{rule}|{a}"][0] for a in (0.01, 0.001, 0.0001)]
    cc = " & ".join("" if rule == "boot" else f2(v) for v in conf)
    lines.append(f"{lab} & {cc} & " + " & ".join(f2(v) for v in mod) + "\\\\")
tab = ("\\begin{tabular}{lcccccc}\n\\toprule\n & \\multicolumn{3}{c}{Conformal} & \\multicolumn{3}{c}{Model-based rule}\\\\\n"
       "\\cmidrule(lr){2-4}\\cmidrule(lr){5-7}\n$\\alpha$ & $10^{-2}$ & $10^{-3}$ & $10^{-4}$ & $10^{-2}$ & $10^{-3}$ & $10^{-4}$\\\\\n\\midrule\n"
       + "\n".join(lines) + "\n\\bottomrule\n\\end{tabular}\n")
open(os.path.join(OUT, "tab_lowpfa.tex"), "w").write(tab)

conf4 = [L[f"{k}|conf|0.0001"][0] for k in ("IN1", "IN4", "OS1_8", "NA4", "CA16", "OSraw", "D-IN4", "PAMF-H(w)", "P-ANMF(bin)", "P-ANMF", "ANMF-SCM(w)", "ANMF-FP(w)")]
conf3 = [L[f"{k}|conf|0.001"][0] for k in ("IN1", "IN4", "OS1_8", "NA4", "CA16", "OSraw", "D-IN4", "PAMF-H(w)", "P-ANMF(bin)", "P-ANMF", "ANMF-SCM(w)", "ANMF-FP(w)")]
anal4 = {k: L[f"{k}|anal|0.0001"][0] for k in ("IN4", "OS1_8", "NA4", "D-IN4", "PAMF-H(w)", "P-ANMF(bin)", "P-ANMF", "ANMF-SCM(w)", "ANMF-FP(w)", "Clip-OS1")}
m("LConfMinFour", min(conf4)); m("LConfMaxFour", max(conf4)); m("LConfMinThree", min(conf3)); m("LConfMaxThree", max(conf3))
m("LAnalMinFour", min(anal4.values()), "{:.1f}"); m("LAnalMaxFour", max(anal4.values()), "{:.0f}")
for key, name in (("IN1|anal|0.001", "LInAnalThree"), ("IN1|anal|0.0001", "LInAnalFour"), ("IN1|boot|0.001", "LBootThree"), ("IN1|boot|0.0001", "LBootFour"),
                  ("ANMF-SCM(w)|anal|0.001", "LScmThree"), ("ANMF-FP(w)|anal|0.001", "LFpThree"), ("ANMF-SCM(w)|anal|0.0001", "LScmFour"), ("ANMF-FP(w)|anal|0.0001", "LFpFour"),
                  ("P-ANMF|anal|0.0001", "LPanmfFour"), ("Clip-OS1|anal|0.0001", "LClipGFour"), ("OS1_8|anal|0.0001", "LOsFour"), ("NA4|anal|0.0001", "LNaFour"),
                  ("PAMF-H(w)|anal|0.0001", "LPamfFour"), ("D-IN4|anal|0.0001", "LDinFour"), ("CA16|anal|0.001", "LCaWhiteThree"), ("OSraw|anal|0.001", "LOsRawThree"),
                  ("Clip-OS1|conf|0.001", "LClipConfThree"), ("Clip-OS1|conf|0.0001", "LClipConfFour")):
    v = L[key][0]; m(name, v, "{:.1f}" if v >= 10 else "{:.2f}")
m("LInConfSpreadThree", L["IN1|conf|0.001"][2], "{:.1f}")

# ------------------------------------------------ Part A table
A = S["A"]
rowsA = [("PAMF-H", "PAMF-H"), ("Integration, AR(4)", "D-IN4"), ("Integration, AR(1)", "D-IN1"), ("Clipped, OS scale", "Clip-OS1"),
         ("Binary, OS scale", "Bin-OS1"), ("ANMF-SCM", "ANMF-SCM"), ("ANMF-Tyler", "ANMF-FP"), ("P-ANMF", "P-ANMF"),
         ("IN-ARCP, first look", "IN1look"), ("Power OS, first look", "OSraw")]
tabA = "\\begin{tabular}{lccc}\n\\toprule\n & \\multicolumn{2}{c}{$\\alpha=0.01$} & $0.001$\\\\\n\\cmidrule(lr){2-3}\n Detector & $P_{\\rm d}=0.5$ & $0.9$ & $0.5$\\\\\n\\midrule\n"
for lab, k in rowsA:
    tabA += f"{lab} & {scr(A[f'{k}|0.01'][0])} & {scr(A[f'{k}|0.01'][1])} & {scr(A[f'{k}|0.001'][0])}\\\\\n"
tabA += "\\bottomrule\n\\end{tabular}\n"
open(os.path.join(OUT, "tab_dwell.tex"), "w").write(tabA)
d = S["A_diffs"]
m("AFpMinusPamf", d["ANMF-FP-PAMF-H"][0], "{:.1f}"); m("AFpMinusPamfLo", d["ANMF-FP-PAMF-H"][1][0], "{:.1f}"); m("AFpMinusPamfHi", d["ANMF-FP-PAMF-H"][1][1], "{:.1f}")
m("AClipMinusDin", d["Clip-DIN1"][0], "{:.1f}"); m("AClipMinusDinLo", d["Clip-DIN1"][1][0], "{:.1f}"); m("AClipMinusDinHi", d["Clip-DIN1"][1][1], "{:.1f}")
m("AOsrawMinusIn", d["OSraw-IN1"][0], "{:.1f}"); m("AOsrawMinusInLo", d["OSraw-IN1"][1][0], "{:.1f}"); m("AOsrawMinusInHi", d["OSraw-IN1"][1][1], "{:.1f}")

# ------------------------------------------------ Part T table
T = S["T"]
NT = (8, 16, 32, 64, 128, 256, 512, 1024)
tabT = ("\\begin{tabular}{rcccc}\n\\toprule\n & \\multicolumn{2}{c}{P-ANMF} & Range CA & ANMF\\\\\n\\cmidrule(lr){2-3}\n"
        "$N$ & conformal & Fisher's $g$ & integration & Tyler\\\\\n\\midrule\n")
for N in NT:
    pc, pa, ca = T[f"P-ANMF|conf|{N}"], T[f"P-ANMF|anal|{N}"], T[f"CA-NCI|conf|{N}"]
    fp = T.get(f"ANMF-FP|conf|{N}")
    tabT += f"{N} & {pc[0]:.2f} ({1e3 * pc[1]:.1f}) & {pa[0]:.2f} ({1e3 * pa[1]:.0f}) & {ca[0]:.3f} & {'--' if fp is None else f'{fp[0]:.2f}'}\\\\\n"
tabT += "\\bottomrule\n\\end{tabular}\n"
open(os.path.join(OUT, "tab_target.tex"), "w").write(tabT)
for N, nm in ((8, "Eight"), (256, "TwoFiveSix"), (1024, "Thousand")):
    m(f"TPanmf{nm}", T[f"P-ANMF|conf|{N}"][0]); m(f"TPanmfPfa{nm}", 1e3 * T[f"P-ANMF|conf|{N}"][1], "{:.1f}")
    m(f"TFisherPfa{nm}", T[f"P-ANMF|anal|{N}"][1], "{:.3f}")
m("TFpEight", T["ANMF-FP|conf|8"][0]); m("TFpSixteen", T["ANMF-FP|conf|16"][0]); m("TCaMax", max(T[f"CA-NCI|conf|{N}"][0] for N in NT), "{:.3f}")

# ------------------------------------------------ Part I + J table
I = S["I"]
det = [("Integration, AR(1)", "D-IN1"), ("PAMF-H", "PAMF-H"), ("P-ANMF", "P-ANMF"), ("ANMF-Tyler", "ANMF-FP"),
       ("Clipped, clean threshold", "Clip-OS1"), ("Clipped, certified", "Clip-OS1-cert"), ("Binary, certified", "Bin-OS1-cert")]
R = J["R"]
tabI = ("\\begin{tabular}{lcccccc}\n\\toprule\n & \\multicolumn{2}{c}{IPIX, $p=2\\%$} & \\multicolumn{2}{c}{IPIX, $p=5\\%$} & \\multicolumn{2}{c}{77 GHz, run C}\\\\\n"
        "\\cmidrule(lr){2-3}\\cmidrule(lr){4-5}\\cmidrule(lr){6-7}\n Detector & $P_{\\rm fa}/\\alpha$ & SCR$_{50}$ & $P_{\\rm fa}/\\alpha$ & SCR$_{50}$ & $P_{\\rm fa}/\\alpha$ & SCR$_{50}$\\\\\n\\midrule\n")
for lab, k in det:
    c = []
    for p in ("0.02", "0.05"):
        v = I[f"{p}|30|{k}|0.01"]; c += [f2(v[0], 1.5, False), scr(v[2])]
    rk = f"C|N|{k}"
    if rk in R:
        c += [f2(R[rk]["pfa"]["all"] / 0.01, 1.5, False), scr(R[rk]["scr50"]["all"])]
    else:
        c += ["--", "--"]
    tabI += f"{lab} & " + " & ".join(c) + "\\\\\n"
tabI += "\\bottomrule\n\\end{tabular}\n"
open(os.path.join(OUT, "tab_interf.tex"), "w").write(tabI)
for p, nm in (("0.02", "Two"), ("0.05", "Five")):
    m(f"IDinPfa{nm}", I[f"{p}|30|D-IN1|0.01"][0], "{:.0f}"); m(f"IPamfPfa{nm}", I[f"{p}|30|PAMF-H|0.01"][0], "{:.0f}")
    m(f"ICertPfa{nm}", I[f"{p}|30|Clip-OS1-cert|0.01"][0]); m(f"IClipPfa{nm}", I[f"{p}|30|Clip-OS1|0.01"][0])
    m(f"ICertCost{nm}", I[f"{p}|30|Clip-OS1-cert|0.01"][2] - A["Clip-OS1|0.01"][0], "{:.1f}")
m("IPfaMinAll", min(I[f"{p}|{j}|{k}|0.01"][0] for p in ("0.02", "0.05") for j in (10, 30) for k in ("D-IN1", "PAMF-H")), "{:.0f}")
m("IPfaMaxAll", max(I[f"{p}|{j}|{k}|0.01"][0] for p in ("0.02", "0.05") for j in (10, 30) for k in ("D-IN1", "PAMF-H")), "{:.0f}")
m("ICertMaxAll", max(I[f"{p}|{j}|{k}-cert|0.01"][0] for p in ("0.02", "0.05") for j in (10, 30) for k in ("Clip-OS1", "Bin-OS1")))
m("ICertUpperMax", max(I[f"{p}|{j}|{k}-cert|0.01"][1] for p in ("0.02", "0.05") for j in (10, 30) for k in ("Clip-OS1", "Bin-OS1")))
# JKU
m("JCertPfaC", R["C|N|Clip-OS1-cert"]["pfa"]["all"] / 0.01); m("JCertPfaCZ", R["C|Z|Clip-OS1-cert"]["pfa"]["all"] / 0.01)
m("JDinPfaC", R["C|N|D-IN1"]["pfa"]["all"] / 0.01); m("JDinPfaCone", R["C|N|D-IN1"]["pfa"]["s1"] / 0.01)
m("JDinPfaA", R["A|N|D-IN1"]["pfa"]["all"] / 0.01); m("JClipPfaC", R["C|N|Clip-OS1"]["pfa"]["all"] / 0.01)
m("JCertScrC", R["C|N|Clip-OS1-cert"]["scr50"]["all"], "{:.1f}"); m("JClipScrC", R["C|N|Clip-OS1"]["scr50"]["all"], "{:.1f}")
m("JCertScrCclean", R["C|N|Clip-OS1-cert"]["scr50"]["s0"], "{:.1f}"); m("JClipScrCclean", R["C|N|Clip-OS1"]["scr50"]["s0"], "{:.1f}")
m("JZScrC", R["C|Z|Clip-OS1"]["scr50"]["all"], "{:.1f}"); m("JZPfaC", R["C|Z|D-IN1"]["pfa"]["all"] / 0.01)
m("JZarGainA", R["A|Z|IN1"]["scr50"]["all"] - R["A|ZAR|IN1"]["scr50"]["all"], "{:.1f}")
m("JDinScrAN", R["A|N|D-IN1"]["scr50"]["all"], "{:.1f}"); m("JDinScrAZ", R["A|Z|D-IN1"]["scr50"]["all"], "{:.1f}")
import re as _re
_h = _re.search(r"A ([0-9.]+), C ([0-9.]+)", open(os.path.join(R12, "r12_jku_summary.txt"), encoding="utf-8").read())
m("JHitA", 100 * float(_h.group(1)), "{:.0f}"); m("JHitC", 100 * float(_h.group(2)), "{:.1f}")
# theory figure
m("ThHorizonOpp", TH["b|lstar"], "{:.1f}"); m("ThKeff", TH["d|keff"], "{:.2f}")
ver = {**S["verdicts"], **J["verdicts"]}
m("RTwelveMet", sum(ver.values()), "{:d}"); m("RTwelveAll", len(ver), "{:d}")
open(os.path.join(OUT, "r12_macros.tex"), "w").write("% generated by make_r12_tables.py from the frozen R12 summaries\n" + "\n".join(mac) + "\n")
print("ok:", len(mac), "macros;", "verdicts", ver)
