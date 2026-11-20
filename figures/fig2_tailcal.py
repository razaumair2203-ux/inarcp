"""Fig. 2: measured false-alarm rate over design on IPIX, plotted from inputs/tab_lowpfa.tex
(values with intervals: Supplementary Table S2).
Usage: python fig2_tailcal.py   (FIG_OUT sets the output folder; default figures/out)
"""
import hashlib
import os
import re
from pathlib import Path

import matplotlib.pyplot as plt
from matplotlib.lines import Line2D


import figstyle as S

HERE = Path(__file__).resolve().parent
TAB = HERE / "inputs/tab_lowpfa.tex"
OUT = Path(os.environ.get("FIG_OUT", str(HERE / "out")))
OUT.mkdir(parents=True, exist_ok=True)

LABELS = {  # printed row label -> figure label: the statistic only; its model-based law is named in the
    "IN-ARCP (CA law)": "IN-ARCP",
    r"\quad residual bootstrap": "IN-ARCP, RB",
    "IN-AR(4) (CA law)": "IN-AR(4)",
    r"OS scale, $k=8$ (OS law)": "OS, $k=8$",
    "NA-AR(4) (Gaussian)": "NA-AR(4)",
    "Power, CA (white law)": "Power, CA",
    "Power, OS (white law)": "Power, OS",
    r"Integration (law \eqref{eq:dwellpfa})": "Integration",
    "PAMF-H, one Doppler (CA law)": "PAMF-H",
    "P-ANMF, one bin (Beta)": "P-ANMF, bin",
    r"P-ANMF, max (Fisher's $g$)": "P-ANMF, max",
    r"ANMF-SCM (Kraut--Scharf)": "ANMF-SCM",
    "ANMF-Tyler (FP law)": "ANMF-Tyler",
    "Clipped, OS scale (Gaussian sim.)": "Clipped",
}

rows, group = [], None
for line in TAB.read_text(encoding="utf-8").splitlines():
    if line.startswith(r"\emph{"):
        group = re.match(r"\\emph\{([^}]*)\}", line).group(1)
        continue
    cells = [c.strip() for c in line.rstrip("\\").split("&")]
    if len(cells) != 7 or cells[0] in ("", r"$\alpha$"):
        continue
    vals = []
    for c in cells[1:]:
        c = re.sub(r"\\textbf\{([^}]*)\}", r"\1", c)
        vals.append(float(c) if c else None)
    rows.append((group, LABELS[cells[0]], vals))
assert len(rows) == 14 and sum(v is not None for _, _, vs in rows for v in vs) == 81

S.apply(8)
# conformal = open markers in the upper lane of each row, model-based = filled markers in the lower lane;
# shape = design rate as before. Faint row guides; no minor-tick comb. Same 81 entries.
# inside the plot, so the data area widens from ~1.9 in to ~2.6 in and the height drops to 2.3 in with the
# same plot height.
# shorter labels; slightly larger markers.
H = float(os.environ.get("FIG2_H", "2.52"))
fig, ax = plt.subplots(figsize=(3.5, H))
ax.axvspan(.5, 2, color=S.BAND, lw=0, zorder=0)
ax.axvline(1, color=S.GREY, lw=.6, zorder=1)
MARK = ("o", "s", "D")
SIZE = (4.4, 4.2, 4.0)
y_of, head_of = {}, {}
y = 0.
for i, (g, lab, vals) in enumerate(rows):
    if i == 0 or g != rows[i - 1][0]:
        head_of[y] = "Per look" if i == 0 else "Eight-pulse dwell"
        y += .9
    y_of[i] = y
    ax.axhline(y + .5, color=S.GRID, lw=.4, zorder=0)
    for j in range(3):
        for off, v, c, fill in ((-.2, vals[j], S.BLUE, False), (.2, vals[3 + j], S.ORANGE, True)):
            if v is None:
                continue
            ax.plot(v, y + off, MARK[j], ms=SIZE[j], color=c,
                    mfc=c if fill else "white", mew=.9, zorder=3)
    y += 1
ax.set_yticks(list(y_of.values()), [r[1] for r in rows])
ax.invert_yaxis()
ax.set_xscale("log")
ax.set_xlim(.02, 110)
ax.set_xticks([.03, .1, 1, 10, 100], ["0.03", "0.1", "1", "10", "100"])
ax.minorticks_off()
ax.set_xlabel(r"Measured $P_{\rm fa}$ / design $\alpha$")
ax.tick_params(axis="y", length=0)
ax.spines["left"].set_visible(False)
import matplotlib.transforms as mtrans
lab_tf = mtrans.blended_transform_factory(ax.transAxes, ax.transData)
for hy, txt in head_of.items():   # group headings on their own (data-free) rows, inside the plot
    ax.text(.012, hy, txt, transform=lab_tf, fontsize=8, style="italic", weight="bold", color=S.DARK,
            ha="left", va="center", zorder=5)
ax.grid(axis="x", color=S.GRID, lw=.5)
ax.set_axisbelow(True)
meth = [Line2D([], [], ls="", marker="o", ms=4.4, color=S.BLUE, mfc="white", mew=.9, label="conformal"),
        Line2D([], [], ls="", marker="o", ms=4.4, color=S.ORANGE, mew=.9, label="model-based")]
rate = [Line2D([], [], ls="", marker=m, ms=sz, color=S.DARK, mfc="white", mew=.9, label=lab)
        for m, sz, lab in zip(MARK, SIZE, (r"$10^{-2}$", r"$10^{-3}$", r"$10^{-4}$"))]
ybot, ytop = y - .35, -.6   # inverted axis: fixed limits so the key positions are exact
ax.set_ylim(ybot, ytop)
ROW_EDGE = (ybot - (y_of[len(rows) - 1] - .5)) / (ybot - ytop)   # top edge of the clipped row
# Keys inside the plot, in empty blocks (no figure-level legend rows): method at top right (rows IN-ARCP
# to IN-AR(4) have no entry above 5); design rate at lower left (the dwell rows Integration to ANMF-Tyler
# have no entry below 0.5; the clipped row below stays clear).
KW = dict(frameon=True, framealpha=1, edgecolor="none", handlelength=.8, handletextpad=.3,
          borderpad=.15, labelspacing=.2, borderaxespad=0)
ax.add_artist(ax.legend(handles=meth, loc="upper right", bbox_to_anchor=(1, 1), **KW))
ax.legend(handles=rate, loc="lower left", bbox_to_anchor=(0, ROW_EDGE), title=r"design $\alpha$",
          title_fontsize=8, **KW)
fig.tight_layout(pad=.3)
fig.savefig(OUT / "fig_tailcal.pdf")
fig.savefig(OUT / "fig_tailcal_check.png", dpi=220)
(OUT / "tailcal_input_sha256.txt").write_text(
    f"{hashlib.sha256(TAB.read_bytes()).hexdigest()}  {TAB.name}\n")
print("Tail calibration: %.2f x %.2f in; 8 pt; 81 plotted entries." % tuple(fig.get_size_inches()))
