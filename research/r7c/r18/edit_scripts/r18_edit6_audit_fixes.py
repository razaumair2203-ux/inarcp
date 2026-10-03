"""R18.1: fixes required by the adversarial claim audit (7 FAILs, 12 WEAKs).

The audit verified every macro against its outcome file and found no arithmetic error in the
macros themselves. The failures were superlatives, conditions and derived arithmetic. Four of
the seven FAILs were in text R18 added; three were pre-existing or came from the same round's
derivations.

Independently re-verified before applying:
  FAIL-1  Clip-OS1's conformal spread is 12.1 at 1e-3 and 6.3e6 at 1e-4, against P-ANMF's
          9.9 and 23 (r12_summary.txt lines 39/67 vs 54/82). P-ANMF is the widest only at
          1e-2. The superlative was false.
  FAIL-3  research/r7c/ipix.py excludes the target bins and one guard bin each side, leaving
          7-9 clutter bins per file, never 14; and a guarded episode spans m+Delta+1 = 25
          pulses, not 17. Recomputed: 87-112 s, not 38 s.
  FAIL-5  No per-quintile vector is saved for Part L, and the two that do exist elsewhere
          (r11_summary.txt:4, audit_existing.txt:11) run the OPPOSITE way - highest rate at
          the LOWEST clutter power. The directional claim was unsupported and probably wrong.
  W1      theory_check_guard.txt measures the guarded decay to look 12 and the law matches it
          (max |z| = 1.65), so Monte Carlo CONFIRMS the delayed decay rather than merely
          predicting it. Looks 0-8 were measured, so "no look beyond the eighth" is the
          correct phrasing.
"""
import os
import sys

PKG = r"c:/Users/DELL/Downloads/MS thess/03_submission_IEEE-TRS"
MAIN = os.path.join(PKG, "manuscript", "main.tex")

EDITS = [
    # ============================================ FAIL-1 + W4: drop the false superlative
    (
        "FAIL-1: Clip-OS1 is less pivotal at 1e-3 and 1e-4, so the superlative is false",
        r"The statistic is also the least pivotal of the thirteen (exploratory): the texture-quintile spread of its rate is \ConfSpreadPanmfTwo{} at $10^{-2}$ and \ConfSpreadPanmfFour{} at $10^{-4}$, against \LInConfSpreadFour{} for IN-ARCP, as Corollary~\ref{cor:texture} leads one to expect for a dwell spanning varying noise.",
        r"Its rate is also strongly texture-dependent (exploratory): the quintile spread is \ConfSpreadPanmfTwo{} at $10^{-2}$ and \ConfSpreadPanmfFour{} at $10^{-4}$, against \ConfSpreadInTwo{} and \LInConfSpreadFour{} for IN-ARCP, as Corollary~\ref{cor:texture} leads one to expect for a dwell spanning varying noise.",
    ),
    # ============================================ FAIL-2 + FAIL-7: the learned comparison
    (
        "FAIL-7: restore 'on IPIX' and 'a different evaluation'; claim no unevidenced protocol",
        r"Learned detectors report $P_{\rm d}=0.91$ at $P_{\rm fa}=10^{-3}$ on these recordings with \TPanmfKiloSec-s observations \cite{qu2023sensors}; over the same \TPanmfKiloPulses{} pulses the self-normalized statistic reaches \TPanmfKiloPd{} at $\TPanmfKiloPfa\times10^{-3}$ (pre-specified, descriptive). Those detectors are trained on labeled targets in these recordings; ours is given no target, and its threshold carries a finite-sample law.",
        r"Learned detectors report $P_{\rm d}=0.91$ at $P_{\rm fa}=10^{-3}$ on IPIX with \TPanmfKiloSec-s observations and a different evaluation \cite{qu2023sensors}; over the same \TPanmfKiloPulses{} pulses the self-normalized statistic reaches \TPanmfThousand{} at $\TPanmfPfaThousand\times10^{-3}$ (pre-specified, descriptive). Those are trained classifiers and ours is given no target, but at this dwell length its measured rate is above the twofold its calibration law bounds, so neither threshold is guaranteed here.",
    ),
    # ============================================ FAIL-3: the calibration record length
    (
        "FAIL-3: 7-9 clutter cells, not 14, and a guarded episode spans 25 pulses, not 17",
        r"At $10^{-4}$ that is \CalEpisodesFour{} episodes, at least \CalSecondsFour~s of clean recording at 1~kHz across 14 range cells, ranked once offline.",
        r"At $10^{-4}$ that is \CalEpisodesFour{} episodes, at least \CalSecondsMin--\CalSecondsMax~s of clean recording at 1~kHz across the \CalCellsMin--\CalCellsMax{} clutter cells of an IPIX file, ranked once offline.",
    ),
    # ============================================ FAIL-4: the units of the stored state
    (
        "FAIL-4: the state is a buffer per cell, not fresh samples every pulse",
        r"at $p$ complex multiply--accumulates and \StatePerCell{} stored samples per cell per pulse.",
        r"at $p$ complex multiply--accumulates per cell per pulse and \StatePerCell{} stored samples per cell.",
    ),
    # ============================================ W1: the measured window, and Monte Carlo
    (
        "W1: looks 0-8 were measured, and the delayed decay is measured, not only predicted",
        r"Only the first \GuardLooksMeasuredWord{} looks were measured; \eqref{eq:rank1} at $\ell-\Delta$ predicts the same decay, delayed.",
        r"No look beyond the \GuardLooksMeasuredWord{}th was measured on these data; Monte Carlo confirms the same decay delayed by $\Delta$ (Supplementary Material).",
    ),
    # ============================================ W2 + W3: per-radar horizon, 5 m/s
    (
        "W2+W3: quote each radar's horizon at its own correlation, and a speed inside the ambiguity limit",
        r"A guard extends the horizon by only $\Delta$ looks: \HorizLooksGuard{} at the opposite Doppler here, which is \HorizMsPrf~ms at a 1~kHz pulse repetition frequency and \HorizSecFrame~s at the 77~GHz frame rate.",
        r"A guard extends the horizon by only $\Delta$ looks, which at the opposite Doppler and each radar's own measured correlation is \HorizMsPrf~ms at a 1~kHz pulse repetition frequency and \HorizSecFrame~s at the 77~GHz frame rate.",
    ),
    (
        "W3: the illustration now uses a radial speed inside the unambiguous interval",
        r"since a target onsets again in each new cell (\CellLooksRef{} looks in a 15~m cell at \CellSpeedRef~m/s, of which \DutyRef\% are visible).",
        r"since a target onsets again in each new cell (\CellLooksRef{} looks in a 15~m cell at \CellSpeedRef~m/s, of which \DutyRef\% are visible; Supplementary Material).",
    ),
    # ============================================ W5: the dichotomy is not exhaustive
    (
        "W5: five other laws fall outside both groups, so the count is a lower bound",
        r"The laws fail in two ways (exploratory).",
        r"The laws fail in at least two ways (exploratory).",
    ),
    # ============================================ W8: the onset cost was a missed prediction
    (
        "W8: disclose that the guard's onset cost exceeded what the protocol allowed",
        r"The guard costs \GuardOnsetCost~dB at onset and a 16-pulse guard \GuardOnsetCostSixteen~dB,",
        r"The guard costs \GuardOnsetCost~dB at onset, more than the protocol allowed for, and a 16-pulse guard \GuardOnsetCostSixteen~dB,",
    ),
    # ============================================ W10: the CFAR loss follows from the ratio
    (
        "W10: the CFAR loss is the extra SCR the ratio implies, not the ratio itself",
        r"the expected $P_{\rm d}$ under calibration is a ratio of Beta functions, the CFAR loss of a conformal threshold \cite{ward2013} (Supplementary Material).",
        r"the expected $P_{\rm d}$ under calibration is a ratio of Beta functions, from which the CFAR loss of a conformal threshold follows \cite{watts2007cfarloss} (Supplementary Material).",
    ),
    # ============================================ parting note: one population per range
    (
        "rule 4: the calibration-set range mixed a dwell minimum with a per-look maximum",
        r"Our $10^{-4}$ calibration sets of \DwellCalMin--\LowCalMax{} episodes give \LowCalPtwoMin--\LowCalPtwoMax.",
        r"Our $10^{-4}$ calibration sets of \LowCalMin--\LowCalMax{} per-look episodes and \DwellCalMin--\DwellCalMax{} dwell segments give \LowCalPtwoMin--\LowCalPtwoMax.",
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
print(f"applied {len(EDITS)} audit fixes to {MAIN}")
