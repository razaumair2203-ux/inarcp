"""Generate every R7 manuscript number and table from saved analysis outputs (no typed-in values).
Inputs: research/r7c/study/results/confirmatory/{analysis.json, unit_stats_cache.json, c5_transfer.json,
analysis_w512.json, analysis_w2048.json}, research/r7c/study/results/holdout/holdout_summary.json,
research/r7c/synthetic/synthetic_results.json, research/r7c/study/results/confirmatory/transfer_*.npz.
Outputs: generated/r7_macros.tex, generated/tab_main.tex, generated/tab_transfer.tex, generated/tab_holdout.tex."""
import os, json, glob
import numpy as np

HERE = os.path.dirname(os.path.abspath(__file__))
R7C = os.path.normpath(os.path.join(HERE, "..", "..", "research", "r7c"))
CONF = os.path.join(R7C, "study", "results", "confirmatory")
OUT = os.path.join(HERE, "generated"); os.makedirs(OUT, exist_ok=True)
ana = json.load(open(os.path.join(CONF, "analysis.json")))
rows = json.load(open(os.path.join(CONF, "unit_stats_cache.json")))
macros = {}


def mac(name, value, fmt="{:.3f}"):
    macros[name] = fmt.format(value) if not isinstance(value, str) else value


def key(stage, m, a, mth):
    return ana[f"{stage}|{m}|{a}|{mth}"]


# ---- primary numbers ----
for m in (8, 16):
    for a, at in ((0.1, "A"), (0.01, "B")):
        for mth in ("IN1", "NA4", "NA2", "IN4", "IN2", "NA1", "LS", "G1", "MON", "U", "RMS", "MLP", "NA4G", "NA1G"):
            k = key("confirmatory", m, a, mth); tag = f"{mth}m{'Eight' if m == 8 else 'Sixteen'}{at}".replace("1", "One").replace("2", "Two").replace("4", "Four")
            mac(f"Ratio{tag}", k["gm_ratio"][0]); mac(f"RatioLo{tag}", k["gm_ratio"][1]); mac(f"RatioHi{tag}", k["gm_ratio"][2])
            mac(f"Cov{tag}", k["cover_mean"]); mac(f"CovMin{tag}", k["cover_min"])
            mac(f"Maxdev{tag}", k["maxdev"][0]); mac(f"Ref{tag}", k["ref"])
            mac(f"Noisy{tag}", k["gm_noisy"]); mac(f"Clean{tag}", k["gm_clean"])
            U = [r for r in rows if r["rot"] in (2, 3) and r["m"] == m and r["alpha"] == a and r["method"] == mth]
            mac(f"Below{tag}", 100 * np.mean([u["cover"] < 1 - a - 0.02 for u in U]), "{:.0f}")
            curve = key("confirmatory", m, a, mth)["curve"]
            mac(f"CurveLow{tag}", curve[0]); mac(f"CurveHigh{tag}", curve[-1])
mac("NNoisyConf", key("confirmatory", 16, 0.1, "NA4")["n_noisy"], "{:d}")
mac("NCleanConf", key("confirmatory", 16, 0.1, "NA4")["n_clean"], "{:d}")
mac("NUnitsConf", len([r for r in rows if r["rot"] in (2, 3) and r["m"] == 16 and r["alpha"] == 0.1 and r["method"] == "IN1"]), "{:d}")

# ---- main table (m=16) ----
names = [("NA4", "Noise-aware AR(4) (proposed)"), ("NA2", "Noise-aware AR(2) (proposed)"), ("IN4", "AR(4), innovation-normalized"),
         ("IN2", "AR(2), innovation-normalized"), ("NA1", "Noise-aware AR(1)"), ("IN1", "IN-ARCP, AR(1) [R6]"),
         ("G1", "Gaussian plug-in of IN-ARCP"), ("MON", "Mondrian IN-ARCP"), ("LS", "Learned-scale CP"),
         ("MLP", "Invariant MLP CP"), ("RMS", "Raw-RMS normalized CP"), ("U", "Unnormalized CP"), ("NA4G", "Gaussian plug-in of NA4")]
lines = [r"\begin{tabular}{lcccccc}", r"\toprule",
         r" & \multicolumn{3}{c}{$1-\alpha=0.90$} & \multicolumn{3}{c}{$1-\alpha=0.99$}\\",
         r"\cmidrule(lr){2-4}\cmidrule(lr){5-7}",
         r"Method & Radius ratio [95\% CI] & Coverage & Max.\ dev. & Radius ratio [95\% CI] & Coverage & Max.\ dev.\\", r"\midrule"]
for code, lab in names:
    cells = []
    for a in (0.1, 0.01):
        k = key("confirmatory", 16, a, code)
        ci = "---" if code == "IN1" else f"{k['gm_ratio'][0]:.3f} [{k['gm_ratio'][1]:.3f}, {k['gm_ratio'][2]:.3f}]"
        cells += [ci if code != "IN1" else "1", f"{k['cover_mean']:.3f}", f"{k['maxdev'][0]:.3f}"]
    lines.append(lab + " & " + " & ".join(cells) + r"\\")
ref1 = key("confirmatory", 16, 0.1, "IN1")["ref"]; ref2 = key("confirmatory", 16, 0.01, "IN1")["ref"]
lines += [r"\midrule", f"Sampling-noise reference for max.\\ dev. & & & {ref1:.3f} & & & {ref2:.3f}\\\\", r"\bottomrule", r"\end{tabular}"]
open(os.path.join(OUT, "tab_main.tex"), "w").write("\n".join(lines) + "\n")

# ---- transfer table ----
T = {}
for p in sorted(glob.glob(os.path.join(CONF, "transfer_*.npz"))):
    d = np.load(p); day, m = os.path.basename(p)[9:-4].rsplit("_m", 1)
    for a in (0.1, 0.01):
        base = d[f"IN1|{a}|radius"].mean()
        for code, _ in names:
            T.setdefault((int(m), a, code), []).append((float(d[f"{code}|{a}|cover"].mean()), float(d[f"{code}|{a}|radius"].mean() / base)))
lines = [r"\begin{tabular}{lccc}", r"\toprule", r"Method & Mean coverage & Worst held-out day & Radius ratio\\", r"\midrule"]
for code, lab in names:
    v = np.array(T[(16, 0.1, code)])
    lines.append(f"{lab} & {v[:,0].mean():.3f} & {v[:,0].min():.3f} & {np.exp(np.log(v[:,1]).mean()):.3f}\\\\")
    if code in ("IN1", "NA4", "LS", "MLP", "U", "RMS", "IN4", "NA4G"):
        tg = code.replace("1", "One").replace("4", "Four")
        mac(f"TrWorst{tg}", v[:, 0].min()); mac(f"TrRatio{tg}", np.exp(np.log(v[:, 1]).mean()))
lines += [r"\bottomrule", r"\end{tabular}"]
open(os.path.join(OUT, "tab_transfer.tex"), "w").write("\n".join(lines) + "\n")

# ---- C5 ----
c5 = json.load(open(os.path.join(CONF, "c5_transfer.json")))
for a, at in ((0.1, "A"), (0.01, "B")):
    R = [r for r in c5 if r["alpha"] == a]; p = np.array([r["predicted"] for r in R]); o = np.array([r["observed"] for r in R])
    mac(f"CFiveMae{at}", np.mean(abs(p - o)), "{:.4f}"); mac(f"CFiveNaive{at}", np.mean(abs(o - (1 - a))), "{:.4f}")
    mac(f"CFiveCorr{at}", np.corrcoef(p, o)[0, 1], "{:.2f}")

# ---- hold-out ----
H = json.load(open(os.path.join(R7C, "study", "results", "holdout", "holdout_summary.json")))
lines = [r"\begin{tabular}{lcccc}", r"\toprule", r" & \multicolumn{2}{c}{$m=8$} & \multicolumn{2}{c}{$m=16$}\\",
         r"\cmidrule(lr){2-3}\cmidrule(lr){4-5}", r"Method & Radius ratio & Coverage (min) & Radius ratio & Coverage (min)\\", r"\midrule"]
for code, lab in names:
    cells = []
    for m in (8, 16):
        U = [h for h in H if h["m"] == m and h["alpha"] == 0.1 and h["method"] == code]
        r = np.exp(np.mean(np.log([u["ratio"] for u in U]))); c = np.array([u["cover"] for u in U])
        cells += [f"{r:.3f}", f"{c.mean():.3f} ({c.min():.3f})"]
        if m == 16:
            tg = code.replace("1", "One").replace("4", "Four").replace("2", "Two")
            mac(f"HoRatio{tg}", r); mac(f"HoCov{tg}", c.mean())
    lines.append(lab + " & " + " & ".join(cells) + r"\\")
lines += [r"\bottomrule", r"\end{tabular}"]
open(os.path.join(OUT, "tab_holdout.tex"), "w").write("\n".join(lines) + "\n")
mac("HoMonInf", "infinite" if any(np.isinf(h["ratio"]) for h in H if h["method"] == "MON" and h["alpha"] == 0.01) else "finite", "{}")

# ---- synthetic ----
S = json.load(open(os.path.join(R7C, "synthetic", "synthetic_results.json")))
for arm in ("sirv", "noise"):
    rs = [r for r in S if r["arm"] == arm and r["m"] == 16]
    by = np.mean([r["IN1"]["by"] for r in rs], 0); ex = np.mean([r["IN1_exact_by"] for r in rs], 0)
    d = np.array([r["IN1"]["by"] for r in rs]) - np.array([r["IN1_exact_by"] for r in rs])
    t = abs(d.mean(0)) / (d.std(0) / np.sqrt(len(rs)))
    A = "Sirv" if arm == "sirv" else "Noise"
    mac(f"Syn{A}InLow", by[0]); mac(f"Syn{A}InHigh", by[-1]); mac(f"Syn{A}MaxT", t.max(), "{:.2f}")
    mon = np.mean([r["MON"]["by"] for r in rs], 0); mac(f"Syn{A}MonLow", mon[0]); mac(f"Syn{A}MonHigh", mon[-1])
    if arm == "noise":
        na = np.mean([r["NA1"]["by"] for r in rs], 0); mac("SynNaLow", na[0]); mac("SynNaHigh", na[-1])
        mac("SynNaGCov", np.mean([r["NA1G"]["cover"] for r in rs])); mac("SynNaRatio", np.mean([r["NA1"]["radius"] / r["IN1"]["radius"] for r in rs]))
        f = np.array([r["na_fit"] for r in rs]); mac("SynRhoHat", np.mean(np.hypot(f[:, 0], f[:, 1]))); mac("SynNuHat", f[:, 2].mean())
mac("SynReps", len([r for r in S if r["arm"] == "noise" and r["m"] == 16]), "{:d}")

# ---- sensitivity windows ----
for w in (512, 2048):
    p = os.path.join(CONF, f"analysis_w{w}.json")
    if os.path.exists(p):
        aw = json.load(open(p))
        for mth in ("IN1", "NA4", "U", "MLP", "RMS", "MON"):
            tg = mth.replace("1", "One").replace("4", "Four")
            mac(f"Maxdev{tg}W{ {512: 'FiveTwelve', 2048: 'TwentyFortyEight'}[w] }", aw[f"confirmatory|16|0.1|{mth}"]["maxdev"][0])

with open(os.path.join(OUT, "r7_macros.tex"), "w") as fh:
    for k, v in sorted(macros.items()):
        fh.write(f"\\newcommand{{\\{k}}}{{{v}}}\n")
print(len(macros), "macros; tables written to", OUT)
