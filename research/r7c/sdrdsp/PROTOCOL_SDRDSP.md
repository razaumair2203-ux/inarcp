# SDRDSP protocol: untouched confirmation on a second sea-clutter radar (frozen BEFORE the data were obtained)

Written 30 Sep 2026. The data (SDRDSP/MTDSP, Naval Aviation University, Yantai: the 2019 staring X-band release and the 2022 dual-polarization release, https://radars.ac.cn) had **not been downloaded** when this file was hashed (`PROTOCOL_SDRDSP.sha256`). No method, setting or expectation below can therefore have been tuned on these data.

**Purpose.**
- It is the only confirmation in the paper on data never exposed during development. The IPIX rotations and the second radar were not untouched in that sense.
- It adds a second sea-clutter radar, from a different decade, site, PRF and range resolution.
- It adds more independent recordings than IPIX's six days.
- If target labels permit, it tests real (not injected) target onsets.

## 0. What may be inspected before the analysis is run
Only the following may be read, to write the loader:
- file lists and file sizes;
- array names, dimensions and data types;
- metadata and documentation: PRF, range-cell spacing, polarization, date and time, sea state, and target range cells or AIS tracks as documented by the providers.

**No statistic of the radar samples may be computed before the analysis:** no power, spectrum, histogram or plot.

The loader is committed, with a hash, before `run_sdrdsp.py` is executed. It performs only these steps:
- reading;
- conversion to complex baseband I/Q;
- removal of each range cell's I and Q means;
- scaling to unit mean power per range cell over the whole file. This is the analogue of the IPIX provider recipe; no I/Q imbalance correction is applied unless the provider documents one.

## 1. Units and sampling
- **Unit:** one file × polarization channel (HH and VV separately where both exist).
- **Clusters for uncertainty:** recording sessions, i.e. distinct acquisition start times more than 10 minutes apart. The bootstrap resamples sessions.
- **Clutter cells:**
  - Exclude all cells documented as containing a target at any time in the file (AIS or provider labels), plus 2 guard cells on each side (6 m cells are finer than IPIX's 15 m).
  - If a file has no target documentation, exclude any cell whose whole-file mean power exceeds the file median by more than 10 dB, plus 2 guard cells. This is a fixed rule, and it is reported.
- **Time constants in seconds, equal to IPIX:**
  - stride 0.256 s, i.e. round(0.256·PRF) pulses;
  - texture proxy ±1.024 s;
  - gaps of 2.0 s between thirds.
- **Episode length** m = 16 pulses, the primary setting as in the paper. This is a shorter time span than on IPIX when the PRF exceeds 1 kHz. The pulse count is fixed, not the time span, because the methods and exact laws are defined per pulse.
- **Thirds** in time: train, calibrate, test. There is one rotation (train = first third), so no rotation reuses data within this confirmation.

## 2. Methods: frozen, no retuning
The following are exactly as in the submitted R9 code and R10:
- IN-ARCP (IN1, including the |r| ≤ 0.98 clamp), IN-AR(4), NA-AR(4) (NPMLE, Nelder–Mead cap 1500), G1, NA4G, unnormalized conformal (U), CA16 and CAloc (local window ±1.024 s);
- the dwell detectors PAMF-H and MTD-CA (Hann), with the IN1-sum, NA4-sum and CAloc-sum dwell statistics;
- nominal levels 1 − α ∈ {0.90, 0.99}; detection at α = 0.01;
- SCR grid −5…25 dB; persistent-target dwell K = 8.

No other method, order, window or hyperparameter may be added to the confirmatory analysis.

## 3. Confirmatory endpoints and pre-stated expectations
Each is marked ✓ or ✗ in `RESULTS_SDRDSP.md`, whatever the outcome.

- **S1 (marginal validity):** mean coverage of every conformal method is within 0.01 of nominal at both levels.
- **S2 (texture-conditional false alarms; the main CFAR claim):**
  - at α = 0.01, the ratio of the largest to the smallest texture-quintile Pfa, averaged over units, is ≤ 2.5 for IN1;
  - it is ≥ 10 for U.
  - The spread is reported for IN4, NA4 and CA16 as well, with exceedance counts.
- **S3 (exact law on the false-alarm scale):** for IN1 at α = 0.01, the exact law (Cor. 1, with the NA1 fit on the training third) predicts each texture quintile's Pfa within a factor of 2, in at least 4 of 5 quintiles.
- **S4 (single-pulse whitening gain):** for injected Swerling-1 targets, IN1's gain over CAloc for Pd = 0.5 at α = 0.01 has a session-bootstrap 95% lower bound > 0 dB. The point estimate is reported against the Prop. 2 prediction from the fitted parameters.
- **S5 (noise-aware efficiency):** the same-order radius ratio NA4/IN4 at 0.90 has a geometric mean < 1, with a 95% upper bound < 1.
- **S6 (dwell comparison):** the SCR for dwell Pd = 0.5 at K = 8 (random Doppler) is reported for IN1-sum, NA4-sum, PAMF-H, MTD-CA and CAloc-sum. The expectation carried over from R10 is C2: PAMF-H needs at least 3 dB less SCR than IN1-sum.
- **S7 (blindness):** IN1's per-look Pd at SCR 10 dB after a persistent-target onset decreases from look 0 to look 4.

## 4. Real targets (secondary; only if labels permit)
- If provider labels or AIS give the target's range cell over time, define an **entry event** as the first pulse at which a target is documented in a cell that it did not occupy during the preceding 0.5 s.
- Every detector is calibrated on the clutter cells of the same file, to a dwell Pfa of 0.01.
- Measured on events whose preceding 16 pulses in that cell are target-free by the documentation:
  - the probability of detection within K ∈ {1, 2, 4, 8} pulses after entry;
  - the first-detection delay.
- There is no directional expectation. If fewer than 20 events exist, the results are descriptive only.
- If the labels do not give per-pulse cell occupancy, this part is reported as not feasible, without substitution.

## 5. Reporting rules
- Deviations go in `DEVIATIONS_SDRDSP.md`: for example, a data format that makes a rule above inapplicable. Each deviation is dated and justified, and none may be chosen after computing outcomes.
- Everything not listed above is exploratory and labelled so.
- If an expectation fails, the paper states it.
