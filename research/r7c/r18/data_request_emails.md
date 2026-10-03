# Data-request emails (3 Oct 2026)

Four requests, in descending order of value. Signature block for all four:

> Muhammad Umair Raza
> Department of Avionics Engineering, College of Aeronautical Engineering
> National University of Sciences and Technology (NUST), Risalpur, Pakistan
> uraza@cae.nust.edu.pk

Background and the reasoning behind each target is in
`../04_reviews/2026-10-03_R18_senior_review/DATASET_SWEEP_R18.md`.

**Addresses.** Those for requests 2 and 3 are taken from the published Open Radar Initiative
paper, where the authors print them themselves. The McMaster address for request 4 is **not**
verified — see the note under it.

---

# 1. CSIR Fynmeet — the campaign that closes the gap

**To:** Dr P. L. Herselman, `pherselman@csir.co.za`
**Why first:** the only campaign found in three sweeps with a real target, a real onset and
ground truth in measured sea clutter. Parsed from his own open documentation (handle
10204/1847): **66 datasets of Type "Target"** against 86 clutter-only; series **TFC15-001…047**
(1 Aug 2006, 9 GHz), **TAD17**, **TSC17** (3 Aug, 9 / 9.125 GHz), **TSC08**, **TSF08** (25 Jul,
6.6 / 9 GHz); Fynmeet tunes 6.6–10.3 GHz, so C through X band. TFC15-001 is 9 GHz, PRF 5 kHz,
678,760 PRIs = 135.75 s, 96 gates at 15 m, fixed-frequency, grazing 0.85–1.27°, SWH 3.23 m,
calibrated at 190.9 dB with per-gate complex offsets, and **"GPS Data: Available"** with the
boat plotted against range *and* azimuth. Its GPS range runs 3000 → 4400 m in 135 s: about 90
gate crossings, one every ~1.5 s, each with GPS truth.

> **Subject:** Request for 2006 Fynmeet trial datasets (target series) — NUST, Pakistan
>
> Dear Dr Herselman,
>
> I am a researcher in the Department of Avionics Engineering, College of Aeronautical
> Engineering, NUST, Pakistan. With two colleagues I have developed a constant-false-alarm-rate
> detector for compound-Gaussian clutter: each range cell is whitened along slow time with an
> autoregressive model, the tested innovation is normalised by the cell's own innovation power,
> and the threshold is set by split-conformal calibration on clean clutter instead of from a
> model. The work gives closed-form false-alarm and detection laws, including one for how a
> persistent target masks itself, and a certificate for clipped pulse integration under pulsed
> interference. It is validated on the McMaster IPIX X-band and the UCL/UCT NetRAD S-band sea
> clutter, and is being submitted to IEEE Transactions on Radar Systems.
>
> Our one remaining gap is a real target with a real onset. Every positive detection result we
> report on measured sea clutter uses targets injected into real clutter, because the IPIX
> target is present throughout each recording. The 2006 Fynmeet trial is the only campaign we
> have found that resolves this. From the overview documents you published on CSIR ResearchSpace
> (handle 10204/1847) we can see that the Type "Target" datasets — the TFC15 series of 1 August
> 2006 at 9 GHz, and the TAD17, TSC17, TSC08 and TSF08 series — log the boat's GPS range and
> azimuth alongside calibrated returns at 5 kHz PRF over 96 gates of 15 m. A boat crossing those
> gates with GPS truth is precisely the real onset our detector needs to be tested against, and
> the fixed-frequency waveform keeps the slow-time sequence coherent.
>
> Those documents state that the datasets are available to research institutes and universities
> on request. May I ask for access to a subset of the target datasets, together with the
> clutter-only recordings from the same day for threshold calibration? A handful would be
> enough — we do not need the whole database. We would sign any data-use agreement, cite the
> DataWare paper and the dataset, acknowledge the CSIR as we already do for the IPIX, NetRAD and
> JKU providers, and share our code and results with you.
>
> With thanks and best regards,
>
> *[signature block]*

---

# 2. NetRAD — the missing 14:42 target recording

**To:** Dr Matthew Ritchie, `m.ritchie@ucl.ac.uk`
**Cc:** Dr Francesco Fioranelli, `F.Fioranelli@tudelft.nl`
**Why:** possibly a higher-probability yes than Fynmeet and far cheaper to grant, because it is
**one file**. The trial log inside the public release states "there is a target in the 14.42
files" and no 14:42 recording is in the deposit. Same instrument, same campaign, same
preprocessing — the paper's code already runs on it — and Ritchie is **already thanked by name
in the Acknowledgment**.

> **Subject:** NetRAD June 2011 sea-clutter release — is the 14:42 target recording available?
>
> Dear Dr Ritchie,
>
> I am a researcher in the Department of Avionics Engineering at NUST, Pakistan. Our group has
> developed a constant-false-alarm-rate detector for compound-Gaussian clutter — per-cell
> autoregressive whitening along slow time, with the threshold set by split-conformal
> calibration on clean clutter rather than from a model — and your NetRAD monostatic sea-clutter
> release (doi 10.5522/04/32676582) is one of its two sea-clutter validations. The paper is being
> submitted to IEEE Transactions on Radar Systems and already acknowledges you and the UCL and
> University of Cape Town NetRAD team.
>
> One question. The trial log in the release, *Sea Clutter Data 09 June 2011.xlsx*, notes that
> "there is a target in the 14.42 files", but no 14:42 recording appears in the deposit: what we
> have are the HH and VV clutter runs and the cross-polar recordings from 12:39 to 13:02. Does
> that 14:42 recording still exist, and could it be added to the deposit or shared with us?
>
> The reason I ask is that this is the one gap left in the paper. Every positive detection result
> we report on measured sea clutter uses targets injected into real clutter, because the IPIX
> target is present throughout each recording and therefore sits inside the very history our
> detector normalises by. A NetRAD recording containing a real target would close that gap on an
> instrument we already process correctly — the clutter-cell selection, the preprocessing and the
> analysis are all in place and validated against your release — so it would be a small step for
> us and a large one for the paper.
>
> I would be glad to sign any data-use agreement, and to share our code and results.
>
> With thanks and best regards,
>
> *[signature block]*

---

# 3. Open Radar Initiative — the uncut raw IQ behind the signatures

**To:** Daniel Gusland, `Daniel.Gusland@ffi.no` (Norwegian Defence Research Establishment)
**Cc:** `F.Fioranelli@tudelft.nl`, `m.ritchie@ucl.ac.uk`, `szgurbuz@ua.edu`
**Why:** the best **non-sea** option. A stationary radar watching real pedestrians, cyclists,
UAVs and vehicles arrive — the right geometry. The public release is `.npy` dictionaries of
Doppler spectra with one signature per radar track, i.e. processed and cut around the target,
which is unusable here. The whole question is whether the uncut raw survives.

> **Subject:** Open Radar Initiative — is the uncut raw data behind the signatures available?
>
> Dear Dr Gusland,
>
> I am a researcher in the Department of Avionics Engineering at NUST, Pakistan, working on a
> constant-false-alarm-rate detector for compound-Gaussian clutter: each range cell is whitened
> along slow time with an autoregressive model, the tested innovation is normalised by the cell's
> own innovation power, and the threshold comes from split-conformal calibration on clean clutter
> rather than from a model. It is validated on the IPIX and NetRAD sea-clutter databases and on a
> 77 GHz FMCW dataset, and is being submitted to IEEE Transactions on Radar Systems.
>
> Your ground-surveillance dataset is close to something we need and have not found elsewhere: a
> stationary radar observing real targets arrive. The released form is `.npy` dictionaries of
> Doppler spectra with one signature per radar track, which is processed and cut around the
> target. What our method needs is the uncut record — the complex samples of each range bin
> through time, including the clutter-only interval *before* a target enters that bin. The
> threshold is calibrated on that clutter, and the event we study is the arrival itself, so a
> segmented signature unfortunately cannot support either step.
>
> Does that raw data still exist behind the published signatures, and would you be willing to
> share even a few recordings of a person or a vehicle approaching the radar? A handful would be
> enough; we do not need the full collection.
>
> I would be glad to sign a data-use agreement, cite the dataset and the Open Radar Initiative
> paper, and share our code and results with you.
>
> With thanks and best regards,
>
> *[signature block]*

---

# 4. IPIX Grimsby 1998 — the missing target information

**To:** the McMaster IPIX Radar Group. The Dartmouth database page says "you are invited to
contact Simon Haykin" and records that the database was created by Rembrandt Bakker and Brian
Currie in 2001.
**Address not verified.** Do not guess it. Take the current address from the McMaster
Electrical and Computer Engineering directory, or send via the department; Prof. Haykin is
emeritus and Brian Currie may have retired, so the department is the safer route.

**Why:** the cheapest ask of all, because **the data are already downloaded-able**. The twelve
CD images are live and unauthenticated at `soma.ece.mcmaster.ca/ipix/data/IPIX_CD{1..12}.ISO`
— about 6.16 GB, 222 NetCDF datasets, 9.39 GHz, PRF 1 kHz, 60,000 sweeps (60 s), 27–35 gates at
30 m, and **144 of the 222 are effectively staring**. Only the ground truth is missing: the
index says "[target information not yet available]" for every file.

> **Subject:** IPIX Grimsby 1998 database — do the target range cells and times survive?
>
> To the McMaster IPIX Radar Group,
>
> I am a researcher in the Department of Avionics Engineering at NUST, Pakistan. Our group has
> developed a constant-false-alarm-rate detector for compound-Gaussian clutter, validated in part
> on the IPIX Dartmouth 1993 database, which we cite and acknowledge; the paper is being
> submitted to IEEE Transactions on Radar Systems.
>
> We have also been working with the Grimsby 1998 release — the twelve CD images on
> soma.ece.mcmaster.ca. For every dataset the index records "[target information not yet
> available]". Does that information survive in the trial records: which range cells held the
> test object, and over which sweeps?
>
> It would make a real difference to us. In the Dartmouth data the target is present throughout
> each recording, so it lies inside the very history our detector uses to normalise, and our
> theory predicts it will be invisible there — which our measurements confirm. What we lack is a
> measured target that *arrives*: one entering a range cell, so that the clean clutter before it
> can calibrate the threshold and the arrival itself is the detection event. Many of the Grimsby
> datasets are staring recordings of 60,000 sweeps, which is exactly the right geometry; only the
> ground truth is missing.
>
> If the target logs survive in any form at all — a spreadsheet, a notebook, even a per-file note
> — we would be very grateful for them, and would of course cite and acknowledge the group.
>
> With thanks and best regards,
>
> *[signature block]*

---

## Practical notes

- **Send 1 and 2 together.** They are independent, and 2 may answer fastest because it is a
  single file from a group already named in the paper's Acknowledgment.
- **Expect to sign something.** Offering that up front, as all four do, removes the main reason
  a custodian hesitates.
- **Ask for a subset, not the database.** Every email does. It is the difference between a
  favour and a project.
- **If any one of these lands**, `CLAUDE.md` rule 5 applies: write the protocol with stated
  expectations and hash it *before* computing any outcome on the new data. The Fynmeet
  documentation being open while the data are gated makes this unusually easy to do properly.
- Ten of the seventeen Fynmeet overview PDFs are in `fynmeet_2006_docs/`; the other seven return
  HTTP 500 from the ResearchSpace API, a repository fault rather than an access restriction.
  Worth retrying before sending email 1, in case they name more target series.
