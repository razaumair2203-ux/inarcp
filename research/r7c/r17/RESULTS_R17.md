# R17 results: real pedestrian onsets at 77 GHz

- **Protocol:** `PROTOCOL_R17.md`, frozen and pushed in commit a4bf4a5 before the data were obtained.
- **Data:** `meas_3_int_A_pedestrian.mat` was downloaded after the freeze. Its MD5 (52d257c4…) matches Zenodo. The providers' video has not been viewed.
- **Run:** `run_r17_jku.py --data`, with all four hashes verified.
- **Outcomes:** `study/results/r17/r17_outcomes.json` (SHA-256 in `r17_outcomes.json.sha256`) and `r17_summary.txt`. The log is `r17/run_r17.log`.
- **Deviations:** none.

## Verdicts
| Item | Pre-stated | Outcome | Verdict |
|---|---|---|---|
| Feasibility | ≥ 20 frames with a confident peak | 31 | feasible |
| E1 | ≥ 20 primary events in ≥ 8 five-frame blocks | 74 events in **7** blocks (onset frames 18–48) | **NOT MET**, so everything below is descriptive only (protocol §4) |
| E2 | Pfa/α in [0.5, 2] for all four detectors (Z, per receiver, 10⁻²) | IN1 0.96, CA-CM 0.98, OS-CM 0.96, Range-CA 1.10 | descriptive (inside the range) |
| E3 | IN1 − CA-CM lower bound > −0.05 (informative if CA-CM ≥ 0.10) | +0.024 [0.007, 0.047]; CA-CM 0.274 | descriptive (on the expected side; the lower bound is also above 0) |
| E4 | IN1 − OS-CM and IN1 − Range-CA lower bounds > 0 | +0.067 [0.046, 0.091]; +0.223 [0.131, 0.349] | descriptive (on the expected side) |
| E5 | IN1 − CA-CM larger in the high static-to-noise half | high +0.047 (n = 37), low 0.000 (n = 37); split at 0.8 dB | descriptive (on the expected side) |

**Why E1 failed.** The person was tracked for only 31 frames (about 6 s) out of 100. All the onsets therefore fall in frames 18–48, which form 7 of the 5-frame bootstrap blocks; the protocol requires 8. With 7 blocks the bootstrap intervals above are understated (pre-freeze review, B4). They are shown only as descriptions.

## Headline numbers (protocol §4; primary analysis: Z, per receiver, α = 10⁻², primary events)
- **Events:** 74 real onset events in 7 blocks. They cover bins 8–179 (1.2–26.8 m, monostatic and bistatic copies of the person) and onset frames 18–48.
- **Pfa/α:** IN1 0.96, CA-CM 0.98, OS-CM 0.96, Range-CA 1.10. The 3-frame null floor is 0.017–0.029.

**Event-mean P_d within 3 frames, with descriptive intervals:**

| Detector | P_d | Interval |
|---|---|---|
| IN1 | 0.297 | [0.165, 0.441] |
| CA-CM | 0.274 | [0.138, 0.418] |
| OS-CM | 0.231 | [0.105, 0.372] |
| Range-CA | 0.074 | [0.018, 0.163] |

**Differences in P_d, with descriptive intervals:**

| Difference | Value | Interval |
|---|---|---|
| IN1 − CA-CM | +0.024 | [0.007, 0.047] |
| IN1 − OS-CM | +0.067 | [0.046, 0.091] |
| IN1 − Range-CA | +0.223 | [0.131, 0.349] |

## Secondary (no expectation)
- **At the onset frame:** P_d is 0.178 (IN1), 0.171 (CA-CM), 0.145 (OS-CM) and 0.046 (Range-CA).
- **At α = 10⁻³ (Z, per receiver):**
  - Pfa/α: 0.87, 0.94, 0.73 and 0.82.
  - P_d within 3 frames: 0.172, 0.149, 0.128 and 0.024.
- **16-channel sum (Z, 10⁻²):** Pfa/α 0.92–1.11 (Range-CA 0.77). P_d within 3 frames is 0.243, 0.209, 0.186 and 0.051.
- **No mitigation (N, per receiver, 10⁻²):** Pfa/α 0.97–1.03. P_d within 3 frames is 0.162, 0.149, 0.108 and 0.090. Fast-time zeroing nearly doubles every clutter-map detector's P_d.
- **Frame-to-frame |r| (Z, per receiver):** median 0.115; 0.577 in the top static decile. This matches the mechanics check (0.12 and 0.61).
- **Secondary events** (86, all onsets of moving energy): the same order as the primary events.

## Reading
- **On one real pedestrian under real interference (scenario A),** IN-ARCP detects real onsets at a calibrated false-alarm rate. It matches the power clutter map and edges it out only where static clutter is coherent from frame to frame, which is what Proposition 2 predicts for nearly white clutter. It beats the OS clutter map and range CA-CFAR.
- **The confirmatory criterion E1 failed on the number of independent blocks** (7 of 8). The result is therefore reported as descriptive.
- **Limitations, as the protocol requires:**
  - one 6-second walk by one person;
  - ground clutter at 77 GHz, not sea clutter;
  - frame-rate rather than pulse-rate slow time;
  - ground truth from the same radar's range-Doppler processing, with no external sensor.
