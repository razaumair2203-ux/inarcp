"""Generate the compact supplement from preserved source fragments and frozen outcomes.

The template fragments below are editorial selections of the frozen R19 text.
Numerical tables are generated from saved JSON, not new experiments. Existing
proofs and five data tables are copied unchanged. Run from any directory.
The old make_supp_sections.py must not be run against the compact source.
"""
from pathlib import Path
import hashlib
import json
import math
import re
import shutil
import numpy as np

REVIEW = Path(__file__).resolve().parent
PKG = REVIEW.parent
# Find the workspace or a fresh public clone; no user-specific absolute fallback.
REPO_ROOT = next((p for p in PKG.parents if (p / "research/r7c").is_dir()
                 or (p / "02_paper_repo_inarcp/research/r7c").is_dir()), None)
if REPO_ROOT is None:
    raise RuntimeError("Run inside the workspace or a full inarcp repository clone")
LIVE = REVIEW / "compact_inputs"
REPO = (REPO_ROOT / "research/r7c" if (REPO_ROOT / "research/r7c").is_dir()
        else REPO_ROOT / "02_paper_repo_inarcp/research/r7c")
OUT = PKG / "supplement"

def read(name):
    return (LIVE / name).read_text(encoding="utf-8")

def span(text, start, end):
    return text[text.index(start):text.index(end)]

def saved(name):
    return json.loads((REPO / name).read_text(encoding="utf-8"))

def table(caption, label, heads, rows):
    return ("\n\\begin{table}[htbp]\n\\centering\\small\\setlength{\\tabcolsep}{4pt}\n"
            + "\\caption{" + caption + "}\\label{" + label + "}\n"
            + "\\begin{tabular}{l" + "c" * (len(heads)-1) + "}\n\\toprule\n"
            + " & ".join(heads) + " \\\\\n\\midrule\n"
            + "\n".join(" & ".join(row) + " \\\\" for row in rows)
            + "\n\\bottomrule\n\\end{tabular}\n\\end{table}\n")

def ci(values):
    return f"{values[0]:.2f} [{values[1]:.2f}, {values[2]:.2f}]"

def endpoint(value):
    if math.isnan(value):
        return "n.r."
    if value == -math.inf or value <= -5:
        return r"$\le-5$"
    if value == math.inf:
        return "n.r."
    return f"{value:.2f}"

NAMES = {
    "ANMF-FP(w)": "ANMF-Tyler", "ANMF-SCM(w)": "ANMF-SCM",
    "CA16": "Power CA", "Clip-OS1": "Clipped, OS scale",
    "D-IN4": "Integration, AR(4)", "IN1": "IN-ARCP", "IN4": "IN-AR(4)",
    "NA4": "NA-AR(4)", "OS1_8": r"OS scale, $k=8$", "OSraw": "Power OS",
    "P-ANMF": "P-ANMF, maximum", "P-ANMF(bin)": "P-ANMF, one bin",
    "PAMF-H(w)": "PAMF-H, one Doppler",
}

def low_rate_table(data, radar, label):
    interval_type = "day" if radar == "IPIX" else "recording"
    s = ("\n% Generated from " + ("r12/r12_summary.json" if radar == "IPIX" else "r15/r15_summary.json")
         + ", Part L. All 13 statistics and residual-bootstrap rows retained.\n"
         + "\\begin{table}[htbp]\n\\centering\\small\n\\caption{" + radar
         + r" pooled $P_{\rm fa}/\alpha$ [95\% " + interval_type
         + r"-cluster interval]. Bold point estimates lie outside $[0.5,2]$. Model rules are those named in the paper's low-rate table.}"
         + "\\label{" + label + "}\n\\begin{tabular}{lcc}\n\\toprule\nStatistic & Conformal & Model-based rule\\\\\n")
    def cell(v):
        vals = [v[0], *v[1]] if radar == "IPIX" else v[:3]
        estimate = f"{vals[0]:.2f}"
        if not .5 <= vals[0] <= 2:
            estimate = r"\textbf{" + estimate + "}"
        return estimate + f" [{vals[1]:.2f}, {vals[2]:.2f}]"
    for alpha, power in [("0.01", "2"), ("0.001", "3"), ("0.0001", "4")]:
        s += r"\midrule\multicolumn{3}{c}{$\alpha=10^{-" + power + r"}$}\\" + "\n"
        for key, name in NAMES.items():
            s += name + " & " + cell(data[key + "|conf|" + alpha]) + " & " + cell(data[key + "|anal|" + alpha]) + " \\\\\n"
        s += "IN-ARCP, residual bootstrap & --- & " + cell(data["IN1|boot|" + alpha]) + " \\\\\n"
    return s + "\\bottomrule\n\\end{tabular}\n\\end{table}\n"


def apply_figure_presentation(text):
    """Add precise references/captions, preserving all existing scientific arrays."""
    edits = json.loads((REVIEW / "supplement_reference_insertions.json").read_text(encoding="utf-8"))
    for info in edits.values():
        if "place_after" in info:
            old = info["place_after"]
            assert text.count(old) == 1, old
            text = text.replace(old, old + "\n" + info["body"])
        if "body_replace" in info:
            old = info["body_replace"]
            assert text.count(old) == 1, old
            text = text.replace(old, info["body_new"])
        if "caption_replace" in info:
            old = info["caption_replace"]
            assert text.count(old) == 1, old
            text = text.replace(old, info["caption_new"])
        if "caption_replace_old_tail" in info:
            old = info["caption_replace_old_tail"]
            assert text.count(old) == 1, old
            text = text.replace(old, info["caption_new_tail"])
        pattern = r"\\includegraphics\[width=[^\]]+\]\{" + re.escape(info["file"]) + r"\}"
        text, count = re.subn(pattern,
            lambda _: r"\includegraphics[width=" + info["width"] + "]{" + info["file"] + "}", text)
        assert count == 1, (info["file"], count)
        blocks = list(re.finditer(r"\\begin\{figure\}.*?\\end\{figure\}", text, re.S))
        block = next(b for b in blocks if "{" + info["file"] + "}" in b[0])
        new = block[0].replace(r"\end{figure}", r"\label{" + info["label"] + "}\n" + r"\end{figure}")
        new = re.sub(r"\\begin\{figure\}\[[^]]+\]", r"\\begin{figure}[htbp]", new)
        text = text[:block.start()] + new + text[block.end():]
    return text

def generate():
    # This is a provenance transformation of a particular R19 snapshot. Fail
    # visibly instead of silently incorporating a later live manuscript.
    expected = {
        "supplement.tex": "1eecd2449aedc50b6b151ca7cdb586962926fc16a179da58fe3f094aa3cd155c",
        "sec_r12_proofs.tex": "f234f25f75713436caed36eac3a36de055dc39bcf2e8815a1d51e239b60a45a3",
        "sec_r14.tex": "316d481b85cbb73ef5e59a06547e9c2ad1a513c761b37a4ab22b5d1aa959e99b",
        "sec_r15.tex": "63d0296406499dd70c0979167eacd8021cecd05a22a1faa511c1028464dd1e8b",
        "sec_r17.tex": "a7b3eda907692648d1ab3e3074292d0afc572192ff80d02cf981e49c625f5ee8",
        "sec_r18.tex": "e18cd126c33417c92dbf47a85c16d4e1ee8e1683f21517715588f1f6864c7fc6",
    }
    for name, digest in expected.items():
        assert hashlib.sha256((LIVE / name).read_bytes()).hexdigest() == digest, f"R19 snapshot changed: {name}"
    OUT.mkdir(parents=True, exist_ok=True)
    original = read("supplement.tex")
    r14 = read("sec_r14.tex")
    r15 = read("sec_r15.tex")
    r17 = read("sec_r17.tex")
    r18 = read("sec_r18.tex")
    R12, R14, R15 = saved("r12/r12_summary.json"), saved("r14/r14_summary.json"), saved("r15/r15_summary.json")
    JKU = saved("r12/r12_jku_summary.json")["R"]
    DET = saved("detection/detection_summary.json")
    header = original[:original.index(r"\begin{document}")]
    header = header.replace(r"\input{verbatim_sizes.tex}", r"""% R20 compact review candidate generated by make_compact_supplement.py.
% Proofs/table inputs are frozen R19 copies; tables below use frozen saved JSON.
\renewcommand{\thetable}{S\arabic{table}}
\renewcommand{\thefigure}{S\arabic{figure}}
\renewcommand{\theequation}{S\arabic{equation}}""")
    chunks = [header, r"""\begin{document}
\sloppy\maketitle
\noindent This supplement supports the paper's conditional laws and measured calibration results. Numerical tables come from frozen saved outcomes; no new radar experiment was run. Protocols, saved summary outputs and plotting arrays are available in the accompanying repository (release \texttt{r21-trs-submission}, \texttt{research/r7c}); Section~\ref{sup:repository} gives their paths. Study labels identify internal hash-recorded protocols, not independent experiments or an external registry. Failed conditions and post-hoc choices remain explicit.
"""]
    exposure = span(original, r"\section{Data exposure}", r"\section{Hold-out series}")
    exposure = exposure.replace("SDRDSP (pending) & Further sea-clutter confirmation & Protocol frozen and hashed before the data were obtained\\\\\n", "")
    chunks += [exposure, span(original, r"\section{Proof of Proposition 2", r"\section{Texture-conditional coverage"), r"\input{sec_r12_proofs.tex}"]
    chunks += [r"""\section{Numerical verification and frozen-output corrections}\label{sup:indep}\label{sup:r12}
The saved \texttt{r12/verify\_laws\_output.txt} contains 400,000-replication Monte Carlo checks. Its 65 primary checks are the rows with $z$-scores excluding bracketed labels: two compound-Gaussian tests of the Gaussian Kraut--Scharf law and four asymptotic fixed-point-law checks. Every primary check lies within three standard errors (maximum $|z|=2.9125$, printed as 2.91); the fixed-point checks have $|z|<1.6$. Beta and certificate rows report distribution agreement or violation rates, not $z$-scores. The compound-Gaussian Kraut--Scharf tests fail 2.8--3.4-fold at $10^{-2}$; this failure remains part of the evidence.

The independent \texttt{r14/theory\_check\_independent.py} imports no implementation of the manuscript laws. Its saved output checks repeated eigenvalues, singular scales, the post-onset law, horizon, tested strong-target OS regime, integration, known-bin P-ANMF, Beta calibration, and certificates under strong, matched and cancelling amplitudes. Bursts calibrated as independent hits violate design (clipped $P_{\rm fa}=0.0114$, binary 0.0192 at design 0.01). Matched burst certificates record no exceedance and lose sensitivity. The separate guarded-AR check has maximum $|z|=2.56$ with 400,000 episodes per point. Protected looks use unchanged tested energy and zero target energy in the history; only the contaminated interval shifts by the guard.

\emph{Two corrections accompany the unchanged full logs.} V8 calibration sizes in \texttt{verify\_laws\_output.txt} came from a faulty search. \texttt{r12/calibration\_size.txt} supersedes them: first acceptable sizes 149, 1,497 and 14,978; permanent cutoffs 313, 3,146 and 31,477 at $\alpha=10^{-2},10^{-3},10^{-4}$. The proof supplies the tail completion. The independent log's $n=23,000$ line checks a formula, not the actual set size. Actual per-look calibration sets contain 17,164--23,130 episodes; their i.i.d. Beta-tail probabilities are about 0.02--0.09. Non-overlap does not imply independence. The R10 ramp log prints R1 as FAILED because a numerical crossing is unavailable when IN-ARCP never reaches $P_{\rm d}=0.5$ by 25~dB; the recorded curves meet that expectation in substance, as Section~\ref{sup:unmet} explains.
"""]
    theory = span(read("sec_dwell.tex"), r"\section{Closed forms", r"\section{Dwell detection")
    chunks += [theory.replace(r"\section{Closed forms", r"\subsection{Closed forms"), r"""\section{False-alarm calibration and pivotality}
Tables~\ref{tab:ipix_ci} and~\ref{tab:netrad_ci} preserve every Part-L ratio and cluster interval, including the residual bootstrap. They are measured pooled rates, not guarantees of exchangeability or equal rates in individual cells. IPIX intervals resample six days; NetRAD intervals resample fourteen recordings. These intervals are approximate. Saturation and ties can make clipped thresholds conservative.
""", low_rate_table(R12["L"], "IPIX", "tab:ipix_ci"), low_rate_table(R15["L"], "NetRAD", "tab:netrad_ci")]
    chunks += [span(r18, r"\subsection{Pivotality across clutter power", r"\subsection{What a cell-wise detector costs}")]
    chunks += [r"\section{Coverage, width and transfer checks}", span(original, r"\section{Synthetic verification}", r"\section{Proof of Proposition 2").replace(r"\section{", r"\subsection{"), span(original, r"\section{Texture-conditional coverage", r"\section{Additional figures").replace(r"\section{", r"\subsection{"), span(original, r"\section{Hold-out series}", r"\section{Summary of the laws}").replace(r"\section{", r"\subsection{")]
    chunks += [r"""\subsection{Dependence, day sensitivity and optimizer diagnostics}
At $\alpha=0.1$, mean lag-one exceedance autocorrelation within an IPIX bin (256-pulse separation) is $-0.007$, with unit range $[-0.067,0.046]$; same-time cross-bin correlation is 0.045. These diagnostics do not prove independence. Observed maximum quintile coverage deviations for IN-ARCP, IN-AR(4), NA-AR(4) and the unnormalized score are 0.036, 0.032, 0.043 and 0.165. The binomial reference is 0.029; dependence-aware time-shift references are 0.033, 0.033, 0.039 and 0.062.

The AR(1) clamp binds in 5 of 56 IPIX units. NA-AR(2) converges in every unit; NA-AR(4) converges in 16 at the 1,500-iteration cap and 55 after a further 4,500 iterations. The exploratory restart changes its radius by geometric factors 0.9989 at coverage 0.90 (unit range 0.9790--1.0132) and 0.9997 at 0.99 (0.9492--1.0327); coverage changes from 0.9019 to 0.9020 and from 0.9905 to 0.9906. Median likelihood gain per training episode is $3.13\times10^{-6}$, maximum $1.54\times10^{-4}$. The median whole-unit GPU time for thirteen procedures is 71~s, not a detector hardware benchmark.
"""]
    rows = []
    for line in read("data/audit_existing.txt").splitlines():
        if "LODO" in line and "fits" not in line:
            left, limits = line.strip().split("LODO", 1)
            name, value = left.rsplit(":", 1)
            for plain, tex in [("Pd=0.5", r"$P_{\rm d}=0.5$"), ("Pd=0.9", r"$P_{\rm d}=0.9$"), ("Pd 0.5", r"$P_{\rm d}=0.5$"), ("Pd 0.9", r"$P_{\rm d}=0.9$"), ("alpha 0.01", r"$\alpha=0.01$")]:
                name = name.replace(plain, tex)
            rows.append([name, value.strip().replace("x", r"$\times$"), limits.strip().replace("..", "--")])
    chunks += [table(r"Leave-one-day-out ranges from \texttt{r10/audit\_existing.txt}. Gains are dB; radius ratio and spread are dimensionless. These complement the approximate six-day cluster intervals.", "tab:lodo", ["Effect", "All six days", "LODO range"], rows), r"""The six daily onset gains of IN-ARCP over local power at $P_{\rm d}=0.5$ are 3.5, 8.4, 13.8, 13.3, 12.2 and 11.4~dB. They should not be read as interchangeable independent replications.

\subsection{Parametric texture and adaptive conformal baselines}
A fitted K-texture law changes NA-AR(4)'s radius by factors 1.0092 [1.0064, 1.0115] at coverage 0.90 and 1.0078 [1.0034, 1.0104] at 0.99; coverage and quintile deviations are essentially unchanged. Within-session ACI with $\gamma=0.005$ or 0.02 gives similar coverage and finite radii; at 0.99, $\gamma=0.02$ gives infinite regions in 0.0115 of episodes. Day-transfer worst coverages improve from 0.8822 for split IN-ARCP to 0.8889 and 0.8965 at coverage 0.90, and from 0.9875 to 0.9889 and 0.9902 at 0.99. Clean-feedback behavior does not establish safety under target-contaminated online feedback: at 5\% contamination ungated ACI gives $0.14\alpha$ with $P_{\rm d}=0.275$ (split: 0.890); gated ACI still gives only $0.55\alpha$ or $0.68\alpha$. Full settings, trajectories and uncertainty remain in the baseline and R10 outputs.

\section{Detection comparisons and target-history contamination}\label{sup:detect}
Injected comparisons share known timing and target-aligned dwells. They test mechanisms, not operational acquisition. The additional detection figure retains the $10^{-3}$ level and full method curves.
\begin{figure}[htbp]\centering\includegraphics[width=.90\textwidth]{fig_detection.pdf}
\caption{Injected Swerling-1 onset detection on IPIX at design false-alarm probabilities 0.01 and 0.001, from the frozen detection output.}\end{figure}
"""]
    rows = []
    for pd in ["0.5", "0.9"]:
        for method in ["IN1", "IN4", "NA4", "G1", "U", "MLP", "LS"]:
            v = DET[f"gain|{method}|0.01|{pd}"]
            rows.append([method, "$"+pd+"$", ci(v["vsCA16"]), ci(v["vsCAloc"])])
    chunks += [table(r"Onset SCR gain at design $P_{\rm fa}=0.01$: mean per-unit gain [95\% day-cluster interval], from \texttt{detection/detection\_summary.json}. Positive means less SCR. Local power uses the non-causal $\pm1024$-pulse window.", "tab:onset_gains", ["Method", "$P_{\\rm d}$", "Gain over CA16 (dB)", "Gain over local power (dB)"], rows)]
    chunks += [read("sec_dwell.tex")[read("sec_dwell.tex").index(r"\section{Dwell detection"):], r"""PAMF-H has the best tested dwell sensitivity. Its endpoint at the lowest tested SCR makes the ANMF-Tyler gap of 5.36 [1.93, 8.83]~dB a lower bound. Clipping costs 2.04 [0.00, 2.90]~dB against AR(1) integration; the onset raw-power-OS/IN-ARCP gap is 10.62 [7.05, 12.69]~dB. The earlier R10 equal-dwell comparison gives PAMF-H a 1.0 [0.3, 1.7]~dB advantage over integrated IN-ARCP at $P_{\rm d}=0.5$ (about 4~dB at 0.9); the studies have separate calibrations. A Hann-windowed range-CA Doppler bank needs @@HANN_GAP@@~dB more SCR than integrated IN-ARCP. PAMF-H's matched-Doppler cost in that study is 4.25~dB.
"""]
    chunks += [r14[:r14.index(r"\noindent Output of")].replace("% Generated by analysis_provenance/make_supp_sections.py from the saved outcomes. Do not edit.\n", "")]
    rows = []
    for radar, data in [("IPIX", R14), ("NetRAD", R15)]:
        for guard in [0, 8, 16]:
            rows.append([radar, str(guard), ci(data[f"G|pfa|{guard}|0.01"]), ci(data[f"G|pfa|{guard}|0.001"]), *[f"{np.mean(data[f'G|look10|{doppler}|{guard}'][1:9]):.2f}" for doppler in ["random", "opposite", "matched"]]])
    chunks += [table(r"Guarded scale: clean rate ratio [cluster interval], and mean per-look $P_{\rm d}$ over looks 1--8 at 10~dB. R14 IPIX and R15 NetRAD; these eight looks do not measure post-guard persistence.", "tab:guards", ["Radar", "$\\Delta$", "$\\alpha=10^{-2}$", "$10^{-3}$", "Random", "Opposite", "Matched"], rows)]
    rows = []
    for radar, data in [("IPIX", R14), ("NetRAD", R15)]:
        for length in [8, 16]:
            rows.append([radar, str(length), *[f"{data[f'G|ramp{length}|cum8@10|{guard}']:.3f}" for guard in [0, 8, 16]]])
    chunks += [table(r"Detection within eight looks for linear emergence, 10~dB SCR and design $P_{\rm fa}=0.01$.", "tab:ramps", ["Radar", "Ramp length", "$\\Delta=0$", "$8$", "$16$"], rows), r"""The earlier pre-onset ramp comparison, corrected R10 verdict, and all R11 failed expectations remain in Section~\ref{sup:unmet}. Exact ramp-law error is 0.016, within the 0.03 expectation. The exploratory post-onset law has mean per-unit/look errors 0.010, 0.003 and 0.008 for random, matched and opposite Doppler. Cumulative-null and equal-dwell comparisons remain in the full onset outputs. The R11 median OS score has onset cost 1.99 [0.89, 3.39]~dB, quintile spread 2.06 and coverage-law error 0.0214; these miss the stated tolerances.
"""]
    rows = []
    for clip in [4, 6, 9, 12, 18]:
        rows.append([str(clip), ci(R14[f"K|clean|{clip}|0.01"]), ci(R14[f"K|clean|{clip}|0.001"])])
    chunks += [table(r"Clean clipped integration, IPIX R14 dense calibration: rate ratio [95\% day-cluster interval].", "tab:clip_scan", ["$\\kappa$", "$\\alpha=10^{-2}$", "$10^{-3}$"], rows)]
    chunks += ["The pre-specified saturation rule chooses $\\kappa=9$ in 17 of 56 units at $10^{-3}$ and finds no eligible tested level ($\\kappa\\le18$) in 16. Applying $\\kappa=9$ to every unit is post hoc: at $10^{-3}$ it changes 10-dB detection from " + f"{R14['clean|clip6|0.001|pd10']:.2f}" + " to " + f"{R14['clean|clip9|0.001|pd10']:.2f}" + ". Sparse R12 and dense R14 calibrations are separate analyses; their endpoints must not be combined.\n"]
    for alpha, apower in [("0.01", "2"), ("0.001", "3")]:
        rows = []
        for hit in ["0.02", "0.05"]:
            for power in ["10", "30"]:
                trimmed = {("0.02", "0.01"):4, ("0.05", "0.01"):5, ("0.02", "0.001"):5, ("0.05", "0.001"):6}[(hit, alpha)]
                for method, label in [("clean-thr clip6", "Clean clip6"), ("cert(bern) clip6", "Certified clip6"), ("cert(bern) clip9", "Certified clip9"), (f"cert(bern) trim t={trimmed}", f"Certified trim{trimmed}"), ("blank(bern masks)", "Blanking")]:
                    v = R14[f"bern|{hit}|{power}|{alpha}|{method}"]
                    rows.append([f"{int(float(hit)*100)}\\%", power, label, ci([v["pfa"], v["lo"], v["hi"]]), f"{v['pd10']:.2f}", f"{v['pd25']:.2f}"])
        chunks += [table(r"IPIX independent-hit remedies at $\alpha=10^{-" + apower + r"}$: rate ratio [95\% day-cluster interval], detection at 10 and 25~dB SCR. R14 dense calibration; interference is 10 or 30~dB above local power. Certificate calibration uses matching independent hits.", "tab:remedies_"+apower, ["Hit rate", "JNR (dB)", "Statistic", "Rate ratio", "$P_{\\rm d}(10)$", "$P_{\\rm d}(25)$"], rows)]
    rows = []
    for hit in ["0.02", "0.05"]:
        for alpha in ["0.01", "0.001"]:
            for method, label in [("clean-thr clip6", "Clean clip6"), ("cert(bern) clip6", "Independent-hit cert., clip6"), ("cert(bern) clip9", "Independent-hit cert., clip9"), ("cert(burst) clip6", "Burst certificate, clip6"), ("blank(bern masks)", "Blanking, independent masks"), ("blank(burst masks)", "Blanking, burst masks")]:
                v = R14[f"burst|{hit}|30|{alpha}|{method}"]
                rows.append([f"{int(float(hit)*100)}\\%", "$10^{-2}$" if alpha=="0.01" else "$10^{-3}$", label, ci([v["pfa"], v["lo"], v["hi"]]), f"{v['pd10']:.2f}"])
    chunks += [table(r"Eight-pulse bursts on IPIX at JNR 30~dB: both hit rates and both design rates, including burst-matched calibration. Burst certificates also detect no target at 25~dB.", "tab:bursts", ["Hit rate", "$\\alpha$", "Statistic", "Rate ratio [95\\% CI]", "$P_{\\rm d}(10)$"], rows), r"""At $10^{-3}$ and 5\% independent hits, every tested clip certificate is vacuous. At $10^{-2}$ and 5\% hits, trimming costs 5.1~dB versus clipping's 5.9~dB for $\kappa=6$, contrary to the expectation that trimming costs more. Fixed-SCR detection is clearer because the certified curves are nearly flat. Burst-matched trimming has no usable choice. The R12 sparse-calibration binary certificate has 10-dB detection within 0.03 of certified clipping at both tested rates and powers. At design $\alpha=10^{-2}$, uncertified integration and PAMF-H exceed design 10--23-fold, while self-normalized statistics stay within 1.21 times design at a sensitivity cost. Full clip grids, SCR costs and sparse-calibration rows remain in the frozen outputs.
""", r18[r18.index(r"\subsection{Pulse blanking: the thresholds}"):].replace("Moved here from Section~\\ref{M-sec:model} of the paper. ", "")]
    chunks += [r"""\section{77~GHz thermal-noise and real-interference checks}\label{sup:jkusel}
Range bins 8--247 and receivers 0, 5, 10 and 15 of both stations are used. The general-form gain curve is post hoc. IN-ARCP's gain over local power rises from $-1.45$~dB in noise-dominated cells to 3.11~dB at 10--20~dB CNR. Only 338 test episodes from two units occupy the highest CNR class, versus 721,095 in the lowest. At design 0.01 its CNR-class rate ratios are 1.07, 1.06, 0.95, 0.52, 0.08 and 0 across $<-5$, $[-5,0)$, $[0,5)$, $[5,10)$, $[10,20)$ and $\ge20$~dB; the support is uneven.
\begin{figure}[htbp]\centering\includegraphics[width=.90\textwidth]{fig_jku.pdf}
\caption{77~GHz ground-clutter coverage by CNR class and SCR gain over local power. The general-form gain interpretation is post hoc.}\end{figure}

For real interference, calibration masks are random 24-chirp blocks from frames 0--49; tests use frames 50--99. N: no fast-time mitigation; Z: zeroing; ZAR: zeroing with AR(8) reconstruction. Test hit rates are 45.4\% in dense A and 4.6\% in sparse C. The empirical masks do not establish exchangeability, clutter independence or inclusion dominance. In sparse C without mitigation, integration runs at 3.56 times design in the 1--2-hit stratum. The clipped certificate costs 3.1~dB on hit-free segments and 6.4~dB overall against clean-threshold clipping. In dense A it never reaches $P_{\rm d}=0.5$ overall. AR reconstruction improves IN-ARCP SCR50 by only 0.18~dB, below the expected 1~dB.
"""]
    rows = []
    for run in ["ref", "A", "C"]:
        for mitigation in ["N", "Z", "ZAR"]:
            for method, name in [("D-IN1", "Integration"), ("Clip-OS1", "Clean clip"), ("Clip-OS1-cert", "Certified clip"), ("Bin-OS1-cert", "Certified binary")]:
                v = JKU[f"{run}|{mitigation}|{method}"]
                rows.append([run, mitigation, name, f"{v['pfa']['all']/.01:.2f}", endpoint(v["scr50"]["all"]), endpoint(v["scr50"]["s0"])])
    chunks += [table(r"Real 77~GHz interference, $\alpha=0.01$: all three mitigations. The last column is the hit-free stratum, not a confidence interval; n.r.: not reached in the tested SCR range. Full per-hit-stratum counts and ratios remain in \texttt{r12/r12\_jku\_summary.txt}.", "tab:jku_interference", ["Run", "Mitigation", "Statistic", "Rate ratio", "SCR50 all", "SCR50 clean"], rows)]
    chunks += [span(r14, r"\section{The real IPIX target", r"\section{77~GHz data:"), r"""History-normalized IN-ARCP and clipping exceed on the primary target cell at only 0.0004 at design $10^{-3}$. This supports full-history self-masking, not real-onset validation. The long-dwell P-ANMF rate exceeds twice design; no i.i.d. Beta guarantee follows for the overlapping real-data windows. The one-second comparison with target-trained literature is descriptive because training and evaluation protocols differ.
""", r15[:r15.index(r"\noindent Output of")].replace("% Generated by analysis_provenance/make_supp_sections.py from the saved outcomes. Do not edit.\n", ""), r"""The full pooled low-rate intervals remain in Table~\ref{tab:netrad_ci}; removing hotspot units is not used to replace the headline results. At $10^{-3}$ the flagged-pulse certificate is wholly vacuous, whereas mask-matched blanking has rate ratio 0.24 (upper recording-cluster bound 0.49) and $P_{\rm d}=0.83$. Flag origin, unexplained excesses and the weak burst remedy remain unresolved.
""", r17[:r17.index("Output of")]]
    chunks += [table(r"Pedestrian primary onsets after zeroing: 74 onsets in seven blocks. All results are descriptive. Detection within three frames, event mean [block-bootstrap interval] at design $10^{-2}$; intervals are understated with seven blocks.", "tab:pedestrian", ["Statistic", "Rate ratio $10^{-2}$", "$P_{\\rm d}$ [interval]", "$P_{\\rm d}$ at $10^{-3}$"], [["IN-ARCP", "0.96", "0.297 [0.165, 0.441]", "0.172"], ["Power clutter map", "0.98", "0.274 [0.138, 0.418]", "0.149"], ["OS clutter map", "0.96", "0.231 [0.105, 0.372]", "0.128"], ["Range CA-CFAR", "1.10", "0.074 [0.018, 0.163]", "0.024"]]), r"""The descriptive IN-ARCP/clutter-map difference is 0.024 [0.007, 0.047]. The raw log's apparent superiority does not override failed E1. Differences against OS and range CA are 0.067 [0.046, 0.091] and 0.223 [0.131, 0.349]. The high/low static-to-noise halves contain 37 onsets each, with differences 0.047 and 0.000 (high-minus-low descriptive interval [0.008, 0.096]). Without zeroing, three-frame detection is 0.162 for IN-ARCP and 0.149 for the clutter map; summing sixteen chirps after zeroing gives 0.243 and 0.209. Secondary-event results, onset-frame endpoints, null floors and other variants remain in the full R17 output. None establishes independent maritime onset performance.

\section{Operating regime and deployment cost}\label{sup:r18}
These passages interpret existing outcomes and arithmetic, not new performance measurements.
""", span(r18, r"\subsection{The operating regime", r"\subsection{Pivotality"), span(r18, r"\subsection{What a cell-wise detector costs}", r"\subsection{Pulse blanking")]
    chunks += [r"""\section{Complete frozen outputs and protocols}\label{sup:repository}
Saved summary outputs and machine-readable plotting inputs are available in the repository. Raw recordings and per-episode NPZ intermediates are not bundled. The original intermediate arrays are retained in the local study archive; reproducing them requires the provider data and study code. Failed conditions, ambiguous attribution, censored endpoints and superseded log values remain accessible. The two corrections in Section~\ref{sup:indep} accompany reuse. The PDF retains every low-rate Part-L ratio and interval, but does not transcribe every per-SCR grid, order, clip setting or diagnostic variant. These extra numerical entries were not independently recomputed in this revision.

\noindent Repository base: \url{https://github.com/razaumair2203-ux/inarcp/tree/r21-trs-submission/research/r7c}.
\begin{itemize}\setlength{\itemsep}{1pt}\setlength{\parsep}{0pt}\setlength{\topsep}{4pt}
\item Main protocol: \texttt{PROTOCOL.md}; detection/onset protocols: \texttt{detection/PROTOCOL\_DETECTION.md}, \texttt{PROTOCOL\_ONSET.md}; baselines: \texttt{baselines/PROTOCOL\_BASELINES.md}; reference radar: \texttt{jku/PROTOCOL\_JKU.md}.
\item R10--R15 and R17: \texttt{r10/PROTOCOL\_R10.md} through \texttt{r15/PROTOCOL\_R15.md} for the studies reported here (R10, R11, R12, R14, R15), and \texttt{r17/PROTOCOL\_R17.md}; verdicts are the corresponding \texttt{RESULTS\_R*.md}. NetRAD deviations: \texttt{r15/DEVIATIONS\_R15.md}; pedestrian mechanics check: \texttt{r17/MECHANICS\_R17.txt}.
"""]
    mapping = {
        "audit_existing": "r10/audit_existing.txt", "baselines_summary": "baselines/baselines_summary.txt",
        "detection_summary": "detection/detection_summary.txt", "dwell_summary": "detection/dwell_summary.txt",
        "jku_summary": "jku/jku_summary.txt", "na4_convergence": "r10/na4_convergence.txt",
        "onset_summary": "detection/onset_summary.txt", "onset_theory": "detection/onset_theory.json",
        "r10_summary": "r10/r10_summary.txt", "r11_summary": "r11/r11_summary.txt",
        "r12_jku_summary": "r12/r12_jku_summary.txt", "r12_summary": "r12/r12_summary.txt",
        "r14_summary": "r14/r14_summary.txt", "r15_attribution": "r15/explore_r15_attribution_output.txt",
        "r15_flag_extent": "r15/explore_r15_flag_extent_output.txt", "r15_hotspots": "r15/explore_r15_hotspots_output.txt",
        "r15_summary": "r15/r15_summary.txt", "r17_summary": "study/results/r17/r17_summary.txt",
        "theory_check_guard": "r14/theory_check_guard_output.txt",
        "theory_check_independent_output": "r14/theory_check_independent_output.txt",
        "theory_checks_output": "detection/theory_checks_output.txt", "theory_os_output": "r11/theory_os_output.txt",
        "theory_ramps": "r10/theory_ramps.txt", "verify_laws_output": "r12/verify_laws_output.txt",
    }
    groups = {}
    for stem, path in mapping.items():
        assert (REPO / path).is_file(), path
        parent, name = path.rsplit("/", 1)
        groups.setdefault(parent, []).append(name)
    for directory, filenames in groups.items():
        chunks.append(r"\item \texttt{" + directory.replace("_", r"\_") + "/}: " + "; ".join(r"\texttt{" + name.replace("_", r"\_") + "}" for name in filenames) + ".")
    bibliography = original[original.index(r"\begin{thebibliography}"):]
    chunks += [r"\item Corrected calibration sizes: \texttt{r12/calibration\_size.txt}.", r"\end{itemize}", bibliography]
    full = "\n".join(chunks)
    # These retained R19 locators referred to terminal dumps now in the index.
    old_r10 = "The R10 output below prints expectation R1 as FAILED."
    assert full.count(old_r10) == 1
    full = full.replace(old_r10, r"The frozen \texttt{r10/r10\_summary.txt} prints expectation R1 as FAILED.")
    assert full.count("(Part W below)") == 1
    full = full.replace("(Part W below)", r"(\texttt{r15/r15\_summary.txt}, Part W)")
    # Use the actual paired comparison, not a subtraction of rounded gains to
    # a third comparator. This also retains its saved bootstrap interval.
    hann = saved("r10/r10_summary.json")["C|gain|IN1sum-MTDhann|K8|0.5"]
    assert full.count("@@HANN_GAP@@") == 1
    full = full.replace("@@HANN_GAP@@", f"{hann[0]:.1f} [{hann[1]:.1f}, {hann[2]:.1f}]")
    assert r"\dataverb" not in full
    for name in ["sec_r12_proofs.tex", "tab_main.tex", "tab_holdout.tex", "tab_transfer.tex", "tab_dwell.tex", "tab_target.tex"]:
        shutil.copyfile(LIVE / name, OUT / name)
    full = apply_figure_presentation(full)
    (OUT / "supplement.tex").write_text(full, encoding="utf-8")
    print("Wrote", OUT / "supplement.tex", len(full), "characters")
    # References needed by the parent manuscript can be fixed without a circular aux dependency.
    counter = 0
    for block in re.split(r"(?=\\begin\{table\})", full):
        if block.startswith(r"\begin{table}"):
            counter += 1
            print(f"Table S{counter}:", re.findall(r"\\label\{([^}]+)\}", block)[:2])
    print("Frozen proofs copied byte-for-byte; numerical tables use no new outcome computation.")

if __name__ == "__main__":
    generate()
