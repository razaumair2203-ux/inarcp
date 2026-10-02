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
- **Not yet in git.** The tag `r16-trs-submission` predates this revision. Its figure scripts still draw the old layout.
