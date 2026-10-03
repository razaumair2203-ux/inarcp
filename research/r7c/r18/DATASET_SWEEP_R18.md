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
