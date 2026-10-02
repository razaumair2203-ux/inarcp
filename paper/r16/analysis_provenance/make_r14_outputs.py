"""R14 outputs for the manuscript: macros (generated/r14_macros.tex), the remedies table (generated/tab_remedies.tex)
and the guard figure (figures/fig_guard_col.pdf), all from the saved R14 outcomes in the code repository:
research/r7c/r14/r14_summary.json and study/results/r14/u_*.npz (analysis: research/r7c/r14/analyze_r14.py).
Usage: python make_r14_outputs.py   (run with the repository .venv)"""
import glob, json, os
import numpy as np
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt

HERE = os.path.dirname(os.path.abspath(__file__))
REPO = os.path.join(HERE, "..", "..", "02_paper_repo_inarcp", "research", "r7c")
if not os.path.isdir(REPO):                                   # working copy outside the workspace
    REPO = r"C:\Users\DELL\Downloads\MS thess\02_paper_repo_inarcp\research\r7c"
S = json.load(open(os.path.join(REPO, "r14", "r14_summary.json")))
MAN = os.path.join(HERE, "..", "manuscript")
U = [dict(np.load(f, allow_pickle=True)) for f in sorted(glob.glob(os.path.join(REPO, "study", "results", "r14", "u_*.npz")))]
assert len(U) == 56
SCR = U[0]["scr_db"]; I10 = int(np.argmin(abs(SCR - 10)))
row = lambda name, cond: S[f"{cond}|0.01|{name}"]

M = {}
look = {g: np.array(S[f"G|look10|random|{g}"]) for g in (0, 8)}
M["GuardMeanLookZero"] = f"{look[0][1:].mean():.2f}"
M["GuardMeanLookEight"] = f"{look[8][1:].mean():.2f}"
M["GuardLookFourZero"] = f"{look[0][4]:.2f}"
M["GuardLookZeroEight"] = f"{look[8][0]:.2f}"
M["GuardOppEight"] = f"{np.mean(S['G|look10|opposite|8'][1:]):.2f}"
M["GuardMatchedEight"] = f"{np.mean(S['G|look10|matched|8'][1:]):.2f}"
M["GuardLawEight"] = f"{np.mean(S['G|law10|random|8'][1:]):.2f}"
M["GuardOnsetCost"] = f"{S['G|scr50look0|random|8'] - S['G|scr50look0|random|0']:.1f}"
M["GuardRampZero"] = f"{S['G|ramp16|cum8@10|0']:.2f}"
M["GuardRampEight"] = f"{S['G|ramp16|cum8@10|8']:.2f}"
M["GuardPfaEight"] = f"{S['G|pfa|8|0.01'][0]:.2f}"
M["GuardPfaEightThree"] = f"{S['G|pfa|8|0.001'][0]:.2f}"
M["GuardTargetEight"] = f"{S['G|target|8|0.001']:.4f}"
M["KappaSixPfaThree"] = f"{S['K|clean|6|0.001'][0]:.2f}"
M["KappaNinePfaThree"] = f"{S['K|clean|9|0.001'][0]:.2f}"
M["KappaSixPdThree"] = f"{S['clean|clip6|0.001|pd10']:.2f}"
M["KappaNinePdThree"] = f"{S['clean|clip9|0.001|pd10']:.2f}"
M["CleanClipPdTen"] = f"{S['clean|clip6|0.01|pd10']:.2f}"
M["CertSixPdTwo"] = f"{row('cert(bern) clip6', 'bern|0.02|30')['pd10']:.2f}"
M["CertSixPdFive"] = f"{row('cert(bern) clip6', 'bern|0.05|30')['pd10']:.2f}"
M["CertNinePdFive"] = f"{row('cert(bern) clip9', 'bern|0.05|30')['pd10']:.2f}"
M["BlankPdFive"] = f"{row('blank(bern masks)', 'bern|0.05|30')['pd10']:.2f}"
M["BlankPfaMax"] = f"{max(row('blank(bern masks)', f'bern|{p}|{j}')['pfa'] for p in (0.02, 0.05) for j in (10, 30)):.2f}"
M["BlankBurstMax"] = f"{max(row('blank(bern masks)', f'burst|{p}|30')['pfa'] for p in (0.02, 0.05)):.1f}"
M["CertBurstMax"] = f"{max(row('cert(bern) clip6', f'burst|{p}|30')['pfa'] for p in (0.02, 0.05)):.2f}"
M["CertBurstFiveSix"] = f"{row('cert(bern) clip6', 'burst|0.05|30')['pfa']:.2f}"     # Table IV bursts column, kappa 6
M["CertBurstFiveNine"] = f"{row('cert(bern) clip9', 'burst|0.05|30')['pfa']:.2f}"    # kappa 9 (not in Table IV)
lo3 = [S[f"bern|0.05|{j}|0.001|blank(bern masks)"]["pfa"] for j in (10, 30)]
M["BlankFiveThreeMin"], M["BlankFiveThreeMax"] = f"{min(lo3):.1f}", f"{max(lo3):.1f}"
tl = {(round(p, 3), a, int(b)): int(t) for p, a, b, t in S["trim_levels"]}
M["TrimTwo"], M["TrimFive"] = str(tl[(0.02, 0.01, 0)]), str(tl[(0.05, 0.01, 0)])
M["CertPfaFiveMax"] = f"{max(row('cert(bern) clip6', f'bern|0.05|{j}')['hi'] for j in (10, 30)):.2f}"
nd = np.array([u["n_dwell"] for u in U])
M["DwellSegsPerUnit"] = f"{int(round(nd[:, 0].mean(), -2)):,}"            # calibration segments per unit (mean)
# certified binary vs certified clipped integration (R12 outcomes, sparse calibration): largest P_d gap at 10 dB
U12 = [dict(np.load(f, allow_pickle=True)) for f in sorted(glob.glob(os.path.join(REPO, "study", "results", "r12", "i_*.npz")))]
assert len(U12) == 56
i10 = int(np.argmin(abs(U12[0]["scr_db"] - 10)))
pd12 = lambda key: np.mean([u[key][1 + i10] for u in U12])
gap = max(abs(pd12(f"I|{p}|{j}|Clip-OS1-cert|0.01") - pd12(f"I|{p}|{j}|Bin-OS1-cert|0.01")) for p in (0.02, 0.05) for j in (10, 30))
M["BinCertGapMax"] = f"{np.ceil(gap * 100) / 100:.2f}"                     # rounded up
# low-false-alarm calibration sets (R12 Part L, non-overlapping episodes) and P{P_fa > 2 alpha} at 1e-4 over their sizes
import math
from scipy import stats
ncal = np.array([u["L|nlook"][0] for u in U12])
p2 = lambda n, a: stats.beta.sf(2 * a, n + 1 - math.ceil((n + 1) * (1 - a)), math.ceil((n + 1) * (1 - a)))
pr = [p2(n, 1e-4) for n in range(int(ncal.min()), int(ncal.max()) + 1)]
M["LowCalMin"], M["LowCalMax"] = f"{int(round(ncal.min(), -2)):,}", f"{int(round(ncal.max(), -2)):,}"
M["LowCalPtwoMin"], M["LowCalPtwoMax"] = f"{min(pr):.2f}", f"{max(pr):.2f}"
# the dwell and Doppler statistics of the same study use non-overlapping 24-pulse segments (fewer per unit)
ndw = np.array([u["L|ndwell"][0] for u in U12])
prd = [p2(n, 1e-4) for n in range(int(ndw.min()), int(ndw.max()) + 1)]
M["DwellCalMin"], M["DwellCalMax"] = f"{int(round(ndw.min(), -2)):,}", f"{int(round(ndw.max(), -2)):,}"
M["DwellCalPtwoMin"], M["DwellCalPtwoMax"] = f"{min(prd):.2f}", f"{max(prd):.2f}"
# expected false alarms per unit at 1e-4 on the TEST thirds (per-look and dwell test counts)
nte_look = np.array([u["L|nlook"][1] for u in U12]); nte_dw = np.array([u["L|ndwell"][1] for u in U12])
M["FaPerUnitMin"], M["FaPerUnitMax"] = f"{min(nte_look.min(), nte_dw.min()) * 1e-4:.1f}", f"{max(nte_look.max(), nte_dw.max()) * 1e-4:.1f}"
# self-normalized detectors under injected interference (R12 Part I, alpha = 0.01): largest Pfa/alpha
I12 = json.load(open(os.path.join(REPO, "r12", "r12_summary.json")))["I"]
# largest excess of uncertified integration under injected interference (R12 Part I, alpha = 0.01), all integrators incl. AR(4)
M["IPfaMaxInt"] = f"{max(I12[f'{p}|{j}|{m}|0.01'][0] for p in ('0.02', '0.05') for j in (10, 30) for m in ('D-IN1', 'D-IN4', 'PAMF-H')):.0f}"
M["SelfNormIntMax"] =f"{max(I12[f'{p}|{j}|{m}|0.01'][0] for p in ('0.02', '0.05') for j in (10, 30) for m in ('P-ANMF', 'ANMF-FP')):.2f}"
M["KappaNineUnits"] = str(sum(float(u["K|rule|0.001"]) == 9.0 for u in U))       # units whose saturation rule picks kappa = 9 at 1e-3
M["KappaRuleUndefUnits"] = str(sum(float(u["K|rule|0.001"]) < 0 for u in U))   # units where no clip level satisfies the rule at 1e-3
M["IpixAbsRMed"] =f"{np.median([abs(complex(*u['r'])) for u in U]):.2f}"                 # median fitted |r| over the 56 units

with open(os.path.join(MAN, "generated", "r14_macros.tex"), "w", encoding="utf8") as f:
    f.write("% Generated by analysis_provenance/make_r14_outputs.py from the saved R14 outcomes. Do not edit.\n")
    for k, v in M.items():
        f.write(f"\\newcommand{{\\{k}}}{{{v}}}\n")

# ---- remedies table: alpha = 0.01, 30 dB, P_d at 10 dB
def cell(v, bold_above=1.2):
    s = f"{v:.2f}"
    return f"\\textbf{{{s}}}" if v > bold_above else s
rows = [("Clipped, clean threshold", "clean-thr clip6", "clip6"),
        ("Certified clipped, $\\kappa=6$", "cert(bern) clip6", None),
        ("Certified clipped, $\\kappa=9$", "cert(bern) clip9", None),
        ("Certified trimmed", "trim", None),
        ("Blanking, mask-matched", "blank(bern masks)", "blank")]
lines = ["\\begin{tabular}{lccccc}", "\\toprule",
         " & None & \\multicolumn{2}{c}{$p_{\\rm h}=2\\%$} & \\multicolumn{2}{c}{$p_{\\rm h}=5\\%$} & Bursts\\\\",
         "\\cmidrule(lr){2-2}\\cmidrule(lr){3-4}\\cmidrule(lr){5-6}\\cmidrule(lr){7-7}",
         " Detector & $P_{\\rm d}$ & $P_{\\rm fa}/\\alpha$ & $P_{\\rm d}$ & $P_{\\rm fa}/\\alpha$ & $P_{\\rm d}$ & $P_{\\rm fa}/\\alpha$\\\\", "\\midrule"]
lines[0] = "\\begin{tabular}{lcccccc}"
for lab, key, clean in rows:
    def k(cond):
        if key == "trim":
            p = float(cond.split("|")[1]); t = tl[(p, 0.01, 0)]
            return row(f"cert(bern) trim t={t}", cond)
        return row(key, cond)
    c2, c5, cb = k("bern|0.02|30"), k("bern|0.05|30"), k("burst|0.05|30")
    none = f"{S[f'clean|{clean}|0.01|pd10']:.2f}" if clean else "--"
    lines.append(f"{lab} & {none} & {cell(c2['pfa'])} & {c2['pd10']:.2f} & {cell(c5['pfa'])} & {c5['pd10']:.2f} & {cell(cb['pfa'])}\\\\")
lines += ["\\bottomrule", "\\end{tabular}"]
open(os.path.join(MAN, "generated", "tab_remedies.tex"), "w", encoding="utf8").write("\n".join(lines) + "\n")

# ---- guard figure: per-look P_d at 10 dB, random and opposite Doppler, g = 0 and 8, with the exploratory law
w = [u["G|clean|0|0.01"][1] for u in U]
pl = lambda key: np.average([u[key] for u in U], axis=0, weights=w)[I10]
# same typeface and styling as Fig. 2 (r12/fig_theory.py): DejaVu Sans, 7.5 pt, light axes; legend outside the data
plt.rcParams.update({"font.family": "sans-serif", "font.size": 7.5, "axes.edgecolor": "#c3c2b7", "axes.labelcolor": "#52514e",
                     "legend.frameon": False, "axes.linewidth": 0.6, "xtick.major.width": 0.6, "ytick.major.width": 0.6})
fig, ax = plt.subplots(figsize=(3.45, 2.35))
ls = np.arange(9)
col = {0: "#52514e", 8: "#2a78d6"}
for g in (0, 8):
    ax.plot(ls, np.mean([u[f"G|law|random|{g}"] for u in U], 0)[I10], color=col[g], lw=0.9, ls="-", alpha=0.6)
    ax.plot(ls, pl(f"G|abrupt|random|{g}|look"), "o", color=col[g], ms=4.2, mfc=col[g] if g else "white", mew=0.9,
            label=f"random Doppler, {'no guard' if g == 0 else 'guard $\\Delta=8$'}")
    ax.plot(ls, pl(f"G|abrupt|opposite|{g}|look"), "^", color=col[g], ms=4.2, mfc=col[g] if g else "white", mew=0.9,
            label=f"opposite Doppler, {'no guard' if g == 0 else 'guard $\\Delta=8$'}")
ax.set_xlabel("Look after onset $\\ell$"); ax.set_ylabel("Per-look $P_{\\rm d}$ (SCR 10 dB)")
ax.set_ylim(-0.03, 1.03); ax.set_xticks(ls); ax.grid(axis="y", color="#e4e3df", lw=0.6)
for sp in ("top", "right"):
    ax.spines[sp].set_visible(False)
ax.legend(fontsize=6.2, frameon=False, loc="upper center", bbox_to_anchor=(0.5, -0.24), ncol=2, columnspacing=1.0, handletextpad=0.3)
fig.tight_layout(pad=0.3)
fig.savefig(os.path.join(MAN, "figures", "fig_guard_col.pdf"))
print("macros:", len(M)); print(open(os.path.join(MAN, "generated", "tab_remedies.tex")).read())
print({k: M[k] for k in list(M)[:14]})
