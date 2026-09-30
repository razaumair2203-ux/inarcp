# R12 results (PROTOCOL_R12.md, sha256 a32706e7…, frozen at commit 86a7055 before outcomes)

Outcome files are hashed in `OUTCOMES_SHA256.txt`. Full outputs:
- `r12_summary.txt/json`: IPIX, with 10,000 day-cluster bootstrap resamples;
- `r12_jku_summary.txt/json`: JKU;
- `verify_laws_output.txt`: theory, 400,000 replications.

**Implementation notes, before the real-data runs:**
- The Fisher-g threshold search was re-bracketed (numerical; the law is unchanged).
- JKU targets are propagated as lone raw-ADC tones through the linear chain, rather than as a comb. The comb leaked −25 dB under zeroing. The protocol only requires a raw-domain beat tone at the CUT bin.

**12 of 18 expectations met.**

| # | Expectation | Outcome | Verdict |
|---|---|---|---|
| S | Every closed form agrees with Monte Carlo | 65 probability checks, max \|z\| = 2.91; certificate: 0 violations in 21 conditions | ✓ |
| L1 | Conformal Pfa/α in [0.8, 1.25] at 1e-2 and 1e-3, and [0.6, 1.6] at 1e-4 | All statistics within the band, except the clipped integrator: 0.67 at 1e-3 and 0.03 at 1e-4, conservative because the statistic saturates at K·c = 48 | ✗ |
| L2 | At 1e-4, at least 3 Gaussian-model rules for whitened statistics exceed 2α | 8 of 9 do: IN4 2.7, NA4 7.5, D-IN4 14, PAMF-H 9.9, P-ANMF bin 5.5, P-ANMF max 50, OS 46, clipped 60. IN-ARCP's CA law gives 1.9 | ✓ |
| L3 | ANMF-SCM law > 1.5α and ANMF-FP law within [0.5, 2]α at 1e-3 | SCM 3.6α ✓; FP 2.7α ✗. Both classical ANMF laws fail on real clutter | ✗ |
| L4 | White laws of CA16 and OSraw off by more than 3× at 1e-3 | OSraw 5.6× ✓; CA16 0.56× (conservative, off by 1.8) ✗ | ✗ |
| L5 | Residual bootstrap for IN1 > 1.2α at 1e-4 | 4.3α | ✓ |
| L6 | Conformal IN1 texture-quintile Pfa spread at 1e-3 ≤ 3 | 1.5 | ✓ |
| A1 | PAMF-H at least 1 dB more sensitive than ANMF-FP at Pd 0.5 | 5.4 dB [1.9, 8.8]. PAMF-H reaches Pd 0.5 already at the grid floor (−5 dB), so this is a lower bound | ✓ |
| A2 | Clip-OS1 within 1.5 dB of D-IN1 | 2.0 dB [0.0, 2.9]. At α = 0.001 the clipped and binary integrators never reach Pd 0.5 (saturation, as in L1) | ✗ |
| A3 | OSraw at least 5 dB worse than IN1 at the first look | 10.6 dB [7.1, 12.7] | ✓ |
| T1 | History-normalized detectors blind on the real target | IN1 Pd 0.0004 and Clip-OS1 Pd 0.0004, against clutter Pfa 0.0010 and 0.0007 | ✓ |
| T2 | P-ANMF Pd increases from N = 8 to 256 in ≥ 80% of units | 86% (mean Pd 0.22 → 0.40) | ✓ |
| T3 | P-ANMF ≥ CA-NCI-range at N = 64 in ≥ 60% of units | 100% (0.30 vs 0.004) | ✓ |
| T4 | Descriptive: P-ANMF mean Pd at N = 1024, 1e-3 | 0.41 (clutter Pfa 0.0026). Fisher-g thresholds give Pfa 0.013–0.40 | — |
| I1 | Certified Clip/Bin: upper bound of Pfa ≤ 1.2α in all four conditions | Largest upper bound 0.61α | ✓ |
| I2 | D-IN1 and PAMF-H ≥ 5α at p = 0.05, JNR 30 dB | 21α and 22α | ✓ |
| I3 | Certified clipped integrator costs ≤ 2 dB at p = 0.02 | 1.4–1.5 dB | ✓ |
| J1 | Clip-OS1-cert Pfa ≤ 1.2α in run C under N and Z | 0.54α and 0.51α | ✓ |
| J2 | D-IN1 under N ≥ 5α in runs A and C | 0.81α (A) and 1.42α (C; 3.6α in segments with 1–2 hit chirps). Real chirp interference mainly masks targets | ✗ |
| J3 | ZAR improves IN1 over Z by ≥ 1 dB in run A | 0.2 dB | ✗ |

## Reading

1. **Calibration is what the conformal threshold adds.**
   - On real sea clutter, the model-based laws of every whitened detector, of the ANMF (SCM and Tyler) and of the AR residual bootstrap exceed their design Pfa by 2–60× at 1e-4.
   - The conformal thresholds hold, to within 0.73–1.47× design, for every statistic except the clipped one, which is conservative.
   - IN-ARCP's own CA law is the most robust model-based rule (1.02 at 1e-3, 1.9 at 1e-4).
2. **Real targets.**
   - On the real IPIX target, history-normalized detectors do not detect it at all. This is consistent with Proposition 3, which was derived after a development check (V4) had shown the same.
   - Self-normalized whitened Doppler (P-ANMF) detects it with Pd 0.22 at 8 pulses and 0.40 at 256 pulses, at design Pfa 1e-3; the measured clutter Pfa was 1.1e-3 and 1.5e-3, and 2.6e-3 at 1,024 pulses.
   - It is far below long-observation learned detectors (Pd 0.91 at 1.024 s, Qu et al. 2023). It is a short-dwell detector, and its analytic thresholds fail on real clutter.
3. **Pulsed interference.**
   - The certificate holds on IPIX with injected interference and on real FMCW interference.
   - The cost:
     - 1.4 dB at a 2% hit rate and 9.4 dB at 5% (IPIX, per pulse);
     - about 3 dB on hit-free segments and 6 dB overall at 4.6% whole-chirp hits (JKU C);
     - near-vacuous at 45% (JKU A).
   - Where fast-time zeroing applies it is cheaper and returns every detector to its clean-reference Pfa. AR gap reconstruction adds 0.2 dB.
4. **Design lesson.** The clip level c = 6, frozen in the protocol, saturates the clipped statistic at α ≤ 1e-3. This suggests, but does not test, choosing the clip level above the per-look threshold at the design α.

## Post-outcome audit (1 Oct 2026)
An independent adversarial audit of the manuscript against these results found 12 problems in the text; every one was fixed in the manuscript. None of them changes a frozen outcome or verdict. The substantive ones:
1. **Real-target blindness.** It had already been observed during development (VALIDATION_REPORT V4). It is now described as consistent with Proposition 3, not as a prediction.
2. **Calibration-size numbers.** `laws.n_required` stepped in 5% increments and returned non-minimal values. P{Pfa > 2α} is not monotone in n. Corrected values (`calibration_size.txt`): smallest n is 149 / 1,497 / 14,978, and the condition holds for every n ≥ 313 / 3,146 / 31,477. The IPIX 1e-4 calibration sets (about 23,000) give 0.056.
3. **Theorem 1.** It needs dominance of the hit pattern in the inclusion order; a rate bound is not enough. It also needs exchangeable clean calibration and test data. The IPIX Part I check uses the calibration hit model itself, so it tests implementation and cost, not model mismatch.
4. **Prior art added:** Lops & Orsini 1989 and Naldi 1999 (clutter-map self-masking); Zaffran et al. 2023 and Levine & Feizi 2020 (mask and sparse-perturbation certification).
