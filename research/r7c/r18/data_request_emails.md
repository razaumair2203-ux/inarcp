# Data-request emails (3 Oct 2026)

Four requests, in order of value. Only the first is drafted in full; say the word and the
others get the same treatment. Background and the reasoning behind each target is in
`../04_reviews/2026-10-03_R18_senior_review/DATASET_SWEEP_R18.md`.

---

## 1. CSIR Fynmeet — Dr P. L. Herselman, `pherselman@csir.co.za`

**Why this one first.** It is the only campaign found in three sweeps that closes the paper's
one evidence gap. From the overview documents he published openly on CSIR ResearchSpace
(handle 10204/1847), which were downloaded and parsed on 3 Oct 2026:

- **66 datasets of Type "Target"** and 86 of Type "Sea Clutter", across the trial;
- the target series are **TFC15-001 … TFC15-047** (1 Aug 2006, **9 GHz**), **TAD17** and
  **TSC17** (3 Aug, 9 / 9.125 GHz) and **TSC08**, **TSF08** (25 Jul, 6.6 / 9 GHz);
- example, TFC15-001: Type Target, **9 GHz**, **PRF 5 kHz**, **678,760 PRIs = 135.75 s**,
  **96 gates at 15 m**, tracking range 3000 m, fixed-frequency waveform, grazing 0.85–1.27°,
  SWH 3.23 m, wind 15.8 kt gusting 23.3, calibration coefficient 190.9 dB with per-gate
  complex offsets;
- **"GPS Data: Available"**, and the sheets plot "Boat — Raw GPS" and "Boat — Proc. GPS"
  against both range and azimuth, over a range that runs 3000→4400 m during the 135 s record.

That last point is the whole reason to ask: **the boat crosses roughly 90 range gates during
one recording, with GPS truth for when.** At 15 m gates that is a gate crossing about every
1.5 s, or every 7,300 pulses — a real target onset in measured sea clutter, with ground truth,
which is exactly what the paper says it lacks. The fixed-frequency waveform keeps the slow-time
sequence coherent, unlike the stepped-frequency Korean set. And 5 kHz for 135 s means slow time
can be subsampled at any lag from 0.2 ms upward, which is the operating regime the paper
identifies as unexplored.

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
> azimuth alongside calibrated returns at 5 kHz PRF over 96 gates of 15 m. A boat crossing
> those gates with GPS truth is precisely the real onset our detector needs to be tested
> against, and the fixed-frequency waveform keeps the slow-time sequence coherent.
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
> Muhammad Umair Raza
> Department of Avionics Engineering, College of Aeronautical Engineering
> National University of Sciences and Technology (NUST), Risalpur, Pakistan
> uraza@cae.nust.edu.pk

**If you want it shorter**, cut the second paragraph to its first two sentences and the dataset
list to "the TFC15 target series of 1 August 2006". The specificity is what earns a reply,
though — it shows the homework is done and makes the request cheap to grant.

---

## 2. NetRAD missing target recording — M. Ritchie (UCL), F. Fioranelli (TU Delft)

**Possibly higher probability than Fynmeet, and much cheaper to grant: it is one file.** The
NetRAD trial log in the public release (`Sea Clutter Data 09 June 2011.xlsx`) states "there is
a target in the 14.42 files", and **no 14:42 recording is in the figshare deposit**
(10.5522/04/32676582). The paper already uses NetRAD, so the instrument, the campaign, the
preprocessing and the analysis code are all in place — this would be a real target at sea on a
dataset already validated in the paper.

M. Ritchie deposited the dataset and **is already thanked by name in the paper's
Acknowledgment**; F. Fioranelli is a co-author of the NetRAD paper the manuscript cites. Ask
whether the 14:42 recording survives and can be added to the deposit.

## 3. Open Radar Initiative raw data — F. Fioranelli / UCL

**The best non-sea option, and the same contact as request 2.** Stationary radar, outdoor, real
pedestrians, cyclists, UAVs and vehicles moving in front of it. The public release is
`.npy` dictionaries of **Doppler spectra, one signature per radar track** (CC BY-NC 4.0), which
is processed and segmented and therefore unusable here. Worth one question: **does the raw IQ
behind those signatures still exist, uncut?** If it does, it is a real-onset dataset in ground
clutter with an open licence.

## 4. IPIX Grimsby 1998 target information — McMaster University

**The cheapest ask of all, because the data are already downloadable.** The twelve ISOs are
live and unauthenticated at `https://soma.ece.mcmaster.ca/ipix/data/IPIX_CD{1..12}.ISO`
(~6.16 GB, 222 NetCDF datasets, verified 2 Oct 2026): 9.39 GHz, PRF 1 kHz, 60,000 sweeps
(60 s), 27–35 range gates at 30 m, and **144 of the 222 files are effectively staring** — the
right recording geometry. The only thing missing is ground truth: the web index says
"[target information not yet available]" for every file.

So one email could unlock a dataset that is **already on disk**. Note it is Lake Ontario, not
open sea, which after the R18 scope correction is no longer a disqualification — the paper now
asks for correlated, textured clutter, and wind-driven lake clutter qualifies.

---

## Note on the documentation download

Ten of the seventeen Fynmeet overview PDFs are in `fynmeet_2006_docs/`. The other seven return
HTTP 500 from the ResearchSpace bitstream API — a repository-side fault, not an access
restriction; retry later. The ten in hand already cover 152 datasets (86 clutter, 66 target),
which is more than enough to specify a request.
