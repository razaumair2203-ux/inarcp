# R17 protocol: a real target with real onsets (frozen before the data were obtained)

Written 2 Oct 2026. `PROTOCOL_R17.sha256` holds the SHA-256 of four files, each computed after converting CRLF line endings to LF:
- this protocol;
- `run_r17_jku.py`;
- the two helpers it imports, `methods.py` and `r12/run_r12_jku.py`.

The run refuses to start if any of the four hashes differs.

## Why
Apart from the IPIX reference target, every detection result in the paper uses injected targets. The IPIX target is present throughout each recording, so it has no onset. No real target with a real onset confirms the paper's positive detection claim: a new return in a range cell is detected at a calibrated false-alarm rate by normalizing the cell's whitened innovation by its own history, at least as well as by normalizing its power.

The JKU 77 GHz dataset already in the paper (Rienessl and Feger, Zenodo 10.5281/zenodo.21933926; file list in `zenodo_files.json`) contains a measurement with a pedestrian. In `meas_3_int_A_pedestrian.mat` "a person was walking in front of Station 1 toward the interferer", under interference scenario A.

**Geometry of the data.**
- Frames are 200 ms apart. Each frame holds 128 chirps of 34 µs.
- Range bins are 15 cm.
- **Within a frame (4.35 ms):** the person stays in one bin, so there is no onset.
- **From frame to frame:** the person moves about 1–2 bins per frame. Each arrival of the person's return in a bin is a real, abrupt onset in that bin's frame-to-frame (scan-to-scan) sequence. This is the setting of clutter-map detectors, which normalize a cell by its own past (Lops 1989; Naldi 1999, both cited in the paper).
- **Two copies.** Because the receivers are real-valued, Station 1 sees every scatterer twice: monostatically, and bistatically via Station 2's transmission, about 15 m (100 bins) farther (documentation, §4). Both copies of the person are real returns of a real target.

## 0. What has been seen before the freeze
**Seen:**
- the dataset documentation (`documentation.pdf`);
- the Zenodo file list and MD5 sums;
- the providers' `processing.py`;
- the mechanics check (below).

**Not seen:**
- `meas_3_int_A_pedestrian.mat` has not been downloaded.
- Its video (`meas_3_int_A_pedestrian.mp4`) has not been viewed, and will not be before the run.

**What may be inspected before the run:** the file's MD5 sum and its array names, shapes and types (`whosmat`).

**The mechanics check.**
- **What it runs:** `--mechanics` runs the whole chain on `meas_2_int_A.mat`, the same interference scenario without the pedestrian, already used in R12. A synthetic walker is injected, with a monostatic and a bistatic copy.
- **How it was used:** its peak error, event count and frame-to-frame |r| shaped the design changes listed at the end of this section.
- **What else was seen:** its output, which was seen before the expectations were written, also prints P_d and false-alarm rates of the four detectors for the synthetic walker. It is saved as `MECHANICS_R17.txt`.
- **What it showed:**
  - median frame-to-frame |r| of 0.12 under mitigation Z;
  - median |r| of 0.61 in the 10% of bins with the largest static-to-noise ratio;
  - P_d within 3 frames for the synthetic walker of 0.46 for IN1 and CA-CM, 0.39 for OS-CM and 0.09 for range CA-CFAR.

**Design changes made after the mechanics check and before `meas_3` was obtained.**
- **The onset rule.** The first draft defined onsets by a single track, which had to stay more than 4 bins away during the history. With the synthetic walker (about 1.25 bins per frame) that rule produced no events.
  - Onsets are now defined by the reference processor (section 2).
  - Up to two peaks per frame are kept, for the monostatic and bistatic copies.
  - The Station 2 consistency check was dropped. Station 2's monostatic and bistatic returns fold onto each other, so a bin-by-bin comparison would not test the track.
- **The primary endpoint** became detection within 3 frames.
- **The 16-channel sum** was added as a secondary look.
- **The expectations** were set from the measured |r| (section 4).

## 1. Data and processing
- **File:** `meas_3_int_A_pedestrian.mat`, MD5 `52d257c47741b0f64433da2ddecad67d`. The array `data_station_1` must have shape (512, 128, 16, 100); it is converted to float64.
- **Per chirp:** the R11/R12 fast-time chain, unchanged: the [1, −1] high-pass, mitigation, a Hann window, an FFT, bins 8–247 (1.2–37 m) and division by |HP|.
- **Mitigation:**
  - **Primary: Z.** R11 zeroing: samples with |x| > 4 × the chirp's median |x|, dilated by ±4 samples, are set to zero.
  - **Secondary: N.** No mitigation.
- **Frame slow time.** For chirp index ch ∈ {0, 32, 64, 96}, the sample of a bin in frame t is its range-profile value in chirp ch of frame t, for t = 0…99.
  - **Primary looks:** receivers rx ∈ {0, 5, 10, 15}. The 16 pairs (rx, ch) are replicate looks at the same events.
  - **Secondary looks:** the 16-channel sum, i.e. the unweighted sum of the 16 receivers' range profiles, with 4 looks (ch). This is not a calibrated beam, and the person's azimuth is not documented.
- **Episode:** frames t−16, …, t of one bin. The history is frames t−16…t−1 (m = 16), and the tested sample is frame t, for t = 16…99.

## 2. Ground truth: a reference processor in another domain
The ground truth uses Station 1's own range-Doppler processing over all 128 chirps and all 16 receivers, with mitigation Z. The detectors under test see one chirp per frame.
- **Range-Doppler power:** for every frame, the range profiles of all 128 chirps and 16 receivers, then a Hann Doppler FFT over the chirps (fftshift; Doppler bins −64…63, 0.45 m/s per bin). Powers are summed over the receivers.
- **Moving power of a bin in a frame:** the largest of these powers over Doppler bins with |index| ≥ 2.
- **Moving-energy ratio MER:** a bin's moving power in a frame divided by its median over the 100 frames, in dB. The median removes the constant Doppler leakage of the static scene. A **moving cell** is a (bin, frame) with MER ≥ 10 dB.
- **Confident peaks.** In each frame:
  - the first peak is the bin of the largest MER, if that MER is at least 13 dB;
  - the second peak is the bin of the largest MER among bins more than 20 bins from the first, if that MER is at least 13 dB.
  - The two copies of the person, about 100 bins apart, give up to two peaks per frame.
- **Onset events.** An event is a (bin, t₀) with t₀ ∈ 16…97, such that:
  - (a) MER ≥ 10 dB in frame t₀;
  - (b) MER < 10 dB in each of frames t₀−16…t₀−1.
  - **Primary events** also satisfy (c): the onset is the person's. A confident peak in frames t₀…t₀+2 lies within ±3 bins of the event bin.
  - **Secondary events:** all events meeting (a) and (b), primary events included.
- **Clean frames** (the single-frame null rule). A (bin, frame) is clean when:
  - no moving cell lies within ±6 bins in that frame, counting only bins 8–247;
  - and no confident peak lies within ±8 bins in frames t−2…t+2.
- **Null episodes:** episodes whose 17 frames t−16…t are all clean for the bin.

## 3. Detectors
All four detectors are scored on the same episodes.
- **IN1 (IN-ARCP).**
  - **Fit:** the AR(1) coefficient r is fitted per (look, bin) with `fit_ols` (clamp 0.98), on the consecutive clean frame pairs of that bin over the whole file. With fewer than 8 such pairs, r = 0. The fit uses the same file as calibration and testing (in-sample by about 1/number of pairs).
  - **Score:** |sample_t − r · sample_{t−1}| / s_r(history), where s_r is the formula of `methods.innovation_scale`, applied with each bin's own r.
- **CA-CM (power clutter map, mean):** |sample_t|² divided by the mean of the 16 history powers.
- **OS-CM (power clutter map, order statistic):** |sample_t|² divided by the 8th smallest of the 16 history powers. This is the clutter-map OS-CFAR comparator of the paper.
- **Range-CA (range CA-CFAR on the current frame):** |sample_t|² divided by the mean power of bins ±3…10 away in the same chirp and frame. That is 2 guard bins and 8 reference bins on each side, with only the bins 8–247 that exist.

**Thresholds.**
- Split-conformal at α ∈ {10⁻², 10⁻³}, per detector, mitigation and look type.
- Calibrated on the null episodes in **even** bins, pooled over the looks. Non-finite scores are left out of calibration; at test, NaN counts as no alarm and +∞ as an alarm. Their number is reported.
- The false-alarm rate is measured on the null episodes in **odd** bins.
- The "3-frame null floor" is also reported: the probability of at least one alarm over three consecutive odd-bin null episodes.
- Detection uses the same thresholds, in all bins. No threshold is recalibrated for any reason.

## 4. Endpoints and expectations
Each expectation is marked in `RESULTS_R17.md` as met, not met, or not informative, whatever the outcome.

**Primary analysis:** mitigation Z, per-receiver looks, α = 10⁻², primary events.
- **Per event:** P_d = the fraction of the 16 looks that exceed the threshold at frame t₀, t₀+1 or t₀+2 ("within 3 frames"). A bin's return builds up over about two frames. The same fraction at t₀ alone is reported as P_d at the onset frame.
- **Summary:** the event mean of P_d.
- **Intervals:** a block bootstrap over onset frames. Events are grouped by t₀ into non-overlapping blocks of 5 frames (t₀ = 16–20, 21–25, …), and the blocks are resampled with replacement. 10,000 resamples, seed 17.
  - **Lower bound:** the 2.5th percentile of the bootstrap means, i.e. the lower end of the two-sided 95% percentile interval.

**What theory predicts here.** Proposition 2 gives the whitening gain over power detection, which is about 1 when the frame-to-frame correlation is small and grows where static clutter is coherent. The mechanics check found:
- median |r| ≈ 0.12;
- ≈ 0.61 in the top decile of static-to-noise ratio.

So parity of IN1 with CA-CM is expected in most bins, and a gain in coherent static bins.

The two other comparators:
- **OS-CM** is expected to lose to both, because an order-statistic scale from 16 samples costs sensitivity (the paper's OS-CFAR loss).
- **Range-CA** is expected to lose because parked cars at nearby ranges inflate its reference. That is the textbook reason clutter maps exist, not a property specific to IN1.

**Expectations.**
- **Feasibility:** at least 20 frames have a confident peak. Otherwise the study is reported as not feasible, and no rule is changed.
- **E1:** at least 20 primary events, falling in at least 8 distinct 5-frame blocks. If E1 fails, everything below is reported as descriptive only, without verdicts.
- **E2 (false-alarm control):**
  - Scope: mitigation Z, per-receiver looks, α = 10⁻².
  - Expectation: for every detector, the odd-bin false-alarm rate divided by α lies in [0.5, 2].
  - If E2 fails for a detector, its results under E3/E4 are still reported, flagged "false-alarm rate not controlled".
- **E3 (non-inferiority to the power clutter map):**
  - E3 is evaluated only if CA-CM's event-mean P_d is at least 0.10. Otherwise it is reported as not informative, with the numbers.
  - Expectation: the lower bound of the event-mean P_d of IN1 minus that of CA-CM is above −0.05.
  - Superiority (lower bound above 0) is also reported, but it is not expected.
- **E4:** the event-mean P_d of IN1 minus that of OS-CM, and of IN1 minus that of Range-CA, each has a lower bound above 0.
- **E5 (mechanism, Proposition 2):**
  - **The ratio.** Each event bin gets a static-to-noise ratio, in dB averaged over the looks. Within one look, the ratio is the median of |sample|² over the bin's clean frames, divided by half the median of |sample_t − sample_{t−1}|² over its clean consecutive pairs.
  - **Events left out.** Bins with fewer than 8 clean frames or 8 clean pairs have no ratio, and their events are left out of E5. Their number is reported.
  - **The split.** The remaining events are split at their median ratio; events at the median go to the low half.
  - **Expectation:** the IN1 − CA-CM difference in event-mean P_d is larger in the high half than in the low half (point estimates). A descriptive bootstrap interval of the high-minus-low difference is reported. The verdict does not use it.

**Headline numbers.** The paper reports these as primary; everything else is secondary:
- the number of primary events and blocks, and the range they cover;
- Pfa/α of the four detectors (Z, per receiver, α = 10⁻²);
- the event-mean P_d within 3 frames of the four detectors, with intervals;
- the differences IN1 − CA-CM, IN1 − OS-CM and IN1 − Range-CA, with intervals;
- the verdicts on E1–E5.

**Also reported, with no expectation:**
- secondary events;
- α = 10⁻³;
- mitigation N;
- the 16-channel sum;
- P_d at the onset frame;
- the 3-frame null floors;
- the median frame-to-frame |r|, overall and in the top static decile;
- the counts of non-finite scores.

## 5. Reporting rules
- Deviations go in `DEVIATIONS_R17.md`, dated and justified. None may be chosen after computing outcomes.
- The results enter the paper whether or not they are favourable, with these limitations stated:
  - one walk by one person;
  - ground clutter at 77 GHz, not sea clutter;
  - frame-rate rather than pulse-rate slow time;
  - ground truth from the same radar's range-Doppler processing, with no external sensor.
