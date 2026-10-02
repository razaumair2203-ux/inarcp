# R15 results: untouched confirmation on NetRAD S-band sea clutter (PROTOCOL_R15.md, sha256 945c5e51…, frozen before outcomes)

**Run.** 2 Oct 2026, 28 units: 14 node-3 recordings × role assignments 2 and 3. Full output is in `analyze_r15.log`, `r15_summary.txt` and `r15_summary.json`; deviations are in `DEVIATIONS_R15.md`. **12 of 15 expectations met.**

**Data.**
- **Correlation.** The AR(1) coefficient is |r| = 0.97–0.98. The frozen clamp at 0.98 binds in 12 of 14 recordings, because S-band sea clutter at 1 kHz is very highly correlated.
- **Flagged pulses.** The wideband rule flags 3.3–22.8% of the **HH** pulses, in bursts with a mean length of 3.7–6.0 pulses. VV is almost clean (≤ 0.08%), apart from rare short events.
  - Whether the flags are interference or range-extended HH sea spikes is **not established**. See the exploratory `explore_r15_flag_extent.py`: flagged pulses have a median of about 108 elevated bins, 85–91% of them outside the clutter window, while unflagged HH pulses have about 80.

## Verdicts
| Exp. | Statement | Outcome | |
|---|---|---|---|
| N1 | Conformal P_fa/α in [0.5, 2] for ≥ 12 of 13 statistics at 10⁻³ and at 10⁻⁴ | 10⁻³: 13 of 13 (1.01–1.36). **10⁻⁴: 7 of 13.** Outside: D-IN4 4.26, P-ANMF(bin) 2.52, P-ANMF 2.33, PAMF-H 2.18, NA4 2.08, and Clip-OS1 0.39 (conservative). The per-look scores stay at 1.02–1.38 | ✗ |
| N2 | ≥ 5 of 9 whitened Gaussian laws > 2× at 10⁻⁴ | 7 of 9; 9 of 11 with both ANMF laws | ✓ |
| N3 | IN1 CA law ≤ 2× at 10⁻⁴ | 1.70 [0.91, 2.66] | ✓ |
| N4 | IN1 quintile spread at 10⁻² ≤ 2.0 and below CA16's | **2.40 against 1.51.** Note: on IPIX, in the same analysis, it was 1.31 against 1.06. The expectation had not been checked against IPIX before it was written | ✗ |
| N5 | PAMF-H within 0.5 dB of the best dwell detector at P_d = 0.5 | Met, but uninformative: every whitened dwell detector reaches P_d = 0.5 at the lowest SCR tested (−5 dB). At P_d = 0.9, PAMF-H needs −3.4 dB (IPIX: 5.1 dB) | ✓ |
| N6 | IN1look needs less SCR than OSraw | OSraw 7.2 dB against IN1look ≤ −5 dB, a gain of ≥ 12 dB | ✓ |
| N7 | g = 0: look-4 P_d ≤ half of look 0 | 0.97 → 0.24 | ✓ |
| N8 | g = 8: mean P_d over looks 1–8 ≥ 0.6 and ≥ 3× that at g = 0 | 0.92 against 0.30. The law (exploratory) gives 0.92 | ✓ |
| N9 | g = 8 clean P_fa/α in [0.8, 1.25] | 1.05 | ✓ |
| N10 | 5% hits, 30 dB: D-IN1 > 2×; certified clip ≤ 1× | 22.0 and 0.10 | ✓ |
| N11 | Certified κ = 9 at 5%: P_d at 10 dB ≥ 0.5 | 0.91 | ✓ |
| N12 | Blanking ≤ 1.25× with independent hits; > 1.25× under 5% bursts | 1.10 and 1.25; 4.11 under bursts | ✓ |
| N13 | Independent-hit certificate > 1× under 5% bursts | 1.66 | ✓ |
| W1 | Flagged pulses: certified clip (empirical hit model) ≤ 1.2× | 0.04, **but vacuous** (P_d = 0.04) | ✓ |
| W2 | Flagged pulses: D-IN1 > 1.5× in hit segments | **1.08** (1–2 hits) and 1.08 (≥ 3 hits) | ✗ |

## Exploratory, post hoc (labelled as such; `explore_r15_hotspots.py`, `explore_r15_hotspots_output.txt`)
**Where the 10⁻⁴ excess of the dwell statistics comes from.**
- It is concentrated in a few units. In 1450/rot3 (VV), D-IN4 has 923 exceedances; 99% fall within 3 s of the test third and 99% coincide with a flagged wideband-interference pulse. In 1501/rot3 (VV), 91% fall within 1 s and 86% coincide with a flagged pulse.
- These are rare, strong interference events that the calibration third did not contain, which breaks the exchangeability that the conformal guarantee needs.
- In 1128/rot3 (HH), the P-ANMF exceedances (467) are spread over a few cells and three seconds, and 48% coincide with flagged pulses.
- The per-look scores were not affected in the pooled numbers.

**Why the frequent HH hits do not raise false alarms.** The hit rule flags a pulse when more than 10% of all 1024 range bins exceed ten times their median, and most of those bins are noise-limited. In the clutter cells, the frequent HH interference is weak relative to sea clutter: D-IN1 runs at 1.05–1.08× even in hit segments. A certificate calibrated on these frequent, bursty hit masks is therefore needlessly conservative and nearly vacuous, while blanking with mask-matched calibration keeps P_d = 0.92 at 0.57× design.

## What this means for the paper
1. **Replicated on an untouched second radar:**
   - conformal calibration to 10⁻³ for every statistic, and to 10⁻⁴ for the per-look scores;
   - failure of the Gaussian-model laws in the tail (9 of 11), with IN-ARCP's CA law the most robust;
   - the guard (0.92 per look against 0.30; the law's 0.92) and its effect on ramps (0.02 → 0.94);
   - the certificate under injected interference, at a small cost (P_d 0.92);
   - the failure of every remedy under bursts.
2. **Not replicated:**
   - conformal calibration of the dwell and Doppler statistics at 10⁻⁴, where real interference events absent from the calibration data break exchangeability;
   - the pivotality ranking against CA16.
3. **New lesson for certification.** A certificate is only as useful as its hit model. A hit rule that flags weak, frequent interference makes the certificate vacuous where an uncertified detector was already calibrated. The hit model should count only hits strong enough in the cells under test.

## Correction after the exploratory checks of 2 Oct 2026
These checks were run after the outcomes, the claim audit and a blind review, and are labeled exploratory.
- The 10⁻⁴ excess of integration and PAMF-H is concentrated in two VV units, 1450 and 1501 (rotation 3). Their calibration thirds contain no flagged pulse, and their test thirds contain brief flagged events. Without these units the excess is 1.56 and 1.33.
- The P-ANMF excess comes from HH unit 1128 (rotation 3), which has flags in both thirds.
- The noise-aware excess (2.08), and an integration excess in 1508 (rotation 2), which has no flags, remain unexplained.
- Calling the HH flags "real interference" above was premature; the paper calls them flagged pulses.
- Design lesson: a hit model built from a rule that also fires on harmless or clutter-like events makes the certificate vacuous.
