# PROTOCOL R14: can the technique be improved? (frozen before any R14 outcome is computed)

Date: 2 Oct 2026. Data: the 56 IPIX evaluation units (14 sessions × 2 like-polarized channels × role assignments 2 and 3). All settings are those of R12 unless stated: M = 16, K = 8, AR(1) fitted by least squares on the training third, conformal thresholds on the calibration third, test on the test third, dense non-overlapping segments (stride = segment length, about 18,000 dwell segments per third and unit, so that α = 10⁻³ is resolvable), Swerling-1 targets with SCR −5…25 dB relative to the local power, 95% day-cluster bootstrap intervals (6 days, 10,000 resamples). Seeds: SHA-256 of "R14|part|file|pol|rot". The runner is `run_r14_ipix.py`. Results go to `study/results/r14/`, the summary to `RESULTS_R14.md`.

A synthetic dry run (`--synthetic`, AR(1)+texture+noise, not IPIX) is allowed before freezing; it checks the mechanics only. Before freezing, the dry run led to two design changes: dense calibration (α = 10⁻³ was not resolvable with segments every 256 pulses) and isolation-based blanking with a robust dwell reference (pure power blanking removed strong persistent targets; a median dwell reference failed when two hits fell in one dwell).

## Weaknesses addressed (from the 1 Oct 2026 reviews and the independent theory check)
- W1, self-masking: a persistent target is lost after about ℓ* ≈ 3.7 looks.
- W3, certificate cost: 1.4 dB at 2% hits and 9.5 dB at 5%. The certified false-alarm rate is about 25× below α in simulation, so the certificate is very conservative.
- W4, fragility: the certificate breaks under bursty hit patterns.
- W5, clip saturation: κ = 6 saturates at α = 10⁻³.
- A paper claim to test: "trimmed sums cannot be certified".

## Part G: guarded (lagged) history scale (W1)
**Statistic.** IN-ARCP-G_g is |Y − r h_m|² / s_r(H_g)². Here H_g holds the M = 16 samples that end g pulses before the last history sample; the predictor still uses the most recent sample. g ∈ {0, 8, 16}, and g = 0 is IN-ARCP.

**Theory.** Prop. 4 holds with ℓ replaced by ℓ − g, so the visibility horizon becomes g + ℓ*. For ℓ ≤ g the scale is clean and P_d = (1 + β/(1 + S_w|d|²))⁻ᵐ.

**Measurements:**
1. Clean test Pfa/α at α ∈ {10⁻², 10⁻³}, and the texture-quintile spread at 10⁻².
2. Persistent abrupt target (random, opposite and clutter Doppler; onset at the first tested pulse): per-look P_d at looks 0–8 at 10 dB, the probability of detection within 8 looks, and the SCR for 0.5 of the latter.
3. Ramps of L ∈ {8, 16} pulses ending at the first tested pulse: probability of detection within 8 looks at 10 dB.
4. The real IPIX target cell: exceedance rate at α = 10⁻³.

**Expectations:**
- **G1:** for g = 16, Pfa/α ∈ [0.8, 1.25] at both α; the quintile spread is at most 1.3 × that of g = 0.
- **G2:** g = 16, random Doppler, 10 dB: mean per-look P_d over looks 1–8 ≥ 0.5, against < 0.4 for g = 0.
- **G3:** onset (look 0) SCR for P_d = 0.5 within 0.5 dB of g = 0.
- **G4:** ramp L = 16: detection within 8 looks at 10 dB is higher than for g = 0 by ≥ 0.2. This is uncertain, because the predictor may track a slow ramp.
- **G5:** the real target remains undetected, with an exceedance rate below 2α. The target fills every history.

## Part K: clip level (W5)
**Setting.** Certified clipped integration (Theorem 1) with κ ∈ {4, 6, 9, 12, 18}, OS history scale k_H = 8, α ∈ {10⁻², 10⁻³}.

**Measurements:**
- clean test Pfa/α and the SCR for P_d = 0.5 (persistent random-Doppler target, dwell from onset);
- under injected Bernoulli interference (p_h ∈ {2%, 5%}, 10 and 30 dB): certified Pfa/α and SCR₅₀.

**Rule, fixed now.** κ_rule = the smallest grid value at which the clean calibration statistic reaches its cap Kκ with probability ≤ α/10. It is computed on calibration data only.

**Expectations:**
- **K1:** κ = 6 is conservative at 10⁻³ (Pfa/α < 0.8), and κ_rule gives Pfa/α ∈ [0.8, 1.25] at both α.
- **K2:** at 10⁻³ the certified clipped integrator with κ_rule reaches P_d = 0.5 below 25 dB in all four interference conditions; with κ = 6 it does not.

## Part T: certified trimmed sum (claim test)
**Statistic.** T_t is the sum of the K − t smallest normalized dwell powers. Its worst case sets corrupted dwell terms to +∞ and corrupted history powers to 0, so it is finite iff at most t dwell innovations are corrupted.

**Rule.** t = the smallest value with P(more than t corrupted dwell innovations) ≤ α/5 under the hit model. This is computed by simulating the hit model; a hit pulse corrupts two AR(1) innovations.

**Expectations:**
- **T1:** certified Pfa/α ≤ 1.2 (upper bound) in every condition.
- **T2:** the rule needs t ≥ 4 of 8 at p_h = 2%, and certified trimming costs more SCR than certified clipping (κ = 6) at both hit rates. So "cannot be certified" should become "can be certified only at a large cost".

## Part X: pulse blanking with mask-matched conformal calibration (W3; a non-certified alternative)
**Statistic.** A normalized power z_i (history or dwell, relative to the median history power) is blanked when it is an isolated spike: z_i > 10 **and** z_i > 4 × a robust level of its own block (history: the median; dwell: the third-smallest z, which stays clean with up to five corrupted terms). A persistent target raises the whole dwell and is therefore kept. The innovation that follows a blanked one is blanked too, because a hit pulse corrupts two innovations. The history scale is the median of the unblanked history powers. The statistic is K × the mean of the unblanked dwell z_i. If every dwell term is blanked, the statistic is 0.

**Calibration.** On clean calibration segments, apply the same blanking rule plus extra random blanking masks from the Bernoulli hit model (mask-matched calibration).

**Guarantee (stated, not proved).** Valid when every hit exceeds the blanking level. Weaker interference stays in the statistic.

**Expectations:**
- **X1:** Pfa/α ≤ 1.25 in all four injected conditions.
- **X2:** the SCR₅₀ cost against clean clipped integration (κ = 6) is ≤ 3 dB at p_h = 5%, against 9.5 dB for the certificate.
- **X3:** clean Pfa/α ∈ [0.8, 1.25].

## Part B: bursty interference (W4)
**Setting.** Hits come in bursts of 8 consecutive pulses with the same average rate p_h ∈ {2%, 5%}, at 30 dB. Compared:
- the certified clip calibrated on the Bernoulli model (misspecified);
- the certified clip calibrated on the burst model;
- Part X with Bernoulli masks.

**Expectations:**
- **B1:** the Bernoulli-calibrated certificate exceeds α (Pfa/α > 1) in at least one burst condition.
- **B2:** the burst-calibrated certificate keeps Pfa/α ≤ 1.2.
- **B3 (revised after the synthetic dry run, before any IPIX outcome):** Part X exceeds α under bursts (Pfa/α > 1.25), because an 8-pulse burst is not an isolated spike; blanking is not a remedy for bursty interference.

## Reporting
- Every expectation is reported as met or not met, with the numbers.
- Post-hoc analyses are labelled exploratory.
- No R14 result enters the main paper unless it replaces weaker content (`CLAUDE.md` rule 1).
