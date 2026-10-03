"""R18 edit pass 2: F2 (operating regime) and F7 (cost and deployment), in full.

Authorized by the user on 3 Oct 2026 to run to 11 printed pages (US$200 overlength), with
the extra page spent on these two findings and on enlarging Figures 2 and 3 (F12).
"""
import os
import sys

PKG = r"c:/Users/DELL/Downloads/MS thess/03_submission_IEEE-TRS"
MAIN = os.path.join(PKG, "manuscript", "main.tex")

EDITS = [
    # ------------------------------------------------------------------ F2: operating regime
    (
        "F2: the horizon as a duration, and the look-interval trade-off",
        r"A guard extends the horizon by only $\Delta$ looks.",
        r"A guard extends the horizon by only $\Delta$ looks: \HorizLooksGuard{} here, "
        r"which is \HorizMsPrf~ms at a 1~kHz pulse repetition frequency and "
        r"\HorizSecFrame~s at the 77~GHz frame rate. The per-look screen therefore needs a "
        r"look interval at which the clutter is still correlated, where its gain lives, and "
        r"long enough that a target re-enters range cells often, since it onsets again in "
        r"each new cell (\CellLooksRef{} looks in a 15~m cell at \CellSpeedRef~m/s, of which "
        r"\DutyRef\% are visible). The two radars sit at the extremes of that trade-off: "
        r"1~kHz with $|r|$ near one, and a frame interval at which the clutter is nearly "
        r"white and the gain is gone.",
    ),
    # ------------------------------------------------- F2: the actionable half, in design rule 1
    (
        "F2: measure the correlation at the intended look interval",
        r"\item Whiten with an AR model fitted on clutter training data and normalize by the innovation scale of a window ending $\Delta$ pulses before the tested pulse ($\Delta=8$ on both radars).",
        r"\item Whiten with an AR model fitted on clutter training data and normalize by the "
        r"innovation scale of a window ending $\Delta$ pulses before the tested pulse "
        r"($\Delta=8$ on both radars). Choose the look interval by measuring $|r|$ at that "
        r"lag first: the gain follows the correlation, and vanishes between 77~GHz frames.",
    ),
    # ------------------------------------------------------------ F7: cost and calibration data
    (
        "F7: what the calibration rule and the cell-wise state cost",
        r"\item Calibrate thresholds conformally on clean clutter: beyond about $3.15/\alpha$ episodes, $\PP\{P_{\rm fa}>2\alpha\}\le0.05$, and more are needed under dependence.",
        r"\item Calibrate thresholds conformally on clean clutter: beyond about $3.15/\alpha$ "
        r"episodes, $\PP\{P_{\rm fa}>2\alpha\}\le0.05$, and more are needed under "
        r"dependence. At $10^{-4}$ that is \CalEpisodesFour{} episodes, about "
        r"\CalSecondsFour~s of clean recording at 1~kHz across 14 range cells. Pivotality "
        r"then buys one threshold for every cell, at $p$ complex multiply--accumulates and "
        r"\StatePerCell{} stored samples per cell per pulse.",
    ),
]

src = open(MAIN, encoding="utf-8").read()
fail = []
for name, old, new in EDITS:
    n = src.count(old)
    if n != 1:
        fail.append(f"  {name}: pattern occurs {n} times")
        continue
    src = src.replace(old, new, 1)

if fail:
    print("FAILED, nothing written:")
    print("\n".join(fail))
    sys.exit(1)

open(MAIN, "w", encoding="utf-8").write(src)
print(f"applied {len(EDITS)} edits to {MAIN}")
