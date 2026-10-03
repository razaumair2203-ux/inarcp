# Third sweep for a real target with a real onset at sea (3 Oct 2026, R18)

**Why a third sweep.** The author asked whether the open-data repositories, where researchers
now routinely deposit datasets, hold anything that closes the paper's one remaining evidence
gap. The two earlier sweeps are in `../2026-10-02_R14-R15_improvement_and_confirmation/DATASETS_SCOUTED.md`
and `dataset_scout/notes_*.md`; the second of those is thorough and covers roughly thirty
candidates across Zenodo, IEEE DataPort, the Illinois Databank, 4TU, NCAR EOL, AFRL SDMS,
CRIRP, CETC, the *Journal of Radars* programme, Ingara and NeXtRAD.

## What the paper actually needs

Not simply "a radar dataset with a ship in it". Four conditions, together:

1. **Measured sea (or at least water) clutter**, not simulation.
2. **Pre-detection samples** — coherent IQ, or at minimum linear amplitude per range cell
   *before* the radar's own CFAR and clutter suppression. The method replaces that stage, so
   it cannot be fed that stage's output.
3. **Slow time per range cell** — a sequence of samples of the *same* cell, pulse to pulse or
   scan to scan, from a stationary platform. A moving platform changes what is in a cell.
4. **A target that appears**, with ground truth for when and where. A target present
   throughout (IPIX, the Korean sphere) cannot produce an onset.

Condition 2 is what eliminates most of the maritime datasets that exist, and condition 4 is
what eliminates most of the rest.

## New this sweep

| Candidate | Verdict |
|---|---|
| **DLR Real-World Marine Radar (RWMR)**, DOI 10.26090/rwmr, *Sensors* 21(14) 4641. Three Baltic Sea X-band datasets (DAAN, DARC, MANV), 527–976 frames at 1 Hz, 6–11 m pixels, **AIS ground truth** with position, course, speed and heading, and **targets that enter and leave coverage** — including one unequipped vessel | **Right targets, wrong layer.** The data are *frame-grabbed radar screen visuals* plus detected point clouds in JSON. Display captures are 8-bit images taken after the radar's own gain, sea-clutter suppression and scan correlation, so condition 2 fails outright: you cannot test a replacement for the detection stage on that stage's output. Access is also open to EU and NATO states only, with others "subject to individual assessment" |
| **IEEE DataPort "sea clutter" catalogue** (the whole keyword listing, which no earlier sweep had read) | Only two datasets. One is scattering-position and refractivity data, not radar returns. The other is the Korean sphere set below |
| **"Measured data to verify the detectability for a small target on the sea-surface"**, Inoh Choi, Korea Maritime & Ocean University, DOI 10.21227/bc58-7p27. X-band 9.35 GHz, HH, PRI 0.4 ms, **a real 0.4 m Styrofoam sphere at −9 dBsm, 440 m, sea state 3–4** | **Already found in the second sweep, and its objection there is sharper than mine.** The 20-deep third axis is *stepped carrier frequency*, not scan time, so consecutive samples sit at different carriers and plain slow-time coherence is broken. Added to that: 6.71 MB total (190 range × 40 pulses × 20 steps) is far too little to calibrate at 10⁻³, let alone 10⁻⁴, which needs about 3,150 and 31,500 episodes; the target is stationary, so there is no onset; and the IEEE DataPort listing says Open Access while the record itself requires a subscription |
| **Qiongzhou Strait X-band pulse-compression dataset** (Haikou, Hainan, 2023; 208,000 training and 12,000 validation echo samples) | **Not released.** The authors state an intention to "open source these data in batches in the future" |
| **STREAM**, University of Birmingham, Zenodo 14215115 / 14174138 / 14174076 / 10075384, **CC BY 4.0**, 1.2 TB. 79 GHz radar suite on the vessel *Valkyrie VI*, Gosport Marina Portsmouth, **sea state ~3 Douglas**, 512 chirps per 128 ms frame, camera and IMU ground truth | **The best openly licensed maritime candidate, and still not a clean fit.** It was listed in the second sweep but not pursued, and re-reading the record shows why it should not be: the radar is *on a moving boat*, so condition 3 fails between frames — a given range bin is a different patch of water each frame, and the onset analysis would need ego-motion compensation first. Within a single 128 ms frame the platform barely moves and the 512 chirps are usable slow time, but no target appears within 128 ms. Zenodo also describes the records as processed rather than raw ADC. A real study here is possible but it is a new project, not a confirmation run |
| **CSIR `small_boat_detection` URL** | Re-verified dead: `http://www.csir.co.za/small_boat_detection/` returns 404 today, as in the second sweep |

## The conclusion, stated plainly

**The data that would close this gap exists and is good. None of it is openly downloadable.**
Every candidate that satisfies all four conditions is either request-gated or geoblocked, and
every candidate that is openly downloadable fails condition 2 or 3. Three sweeps have now
reached the same place by different routes, which is itself worth reporting to a reviewer.

## The one realistic route, and it is an author action

**CSIR Fynmeet (South Africa) is the dataset to ask for.** It satisfies all four conditions
better than anything else in existence:

- Cape Agulhas, winter 2006, two weeks, hundreds of recordings, wideband X-band Fynmeet;
- **calibrated** reflectivity, coherent, stationary shore-based platform;
- **three types of small boat** — a 5.7 m rigid inflatable, a glass-fibre ski boat and a
  fishing vessel — **manoeuvring at different ranges and azimuths**, which is exactly the
  range-cell crossing that produces real onsets;
- **recorded boat positions and orientations**, plus wave height, direction and weather, so
  the ground truth is there;
- 55 fixed-frequency and 43 stepped-frequency recordings, stored as structured MATLAB `.mat`
  files;
- UK radar specialists called it "one of the best of its kind in the world", and the CSIR
  states the datasets "will be made available to research institutes or universities upon
  request". NUST is a university.

The web portal is gone but the group is not. Contact routes found this sweep:

- CSIR Radar and Electronic Warfare, contact page: https://defsec.csir.co.za/radar-and-electronic-warfare-rew/contact-us
- `dpss@csir.co.za` (Defence, Peace, Safety and Security unit), telephone +27 12 841 2780
- J. C. Cilliers, `jcilliers@csir.co.za` — principal researcher, co-author of the DataWare paper
- H. J. de Wind, `rdewind@csir.co.za` — co-author of the DataWare paper

The DataWare paper describing the database is already in the manuscript's bibliography as
`dewind2010csir`, uncited.

**Second route, if CSIR declines:** the *Journal of Radars* / SDRDSP release from Naval
Aviation University (Yantai, X-band, circular scan, 28 archives, about 42 GB) is open on
registration but `radars.ac.cn` times out from Pakistan. A colleague or co-author outside the
geoblock could fetch it. The author excluded this programme earlier; the exclusion is theirs
to revisit.

## What this means for the submission

Nothing blocks it. The paper states the gap in the Discussion and names the required campaign
in the Conclusion, the search is documented across three sweeps, and a reviewer who asks "why
no real target at sea?" gets a complete and verifiable answer. If CSIR grants access, that is
a strong follow-up paper — or a revision, if the first round takes long enough — and the
frozen-protocol discipline of `CLAUDE.md` rule 5 applies before any statistic is computed on
it.

## Addendum, same day: the author found the CSIR ResearchSpace record

https://researchspace.csir.co.za/items/c72f2882-3afc-4e57-aeb8-8e5bf4963529 —
**"2006 Fynmeet Sea Clutter Measurement Trial: Datasets", P. L. R. Herselman, 6 Sep 2007,
handle 10204/1847.** This is the right trail. What the record holds is **17 openly
downloadable PDFs** (about 73 MB, one per trial day) — the *dataset overview sheets*, not the
measurements. The measurements are the `.mat` files CSIR supplies on request.

That is better than it sounds, for two reasons.

**First, the sheets give the hard parameters.** Read from `Herselman6_2007.pdf` (dataset
overview for 02-Aug-2006, datasets CFA16-023 and CFA16-024):

| | |
|---|---|
| Trial | Overberg Test Range, Arniston, South Africa, 18 July – 4 August 2006 |
| Transmit frequency | **6.9 GHz — C-band**, not X-band. Fynmeet is a C-band facility |
| PRF | **5 kHz** |
| Record length | **299,359 PRIs = 59.87 s** per dataset |
| Range | 96 gates, **15 m resolution**, 1440 m extent, tracking range 7000 m |
| Mode | staring (antenna azimuth fixed at 94.13°), fixed-frequency waveform |
| Grazing angle | 0.427–0.525° — very low |
| Calibration | per-gate complex offsets for odd and even gates are tabulated, and the plots are **RCS in dBm²**, so the data are calibrated complex IQ |
| Environment | instantaneous wind 17.5 kt gusting 33 kt, 8-hour average 13.1 kt |
| Per-dataset "Type" field | "Sea Clutter" for these two, which implies other datasets carry a target type |

**Three consequences for the paper.** (i) C-band would be a **third band** alongside X-band
IPIX and S-band NetRAD, which is a much stronger generalization claim than two. (ii) 5 kHz for
60 s is 300,000 pulses per gate, so slow time can be subsampled at **any** lag from 0.2 ms to
seconds — the whole middle regime that the R18 operating-regime finding says is unexplored and
that neither IPIX, NetRAD nor JKU can reach. (iii) a boat at 5 m/s crosses a 15 m gate in 3 s,
i.e. 15,000 pulses, so range-cell crossings are resolved rather than inferred.

**Second, the documentation being open while the data are gated is exactly the right order for
`CLAUDE.md` rule 5.** The sheets state which datasets carry a boat, its geometry and the sea
state, so a protocol with stated expectations can be frozen and hashed **before** the data are
requested, let alone received. That is a stronger pre-registration than any study in the paper
so far, including NetRAD.

**Direct contact, from the PDF itself:** "These datasets have been stored in structured
Mathworks Matlab (*.mat) files and will be made available to research institutes or
universities upon request. For more information contact **Dr PL Herselman at
pherselman@csir.co.za**." That supersedes the generic addresses above as the first approach.

## Addendum 2: the sea requirement was mine, not the method's

The author asked why the search was restricted to sea clutter at all. Correctly. The method is
not sea-specific:

- the clutter model is compound-Gaussian with AR speckle and thermal noise, which is a clutter
  *class* — windblown land clutter and weather clutter are modelled the same way — not a
  clutter *source*;
- the conformal threshold is distribution-free and assumes only exchangeability;
- **Theorem 1 "needs none of these assumptions"**, in the paper's own words;
- the manuscript already mentions 77 GHz **15 times** against 11 for sea clutter, and the
  R17 onset study is in ground clutter.

The search was narrowed because the paper's Conclusion names "real-target campaigns **at sea**"
as the next step — so the search followed the paper's framing rather than the method's scope.
That clause is narrower than the method and is worth widening.

**But dropping "sea" widens the usable pool far less than the raw count suggests**, because the
binding constraint is the recording geometry, not the clutter type:

- **classification datasets are cut around the target** (for example the 75,868-sample Zenodo
  drone/bird/human set at 77 GHz). Segmenting around the target destroys the onset: there is no
  clean-clutter history before the arrival;
- **point-cloud and range-Doppler-map datasets are post-detection** — condition 2;
- the **raw-ADC** sets (RaDICaL, ColoRadar, the UW set) are **frame-gated** like JKU, so they
  offer a lag of tens of microseconds within a frame or hundreds of milliseconds between
  frames, and nothing in between — the same wall R17 hit;
- vessel- and vehicle-mounted sets fail condition 3.

So the restated, band-agnostic requirement is: **a stationary radar logging continuously, at a
slow-time lag anywhere in roughly 1–50 ms, with range cells fine enough that a real target
crosses them inside the record, kept uncut.** Fynmeet is the best instance of that geometry
found in three sweeps — and it is the best instance whether or not it happens to be sea.

## Addendum 3: the Fynmeet documentation was downloaded and parsed

The 17 overview PDFs are open. Ten were retrieved on 3 Oct 2026 into
`../../05_thesis_direction/fynmeet_2006_docs/`; the other seven return HTTP 500 from the
ResearchSpace bitstream API, which is a repository fault rather than an access restriction.
The ten in hand cover **152 datasets**, and parsing their Experiment Summary blocks settles
the question:

| | |
|---|---|
| Type **"Sea Clutter"** | **86 datasets** — CFA (6.9 GHz), CFC (9 GHz), CSC, CFB (8 GHz), CFE (10.3 GHz) |
| Type **"Target"** | **66 datasets** — **TFC15-001…047** (1 Aug 2006, 9 GHz), **TAD17**, **TSC17** (3 Aug, 9 / 9.125 GHz), **TSC08**, **TSF08** (25 Jul, 6.6 / 9 GHz) |

Fynmeet is tunable across **6.6, 6.9, 8, 9, 9.125 and 10.3 GHz**, so it spans C to X band — an
earlier note calling it "C-band" from a single sheet was too narrow.

**Example target dataset, TFC15-001:** Type Target, 9 GHz, PRF 5 kHz, 678,760 PRIs = **135.75 s**,
96 gates at 15 m, tracking range 3000 m, fixed-frequency waveform, grazing 0.85–1.27°, SWH
3.23 m, wind 15.8 kt gusting 23.3, calibration coefficient 190.9 dB with per-gate complex
offsets, complex conjugate applied. **"GPS Data: Available"**, and the sheets plot "Boat — Raw
GPS" and "Boat — Proc. GPS" against both range and azimuth.

**The decisive detail: the boat's GPS range runs 3000 → 4400 m during the 135 s record.** At
15 m gates that is roughly 90 gate crossings, about one every 1.5 s or 7,300 pulses, each with
GPS truth for when it happens. That is a real target onset in measured sea clutter with ground
truth — the paper's one stated gap — and the fixed-frequency waveform keeps the slow-time
sequence coherent, which is what the stepped-frequency Korean set could not offer. 5 kHz over
135 s also means slow time can be subsampled at any lag from 0.2 ms upward, covering the
middle regime that the operating-regime finding says nothing in the paper reaches.

All four requests, with the Fynmeet one drafted in full, are in
`../../05_thesis_direction/data_request_emails.md`.

## Addendum 4: what is downloadable now, after dropping the sea requirement

Asked directly: is anything usable openly downloadable? One candidate, and it is a good one.

**IPIX Grimsby 1998 is already downloadable and has the right recording geometry.** Twelve ISOs,
live and unauthenticated, about 6.16 GB, 222 NetCDF datasets: 9.39 GHz, PRF 1 kHz, 60,000
sweeps (60 s), 27–35 gates at 30 m, and **144 of 222 files effectively staring**. The only
missing piece is ground truth — the web index says "[target information not yet available]" for
every file. So a single email to McMaster could make a dataset that is already on disk usable.
It is Lake Ontario rather than open sea, which after the scope correction above is no longer a
disqualification: wind-driven lake clutter is correlated and textured.

Everything else openly downloadable still fails one of the four conditions, as recorded above.
