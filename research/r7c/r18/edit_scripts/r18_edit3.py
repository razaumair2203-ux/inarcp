"""R18 edit pass 3: wording and accuracy fixes to the pass 1-2 text, found by reading the
rendered PDF.

Four items:
  1. "Looks beyond the 8th" -> a word form, which reads properly.
  2. The F4 sentence relied on an elided verb across a comma; made two clauses.
  3. Pivotality is a property of the statistic, not of its false-alarm rate.
  4. ACCURACY: the guarded horizon 11.7 is the value at the OPPOSITE Doppler (Section III-D
     gives 3.7 there and a negative horizon at the clutter Doppler), so the qualifier is
     required. Also repaired a broken parallel in the same sentence.
"""
import os
import sys

PKG = r"c:/Users/DELL/Downloads/MS thess/03_submission_IEEE-TRS"
MAIN = os.path.join(PKG, "manuscript", "main.tex")

EDITS = [
    (
        "1. word form for the measured guard window",
        r"Looks beyond the \GuardLooksMeasured{}th were not measured;",
        r"Only the first \GuardLooksMeasuredWord{} looks were measured;",
    ),
    (
        "2. give the second clause its verb",
        r"(texture-quintile spread \AnalSpreadOsThree{} and \AnalSpreadFisherThree{} at $10^{-3}$, against \AnalSpreadInThree{} for the CA law), the clipped and ANMF rules almost evenly across clutter power (\AnalSpreadClipThree--\AnalSpreadFpThree).",
        r"(texture-quintile spread \AnalSpreadOsThree{} and \AnalSpreadFisherThree{} at $10^{-3}$, against \AnalSpreadInThree{} for the CA law); the clipped and ANMF rules fail almost evenly across clutter power (\AnalSpreadClipThree--\AnalSpreadFpThree).",
    ),
    (
        "3. pivotality belongs to the statistic",
        r"and its rate is the least pivotal of the thirteen: the texture-quintile spread is \ConfSpreadPanmfTwo{} at $10^{-2}$ and \ConfSpreadPanmfFour{} at $10^{-4}$, against \LInConfSpreadFour{} for IN-ARCP,",
        r"and it is the least pivotal of the thirteen: the texture-quintile spread of its rate is \ConfSpreadPanmfTwo{} at $10^{-2}$ and \ConfSpreadPanmfFour{} at $10^{-4}$, against \LInConfSpreadFour{} for IN-ARCP,",
    ),
    (
        "4. the horizon value is the one at the opposite Doppler; repair the parallel",
        r"A guard extends the horizon by only $\Delta$ looks: \HorizLooksGuard{} here, which is \HorizMsPrf~ms at a 1~kHz pulse repetition frequency and \HorizSecFrame~s at the 77~GHz frame rate. The per-look screen therefore needs a look interval at which the clutter is still correlated, where its gain lives, and long enough that a target re-enters range cells often,",
        r"A guard extends the horizon by only $\Delta$ looks: \HorizLooksGuard{} at the opposite Doppler here, which is \HorizMsPrf~ms at a 1~kHz pulse repetition frequency and \HorizSecFrame~s at the 77~GHz frame rate. The per-look screen therefore needs a look interval short enough that the clutter is still correlated at that lag, where its gain lives, and long enough that a target re-enters range cells often,",
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
