"""R18.1: fixes required by the two blind pairwise reviews (orders 1 and 2).

Five of these are defects R18 itself introduced; the rest are pre-existing overclaims that
both reviewers flagged and that can be corrected exactly, without new computation.

Both reviewers independently found items 1-5. Item 6 (the Kraut-Scharf inference) was called
"the clearest logical error in either version". Items 11-12 restore two sentences the
reviewers said R18 should not have cut.
"""
import os
import sys

PKG = r"c:/Users/DELL/Downloads/MS thess/03_submission_IEEE-TRS"
MAIN = os.path.join(PKG, "manuscript", "main.tex")

EDITS = [
    # ===================================================== 1. ABSTRACT: restore the qualifier
    (
        "1a. ABSTRACT FAIL: the certificate that behaves as on IPIX is the injected-interference one",
        r"the guard and the certificate behave as on IPIX",
        r"the guard and the injected-interference certificate behave as on IPIX",
    ),
    (
        "1b. abstract: pay for 1a",
        r"At that design rate, with injected interference on 5\% of pulses,",
        r"At that rate, with injected interference on 5\% of pulses,",
    ),
    (
        "1c. abstract: the 0.24 arm has no guard, so those looks are not guarded looks",
        r"of an injected persistent 10~dB target over its eight guarded looks from \GuardMeanLookZero{} to \GuardMeanLookEight,",
        r"of an injected persistent 10~dB target over the first eight looks from \GuardMeanLookZero{} to \GuardMeanLookEight,",
    ),
    # ===================================================== 2. the learned-detector comparison
    (
        "2. 'ours on neither' is false: a conformal threshold is also empirical",
        r"Those detectors are trained on this target in these recordings and thresholded empirically, ours on neither.",
        r"Those detectors are trained on labeled targets in these recordings; ours is given no target, and its threshold carries a finite-sample law.",
    ),
    # ===================================================== 3. the guard-length comparison
    (
        "3. the measured window cannot favour the shorter guard; state both sides",
        r"The guard costs \GuardOnsetCost~dB at onset, a 16-pulse guard \GuardOnsetCostSixteen~dB for the same \GuardMeanLookSixteen{} over this window, so $\Delta=8$ is the cheaper choice.",
        r"The guard costs \GuardOnsetCost~dB at onset and a 16-pulse guard \GuardOnsetCostSixteen~dB, for the same \GuardMeanLookSixteen{} over the looks measured; those looks cannot separate the two, and \eqref{eq:horizon} puts the longer guard's horizon eight looks further out.",
    ),
    # ===================================================== 4. the pivotality claim in rule 2
    (
        "4. one shared threshold, and only approximately: quote the measured spread",
        r"Pivotality then buys one threshold for every cell, at $p$ complex multiply--accumulates and \StatePerCell{} stored samples per cell per pulse.",
        r"Pivotality then buys one threshold shared by all cells, approximately so where clutter dominates noise (texture spread \LInConfSpreadFour{} at $10^{-4}$), at $p$ complex multiply--accumulates and \StatePerCell{} stored samples per cell per pulse.",
    ),
    # ===================================================== 5. the calibration-data figure
    (
        "5. 3.15/alpha is the i.i.d. bound, so the record length is a lower bound",
        r"At $10^{-4}$ that is \CalEpisodesFour{} episodes, about \CalSecondsFour~s of clean recording at 1~kHz across 14 range cells.",
        r"At $10^{-4}$ that is \CalEpisodesFour{} episodes, at least about \CalSecondsFour~s of clean recording at 1~kHz across 14 range cells, ranked once offline.",
    ),
    # ===================================================== 6. the Kraut-Scharf inference
    (
        "6. the inference that follows is about the model, not about the tails",
        r"The Kraut--Scharf law fails 2.8--3.4-fold even in simulated compound-Gaussian clutter (Supplementary Material), so the SCM failure need not stem from the clutter tails.",
        r"The Kraut--Scharf law fails 2.8--3.4-fold even in simulated compound-Gaussian clutter (Supplementary Material), so the SCM failure is already present under the model and need not come from any departure of real clutter from it.",
    ),
    # ===================================================== 7. the two-mechanism claim
    (
        "7. a max/min spread gives no direction; drop the directional claim and label it",
        r"The laws fail in two ways: the OS and Fisher's-$g$ laws fail where the clutter is strongest (texture-quintile spread \AnalSpreadOsThree{} and \AnalSpreadFisherThree{} at $10^{-3}$, against \AnalSpreadInThree{} for the CA law); the clipped and ANMF rules fail almost evenly across clutter power (\AnalSpreadClipThree--\AnalSpreadFpThree).",
        r"The laws fail in two ways (exploratory): the rate of the OS and Fisher's-$g$ laws depends strongly on clutter power (texture-quintile spread \AnalSpreadOsThree{} and \AnalSpreadFisherThree{} at $10^{-3}$, against \AnalSpreadInThree{} for the CA law), whereas the clipped and ANMF rules fail almost evenly across it (\AnalSpreadClipThree--\AnalSpreadFpThree).",
    ),
    # ===================================================== 8. label the ranking as exploratory
    (
        "8. ranking the thirteen by pivotality is a post-hoc reading of a pre-specified output",
        r"The statistic is also the least pivotal of the thirteen: the texture-quintile spread of its rate is",
        r"The statistic is also the least pivotal of the thirteen (exploratory): the texture-quintile spread of its rate is",
    ),
    # ===================================================== 9. state the design rate
    (
        "9. the Gaussian-threshold equivalence holds at this design rate, not generally",
        r"The Gaussian threshold of IN-ARCP gives the same sensitivity at a similar false-alarm rate, so the gain comes from whitening, not from calibration.",
        r"At this design rate the Gaussian threshold of IN-ARCP gives the same sensitivity at a similar false-alarm rate, so the gain comes from whitening, not from calibration.",
    ),
    # ===================================================== 10. distinguish the two CAloc gains
    (
        "10. name the comparison, so 9.9 dB is not read against the 9.8 dB of Section V-B",
        r"IN-ARCP's first-look gain over CAloc falls from \RampGainOne~dB for an abrupt onset in this comparison",
        r"IN-ARCP's first-look gain over CAloc falls from \RampGainOne~dB for an abrupt onset in the ramp comparison",
    ),
    # ===================================================== 11. restore the PAMF sentence
    (
        "11. restore the sentence that says the per-look score is not new",
        r"We call it IN-ARCP (innovation-normalized autoregressive conformal prediction)",
        r"The per-look score is a one-pulse parametric adaptive matched filter (PAMF) test \cite{roman2000}. We call it IN-ARCP (innovation-normalized autoregressive conformal prediction)",
    ),
    # ===================================================== 12. restore the clutter-map cites
    (
        "12. restore the attribution at the point of the claim",
        r"Second, a detector that normalizes a cell by its own past can mask a target that persists into that past.",
        r"Second, a detector that normalizes a cell by its own past can mask a target that persists into that past, as clutter-map detectors do \cite{lops1989,naldi1999}.",
    ),
    # ===================================================== 13. 'measures', not 'confirms'
    (
        "13. the blindness was seen in development, so the pre-specified test measures it",
        r"a pre-specified test confirms it for IN-ARCP and the clipped integrator:",
        r"a pre-specified test measures it for IN-ARCP and the clipped integrator:",
    ),
    # ===================================================== 14. label the clip level post hoc
    (
        "14. the pre-specified saturation rule held in 17 of 56 units, so the recommendation is post hoc",
        r"integrate clipped innovations ($\kappa\approx9$) with a certified threshold",
        r"integrate clipped innovations ($\kappa\approx9$, post hoc) with a certified threshold",
    ),
    # ===================================================== 15. scope the Conclusion
    (
        "15. every sea-clutter certificate test had the hit model right by construction",
        r"The certificate holds on sea clutter and on real FMCW interference at a cost that grows to vacuity at high hit rates;",
        r"The certificate holds where the hit model dominates the hit pattern---on sea clutter with injected hits, and on real FMCW interference---at a cost that grows to vacuity at high hit rates;",
    ),
    # ===================================================== 16. Table IV worst-case grade
    (
        "16. the caption says grades follow the worst case, so name the exception",
        r"Conformal, IPIX, to $10^{-4}$ & W & 12 of 13 in \LConfMinFour--\LConfMaxFour{} &&",
        r"Conformal, IPIX, to $10^{-4}$ & W / P & 12 of 13 in \LConfMinFour--\LConfMaxFour; clipped \LClipConfFour{} &&",
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
print(f"applied {len(EDITS)} review fixes to {MAIN}")
