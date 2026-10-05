# R22-M: idealized range response and unknown acquisition timing

Date: 5 October 2026. Freeze this protocol, configuration, runner and imported implementations before raw-data preparation, fitted parameters, calibration or detector outcomes. This is a prospectively locked extension on already exposed NetRAD clutter, not untouched external validation. Preserve R21 and all earlier outcomes.

## Question, expectations and scope

Does the short-history innovation score acquire a continuously present, migrating target when it receives neither a native-cell step onset nor a timing oracle? Compare complete range/time acquisitions, including measured background exceedances. The provider confirms 6 m native range-bin spacing, but supplies no verified complex point-spread function. The two sinc responses below are idealizations. This experiment cannot establish performance for authentic hardware range sidelobes or real targets.

M1: all 14 fixed records and both rotations complete, with finite fits, scores and thresholds. M2: held-out null acquisition rates fall within 0.5--2 times the design probability for each method after refitting; evaluate and report every failure. These dependent windows do not acquire exchangeability merely through disjoint segmentation. M3: the primary paired comparisons of guarded versus unguarded IN, and guarded IN versus every competing method, can be estimated for every fixed condition. No superiority, noninferiority or ranking is assumed. The physics makes a universal IN advantage implausible: continuous occupancy can contaminate its scale, and the migration in an eight-pulse guard is small relative to either idealized response width. This is a practical boundary test, not an outcome-selected attempt to recover a favourable claim.

## Data, partitions and preprocessing

Use all 14 existing monostatic node-3 HH/VV `Data_matched` files named in the configuration, and their existing fixed clutter-bin intervals in `r15/netrad.py`. Keep all observed pulses, including interference; remove only trailing all-zero padding by the existing provider-style rule. No hit-based exclusion or new cell selection is allowed.

For each complete recording, retain the existing whole-record per-bin complex mean removal and residual RMS normalization. Save original means and gains. This is an inherited preprocessing convention, not a train-only fitted front end. Inject targets in original matched-filter units, then divide each target bin by that bin's fixed gain; do not normalize every injected bin to the same apparent target power.

Split pulses into thirds A/B/C, with a 2,000-pulse trailing gap in A and B. Rotations are train/cal/test B/C/A and C/A/B. Fit the existing AR(1) least-squares coefficient from all designated training clutter bins using 17-sample episodes at stride 256, with the existing magnitude clamp 0.98. Save the coefficient and all source identities. A fitted AR coefficient does not certify the true-AR or common-texture assumptions.

Select four nonoverlapping three-bin groups by uniformly spaced native-bin indices, using the exact index-only rule in the runner. Do not choose groups using detection outcomes. Each acquisition has 40 prefix samples and 1,024 search endpoints; acquisitions are contiguous, disjoint 1,064-pulse units within their split. Every group is evaluated at every window, giving dependent spatial replicates. Planning geometry gives approximately 152--160 calibration/test units per rotation for 130,000 pulses; report actual saved counts, never these planning counts as outcomes.

## Identical acquisition searches and comparator definitions

All eight methods receive the same complete segment and declare an acquisition if any score exceeds their threshold in the identical three-native-bin by 1,024-endpoint search. No camera/range trajectory, target Doppler or crossing time is supplied to a detector. A Doppler-bank maximum is included inside that detector's acquisition calibration.

Use m=16 and guards Delta=0,8. IN uses |x[t]-r x[t-1]| squared over the innovation-history scale, including the stationary first-history term (1-|r| squared)|x[first]| squared /m. CA uses raw current power over raw history mean. OS uses raw current power over the eighth smallest of 16 raw history powers. These six methods have identical histories at a given guard.

PAMF-H1-K8-G8 uses the latest eight AR(1) innovations, a fixed 64-frequency DFT bank, maximum coherent power divided by eight, and a 16-sample innovation history ending eight samples before the earliest raw sample of the current dwell. P-ANMF1-N16 uses the latest 16 AR(1) innovations and the same fixed 64-frequency bank, normalizing maximum squared DFT amplitude by 16 times current-dwell energy. These are explicitly named AR(1) variants; they do not silently replace the earlier AR(4), eight-look P-ANMF experiment. The numerator's steady-tone innovation factor cancels in its normalized steering direction; no step-onset steering is supplied.

Calibrate each method's full search maximum on its designated calibration split at acquisition alpha=0.01, using the existing split rank k=ceil((n_cal+1)(1-alpha)) and strict score>threshold. For n_cal=152--160, k=n_cal: the largest calibration maximum. Under independent continuous exchangeable scores the actual rank tail is 1/(n_cal+1), approximately 0.0062--0.0065, rather than exactly 0.01. The measured data have dependencies and distribution shift; report the realized rank, ideal rank-tail mass and held-out null rates separately. Nominal equality does not imply equal realized false-alarm rates. Do not refit to equalize test rates.

## Continuous physical target model

For every test acquisition and its prefix, use one complex CN(0,1) amplitude held over the complete 1.064 s segment. This Swerling-1-like segment amplitude is an additional idealization, not verified real-target coherence. Share this amplitude and the random crossing time across all methods and all conditions.

Radial speeds are -15,-5,+5,+15 m/s. Positive speed means increasing range. Carrier is 2.4 GHz, slow-time sample rate 1,000 Hz, and Doppler is -2 v f_c/c with c=299792458 m/s. Sample the corresponding aliased complex phase at the native slow-time rate. The target crosses the group's central native-bin centre at one uniformly selected integer search look in [128,895]. Its range relative to that centre is v(t-t_cross)/1,000 m throughout the prefix and search. It is continuously present; there is no injected step at the crossing or acquisition boundary.

At each native bin, multiply the shared target amplitude by sinc(2 B delta_range/c), using NumPy's normalized sinc and a real, zero-phase rectangular-spectrum response. Effective bandwidth is either 22.5 or 45 MHz. Native sample spacing remains the verified 6 m in both cases; bandwidth-derived resolution is not relabelled as native spacing. No measured hardware filter, taper, PSF phase or range sidelobes are claimed.

On-centre SCR is 0,10,20 dB relative to the central bin's existing local surrounding raw-power proxy. The proxy excludes the entire 1,064-pulse acquisition and uses the same split-contained +/-1,024-pulse surroundings. Save every proxy. Thus there are exactly 24 fixed speed/bandwidth/SCR conditions per unit. The deterministic seed is the first eight SHA-256 digest bytes, little-endian, of `seed_namespace|tag|rotation`; keep the configuration namespace `R22-M-draft-v1` unchanged. Its word "draft" has no inferential meaning and avoids an unnecessary seed change. Draw all complex amplitudes first, then crossing times, exactly as the frozen runner implements.

## Endpoints, reporting and interpretation

Primary target outcome is any acquisition exceedance in the full prescribed search. Separately save any exceedance within one native spacing (6 m) of the true target trajectory, first-exceedance look, first-local-exceedance look and whether the highest-score bin at the first declaration is local. The local mask is evaluation only, not a detector search restriction. Report null acquisition rates alongside target acquisition rates: a background alarm during a target window does not establish target attribution.

Save per-window binary outcomes for every method and condition, calibration/test maxima, thresholds, target draws, native groups, fits and provenance. Primary aggregation weights each unit by its test-window count. Report all 24 conditions, and paired IN-G8 minus IN-G0 and IN-G8 minus each comparator, without selecting the best speed, response width or SCR after outcomes. Obtain descriptive 95% paired cluster percentile intervals from 10,000 bootstrap resamples of the 14 complete recordings, retaining both rotations and all windows of each selected recording. Seed from SHA-256 `R22|M|bootstrap`, first eight hex characters. Report episode counts and dependence, not a binomial interval treating range windows as independent acquisitions.

No post-outcome retuning, additional speed/SCR/width grid, favourable null filtering, target-conditioned steering or changed timing endpoint is permitted. A failed comparison narrows the proposed deployment claim. Any separately motivated subsequent analysis must be explicitly labelled and separately registered before execution.

## Execution and independent checks

The deterministic mechanics audit uses fabricated arrays only. Independent checks have verified scalar IN/CA/OS scores, coherent histories and DFT normalization, common raw-unit injection, all search endpoints and the finite calibration rank. Before real-data execution create `MIGRATION_FREEZE.json` containing exact SHA-256 identities for this protocol, config, runner and imported `methods.py` and `r15/netrad.py`; publish the registration on the isolated research branch.

Prepare raw caches serially after the freeze gate. Store original gains/means, input SHA-256 and cached complex-array SHA-256. Then score at most four disjoint tag subsets in parallel with `--require-prepared`; no parallel raw MAT fallback is allowed. Prepared caches must match the entire freeze manifest and content hashes. Each unit has an atomic, unique output; reject existing output rather than overwrite it. Log failed/completed identities and runtime. Independently audit saved outcomes before any manuscript integration. Raw provider records remain local; publish aggregate outcomes and reproducible code/provenance without redistributing raw data.
