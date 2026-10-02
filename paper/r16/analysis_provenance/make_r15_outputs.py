"""R15 outputs for the manuscript: macros (generated/r15_macros.tex) and the IPIX-vs-NetRAD confirmation table
(generated/tab_netrad.tex), from the saved outcomes in the code repository: research/r7c/r15/r15_summary.json (NetRAD,
analysis analyze_r15.py) and, for the IPIX column, r12/r12_summary.json and r14/r14_summary.json. The statistic sets are
those of the IPIX macros (make_r12_tables.py, make_r13_macros.py), so the two columns are computed identically.
Usage: python make_r15_outputs.py [summary.json]   (run with the repository .venv)"""
import json, os, sys
import numpy as np

HERE = os.path.dirname(os.path.abspath(__file__))
REPO = os.path.join(HERE, "..", "..", "02_paper_repo_inarcp", "research", "r7c")
if not os.path.isdir(REPO):
    REPO = r"C:\Users\DELL\Downloads\MS thess\02_paper_repo_inarcp\research\r7c"
MAN = os.path.join(HERE, "..", "manuscript")
N = json.load(open(sys.argv[1] if len(sys.argv) > 1 else os.path.join(REPO, "r15", "r15_summary.json")))
I12 = json.load(open(os.path.join(REPO, "r12", "r12_summary.json")))
I14 = json.load(open(os.path.join(REPO, "r14", "r14_summary.json")))

CONF12 = ("IN1", "IN4", "OS1_8", "NA4", "CA16", "OSraw", "D-IN4", "PAMF-H(w)", "P-ANMF(bin)", "P-ANMF", "ANMF-SCM(w)", "ANMF-FP(w)")
WHITE11 = ("IN1", "IN4", "OS1_8", "NA4", "D-IN4", "PAMF-H(w)", "P-ANMF(bin)", "P-ANMF", "ANMF-SCM(w)", "ANMF-FP(w)", "Clip-OS1")


def calib(L):
    c4 = [L[f"{k}|conf|0.0001"][0] for k in CONF12]
    c3 = [L[f"{k}|conf|0.001"][0] for k in CONF12]
    over = [k for k in WHITE11 if L[f"{k}|anal|0.0001"][0] > 2]
    return dict(c3=(min(c3), max(c3)), c4=(min(c4), max(c4)), over=len(over), in1anal4=L["IN1|anal|0.0001"][0],
                spread_in=L["IN1|conf|0.01"][-1], spread_ca=L["CA16|conf|0.01"][-1])


ip, ne = calib(I12["L"]), calib(N["L"])
# detection (alpha = 0.01): SCR for Pd = 0.5 of PAMF-H, and the first-look gain of IN-ARCP over the raw-power OS detector
ipA = {k.split("|")[0]: v for k, v in I12["A"].items() if k.endswith("|0.01")}
neA = N["A"]
gain = lambda A: A["OSraw"][0] - A["IN1look"][0]
# guard (alpha = 0.01, 10 dB, random Doppler): mean per-look Pd over looks 1-8
gmean = lambda S, g: float(np.mean(S[f"G|look10|random|{g}"][1:]))
# injected interference (alpha = 0.01, 30 dB, 5%): uncertified non-coherent integration, certified clip (kappa 6), bursts
ip_din = I12["I"]["0.05|30|D-IN1|0.01"][0]; ne_din = N["I|0.05|30|D-IN1"][0]
ip_cert = I14["bern|0.05|30|0.01|cert(bern) clip6"]; ne_cert = N["bern|0.05|30|0.01|cert(bern) clip6"]
ip_bl = I14["burst|0.05|30|0.01|blank(bern masks)"]["pfa"]; ne_bl = N["burst|0.05|30|0.01|blank(bern masks)"]["pfa"]

f2 = lambda x: f"{x:.2f}"
f1 = lambda x: f"{x:.1f}"
scr = lambda x: "n.r." if x is None or x == float("inf") else (r"$\le-5$" if x == float("-inf") or x <= -5 else f"${x:.1f}$" if x < 0 else f"{x:.1f}")
def gain_txt(A):
    """SCR gain of IN-ARCP over the raw-power OS detector at P_d = 0.5; a lower bound when IN-ARCP is at the grid floor."""
    lo, hi = A["IN1look"][0], A["OSraw"][0]
    return (r"$\ge$" + f"{hi + 5:.0f}") if (lo == float("-inf") or lo <= -5) else f"{hi - lo:.1f}"


neW = f"{f2(N['W|D-IN1|clean|0.01|all'][0])} / {f2(N['W|clip6|cert|0.01|all'][0])} ({f2(N['W|clip6|cert|0.01|all'][2])})"
rows = [
    (r"Conformal, $10^{-3}$ (12 statistics)", f"{f2(ip['c3'][0])}--{f2(ip['c3'][1])}", f"{f2(ne['c3'][0])}--{f2(ne['c3'][1])}"),
    (r"Conformal, $10^{-4}$ (12 statistics)", f"{f2(ip['c4'][0])}--{f2(ip['c4'][1])}", f"{f2(ne['c4'][0])}--{f2(ne['c4'][1])}"),
    (r"Model-based laws $>2\times$ at $10^{-4}$", f"{ip['over']} of 11", f"{ne['over']} of 11"),
    (r"IN-ARCP CA law at $10^{-4}$", f2(ip["in1anal4"]), f2(ne["in1anal4"])),
    (r"Guard: $P_{\rm d}$ per look, $\Delta=0$ / 8", f"{f2(gmean(I14, 0))} / {f2(gmean(I14, 8))}", f"{f2(gmean(N, 0))} / {f2(gmean(N, 8))}"),
    (r"5\% hits: AR(1) integration", f"{ip_din:.0f}", f"{ne_din:.0f}" if ne_din >= 10 else f1(ne_din)),
    (r"5\% hits: certified clip ($P_{\rm d}$)", f"{f2(ip_cert['pfa'])} ({f2(ip_cert['pd10'])})", f"{f2(ne_cert['pfa'])} ({f2(ne_cert['pd10'])})"),
    (r"5\% bursts: blanking", f2(ip_bl), f2(ne_bl)),
    (r"Flagged pulses: integration / certified ($P_{\rm d}$)", "--", neW),
]
lines = [r"\begin{tabular}{lcc}", r"\toprule", r" & IPIX & NetRAD\\", r"\midrule"] + [f"{a} & {b} & {c}\\\\" for a, b, c in rows] + [r"\bottomrule", r"\end{tabular}"]
open(os.path.join(MAN, "generated", "tab_netrad.tex"), "w", encoding="utf8").write("\n".join(lines) + "\n")

rec = N["recordings"]
hits = sorted(v["hit_rate"] for v in rec.values())
# EXPLORATORY (r15/explore_r15_attribution.py): pooled 1e-4 ratios without the two units with the largest integration excess,
# whose calibration thirds contain no flagged pulse while their test thirds do (1450_16 rot3, 1501_53 rot3)
import glob as _g
_U = {os.path.basename(f)[2:-4]: np.load(f, allow_pickle=True) for f in _g.glob(os.path.join(REPO, "study", "results", "r15", "n_*.npz"))}
_keep = [k for k in _U if k not in ("1450_16_rot3", "1501_53_rot3")]
_pool = lambda s, ks: sum(_U[k][f"L|{s}|conf|0.0001"][0] for k in ks) / sum(_U[k][f"L|{s}|conf|0.0001"][1] for k in ks) / 1e-4
ATTR = {"NetAttrDin": f2(_pool("D-IN4", _keep)), "NetAttrPamf": f2(_pool("PAMF-H(w)", _keep))}
M = {
    "NetConfMinFour": f2(ne["c4"][0]), "NetConfMaxFour": f2(ne["c4"][1]),
    "NetConfMinThree": f2(ne["c3"][0]), "NetConfMaxThree": f2(ne["c3"][1]),
    "NetOver": str(ne["over"]), "NetInAnalFour": f2(ne["in1anal4"]),
    "NetSpreadIn": f2(ne["spread_in"]), "NetSpreadCa": f2(ne["spread_ca"]),
    "NetGuardZero": f2(gmean(N, 0)), "NetGuardEight": f2(gmean(N, 8)),
    "NetGuardPfa": f2(N["G|pfa|8|0.01"][0]),
    "NetDinFive": f"{ne_din:.0f}" if ne_din >= 10 else f1(ne_din),
    "NetCertPfa": f2(ne_cert["pfa"]), "NetCertPd": f2(ne_cert["pd10"]),
    "NetBlankBurst": f2(ne_bl),
    "NetHitMin": f"{100 * hits[0]:.1f}", "NetHitMax": f"{100 * hits[-1]:.1f}",
    "NetAbsRMin": f2(min(v["r"] for v in rec.values())), "NetAbsRMax": f2(max(v["r"] for v in rec.values())),
    "NetMet": str(sum(N["verdicts"].values())), "NetExp": str(len(N["verdicts"])),
    "NetSpreadInIpix": f2(ip["spread_in"]), "NetSpreadCaIpix": f2(ip["spread_ca"]), "NetSpreadInFour": f2(N["L"]["IN4|conf|0.01"][-1]), "NetOSGain": gain_txt(neA), "NetPamfNine": scr(neA["PAMF-H"][1]),
    "NetLawEight": f2(float(np.mean(N["G|law10|random|8"][1:]))), "NetLookFourZero": f2(N["G|look10|random|0"][4]),
    "NetRampZero": f2(N["G|ramp16|cum8@10|0"]), "NetRampEight": f2(N["G|ramp16|cum8@10|8"]),
    "NetCertBurst": f2(N["burst|0.05|30|0.01|cert(bern) clip6"]["pfa"]),
    "NetPerLookMax": f2(max(N["L"][f"{k}|conf|0.0001"][0] for k in ("IN1", "IN4", "OS1_8", "CA16", "OSraw"))),
    "NetDwellMax": f2(max(N["L"][f"{k}|conf|0.0001"][0] for k in ("D-IN4", "PAMF-H(w)", "P-ANMF(bin)", "P-ANMF"))),
    "NetNaFour": f2(N["L"]["NA4|conf|0.0001"][0]),
    "NetNOverTwoFour": str(sum(N["L"][f"{k}|conf|0.0001"][0] > 2 for k in CONF12 + ("Clip-OS1",))),
    "NetNOverTwoFourWord": ("zero one two three four five six seven eight nine ten eleven twelve thirteen".split()
                            [sum(N["L"][f"{k}|conf|0.0001"][0] > 2 for k in CONF12 + ("Clip-OS1",))]),
    "NetWDinThree": f2(N["W|D-IN1|clean|0.001|all"][0]),
    # Part W strata of the same statistic: segments with no flagged pulse (s0) and with one or more (s12, s3)
    "NetWDinNone": f2(N["W|D-IN1|clean|0.01|s0"][0]),
    "NetWDinNoneThree": f2(N["W|D-IN1|clean|0.001|s0"][0]),
    "NetWDinFlagMax": f2(max(N[f"W|D-IN1|clean|0.01|{s}"][0] for s in ("s12", "s3"))),
    "NetWDinFlagMaxThree": f2(max(N[f"W|D-IN1|clean|0.001|{s}"][0] for s in ("s12", "s3"))),
    **ATTR,
    "NetNOutFour": str(sum(not (0.5 <= N["L"][f"{k}|conf|0.0001"][0] <= 2) for k in CONF12 + ("Clip-OS1",))),
    "NetHitHHMin": f"{100 * min(v['hit_rate'] for v in rec.values() if v['pol'] == 'HH'):.0f}",
    "NetHitHHMax": f"{100 * max(v['hit_rate'] for v in rec.values() if v['pol'] == 'HH'):.0f}",
    "NetHitVVMax": f"{100 * max(v['hit_rate'] for v in rec.values() if v['pol'] == 'VV'):.1f}",
}
if "W|eligible_recordings" in N:
    M["NetWElig"] = str(N["W|eligible_recordings"])
    for key, name in (("W|clip6|cert|0.01|all", "NetWCert"), ("W|D-IN1|clean|0.01|s12", "NetWDinHit"), ("W|D-IN1|clean|0.01|all", "NetWDin"),
                      ("W|clip6|clean|0.01|all", "NetWClip"), ("W|blank|mask|0.01|all", "NetWBlank")):
        if key in N:
            M[name] = f2(N[key][0]); M[name + "Pd"] = f2(N[key][2])
with open(os.path.join(MAN, "generated", "r15_macros.tex"), "w", encoding="utf8") as f:
    f.write("% Generated by analysis_provenance/make_r15_outputs.py from the saved R15 (NetRAD) and R12/R14 (IPIX) outcomes. Do not edit.\n")
    for k, v in M.items():
        f.write(f"\\newcommand{{\\{k}}}{{{v}}}\n")
print("\n".join(lines)); print(M)
