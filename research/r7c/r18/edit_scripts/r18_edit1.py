"""R18 edit pass 1: the findings that fit inside the redundancy already identified.

Implements F1, F3, F4, F5, F6, F8, F9 and the compensating cuts C2, C3, C4, C6, C8, C9, C11,
C15, C19, C7. F2 and F7 are deferred to pass 2 because they depend on the page decision.

Every replacement is exact-string and asserted, so the script fails loudly rather than
silently mangling the manuscript.
"""
import os
import sys

PKG = r"c:/Users/DELL/Downloads/MS thess/03_submission_IEEE-TRS"
MAIN = os.path.join(PKG, "manuscript", "main.tex")

EDITS = [
    # ---------------------------------------------------------------- C9: Introduction cuts
    (
        "C9a intro: defer the adaptive-detector mechanism to Related Work",
        r"Adaptive detectors restore scale invariance with a covariance estimated from secondary data \cite{kelly1986glrt,conte1995,kraut1999,pascal2008fp} or with an AR whitening filter \cite{roman2000,michels2000}, but take their thresholds from Gaussian laws or simulation, whose tail accuracy on real clutter is rarely measured.",
        r"Adaptive and AR-whitening detectors restore scale invariance (Section~\ref{sec:related}), but take their thresholds from Gaussian laws or simulation, whose tail accuracy on real clutter is rarely measured.",
    ),
    (
        "C9b intro: the clutter-map citations live in Related Work",
        r"Second, a detector that normalizes a cell by its own past can mask a target that persists into that past, as clutter-map detectors do \cite{lops1989,naldi1999}.",
        r"Second, a detector that normalizes a cell by its own past can mask a target that persists into that past.",
    ),
    (
        "C9c intro: the PAMF identity is stated in Section III-B",
        r"The per-look score is a one-pulse parametric adaptive matched filter (PAMF) test \cite{roman2000}. We call it IN-ARCP",
        r"We call it IN-ARCP",
    ),
    (
        "C9d intro: the OS counterpart is already in the preceding sentence",
        r"moves the horizon by the guard length. We also give the OS counterpart. Monte Carlo confirms",
        r"moves the horizon by the guard length. Monte Carlo confirms",
    ),
    (
        "C9e intro: trim the calibration contribution to the claim",
        r"On IPIX these thresholds hold the false-alarm rate to $10^{-4}$, and on NetRAD S-band sea clutter to $10^{-3}$, where the model-based laws of most whitened detectors and of the adaptive normalized matched filter (ANMF) fail.",
        r"On IPIX these thresholds hold the rate to $10^{-4}$ and on NetRAD S-band sea clutter to $10^{-3}$, where the model-based laws of most whitened detectors and of the adaptive normalized matched filter (ANMF) fail.",
    ),
    # ---------------------------------------------------- Related Work: label, and Kelly moved in
    (
        "C9f: label Related Work, and carry Kelly's GLRT across with the secondary-data sentence",
        r"\section{Related Work}" "\n" r"\emph{Normalized detection in compound-Gaussian clutter.}",
        r"\section{Related Work}\label{sec:related}" "\n" r"\emph{Normalized detection in compound-Gaussian clutter.}",
    ),
    (
        "C9g: Kelly and Conte join the secondary-data sentence they describe",
        r"normalizes by a covariance estimated from secondary data with the sample covariance matrix (SCM) \cite{kraut1999}",
        r"normalizes by a covariance estimated from secondary data \cite{kelly1986glrt} with the sample covariance matrix (SCM) \cite{kraut1999}",
    ),
    # ---------------------------------------------------------------- C19: blanking detail out
    (
        "C19: move the pulse-blanking thresholds to the supplement",
        r"Pulse blanking, a non-certified alternative, discards an innovation power, and the innovation after it, when the power exceeds both ten times the history median and four times a robust level of its block. That level is the history median for history terms and the third-smallest dwell power for dwell terms. The remaining dwell powers are integrated.",
        r"Pulse blanking, a non-certified alternative, discards an innovation power and the one after it when the power exceeds both ten times the history median and four times a robust level of its block, and integrates the rest (Supplementary Material).",
    ),
    # ---------------------------------------------------------------- C11: ANMF settings
    (
        "C11: the dwell length is already stated for every dwell detector",
        r"The ANMF uses the 8-pulse dwell and secondary vectors from clutter cells at least two cells away, at five time positions (20--35 vectors).",
        r"The ANMF uses secondary vectors from clutter cells at least two cells away, at five time positions (20--35 vectors).",
    ),
    # ---------------------------------------------------------------- F8: name the CFAR loss
    (
        "F8: name the CFAR loss of the conformal threshold",
        r"For a known-scale Swerling-1 detector, the expected $P_{\rm d}$ under calibration is a ratio of Beta functions (Supplementary Material).",
        r"For a known-scale Swerling-1 detector, the expected $P_{\rm d}$ under calibration is a ratio of Beta functions, the CFAR loss of a conformal threshold \cite{ward2013} (Supplementary Material).",
    ),
    # ---------------------------------------------------------------- F6: non-exchangeability
    (
        "F6: cite the radar and the statistics literature on non-exchangeability",
        r"These exceed sampling noise and suggest that the calibration and test thirds of a session are not exactly exchangeable.",
        r"These exceed sampling noise and suggest that the calibration and test thirds of a session are not exactly exchangeable, as the non-stationarity of sea clutter implies \cite{greco2010}; bounding the coverage gap it leaves would need a budget for the drift between them \cite{barber2023}.",
    ),
    # ---------------------------------------------------------------- F4: how the laws fail
    (
        "F4: separate the two mechanisms of model-law failure",
        r"A residual bootstrap of real innovations still exceeds design \LBootFour-fold at $10^{-4}$, consistent with dependence among an episode's innovations, which independent resampling discards.",
        r"A residual bootstrap of real innovations still exceeds design \LBootFour-fold at $10^{-4}$, consistent with dependence among an episode's innovations, which independent resampling discards. The laws fail in two ways: the OS and Fisher's-$g$ laws fail where the clutter is strongest (texture-quintile spread \AnalSpreadOsThree{} and \AnalSpreadFisherThree{} at $10^{-3}$, against \AnalSpreadInThree{} for the CA law), the clipped and ANMF rules almost evenly across clutter power (\AnalSpreadClipThree--\AnalSpreadFpThree).",
    ),
    # ---------------------------------------------------------------- C3, C2: pivotality prose
    (
        "C3: tighten the pivotality statement",
        r"Normalizing a prediction residual by the raw history RMS therefore does not keep the score pivotal (with a null distribution free of the clutter power), whereas innovation normalization keeps it approximately so where clutter dominates noise.",
        r"Normalizing by the raw history RMS therefore does not keep the score pivotal---its null free of the clutter power---whereas innovation normalization approximately does where clutter dominates noise.",
    ),
    (
        "C2: merge the two CA16 pivotality sentences",
        r"In the larger calibration sets of the low-false-alarm analysis, the spread at $10^{-2}$ is \NetSpreadInIpix{} for IN-ARCP and \NetSpreadCaIpix{} for the CA16 power ratio. CA16 is thus more pivotal still, but it needs \DetINGainCAHalf~dB more SCR.",
        r"In the larger low-false-alarm calibration sets it is \NetSpreadInIpix{} for IN-ARCP and \NetSpreadCaIpix{} for CA16, which is thus more pivotal still but needs \DetINGainCAHalf~dB more SCR.",
    ),
    # ---------------------------------------------------------------- C4: drop the signpost
    (
        "C4: drop a signpost sentence",
        r"The clipped integrator costs \AClipMinusDin~dB [\AClipMinusDinLo, \AClipMinusDinHi] against AR(1) integration at $\alpha=0.01$, and the binary integrator costs more. Two classical alternatives are less sensitive. The power OS detector",
        r"The clipped integrator costs \AClipMinusDin~dB [\AClipMinusDinLo, \AClipMinusDinHi] against AR(1) integration at $\alpha=0.01$, and the binary integrator costs more. The power OS detector",
    ),
    # ---------------------------------------------------------------- F5: guard window and cost
    (
        "F5: state the measured window and justify the guard length",
        r"The law gives \GuardLawEight{} (exploratory), and the conformal false-alarm rate stays at \GuardPfaEight{} times design. The guard costs \GuardOnsetCost~dB at onset, plausibly because its scale is eight pulses older.",
        r"The law gives \GuardLawEight{} (exploratory), and the conformal false-alarm rate stays at \GuardPfaEight{} times design. Looks beyond the \GuardLooksMeasured{}th were not measured; \eqref{eq:rank1} at $\ell-\Delta$ predicts the same decay, delayed. The guard costs \GuardOnsetCost~dB at onset, a 16-pulse guard \GuardOnsetCostSixteen~dB for the same \GuardMeanLookSixteen{} over this window, so $\Delta=8$ is the cheaper choice.",
    ),
    # ---------------------------------------------------------------- C8, F9: target paragraph
    (
        "C8+F9: drop the development aside and macro-ise the exceedance rate",
        r"This blindness was seen during development and is explained by Proposition~\ref{prop:blind}; a pre-specified test confirms it for IN-ARCP and the clipped integrator: both exceed their thresholds on the target cell at a rate of 0.0004 at $\alpha=10^{-3}$, below their clutter false-alarm rates.",
        r"Proposition~\ref{prop:blind} explains it, and a pre-specified test confirms it for IN-ARCP and the clipped integrator: both exceed on the target cell at \TargetBlindRate{} at $\alpha=10^{-3}$, below their clutter rates.",
    ),
    # ---------------------------------------------------------------- F3: P-ANMF is least pivotal
    (
        "F3: report the texture dependence of the recommended remedy",
        r"Its measured clutter false-alarm rates there are $\TPanmfPfaEight$ and $\TPanmfPfaTwoFiveSix\times10^{-3}$, above the design $10^{-3}$ (Supplementary Material).",
        r"Its measured clutter false-alarm rates there are $\TPanmfPfaEight$ and $\TPanmfPfaTwoFiveSix\times10^{-3}$, above the design $10^{-3}$, and its rate is the least pivotal of the thirteen: the texture-quintile spread is \ConfSpreadPanmfTwo{} at $10^{-2}$ and \ConfSpreadPanmfFour{} at $10^{-4}$, against \LInConfSpreadFour{} for IN-ARCP, as Corollary~\ref{cor:texture} leads one to expect for a dwell spanning varying noise.",
    ),
    # ---------------------------------------------------------------- F1: the matched comparison
    (
        "F1: give the paper's own number at the literature's observation length",
        r"Learned detectors report $P_{\rm d}=0.91$ at $P_{\rm fa}=10^{-3}$ on IPIX with 1.024-s observations and a different evaluation \cite{qu2023sensors}.",
        r"Learned detectors report $P_{\rm d}=0.91$ at $P_{\rm fa}=10^{-3}$ on these recordings with \TPanmfKiloSec-s observations \cite{qu2023sensors}; over the same \TPanmfKiloPulses{} pulses the self-normalized statistic reaches \TPanmfKiloPd{} at $\TPanmfKiloPfa\times10^{-3}$ (pre-specified, descriptive). Those detectors are trained on this target in these recordings and thresholded empirically, ours on neither.",
    ),
    # ---------------------------------------------------------------- C6: clip-level rule
    (
        "C6: tighten the clip-level rule sentence",
        r"A pre-specified saturation rule on calibration data most often picks $\kappa=9$ ({\KappaNineUnits} of \NUnitsConf{} units) and is not met by any tested clip level ($\kappa\le18$) in \KappaRuleUndefUnits{} units.",
        r"A pre-specified saturation rule picks $\kappa=9$ in {\KappaNineUnits} of \NUnitsConf{} units and is met by no tested level ($\kappa\le18$) in \KappaRuleUndefUnits.",
    ),
    # ---------------------------------------------------------------- C7: Table IV not re-told
    (
        "C7: do not re-tell two rows of Table IV in prose",
        r" A persistent target at the clutter Doppler is lost after onset even with a guard, and data-calibrated thresholds still depart from design on NetRAD at $10^{-4}$.",
        r"",
    ),
    # ---------------------------------------------------------------- C15: design rule 1
    (
        "C15: design rule 1 need not restate the definition of Section III-B",
        r"\item Whiten with an AR model fitted on clutter training data, and normalize by the RMS innovation scale over a window that ends $\Delta$ pulses before the tested pulse; the guard keeps a target out of the scale for $\Delta$ looks ($\Delta=8$ on both radars).",
        r"\item Whiten with an AR model fitted on clutter training data and normalize by the innovation scale of a window ending $\Delta$ pulses before the tested pulse ($\Delta=8$ on both radars).",
    ),
    # ---------------------------------------------------------------- abstract: word-neutral
    (
        "F5 abstract: name the window the mean is taken over (word-neutral swap)",
        r"an eight-pulse guard raises the mean per-look detection probability of an injected persistent 10~dB target from \GuardMeanLookZero{} to \GuardMeanLookEight, except at the clutter Doppler.",
        r"an eight-pulse guard raises the per-look detection probability of an injected persistent 10~dB target over its eight guarded looks from \GuardMeanLookZero{} to \GuardMeanLookEight, except at the clutter Doppler.",
    ),
    (
        "abstract: pay for it (1)",
        r"conformal thresholds keep 12 of 13 statistics within \LConfMinFour--\LConfMaxFour{} times the design rate down to $10^{-4}$",
        r"conformal thresholds keep 12 of 13 statistics within \LConfMinFour--\LConfMaxFour{} times design down to $10^{-4}$",
    ),
    (
        "abstract: pay for it (2)",
        r"the guard and the injected-interference certificate behave as on IPIX",
        r"the guard and the certificate behave as on IPIX",
    ),
    # ---------------------------------------------------------------- new macro file
    (
        "input the R18 macros",
        "\\input{generated/r17_macros.tex}",
        "\\input{generated/r17_macros.tex}\n\\input{generated/r18_macros.tex}",
    ),
    (
        "header: record the round",
        r"% R17 (3 Oct 2026): R16.1 plus a pre-specified, descriptive real-onset test (a walking person at 77 GHz; research/r7c/r17).",
        "% R18 (3 Oct 2026): senior-reviewer round. See 04_reviews/2026-10-03_R18_senior_review/.\n"
        r"% R17 (3 Oct 2026): R16.1 plus a pre-specified, descriptive real-onset test (a walking person at 77 GHz; research/r7c/r17).",
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
