# R10 results (PROTOCOL_R10.md, frozen 30 Sep 2026 10:31 PKT, sha256 5ad902ad…; runner committed 2f974a7 before outcomes)

**Data.** 56 IPIX units (rotations 2–3), 74,980 test segments. Full output: `r10_summary.txt`.
- These recordings were seen during development, so this is a frozen-protocol evaluation.
- The dwell Pfa of every detector is 0.0095–0.0111 at design 0.01, and 0.0005–0.0012 at 0.001.

## Stated expectations
| # | Expectation | Outcome | Verdict |
|---|---|---|---|
| C1 | PAMF-H(K′=1) ≡ IN4, \|ΔPd\| < 0.005 | max \|ΔPd\| = 0.0000; statistic identical to 1.8e-15 | ✓ |
| C2 | PAMF-H ≥ 3 dB better than IN1-sum at K′ = 8, Pd 0.5 | 1.01 dB [0.34, 1.67] (at Pd 0.9: 3.95 dB [3.32, 4.43]) | ✗ (IN-ARCP is closer to the classical detector than predicted) |
| C3 | MTD-CA ≥ 5 dB better than CAloc-sum at K′ = 8 | 5.70 dB [1.71, 8.63] | ✓ |
| C4 | PAMF-H matched-Doppler ≥ 3 dB worse than random | 4.25 dB | ✓ |
| R1 | R-pre: IN1's single-look gain over CAloc decreases in L and is < 5 dB at L = 16 | 9.86 → 8.65 → 4.65 dB for L = 1, 4, 8. At L = 16, IN1 never reaches Pd 0.5 at SCR ≤ 25 dB (Pd 0.014 at 10 dB), while CAloc reaches it at 9.1 dB; the gain is therefore not estimable (below any finite value). | ✓ in substance. The scripted check printed FAILED only because the L = 16 gain is undefined (NaN); this is reported, not hidden. |
| R2 | Exact-law MAE for IN1 per-look Pd (ramps) ≤ 0.03 | 0.016 overall. R-pre: 0.001–0.009 (the L = 16 blindness is predicted as 0.015 vs 0.014 measured). R-in: 0.021/0.033/0.037 for L = 4/8/16, under-predicting the early looks | ✓ (overall; the slow in-dwell ramps exceed 0.03 individually) |
| R3 | R-in: IN1's first-detection look increases with L | 0.12, 0.91, 1.94, 2.84 | ✓ |
| A1 | Naive ACI at π = 0.05: clean Pfa < 0.8α and Pd below split | Pfa 0.14α; Pd 0.275 vs 0.890 (γ = 0.02) | ✓ (strong desensitization) |
| A2 | Gated ACI keeps clean Pfa in [0.8α, 1.2α] at π = 0.05 | 0.55α; Pd 0.635 (γ = 0.02). 0.68α, Pd 0.834 (γ = 0.005) | ✗ (the gate only partly protects) |

## What the results mean for the paper
1. **The classical parametric adaptive matched filter captures the same whitening gain.**
   - PAMF-H (AR(4) whitening, history-anchored normalization, Doppler-steered) and the conformal family are within about 1 dB at Pd 0.5 over an eight-pulse dwell. At K′ = 1 they coincide exactly with IN4.
   - The noise-aware sum matches PAMF-H at Pd 0.5 (+0.08 dB [−0.14, 0.30]) and is 0.70 dB [0.49, 1.03] better at Pd 0.9.
   - IN-ARCP is 4 dB worse than PAMF-H at Pd 0.9, because of post-onset blindness.
   - **So the detection gain is not an advantage over classical correlation-aware detection.** The paper must present the disc's exceedance as a PAMF-type test with a calibrated threshold, not as a better detector.
2. **Short-dwell coherent Doppler processing is not competitive here.** MTD over 8 pulses at 1 kHz (125 Hz resolution) with range-cell CA-CFAR needs 5–6 dB more SCR than the whitening detectors at Pd 0.5 and 11–15 dB more at Pd 0.9. It is 4–5 dB *better* than non-coherent power integration. A full coherent processing interval (tens to hundreds of pulses) was not tested.
3. **Gradual emergence is a severe limitation of history-normalized per-look screening.**
   - If the target rises over L pulses before the first look (R-pre), IN-ARCP's first-look gain over the power detector falls from 9.9 dB (abrupt) to 4.7 dB (L = 8). At L = 16 it essentially never detects (Pd ≤ 0.014 at 10 dB).
   - NA4 degrades less, but its SCR for Pd 0.5 is 18.7 dB at L = 16.
   - PAMF-H over the dwell keeps −1.8 dB, and the power detector is unaffected.
   - At 1 kHz, 16 pulses is 16 ms. Targets that migrate into a cell or emerge from sea-surface shadowing rise far more slowly. **The per-look onset screen is therefore limited to genuinely abrupt returns.** The paper must state this in the abstract-level claims.
4. **Online ACI must not treat target returns as clutter feedback.**
   - With 5% of time steps contaminated, naive ACI drives the clean false-alarm rate to 0.14α and Pd from 0.89 to 0.28.
   - A simple guard gate recovers part of this (Pd 0.63–0.83) but does not restore the budget.
   - Operational online calibration needs a target-aware update. This is an open problem the paper states rather than solves.

## Exploratory audit of existing outcomes (not in the protocol; requested by the review)
- **`audit_existing.txt`:**
  - Conditional Pfa/α by IPIX texture quintile and by JKU CNR class, with counts.
  - Exceedance dependence: lag-1 −0.007, cross-bin 0.045.
  - A dependence-aware time-shift reference for the quintile deviation: 0.033, against 0.036 observed for IN1.
  - Leave-one-day-out ranges of the headline effects.
  - Fit diagnostics: the |r| clamp binds in 5/56 units; NA-AR(4) Nelder–Mead reached its 1500 cap in 40/56 units.
- **`na4_convergence.txt`:** restarting the capped NA-AR(4) fits for up to 4,500 further iterations converges 55/56 units.
  - Median log-likelihood gain: 3e-6 per episode.
  - Radius ratio 0.999 (0.979–1.013); coverage unchanged.
  - The reported NA results therefore do not depend on full convergence.
