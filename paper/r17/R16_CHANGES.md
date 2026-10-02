# R16 changes relative to R15 (2 Oct 2026)

R16 is a **prose and narrative revision** of R15. It also adds a map of where the detector works and where it fails, which the author asked for.
- **Unchanged:** the science, data, code and results. Every number is still a macro generated from saved outcomes.
- **One new macro:** `\KappaRuleUndefUnits` (16), from `analysis_provenance/make_r14_outputs.py`.
- **Length:** the paper stays at 10 pages, and the supplement grows to 30.

## 1. Why
The author suspected that the many revision rounds had degraded the wording: vague, not contextual, disjointed, with poor sentence construction. A blind benchmark of five versions (R07, R09, R12, R13 and R15) was run with three independent judges and 10 KPIs, alongside automated prose metrics. It confirmed the complaint in part.

**What had improved through R15:**
- the narrative;
- the radar framing;
- claim calibration.

**What had declined and stayed low:**
- **Sentence construction:** 7.0 in R07, 4.7 in R15.
- **Readability:** 6.7 in R07, 5.0 in R15.

**The cause was density, not vagueness.**
- Sentences averaged 29 words.
- 35% of sentences carried four or more numbers.
- Only 2.8% of sentences opened with a logical connective.

The full record is in `../04_reviews/2026-10-02_R16_prose_benchmark/`.

## 2. What changed
- **Narrative spine.**
  - The introduction now names the three problems: thresholds in the far tail, self-masking of persistent targets, and pulsed interference. Each contribution answers one of them.
  - Each section and subsection opens with its question or role.
  - The Results follow the theory: false alarms, then new targets, then persistent and emerging targets (the guard, ramps and the real target in one subsection), then interference, then the second radar.
- **Sentences.** Overloaded sentences were split, and numbers that the tables already carry were removed from the prose.
  - Mean sentence length fell from 26.5 to 23.2 words.
  - Sentences over 40 words fell from 13.5% to 7.1%.
  - Flesch reading ease rose from 33.1 to 39.4, and the Fog index fell from 18.5 to 16.8.
- **Terms.** Radar meanings are now given once each, for:
  - hit versus exceedance;
  - exchangeable;
  - pivotal;
  - coverage.
- **Moves.** The clip-level result moved to the interference section, and the guard-on-ramp result moved to the persistent-target subsection.
- **New Table IV: where the detector works and where it fails.** It covers about 20 tested scenarios, graded W/P/F with a stated rule, and replaces the Limitations list.
  - It comes with a paragraph that names four sources of failure: a target in the scale, interference in an uncertified dwell, certificate cost under bursts or frequent hits, and model-based thresholds.
  - A paragraph of assumed or partly tested conditions follows. Every R15 limitation is still stated.
- **The R15 laws table (Table I)** moved to the supplement ("Summary of the laws"), to keep 10 pages (CLAUDE.md rule 1). The equations stay in Section IV.
- **Design rules** are now a four-item list. It adds "excise in fast time first" and "at low hit rates (vacuous at 10⁻³ with 5% hits)".
- **Acknowledgment.** The AI disclosure follows the author's short framing. It still names the AI systems and the sections, as IEEE policy requires, and it also mentions the derivations.
- **References.** Five peripheral references were removed: alnaffouri2016, farina1997, huber1965robust, dewolf2025 and sangston2012, plus gibbs2021aci, which now points to the supplement. The IPIX prior-art sentence (haykin1995) was kept.
- **Code tag.** It is now `r16-trs-submission`.

## 3. Independent checks (CLAUDE.md rules 6 and 8)
- **Blind panel 2.** Three judges each scored R13, R15 and R16 with different label orders. R16 had the highest mean KPI: **7.62**, against 6.52 for R15 and 6.48 for R13. All three judges ranked R16 first, preferring it to R15 with probabilities 0.80, 0.75 and 0.82.
- **Claim audit of the rewrite.** Two auditors returned **BLOCK**, with three FAILs, all fixed:
  1. The abstract had dropped "injected" from the IPIX interference result and the NetRAD certificate claim.
  2. The Discussion's single-pattern sentence overgeneralized. It is now the four-source sentence.
  3. The "Low CNR, 77 GHz" row of Table IV named the wrong CNR class.
- **WEAK items also fixed:**
  - the clip-level rule is undefined in 16 units (new macro);
  - "without interference" was added to the clip-level result;
  - three Table IV rows were regraded W → P;
  - "reproduce" became "behave as on IPIX";
  - "A guard restores visibility" became "A guard delays the loss";
  - the OS-law derivation was corrected;
  - "exceedance" now has one meaning;
  - two hedges were restored ("not an untouched confirmation"; "at a similar false-alarm rate");
  - the learned-detector comparison was restored, with its observation-length context;
  - "such clutter" was fixed in the Conclusion.
- **Final checks after the last edit:** a claim audit of every change since the audited draft, and a blind pairwise review in both orders. See `ROUND_R16.md` in the review folder.

## Figure revision (2 Oct 2026, after the tag)
The figures were revised after a domain review and an adversarial figure-and-table audit. No result changed: no number and no macro differs from the tagged R16.
- **Figs. 3 and 4 merged.** The page cuts had printed them at 47% and 53% scale, with text of about 3–4 pt. They are now one two-column Fig. 3, with (a) detection at onset and (b) per-look detection after onset with and without the guard. It is drawn at print size with 8 pt text by `analysis_provenance/make_fig_detection.py`, from the same saved outcomes.
  - In (b), the two guard settings are offset slightly, so the "opposite Doppler, no guard" marker cited in the text (0.940 at look 1) is visible again.
  - The caption now states that the curves average P_d over units while the text averages per-unit gains (7.0 dB in the text, 7.5 dB read off the curves). It also gives NA-AR(4)'s gain (`\DetNAFourGainCAHalf`) and states that the means in the text are over looks 1–8.
- **Fig. 2 redrawn.**
  - Panel (a) had a clipped y-label; the Doppler offsets are now labelled directly.
  - The legends no longer cover data.
  - Text is 8 pt and legends 6.3–6.8 pt.
  - In (d), a rate of zero is drawn as an open triangle at the Monte Carlo resolution (10⁻⁵), and the caption says that (d) is Monte Carlo only.
  - The figure is now defined where Section IV first cites it, so it prints on p. 4 instead of p. 6.
- **Table III.** The row "5% hits: integration" now reads "AR(1) integration". The abstract's "up to 23-fold" is AR(4).
- **Checks.**
  - 10 pages, 0 overfull boxes, 0 undefined references.
  - The supplement text is unchanged.
  - Both Overleaf ZIPs were rebuilt and compiled from empty folders.
  - The prose metrics are flat: Flesch 39.4 → 39.6; sentences over 40 words 7.1 → 7.4%, from the captions.
  - Blind pairwise comparison of the figure pages preferred the revision in both orders (0.85, 0.85).
  - An adversarial audit traced every plotted and tabulated value to the saved outcomes and found no blocking issue.
- **Retired files:** `99_archive/paper_versions/R16_figures-superseded_2026-10-02/`.
- **In git:** commit f3fde6e on `research/r7-clutter`, pushed. The tag `r16-trs-submission` predates it.

## R16.1: evidence levels stated (2 Oct 2026)
An external review asked whether each claim states its level of evidence: derivation, agreement with Monte Carlo, real data, injected or real targets. Most of this was already in the paper: Fig. 2, the development status of IPIX and NetRAD, and the IPIX interference test described as an implementation check. Two gaps in the text remained, and R16.1 closes them: the agreement with Monte Carlo was not given as a number, and the summaries did not say that the targets were injected. A data gap remains (below). No result changed and no study was run. The one new macro file, `generated/verification_macros.tex`, is generated by `analysis_provenance/make_verification_macros.py` from the saved Monte Carlo output.
- **Monte Carlo agreement given as a number.**
  - **Before:** contribution 1 said "Monte Carlo confirms every law under the model".
  - **Now:** it says "Monte Carlo confirms the laws under the model; in its main run, all `\NLawChecks` (65) checks of the closed forms lie within `\LawChecksZBound` (3) standard errors".
  - **Why 3:** the printed maximum, 2.91, is rounded from 2.9125. The bound of 3 is the one the script's own count guarantees.
  - **Why "every law" went:** some laws have no model-level check, namely the guard's null law and the non-vacuous trimmed certificate.
- **Injected targets named in the summaries.**
  - The abstract and the conclusion now say "injected" for the persistent 10 dB target.
  - The abstract says "detects that target" for the certified-integration result. It is the same target type.
  - The Discussion now says that, apart from the IPIX reference target, the real-data detection results rest on injected targets with known timing, to which the dwell is aligned. This replaces "Injected targets have an aligned onset". Section V likewise says the dwell starts "at the first full-amplitude target pulse" rather than "at the target onset", which was false for ramps. The cover letter's two target statements say "injected" too.
- **Cuts that hold 10 pages (rule 1).**
  - Removed "Thermal noise therefore caps the whitening gain.", which repeats its subsection title.
  - "on NetRAD, whose data played no part in development" became "on NetRAD, unused in development".
  - "at a design of 0.01" became "at $\alpha=0.01$" in the 77 GHz paragraph.
- **Supplement.**
  - The R12 Monte Carlo section now says exactly which rows the 65 checks are, and which are excluded.
  - Its opening says "most closed forms" instead of "every closed form". K_eff is only computed there, not checked by Monte Carlo, and the guarded law is not in that run; it is in Section sup:indep.
  - The list for the independent re-check now names the laws it actually covers: the strong-target OS law (7), the integration laws, the known-bin P-ANMF law, the Beta law by Monte Carlo and the calibration sizes by exact computation. This edit was made in its generator, `make_supp_sections.py`.
- **Package.**
  - `declarations.md` now quotes the Acknowledgment word for word. It had left out "derivations".
  - The code tag is now **`r16.1-trs-submission`**, in the paper, the cover letter and the declarations. The R16 entries above that name `r16-trs-submission` are historical.
  - The Overleaf ZIPs are `INARCP_R16.1_*`.
- **Not done, because text cannot fix it.** No real target with a real onset confirms the positive detection results. That needs new data, for example cooperative targets crossing range cells (CSIR/SDRDSP).
- **Checks.**
  - **Build:** 10 pages, 0 overfull boxes, 0 undefined references. The abstract stays within the limit (255 → 254 by the metrics script's count).
  - **Prose metrics:** flat. Flesch 39.6 → 39.5; sentences over 40 words 7.4 → 7.0%; numbers per sentence 3.43 → 3.42. Sentences over 35 words rose 19.2 → 20.0%, from the new verification sentence and the corrected Section V dwell sentence. Both changes were made for accuracy.
  - **Blind pairwise, both orders, three rounds:** 0.72/0.78, then 0.72/0.75, then 0.78/0.80, all for R16.1.
  - **Adversarial claim audits:** three rounds. Fixed along the way: the rounding of 2.91, "every law", "65" read as the whole verification, the ramp timing, the stale generator, and the declarations text. Two further focused audits ran: one of the Discussion fix, which found the same timing error in Section V, and one of the Section V fix, the last manuscript edit before the tag.
  - **Record:** `../04_reviews/2026-10-02_R16.1_evidence_levels/`.

## R17: a real target with real onsets (3 Oct 2026)
R16.1 left one weakness that text could not fix: no real target with a real onset confirmed the positive detection results. R17 adds a pre-specified test on real data.

### Finding the data
- **SDRDSP** is geoblocked here, and its IEEE DataPort copy needs a subscription and has no files.
- **The CSIR small-boat database site** no longer exists (404).
- **The NetRAD release** omits the trial log's one target recording (14:42).
- **The JKU 77 GHz dataset** already in the paper has a measurement, never downloaded or used, in which a person walks through the scene under interference scenario A (`meas_3_int_A_pedestrian.mat`). Frames are 200 ms apart, and the person crosses the 15-cm range bins between frames. So each arrival of the person's return in a bin is a real onset in that bin's frame-to-frame (clutter-map) sequence.

### The study
- **Pre-specification:** protocol `research/r7c/r17/PROTOCOL_R17.md`, with hashes of the protocol, the code and two helpers. It was committed and pushed (a4bf4a5) before the file was downloaded.
- **Pre-freeze review:** an independent review found 9 blocking issues, all fixed before freezing. The most important was that Station 1 sees the person twice, directly and bistatically.
- **Mechanics check:** run on the scenario-A run without the pedestrian, with a synthetic walker.
- **Outcome:** commit 2587fa7, `RESULTS_R17.md`.
  - **E1 not met.** There are 74 onsets of the direct and bistatic returns, but in only 7 distinct five-frame blocks; at least 8 were required. So everything else is descriptive.
  - **Descriptive results (mitigation Z, per-receiver looks, α = 10⁻²):**
    - false-alarm rates of 0.96–1.10 times design;
    - per-look P_d within three frames of 0.30 (IN-ARCP), 0.27 (power clutter map), 0.23 (OS clutter map) and 0.07 (range CA-CFAR);
    - IN-ARCP's edge over the clutter map lies in the half of the bins with stronger static returns (+0.05 against 0.00).

### In the paper
- **Section VI-B:** a paragraph reporting the result as descriptive. It states the dense interference and its fast-time zeroing, the 16 receiver–chirp tests, the ground-truth source, why IN-ARCP only matches the clutter map here (nearly uncorrelated frame-to-frame clutter, Proposition 2) and the block shortfall.
- **Table IV:** the empty left slot gets the row "Real onsets, 3 frames, 77 GHz".
- **Discussion:** the limitation now names the walking person and states the four limitations the protocol requires: one walk, tracked for about six seconds; ground clutter; frame-rate slow time; and ground truth from the radar itself.
- **Section V:**
  - one sentence on the pedestrian run;
  - the tally becomes "Of the 53 outcomes predicted for the four final studies, 13 were not met and 4, all from the pedestrian study, were left without a verdict".
- **Introduction:** unchanged in substance. An early draft added the walking person to the sentence that lists what tests the three contributions; it was removed, because the walk tests none of them.
- **Conclusion:** names real-target campaigns at sea as the next step.
- **Also fixed:**
  - the ramp sentence, which now says the ramp reaches full amplitude at the first look;
  - "the real target" is now "the IPIX target" wherever a second real target could be meant.

**What made room (rule 1):**
- the 77 GHz CNR paragraph, shortened (the CNR-range clause and the 1.07 → 0.08 numbers, which Table IV keeps, are gone). It keeps the coverage check against Corollary 1: 0.897 to 0.962 against the law's 0.932, with a mean absolute deviation over all classes of 0.010, and a false-alarm rate that falls further than predicted.
- the roadmap sentence of the Introduction;
- the perceptron spread clause;
- the receiver/bin pointer;
- the repeated excision sentence of Section VI-D, which design rule 3 and the Conclusion keep;
- the AR gap-reconstruction detail and a sentence restating the K_eff result;
- the burst numbers already in Table II;
- "Other laws: Supplementary Material" and the CA16/CAloc definition in the figure captions;
- small rewordings.

**Restored after the blind reviewers flagged their loss:**
- the day-to-day spread of the CAloc gain;
- the range-CA baseline on the IPIX target;
- "in simulation";
- the NetRAD diagnostic detail;
- the Conclusion's full law list and its excision clause.

**Supplement:**
- `sec_r17.tex` (generated): design, ground truth, outcome, limitations, mechanics-check disclosure, verbatim output;
- an exposure-table row;
- the unmet-expectations tally and bullet;
- eleven protocols listed.

**Code tag:** `r17-trs-submission`.

### Checks
- **Build:** 10 pages, 0 overfull boxes, 0 undefined references; the supplement is 31 pages.
- **Prose metrics** (`04_reviews/2026-10-03_R17_real_onsets/`): see `ROUND_R17.md`.
- **First round of review:**
  - a blind pairwise review in both orders preferred R17 modestly (0.60, 0.55);
  - the adversarial claim audit found 4 blocking text errors. "7 of the eight blocks set in advance" misstated the rule; the CNR classes were wrong; the protocol's limitations were missing; and the cover letter's "pre-registered" contradicted "an internal record".
  - All were fixed, with the reviewers' requested restorations.
- **Final round:** recorded in `ROUND_R17.md`.
