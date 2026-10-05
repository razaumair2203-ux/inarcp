# R22-G: long post-onset trajectories in measured clutter

Date: 5 October 2026. This protocol is frozen and SHA-256 recorded before any new fitted parameter, threshold or detection outcome is computed. The experiment extends the exposed R14/R15 recordings; it is an explicitly motivated extension, not new untouched external confirmation. Scientific R21 files and published tags remain frozen until the new evidence is audited.

## Question and scope

Does the guarded history-normalized score follow its predicted delayed self-masking on measured clutter beyond the eight-look window already reported? Test entire trajectories through full scale contamination. A delayed failure can substantiate the design analysis even when it does not establish sustained-detection superiority. No new jammer/interference design is part of this experiment.

## Fixed data and preprocessing

- All 14 Dartmouth IPIX files in `ipix.FILES`, both like-polarized channels, rotations 2 and 3: 56 units. Provider preprocessing and target-bin exclusion are exactly those in `ipix.load`.
- All 14 NetRAD monostatic node-3 HH/VV files in `r15.netrad.FILES`, rotations 2 and 3: 28 units. Use the existing processed clutter arrays; no sample-dependent re-selection of cells or records. Same preprocessing as R15.
- Retain R14/R15 train/calibration/test thirds and 2,000-pulse gaps. No data selection based on new detection performance. Use training episodes of 17 samples at stride 256 for AR(1) least squares with the existing radial 0.98 clamp.
- Source/raw-file identities and existing processing hashes are recorded in the run manifest. Failed inputs stop or are explicitly documented; do not silently remove a unit. Report actual segments, not planned counts.

## Detector, segmentation and calibration

History length m=16; slow-time guard Delta in {0,8,16}. At pulse t, numerator is |x[t]-r*x[t-1]|^2. Scale is `innovation_scale(x[t-Delta-m:t-Delta],r)^2`, including its initial `(1-|r|^2)*|x[first]|^2/m` boundary term. The latest predictor sample is retained even when it lies in the guard.

Onset index is 32. Long test segments have length 81 with stride 81, giving looks 0..48. For exact calibration continuity with R14/R15, calibration segments retain length/stride 41; compute the look-0 score at index32 and its conformal quantile for per-look alpha=0.01. Fit/calibrate only on assigned train/calibration data. Never calibrate a threshold to new test scores. Report the actual per-guard q^2 and test null rates.

Calibration/test start indices follow the existing exclusive-stop segmentation convention. The longer test stride gives disjoint test episodes; that does not prove exchangeability. Per-look events within an episode are dependent and must not be treated as independent replicates.

## Target experiment

Inject a persistent abrupt Swerling-1 target from index32 through the end of each long test segment. Target complex amplitude is one CN(0,1) draw per segment, common across its pulses and shared across guard/SCR conditions. SCR is {10,20} dB relative to the existing local power proxy, excluding the full 81-sample test segment and using the established +/-1,024-pulse window. No onset gain grid or SCR50 interpolation is added in this part.

Doppler is (i) uniform on [-pi,pi), (ii) the fitted clutter Doppler arg(r), (iii) arg(r)+pi. Random draws use a unit-specific deterministic seed from the first eight hex characters of SHA-256(`R22|G|radar|record|polarization|rotation`). Record full seed strings. Identical amplitude draws are used across Doppler cases; only the random-Doppler case consumes a separate uniform draw array.

## Analytical comparison

Use the existing rank-one formula with **actual per-unit, per-guard conformal threshold**, m16, fitted r and the exact target profile's innovation energies. This is an exploratory plug-in prediction on real noise/texture/model error, not an exact real-clutter theorem.

For the ideal true-AR/no-noise model, the general target-profile calculation must account for the first history sample's stationary initialization. For a unit-height persistent tone:

- Look0: E0=S/(1-|r|^2), EH=0.
- Look>0: E0=S*|1-r*exp(-j*omega)|^2/(1-|r|^2).
- Look<=Delta: EH=0.
- Delta<look<Delta+m: EH=S/(1-|r|^2)*[1+(look-Delta-1)*|1-r*exp(-j*omega)|^2].
- Look>=Delta+m: EH=S + S/(1-|r|^2)*(m-1)*|1-r*exp(-j*omega)|^2.

Do not extrapolate the partial-contamination formula indefinitely. Verify indexing and the arbitrary-profile energies using direct finite-window calculations before raw-data execution. The full-history calculation specializes the existing rank-one proposition rather than changing it.

Average the analytical random-Doppler predictions over each unit's actual registered Doppler draws (or the fixed first 2,000 if more are present, explicitly recorded); use exact matched/opposite Doppler otherwise. Aggregate units with episode-count weights, consistently for empirical and analytical curves. Retain unit curves so alternative weighting can be disclosed as secondary rather than silently substituted.

## Registered outputs and expectations

Primary outputs for every radar/guard/SCR/Doppler are:

1. Per-look detection at every look0..48, counts and denominators; corresponding clean-null trajectories.
2. Mean detection in windows1..8,9..16,17..24,25..32 and41..48.
3. Paired guard differences for those means, with 95% cluster intervals.
4. Mean absolute empirical-versus-plug-in law error separately for the partial-contamination domain and full-history domain.
5. First below-0.5 post-onset crossing, if defined; report not reached/initially below rather than inventing a horizon. Also report any later rebound above0.5, so an initial crossing cannot conceal nonmonotonicity.

Pre-stated expectations, reported whether met or not:

- G1: mean clean false-alarm/design ratio over looks0..48 lies in [0.5,2] for every guard/radar. This is empirical and is not guaranteed by the episode assumptions.
- G2: for random Doppler at20dB, the weighted mean absolute plug-in error in the partial-contamination domain is <=0.10 for each radar/guard. No success is presumed for full-history predictions.
- G3: at10dB and random Doppler, guard16 improves mean detection over looks9..16 by at least0.20 versus guard0 on each radar.
- G4: at20dB, mean detection over looks41..48 is below0.10 for every guard in the random and opposite Doppler cases on each radar. A failure would narrow the anticipated self-masking description; do not censor it.

Secondary outputs: probability of at least one exceedance in the registered look windows under both null and target. These are descriptive acquisition probabilities at a **per-look** alpha. They must not be described as acquisition false-alarm-controlled comparisons; that requires separately calibrated window-max statistics in a different protocol.

## Uncertainty, execution and reporting

IPIX intervals resample its six recording days; NetRAD intervals resample its14 recording identities. Use 10,000 paired cluster-bootstrap resamples, seed SHA-256(`R22|G|bootstrap|radar`) first eight hex characters. Retain all units in each sampled cluster. Weight rates by actual episode counts; bootstrap paired differences together. Do not give binomial intervals treating overlapping looks, cells or rotations as independent trials.

Save per-unit aggregate counts, thresholds, r, seeds, source identities and numerical errors under `study/results/r22_guard`; save summary JSON/CSV and the execution/code manifest under `r22/`. Batching and worker count affect execution only; use float64/complex128. Any changes after freeze are documented as amendments **before** affected outcomes are inspected; any analysis chosen after seeing outcomes is explicitly exploratory.

The independent auditor must verify protocol hash, score indexing, first-history boundary, threshold source, unit completeness, weighting/cluster intervals and saved-count arithmetic. If the experiment provides material insight, integrate it into the paper by replacing weaker content within the existing11-page cap; otherwise report it in the research record without bloating the manuscript.
