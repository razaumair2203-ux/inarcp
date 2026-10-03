"""R18.2: the final claim audit's main-text WEAK items.

W1   "A guard extends the horizon by only Delta looks, which ... is 12 ms" — the antecedent is
     wrong. 12 ms is the whole guarded horizon Delta + l*, not the Delta extension (8 ms).
W2   Design rule 1's "(Delta = 8 on both radars)" carried no basis, after the Results were
     rewritten to say the measured looks cannot separate Delta = 8 from Delta = 16. The
     one-sided preference had simply moved from the Results into the design rules.
W3   \\eqref{eq:horizon} is (6), which is l*(omega) and contains no Delta; the Delta + l*
     result is in the running text of Section IV-E. Cite the quantity, not the equation.
W4   "over the first eight looks" is ambiguous: the paper treats l = 0 as a look, so it reads
     as looks 0-7, whose means are 0.35 and 0.82, not 0.24 and 0.82. The measured window is
     looks 1-8 for both arms. Word-neutral in the abstract.
W6   The Kraut-Scharf simulation was run at alpha = 1e-2 only, while the failures the sentence
     explains are quoted at 1e-3 and 1e-4.
W12  Table IV's caption says a slash separates the two conditions of a row; the split grade
     "W / P" needs a matching split in the Scenario cell.
"""
import os
import sys

PKG = r"c:/Users/DELL/Downloads/MS thess/03_submission_IEEE-TRS"
MAIN = os.path.join(PKG, "manuscript", "main.tex")

EDITS = [
    (
        "W4: name the measured window exactly, word-neutral in the abstract",
        r"of an injected persistent 10~dB target over the first eight looks from \GuardMeanLookZero{} to \GuardMeanLookEight,",
        r"of an injected persistent 10~dB target over looks 1--8 after onset from \GuardMeanLookZero{} to \GuardMeanLookEight,",
    ),
    (
        "W1: 12 ms is the whole guarded horizon, not the extension",
        r"A guard extends the horizon by only $\Delta$ looks, which at the opposite Doppler and each radar's own measured correlation is \HorizMsPrf~ms at a 1~kHz pulse repetition frequency and \HorizSecFrame~s at the 77~GHz frame rate.",
        r"A guard extends the horizon by only $\Delta$ looks, so the whole guarded horizon, at the opposite Doppler and each radar's own measured correlation, is \HorizMsPrf~ms at a 1~kHz pulse repetition frequency and \HorizSecFrame~s at the 77~GHz frame rate.",
    ),
    (
        "W3: cite the quantity, since (6) carries no guard",
        r"Those looks cannot separate the two, and \eqref{eq:horizon} puts the longer guard's horizon eight looks further out.",
        r"Those looks cannot separate the two, and the horizon $\Delta+\ell^*$ puts the longer guard's eight looks further out.",
    ),
    (
        "W6: the simulated failure was measured at one design rate",
        r"The Kraut--Scharf law fails 2.8--3.4-fold even in simulated compound-Gaussian clutter (Supplementary Material).",
        r"The Kraut--Scharf law fails 2.8--3.4-fold at $10^{-2}$ even in simulated compound-Gaussian clutter (Supplementary Material).",
    ),
    (
        "W2: give design rule 1's guard length a basis",
        r"before the tested pulse ($\Delta=8$ on both radars). Choose the look interval",
        r"before the tested pulse ($\Delta=8$ on both radars here; a longer guard buys proportionally more horizon at a small onset cost). Choose the look interval",
    ),
    (
        "W12: split the Scenario cell to match the split grade, as the caption requires",
        r"Conformal, IPIX, to $10^{-4}$ & W / P & 12 of 13 in \LConfMinFour--\LConfMaxFour; clipped \LClipConfFour{} &&",
        r"Conformal, IPIX, $10^{-4}$, 12 of 13 / clipped & W / P & \LConfMinFour--\LConfMaxFour{} / \LClipConfFour{} &&",
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
print(f"applied {len(EDITS)} final-audit fixes to {MAIN}")
