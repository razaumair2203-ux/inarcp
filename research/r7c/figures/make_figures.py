"""Publication figures from saved records only (no refitting). Outputs PDF + PNG in this folder.
Palette: validated reference categorical slots (light mode); every series also has a distinct
marker/linestyle and a direct label (greyscale-safe; relief for sub-3:1 slots)."""
import os, json
import numpy as np
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
import matplotlib.ticker
OFF = {0.1: {"NA2": (3, -9), "NA1": (-14, -10), "G1": (3, -9)}, 0.01: {"NA2": (3, -9), "NA1": (-6, 5), "IN4": (2, -11), "G1": (3, -10), "IN1": (3, 4)}}

HERE = os.path.dirname(os.path.abspath(__file__)); R7 = os.path.dirname(HERE)
RES = os.path.join(R7, "study", "results", "confirmatory")
S = ["#2a78d6", "#eb6834", "#1baf7a", "#eda100", "#e87ba4", "#008300"]
INK, INK2, MUTED, GRID, AXIS = "#0b0b0b", "#52514e", "#898781", "#e1e0d9", "#c3c2b7"
plt.rcParams.update({"font.family": "sans-serif", "font.size": 8, "axes.edgecolor": AXIS, "axes.labelcolor": INK2,
                     "xtick.color": MUTED, "ytick.color": MUTED, "axes.grid": True, "grid.color": GRID,
                     "grid.linewidth": 0.5, "axes.spines.top": False, "axes.spines.right": False,
                     "legend.frameon": False, "lines.linewidth": 2, "savefig.dpi": 300})


def save(fig, name):
    fig.savefig(os.path.join(HERE, name + ".pdf"), bbox_inches="tight")
    fig.savefig(os.path.join(HERE, name + ".png"), bbox_inches="tight")
    plt.close(fig)


rows = json.load(open(os.path.join(RES, "unit_stats_cache.json")))
ana = json.load(open(os.path.join(RES, "analysis.json")))
conf = [r for r in rows if r["rot"] in (2, 3)]

# ---- Fig 1: texture-conditional coverage (confirmatory, m=16), two alphas ----
series = [("IN1", "IN-ARCP (R6)", S[0], "o", "-"), ("NA4", "Noise-aware AR(4)", S[1], "s", "-"),
          ("MON", "Mondrian IN-ARCP", S[2], "^", "--"), ("U", "Unnormalized CP", S[3], "D", ":"),
          ("RMS", "Raw-RMS normalized CP", S[4], "v", "-."), ("MLP", "Invariant MLP CP", S[5], "P", (0, (5, 1)))]
fig, axes = plt.subplots(1, 2, figsize=(7.0, 2.7))
for ax, al in zip(axes, (0.1, 0.01)):
    x = np.arange(1, 6)
    ref = np.mean([r["ref"] for r in conf if r["m"] == 16 and r["alpha"] == al and r["method"] == "IN1"])
    ax.axhspan(1 - al - ref, 1 - al + ref, color=GRID, alpha=0.6, lw=0)
    ax.axhline(1 - al, color=AXIS, lw=1)
    for code, lab, col, mk, ls in series:
        c = np.mean([r["by"] for r in conf if r["m"] == 16 and r["alpha"] == al and r["method"] == code], 0)
        ax.plot(x, c, color=col, marker=mk, ms=5, ls=ls, lw=1.6, label=lab)
    ax.set_xticks(x, ["1\n(lowest)", "2", "3", "4", "5\n(highest)"])
    ax.set_xlabel("Texture quintile (local clutter power)"); ax.set_title(f"Nominal {1-al:.2f}", color=INK, fontsize=9)
    ax.set_ylabel("Coverage")
axes[0].set_ylim(0.72, 1.0); axes[1].set_ylim(0.945, 1.0)
h, l = axes[0].get_legend_handles_labels()
fig.tight_layout(rect=[0, 0.2, 1, 1]); fig.legend(h, l, loc="lower center", ncol=3, bbox_to_anchor=(0.5, 0.04))
fig.text(0.5, 0.0, "Shaded band: expected maximum quintile deviation from sampling noise alone. IPIX, confirmatory rotations, m = 16.",
         ha="center", color=MUTED, fontsize=7)
save(fig, "fig_texture_conditional")

# ---- Fig 2: per-unit radius ratios by noise regime (confirmatory, m=16, alpha=.1) ----
meths = [("NA4", "NA-AR(4)"), ("NA2", "NA-AR(2)"), ("IN4", "AR(4)"), ("NA1", "NA-AR(1)"), ("LS", "Learned scale"), ("G1", "Gaussian\nplug-in")]
fig, ax = plt.subplots(figsize=(7.0, 2.8)); rng = np.random.default_rng(0)
for i, (code, lab) in enumerate(meths):
    U = [r for r in conf if r["m"] == 16 and r["alpha"] == 0.1 and r["method"] == code]
    for regime, col, mk, off in (("noise-affected", S[1], "s", -0.15), ("clean", S[0], "o", 0.15)):
        v = [u["ratio"] for u in U if (u["noise_index"] > 0.01) == (regime == "noise-affected")]
        ax.scatter(i + off + rng.uniform(-0.07, 0.07, len(v)), v, s=14, color=col, marker=mk, edgecolor="white", lw=0.4,
                   label=regime if i == 0 else None, zorder=3)
    g = ana[f"confirmatory|16|0.1|{code}"]["gm_ratio"]
    ax.errorbar(i, g[0], yerr=[[g[0] - g[1]], [g[2] - g[0]]], fmt="_", color=INK, ms=16, mew=2, capsize=3, zorder=4)
ax.axhline(1, color=AXIS, lw=1); ax.set_yscale("log"); ax.yaxis.set_minor_formatter(matplotlib.ticker.NullFormatter()); ax.set_yticks([0.5, 0.7, 0.85, 1, 1.2], ["0.5", "0.7", "0.85", "1", "1.2"])
ax.set_xticks(range(len(meths)), [l for _, l in meths]); ax.set_ylabel("Mean radius / IN-ARCP (log)")
ax.legend(title="Session regime (dots = session-channel-rotation units)", loc="upper left", ncol=2, fontsize=7, title_fontsize=7)
ax.text(len(meths) - 0.5, 0.52, "black bar: geometric mean, 95% day-cluster bootstrap CI", ha="right", color=MUTED, fontsize=7)
save(fig, "fig_width_ratios")

# ---- Fig 3: synthetic exact vs simulated conditional coverage ----
syn = json.load(open(os.path.join(R7, "synthetic", "synthetic_results.json")))
fig, axes = plt.subplots(1, 2, figsize=(7.0, 2.6), sharey=True)
xl = ["<0", "0-5", "5-10", "10-15", "15-20", ">20"]; x = np.arange(6)
for ax, arm, ttl in zip(axes, ("sirv", "noise"), ("Pure compound-Gaussian", "Clutter + thermal noise")):
    rs = [r for r in syn if r["arm"] == arm and r["m"] == 16]
    ax.axhline(0.9, color=AXIS, lw=1)
    ax.plot(x, np.mean([r["IN1_exact_by"] for r in rs], 0), color=S[0], lw=1.6, label="IN-ARCP exact (Prop. 1)")
    ax.plot(x, np.mean([r["IN1"]["by"] for r in rs], 0), color=S[0], marker="o", ls="none", ms=6, label="IN-ARCP simulated")
    ax.plot(x, np.mean([r["MON"]["by"] for r in rs], 0), color=S[2], marker="^", ls="--", lw=1.4, ms=5, label="Mondrian simulated")
    if arm == "noise":
        ax.plot(x, np.mean([r["NA1"]["by"] for r in rs], 0), color=S[1], marker="s", ls="-", lw=1.4, ms=5, label="Noise-aware simulated")
        ax.plot(x, np.mean([r["NA1G"]["by"] for r in rs], 0), color=S[3], marker="D", ls=":", lw=1.4, ms=5, label="Noise-aware plug-in")
    ax.set_xticks(x, xl); ax.set_xlabel("True clutter-to-noise ratio (dB)"); ax.set_title(ttl, color=INK, fontsize=9)
axes[0].set_ylabel("Conditional coverage"); axes[0].set_ylim(0.85, 0.94)
h, l = axes[1].get_legend_handles_labels()
fig.tight_layout(rect=[0, 0.2, 1, 1]); fig.legend(h, l, loc="lower center", ncol=3, bbox_to_anchor=(0.5, 0.04))
fig.text(0.5, 0.0, "200 replications per panel, m = 16, nominal 0.90; Monte Carlo SE <= 0.0014.", ha="center", color=MUTED, fontsize=7)
save(fig, "fig_synthetic_exact")

# ---- Fig 4: coverage vs size, conformal vs plug-in (confirmatory, m=16) ----
fig, axes = plt.subplots(1, 2, figsize=(7.0, 2.8))
fam = {"IN1": 0, "IN4": 0, "NA1": 0, "NA2": 0, "NA4": 0, "G1": 1, "NA1G": 1, "NA2G": 1, "NA4G": 1, "U": 2, "RMS": 2, "LS": 2, "MLP": 2, "MON": 2}
famlab = ["Conformal, innovation-normalized", "Gaussian plug-in (no calibration)", "Other conformal baselines"]
mk = ["o", "s", "^"]
for ax, al in zip(axes, (0.1, 0.01)):
    for f in range(3):
        pts = [(k, ana[f"confirmatory|16|{al}|{k}"]) for k, v in fam.items() if v == f]
        ax.scatter([p["gm_ratio"][0] for _, p in pts], [p["cover_mean"] for _, p in pts], color=S[f], marker=mk[f], s=30,
                   edgecolor="white", lw=0.5, label=famlab[f], zorder=3)
        for k, p in pts:
            ax.annotate(k, (p["gm_ratio"][0], p["cover_mean"]), xytext=OFF[al].get(k, (3, 3)), textcoords="offset points", fontsize=6.5, color=INK2)
    ax.axhline(1 - al, color=AXIS, lw=1); ax.set_xlabel("Mean radius / IN-ARCP"); ax.set_ylabel("Mean coverage")
    ax.set_title(f"Nominal {1-al:.2f}", color=INK, fontsize=9)
h, l = axes[0].get_legend_handles_labels()
fig.tight_layout(rect=[0, 0.1, 1, 1]); fig.legend(h, l, loc="lower center", ncol=3, bbox_to_anchor=(0.5, 0.0))
save(fig, "fig_coverage_size")
print("figures written to", HERE)
