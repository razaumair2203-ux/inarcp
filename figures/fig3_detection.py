"""Fig. 3: detection of Swerling-1 targets injected into IPIX, plotted from inputs/fig3_panel_a.json
and inputs/fig3_panel_b.json.
Usage: python fig3_detection.py   (FIG_OUT sets the output folder; default figures/out)
"""
import hashlib
import json
import os
from pathlib import Path

import numpy as np
import matplotlib.pyplot as plt
from matplotlib.lines import Line2D

import figstyle as S

HERE = Path(__file__).resolve().parent
ROOT = HERE.parent
IN_A = HERE / "inputs/fig3_panel_a.json"
IN_B = HERE / "inputs/fig3_panel_b.json"
OUT = Path(os.environ.get("FIG_OUT", str(HERE / "out")))
OUT.mkdir(parents=True, exist_ok=True)
A = json.loads(IN_A.read_text(encoding="utf-8"))
B = json.loads(IN_B.read_text(encoding="utf-8"))
assert A["schema"] == "inarcp.figure3.frozen_plot_input.v1"
assert A["provenance"]["unit_count"] == 56
S.apply(8)
W, H = 7.16, 1.86
L, AW, GAP, Bm, TOP = .47, 3.00, .58, .40, .19
fig = plt.figure(figsize=(W, H))
a = fig.add_axes([L / W, Bm / H, AW / W, (H - Bm - TOP) / H])
b = fig.add_axes([(L + AW + GAP) / W, Bm / H, AW / W, (H - Bm - TOP) / H])

scr = np.array(A["scr_db"])
for name, c, ls, lab in (("IN1", S.BLUE, "-", "IN-ARCP"),
                         ("NA4", S.ORANGE, "-.", "NA-AR(4)"),
                         ("CA16", S.DARK, "--", "CA16"),
                         ("CAloc", S.GREY, ":", "CAloc")):
    a.plot(scr, A["panel_a"][f"{name}|0.01|pd"], ls=ls, color=c, lw=1.5, label=lab)
a.plot(scr, A["panel_a"]["IN1|0.01|pred"], "o", color=S.BLUE, ms=3.8, mfc="white", mew=.9,
       label="law (Cor. 2)")  # circles: law of Corollary 2 with each unit's fitted model
a.legend(loc="lower right", handlelength=2.3, labelspacing=.1, borderaxespad=.1)  # SCR > 15 dB: all curves > 0.8
a.set(xlim=(-5.5, 25.5), ylim=(-.02, 1.02), xlabel="SCR (dB)", ylabel=r"$P_{\rm d}$", yticks=[0, .5, 1])
a.set_title("(a) Target in the tested pulse")
S.grid(a)

d = B["radars"]["IPIX"]
looks = np.array(d["looks"])
si, di = d["scr_db"].index(10), d["dopplers"].index("random")
colors = {0: S.DARK, 8: S.BLUE, 16: S.ORANGE}
marks = {0: "o", 8: "s", 16: "^"}  # guard identity is never colour alone
for gi, guard in enumerate(d["guards"]):
    c = colors[guard]
    emp = np.array(d["target_per_look_probability"])[di, si, gi]
    ci = np.array(d["target_per_look_interval"])[di, si, gi]
    law = np.array(d["ideal_plugin_per_look_probability"])[di, si, gi]
    every = list(range(gi, 25, 4))
    b.fill_between(looks, ci[:, 0], ci[:, 1], color=c, alpha=.2, lw=0)
    b.plot(looks, emp, color=c, lw=1.6, zorder=3)                       # measured (solid)
    b.plot(looks, law, color=c, lw=1.0, ls=(0, (3, 2)), zorder=4)       # law (dashed), above the solid
    b.plot(looks[every], emp[every], marks[guard], color=c, ms=3.8, mfc="white", mew=.9, zorder=5)
    b.plot([], [], color=c, lw=1.6, marker=marks[guard], ms=3.8, mfc="white", mew=.9,
           label=rf"$\Delta={guard}$")
h, l = b.get_legend_handles_labels()
h += [Line2D([], [], color=S.GREY, lw=1.6),
      Line2D([], [], color=S.GREY, lw=1.0, ls=(0, (3, 2))),
      plt.Rectangle((0, 0), 1, 1, color=S.GREY, alpha=.3, lw=0)]
l += ["measured", "law (Prop. 3)", "95% interval"]
b.legend(h, l, loc="upper right", title="Slow-time guard", handlelength=2.3, labelspacing=.08,
         borderaxespad=.1)  # looks > 24: every curve is at zero
b.set(xlim=(-.5, 48.5), ylim=(-.015, 1.02), xticks=np.arange(0, 49, 8), yticks=[0, .5, 1],
      xlabel=r"Look after onset $\ell$", ylabel=r"Per-look $P_{\rm d}$")
b.set_title("(b) Persistent target, SCR 10 dB")
S.grid(b, "y")

fig.savefig(OUT / "fig_detection.pdf")
fig.savefig(OUT / "fig_detection_check.png", dpi=220)
(OUT / "detection_input_sha256.txt").write_text("".join(
    f"{hashlib.sha256(p.read_bytes()).hexdigest()}  {p.name}\n" for p in (IN_A, IN_B)))
print("Fig. 3: %.2f x %.2f in, printed at 100%%; 8 pt text." % tuple(fig.get_size_inches()))
