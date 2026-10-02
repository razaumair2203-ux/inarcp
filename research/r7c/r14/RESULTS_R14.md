# R14 results: can the technique be improved? (PROTOCOL_R14.md, sha256 9f771091…, frozen before outcomes)

**Run.** 2 Oct 2026, 56 IPIX units, 26 CPU workers. Full numbers are in `r14_summary.txt` and `r14_summary.json`; the analysis is `analyze_r14.py`. **12 of 15 expectations met.**

## Verdicts
| Exp. | Statement | Outcome | |
|---|---|---|---|
| G1 | Guard g = 16 keeps Pfa/α ∈ [0.8, 1.25]; quintile spread ≤ 1.3× that of g = 0 | Pfa/α 1.00 [0.93, 1.03] (10⁻²) and 1.03 [0.81, 1.15] (10⁻³). Spread 1.86 against 1.44, within 1.3× (barely) | ✓ |
| G2 | g = 16, random Doppler, 10 dB: mean per-look P_d over looks 1–8 ≥ 0.5, and < 0.4 for g = 0 | 0.82 against 0.24. Per look: g = 0 gives 0.88, 0.71, 0.64, 0.50, 0.08, 0.01, 0, 0, 0; g = 8 and g = 16 hold 0.82 at every look. Opposite Doppler: 0.94–0.95 at every look | ✓ |
| G3 | Onset (look 0) SCR₅₀ within 0.5 dB of g = 0 | −1.4 dB (g = 0), −0.5 dB (g = 8), −0.1 dB (g = 16). **The guard costs 0.9 dB (g = 8) and 1.3 dB (g = 16) at onset** | ✗ |
| G4 | Ramp L = 16: detection within 8 looks at 10 dB improves by ≥ 0.2 | 0.032 → 0.869 (g = 8) and 0.903 (g = 16). For L = 8: 0.745 → 0.908 | ✓ |
| G5 | Real IPIX target still undetected (exceedance < 2α at 10⁻³) | 0.0008 (g = 16) and 0.0003 (g = 0) | ✓ |
| K1 | κ = 6 conservative at 10⁻³; κ_rule calibrated at both α | κ = 6: 0.67 [0.35, 0.94] at 10⁻³. κ_rule (mode) is 6 at 10⁻² (1.05) and 9 at 10⁻³ (0.90 [0.58, 1.15]) | ✓ |
| K2 | At 10⁻³, the κ_rule certificate reaches P_d = 0.5 below 25 dB in all four interference conditions; κ = 6 does not | At p_h = 5% the certificate is vacuous at 10⁻³ for every κ (P_d = 0). At 2%, κ = 9 gives SCR₅₀ 8.8–8.9 dB and κ = 18 gives 4.2–4.3 dB, while κ = 6 is not reached. The rule was undefined for 16 units at 10⁻³ | ✗ |
| T1 | Certified trimmed sum keeps Pfa/α ≤ 1.2 (upper bound) | ≤ 0.49 everywhere under Bernoulli hits | ✓ |
| T2 | Rule needs t ≥ 4 of 8 at 2%, and trimming costs more than clipping (κ = 6) at both rates | t = 4/5 at 2% and 5/6 at 5% (as predicted). Cost: trim +2.0 vs clip +1.5 dB at 2%, but trim **+5.1 vs clip +5.9 dB** at 5%. Trimming is not costlier at 5% | ✗ |
| X1 | Blanking with mask-matched calibration: Pfa/α ≤ 1.25 in the four Bernoulli conditions (α = 10⁻²) | 1.05, 1.08, 1.13, 1.21 | ✓ |
| X2 | Blanking cost ≤ 3 dB at p_h = 5% | +1.5 to +1.6 dB, against +5.9 to +6.1 dB for the certificate (κ = 6) | ✓ |
| X3 | Blanking calibrated on clean data | 1.07 [1.03, 1.09] (10⁻²) and 1.06 [0.93, 1.14] (10⁻³) | ✓ |
| B1 | The Bernoulli-calibrated certificate exceeds α under bursts | 1.46 (2%) and 1.25 (5%) at 10⁻². Up to 8.5 at 10⁻³ (κ = 18) | ✓ |
| B2 | The burst-calibrated certificate keeps Pfa/α ≤ 1.2 | 0.00, **but vacuous**: it never detects (P_d = 0) | ✓ (vacuous) |
| B3 | Blanking exceeds α under bursts | 2.31 (2%) and 4.14 (5%) at 10⁻². An 8-pulse burst is not an isolated spike | ✓ |

## Detection probability at 10 dB (α = 10⁻², 30 dB interference)
The SCR for P_d = 0.5 is fragile here: under 5% hits the certified detection curve is almost flat (0.65–0.75 at 25 dB), so its 0.5 crossing moves by several dB with small changes in the curve. R12's "9.5 dB" and R14's "6 dB" come from such crossings, while the per-unit median SCR₅₀ is −1.6 and −1.7 dB in both studies. **Report P_d at fixed SCR instead.**

| Detector | No interference | p_h = 2% | p_h = 5% | bursts, 5% (Pfa/α) |
|---|---|---|---|---|
| Clipped, clean threshold (κ = 6) | 0.86 | 0.85 (Pfa/α 1.10) | 0.85 (1.28) | 3.98 |
| Certified clipped, κ = 6 | — | 0.81 (0.55) | 0.64 (0.12) | 1.25 |
| Certified clipped, κ = 9 | 0.85 (clean thr.) | 0.81 (0.53) | 0.71 (0.14) | 1.66 |
| Certified trimmed sum (t = 4 / 5) | — | 0.79 (0.57) | 0.72 (0.23) | 3.60 |
| Blanking, mask-matched calibration | 0.79 | 0.79 (1.08) | 0.78 (1.21) | 4.14 |

At α = 10⁻³ with no interference, P_d at 10 dB is 0.46 for κ = 6, 0.68 for κ = 9 and 0.73 for κ = 18. The clip level matters at low α.

## What this means for the technique
1. **Self-masking is a design choice, not a limit.** A guard of g pulses between the history and the tested pulse shifts the visibility horizon to g + ℓ* (Prop. 4 with ℓ − g). On IPIX it keeps a persistent target at 0.82 per look for all 8 looks, against 0.00 by look 5 without it. It also turns gradual emergence over 16 pulses from undetected (0.03) to detected (0.87).
   - **Cost:** 0.9 dB at onset with g = 8.
   - **Limits:** the real IPIX target, present throughout, remains undetected. Targets at the clutter Doppler remain hard (0.07), which is the whitening loss.
2. **Clip level.** κ = 9 instead of 6 removes the saturation at 10⁻³ at no cost at 10⁻².
3. **The paper's claim that "trimmed sums cannot be certified" is false.** They can be certified when P(more than t corrupted dwell innovations) < α. With AR(1) innovations this needs t = 4–6 of 8, at a cost comparable to clipping.
4. **Blanking with mask-matched calibration** is the cheaper non-certified alternative for isolated pulses: P_d 0.78 against 0.64 at 5% hits, with Pfa/α ≤ 1.21. It fails for bursts (4×) and at 10⁻³ with 5% hits (1.7–2.2×; 2.25 before rounding).
5. **Bursty interference (8-pulse bursts)** defeats every method at these rates. The Bernoulli certificate exceeds α by up to 1.5× (10⁻²); a burst-calibrated certificate is vacuous; blanking exceeds α 2–4×. This is a real limit of slow-time integration.
