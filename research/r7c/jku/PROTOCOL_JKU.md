# R8-J protocol: second radar, 77 GHz FMCW ground clutter (JKU Linz open dataset); frozen before outcomes

Written 29 Sep 2026. Hash: `PROTOCOL_JKU.sha256`.
- **Before the freeze:** only format and design quantities were inspected, on 4 Rx × 10 frames of `meas_5_int_C`: per-bin median power, per-bin lag-1 chirp correlation, and the chirp hit rate of interference.
- **Not yet computed:** no coverage, width or detection outcome on any file.

## Data
- **Source:** Rienessl & Feger, "77-GHz FMCW Radar Network ADC Data under Various Interference Scenarios at Parking Lot", Zenodo 10.5281/zenodo.21933926 (CC-BY-4.0).
- **Radar:** 76–77 GHz, T_rep = 34 µs, 512 real ADC samples per chirp, 128 chirps per frame, 16 Rx, 100 frames (20 s).
- **Primary file:** `meas_0_ref.mat`, the clean reference run with a static scene and no interferer. It is checked against the Zenodo MD5.
- **Secondary file (J4 only):** `meas_5_int_C.mat` (interferer scenario C).

## Preprocessing (fixed)
1. Apply the dataset's fast-time high-pass filter [1, −1].
2. Apply a Hann window, a 512-point FFT, and keep the single-sided bins.
3. Keep range bins 8–247.
4. Divide each range bin by its known high-pass magnitude |1 − e^{−jω_k}|, so that the receiver noise floor is equal across bins.
   - This is a deterministic per-bin scaling.
   - Innovation-normalized scores are invariant to it.
   - The noise-aware model assumes a single noise power.
5. Use channels Rx ∈ {0, 5, 10, 15} of both stations.

## Episodes, splits and units
- **Episode:** 17 consecutive chirps (m = 16) of one range bin, Rx and frame, with stride 17 (7 per frame).
- **Frame thirds:** A = frames 0–32, B = 34–65, C = 67–99.
- **Rotations** (train, calibrate, test): 1 = (A, B, C), 2 = (B, C, A), 3 = (C, A, B). All three are confirmatory, because no development was done on this data.
- **Units:** station × Rx × rotation = 2 × 4 × 3 = 24.
- **Training:** a seeded subsample of 20,000 episodes. All calibration and test episodes are used.

## Methods
U, RMS, IN1, IN4, NA1, NA4 (conformal), G1 and NA4G (plug-ins), CA16 (|Y| / RMS(H)), and CAloc.
- CAloc uses |Y| / sqrt(P_loc), where P_loc is the mean power of the same bin, Rx and frame over the chirps outside the episode.
- All model fits are unchanged from R7, via `centers_scales`, except that MLP and LS are omitted.
- Levels 1 − α ∈ {0.90, 0.99}.

## CNR classes
- **Episode CNR:** ĉ = max(P_loc/ν̂ − 1, 10^−3), where ν̂ is the NA1 noise power fitted on the unit's training episodes.
- **Classes (dB):** < −5, [−5, 0), [0, 5), [5, 10), [10, 20), ≥ 20.

## Endpoints and stated expectations
- **J1.** Marginal coverage of the conformal methods is within ±0.01 of nominal, averaged over units.
- **J2.** IN1 coverage conditional on CNR class.
  - It is compared with the exact law G_{cR+I}(q̂; r), which uses:
    - the unit's fitted r and conformal q̂;
    - the NA1-fitted ρ;
    - c equal to the class-mean ĉ.
  - Expectation: MAE ≤ 0.02 at 0.90.
  - Expectation: NA1 and NA4 have a smaller maximum class deviation than IN1.
- **J3.** Detection gain over CAloc for injected Swerling-1 targets in Y.
  - SCR is relative to P_loc; the grid is −5 to 25 dB; α = 0.01; the gain is measured at Pd = 0.5, per CNR class.
  - Expectation 1: IN1 gains in the classes ≥ 10 dB and loses in the class < −5 dB, following the sign of 10 log10 G_IN(c), with G_IN(c) = (1+c)/(1+|r|²+c(1−|r|²)).
  - Expectation 2: in every class, NA4's gain is ≥ IN1's gain − 0.5 dB.
- **J4 (descriptive).** Using models trained and calibrated on `meas_0` (rotation 1 splits), test on `meas_5_int_C` frames 67–99. Report coverage separately for episodes whose Y-chirp is interference-hit and for clean episodes.
  - A hit is a chirp whose total range-profile power exceeds 2× the frame median, over bins 20–250.

## Reporting
- Every outcome is reported.
- Uncertainty: cluster bootstrap over Rx × station (8 clusters), 10,000 resamples.
- GPU backend for the NA fits.
