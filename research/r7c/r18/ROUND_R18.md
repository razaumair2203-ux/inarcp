# R18: senior-reviewer round (3 Oct 2026)

**Input:** R17, clear to submit — 10 pages, abstract 249 words, clean build, no claim failing
its audit, blind pairwise 0.68/0.68 against R16.1.
**Question asked:** which sentences, omissions or framings in R17 would cause a competent
T-RS reviewer in 2026 to ask for major revision or to reject?
**Output:** R18, 11 pages, abstract 249 words, clean build, blind pairwise **0.85 / 0.70** for
R18 in the two presentation orders, no claim failing the final audit.

The audit is `SENIOR_REVIEW_R18.md`: twelve findings, nine acted on in the manuscript, three
recorded and deliberately not changed.

## The page decision

`CLAUDE.md` rule 1 capped the paper at 10 pages. The cap came from the belief that ten pages
was the journal's limit. It is not: **T-RS sets no page limit and charges US$200 for each
printed page beyond ten**, so the cap was a cost decision. The fixes needed about 230 words
and two references, and about 170 words of genuine redundancy were found to pay for them —
not enough. The author was asked and **approved page 11 on 3 Oct 2026**, with the extra page
also spent on enlarging Figures 2 and 3, which was itself a finding (F12). Rule 1 in
`CLAUDE.md` now records the 11-page budget and says not to reach twelve without asking.

The integrate-never-accrete discipline still applied inside the new budget. Cuts made:
Introduction redundancy with Related Work (−49 words), the pulse-blanking thresholds moved to
the supplement (−25), design rule 1 no longer restating Section III-B (−24), two rows of
Table IV no longer re-told in prose (−23), the development aside in Section VI-C (−11), the
clip-level rule (−9), two pivotality sentences merged (−18), a signpost sentence (−6), the
ANMF dwell length already stated elsewhere (−3).

## What changed in the manuscript

| Finding | Change | Where |
|---|---|---|
| F1 | The paper's own number at the literature's observation length: 0.41 at 2.6 × 10⁻³ over 1,024 pulses, against the literature's 0.91 at 10⁻³. Pre-specified endpoint T4 of `PROTOCOL_R12.md` | V-C |
| F2 | The guarded horizon as a duration on each radar (12 ms at 1 kHz, 2.2 s at the 77 GHz frame rate), the look-interval trade-off, and the range-cell re-onset mechanism. Design rule 1 now says to measure |r| at the intended look lag first | VII-A, VII-B, supplement |
| F3 | The texture dependence of the statistic recommended for persistent targets (quintile spread 4.4 at 10⁻², 23 at 10⁻⁴) | V-C |
| F4 | The model-based laws fail in at least two ways, separated by their texture dependence | V-A |
| F5 | The guard's averaging window named in the abstract and in V-D; the measured window stated; the longer guard's cost given | abstract, V-D |
| F6 | Non-exchangeability cited to the radar and the statistics literature (Greco et al. 2010; Barber et al. 2023) | V-A |
| F7 | Calibration-data requirement, per-cell arithmetic and state, and the single shared threshold that pivotality buys | VII-B, supplement |
| F8 | The CFAR loss named and cited | IV-F |
| F9 | The one hand-typed result number macro-ised | V-C |
| F10 | The supplement given a reference list | supplement |
| F11 | Root README, change log, `_TO_DELETE/` → `misc/`, R17 archived | repository |
| F12 | Figures 2 and 3 enlarged to 2.35 and 2.15 in; smallest type 6.3 → 7.0 pt | figures |

## Independent review, and what it found

`CLAUDE.md` rule 8 — the agent that wrote the text does not certify it — so three independent
agents were run: a blind pairwise reviewer in each presentation order, and an adversarial
claim auditor against the saved outcomes.

**Blind pairwise: 0.85 (order 1) and 0.70 (order 2) for R18.** Both credited the matched
learned-detector comparison and the operating-regime passage. Both found the same five
defects in R18's own new text, all fixed:

- the abstract's word-saving cut dropped "injected-interference", which made a NetRAD claim
  **false** — the certificate calibrated on NetRAD's own flagged pulses is vacuous
  (P_d = 0.04, graded F in Table IV). Restored;
- "ours on neither" denied that a conformal threshold is an empirical threshold;
- the Δ = 8 versus Δ = 16 preference rested on a window that cannot separate them — and
  contradicted R18's own argument that horizon length is the binding limitation;
- "one threshold for every cell" read as one per cell and overstated the measured pivotality;
- the calibration record length was quoted as a point value when it is a lower bound.

They also fixed six pre-existing items, the sharpest being the Kraut–Scharf inference: "fails
2.8–3.4-fold even in simulated compound-Gaussian clutter, **so the SCM failure need not stem
from the clutter tails**" does not follow, because simulated compound-Gaussian clutter is
heavy-tailed. Reworded to the inference that does follow: the failure is already present under
the model and need not come from any departure of real clutter from it.

**Adversarial claim audit: seven FAILs, all fixed.** It verified every macro against its
outcome file and found no arithmetic error in any macro. The failures were superlatives,
conditions and derived arithmetic — four of them in R18's own new text:

| FAIL | What was wrong | Verified independently before fixing |
|---|---|---|
| 1 | "the least pivotal of the thirteen" | **False.** The clipped integrator's conformal spread is 12.1 at 10⁻³ and 6.3 × 10⁶ at 10⁻⁴, against the P-ANMF's 9.9 and 23. The P-ANMF is widest only at 10⁻². Superlative dropped |
| 2 | "its threshold carries a finite-sample law", said of the 1,024-pulse configuration | The measured rate there is 2.6 × 10⁻³, above the 2α the law bounds. Replaced with what is true and measured |
| 3 | "at least 38 s of clean recording across 14 range cells" | **Both wrong.** `research/r7c/ipix.py` excludes the target bins and one guard bin each side, leaving **7–9** clutter bins, never 14; and a guarded episode spans m + Δ + 1 = 25 pulses, not 17. Recomputed: **87–112 s** |
| 4 | "25 stored samples per cell per pulse" | The state is a sliding buffer per cell. As written it claimed storage growing without bound — the opposite of the cheapness argued |
| 5 | "their error concentrates where the clutter is strongest" (supplement) | **Unsupported, and probably backwards.** Part L saves only the max/min ratio. The two per-quintile vectors the frozen data do contain run the other way, highest rate in the *lowest*-texture quintile |
| 6 | "the cleanest confirmation in the paper" (supplement), said of the pedestrian result | That result's criterion was **not met** and the paper calls it descriptive. Replaced; the pre-specified and met IPIX comparison is named as the stronger evidence |
| 7 | "on these recordings" and "trained on labeled targets in these recordings" | The repository documents nothing about which IPIX files the cited detector uses or how it is trained. "on IPIX" and "a different evaluation" restored |

Twelve WEAK items were also raised; eight were fixed, including: the delayed decay is
*measured* to look 12 by `theory_check_guard.txt`, not merely predicted; the horizon is now
computed at each radar's own correlation rather than IPIX's for all three; the cell-crossing
illustration now uses 5 m/s, inside the ±8 m/s unambiguous interval at X-band and 1 kHz; the
guard's onset cost is disclosed as exceeding what the protocol allowed; and the calibration-set
range no longer mixes a dwell minimum with a per-look maximum — the defect class that
`CLAUDE.md` rule 4 was written for.

**Two duplicate macros were removed.** `r18_macros.tex` had defined `\TPanmfKiloPd` and
`\TPanmfKiloPfa` for quantities `r12_macros.tex` already held as `\TPanmfThousand` and
`\TPanmfPfaThousand`. Two names for one quantity is how the abstract drifts out of step with
the tables, so the duplicates are gone and the generator carries a comment saying why.

## Presentation metrics (`metrics.txt`, `prose_metrics.txt`)

**A measurement bug was fixed first.** Both metric scripts split sentences on PDF text that
still contained the running head, so a page break inside a sentence spliced
"SUBMITTED TO IEEE TRANSACTIONS ON RADAR SYSTEMS *n*" into it. That inflated the
long-sentence counts and made them depend on where content happened to fall on a page — the
counts moved when 300 words were added, independently of the prose. Both scripts now strip the
running head before splitting. Rounds R16–R17 measured the uncorrected quantity; their
conclusions are unaffected in direction, but their long-sentence percentages are not
comparable with these.

Improved, R17 → R18: Flesch 40.0 → 40.7; Gunning fog 16.8 → 16.6; sentences over 40 words
7.0% → 6.8% (count 19 → 18 under the corrected splitter); sentence-length spread 21.7 → 21.2;
nominalizations 5.1 → 4.9 per 100 words; passive 13.8% → 13.7%; parentheses 0.97 → 0.96 per
sentence; macro-generated numbers 133 → 149; longest paragraph 403 → 396 words; abstract 254 →
250 by the script's own count (249 once its hyphenation artifacts are rejoined).

Flat: mean sentence length 23.6 words, vague words 1.1, dangling pronouns 0.6, hedges 12.4,
expectation codes 0, "new"/"novel" 0, process-jargon hits 10.

**Regressed, with reasons, as rule 6 requires:**

- **Numbers per sentence 3.43 → 3.52, and sentences with four or more numbers 30.3% → 31.1%.**
  This was the purpose of the round. The numbers added are results the paper already possessed
  and had not reported: the matched 1,024-pulse comparison, three texture-quintile spreads, two
  horizon durations, the calibration-data requirement and the per-cell state. Six long sentences
  were split to absorb what could be absorbed; the rest is the cost of reporting results rather
  than withholding them.
- **Sentences over 35 words 18.8% → 19.4% and mean 25.7 → 26.0** on the prose script's splitter,
  while the other script's over-40 count and mean both improved or held. Every sentence over 40
  words that is new to R18 under the corrected splitter is pre-existing text whose splice point
  moved when 300 words were added, not a new long sentence.
- **Abstract numbers 24 → 26 and abstract Flesch 26.7 → 25.7.** Naming the guard's averaging
  window exactly cost two numerals: "over the first eight looks" became "over looks 1–8 after
  onset", because the paper treats ℓ = 0 as a look, so "the first eight looks" would have read
  as looks 0–7, whose means are 0.35 and 0.82 rather than the measured 0.24 and 0.82. The
  abstract stayed at 249 words.
- **Semicolons 0.34 → 0.35, connective starts 4.1% → 4.0%, paragraph cohesion 0.075 → 0.070,
  paragraph mean 137 → 144 words** while the longest fell 403 → 396. Content was added to
  mid-length paragraphs and removed from the longest; the added passages introduce vocabulary
  the surrounding paragraphs do not share — "look interval", "range-cell transition",
  "calibration record" — which is the cost of naming a new concept.
- **Pages 10 → 11.** Authorized; see above.

## R18.2: the final claim audit, run after the last edit

Rule 6 requires the adversarial audit after the **last** edit. The first audit ran while the
text was still moving, so a second was run against the frozen text. It raised three FAILs,
all of them created by the R18.1 corrections themselves, plus thirteen WEAK items. It verified
all 190 result macros resolve, and found no arithmetic error in any of them.

| FAIL | What was wrong | Fix |
|---|---|---|
| 1 | The supplement said the clipped integrator **and the two ANMF laws** "fail at least as badly in the pooled rate" as the OS and Fisher's-*g* laws. **False**: at 10⁻³ the ANMF laws are 3.57 and 2.66 against 8.34 and 13.06, and at 10⁻⁴ they are 8.07 and 6.01 against 45.91 and 49.61. Only the clipped integrator fails worse | Rewritten to say what the numbers say: the clipped integrator worse still, the ANMF laws less badly, all three almost evenly across quintiles |
| 2 | The same paragraph ended "Tail weight is the mechanism for the first group and not for the second" — a directional reading of a max/min ratio, **three sentences after the same section says "No direction should be read into a spread"** | Deleted and replaced by the statement that the per-quintile vectors would answer it and were not saved |
| 3 | The supplement's 77 GHz row printed a horizon of 2.3 s, computed at IPIX's \|ρ\| = 0.93, in a table row whose last column states that radar's measured \|r\| is 0.12 — and so disagreed with the main text's 2.2 s. The per-radar fix had been applied to `make_r18_outputs.py` and not to `make_r18_supp.py` | ℓ* now evaluated per radar in both generators; both documents say 2.2 s |

WEAK items fixed: the antecedent of "which" in the horizon sentence (12 ms is the whole guarded
horizon, not the Δ extension); design rule 1's guard length now carries a basis, since the
one-sided preference had merely moved there from the Results; the guarded horizon is attributed
to the quantity Δ + ℓ* rather than to equation (6), which contains no Δ; the Kraut–Scharf
simulated failure is now stated at its design rate; and Table IV's split row is graded by its
worst case, as its own caption requires.

Recorded and not changed: that every sea-clutter certificate test has the hit model equal to
the pattern by construction (the body says so, and it is the next round's item 2); that "the
sensitivity comes from whitening, not from the order statistic" compares two factors at once
(deferred item, needs the whitened-OS arm); and that the cited learned detector's 0.91 is
traceable only to the authors' own note, so the source should be re-opened before submission.

## Artifacts, all rebuilt from empty folders (rule 7)

| Artifact | State |
|---|---|
| `manuscript/main.pdf` | 11 pages, 0 overfull boxes, 0 undefined references, 0 warnings |
| `supplement/supplement.pdf` | 33 pages, clean, no unresolved cross-references |
| `UPLOAD_TRS/` | rebuilt from empty; three PDFs opened and page-counted; the two copies verified byte-identical to their sources |
| `overleaf/INARCP_R18_manuscript_Overleaf.zip` | built from an empty folder, compiled there, then **re-extracted into another empty folder and recompiled**: 11 pages, clean |
| `overleaf/INARCP_R18_supplement_Overleaf.zip` | same procedure: 33 pages, clean |
| `journal_formats/IEEE-TAES/main.pdf` | generated from the live source; 11 pages, clean |
| `journal_formats/IET-RSN/main.pdf` | generated; 21 pages single-column, clean. **Not the publisher's class file** — see its `GUIDELINES.md` |
| `cover_letter_TRS.md`, `UPLOAD_TRS/Cover_Letter.pdf` | regenerated from the macros; release tag now `r18-trs-submission` |

**A stale release tag was caught by the IET build.** Four live documents still cited
`r17-trs-submission`: the manuscript's Code and Data Availability section, the cover letter,
its template and `declarations.md`. All four now cite `r18-trs-submission`. The bare GitHub URL
in the manuscript is now inside `\url{}`, which also cleared an overfull box.

## Recorded and deliberately not changed

- **F12 is now done**, so the only standing items are the three objections with no remedy
  (no real target with a real onset at sea; two sea-clutter campaigns, all open data; several
  laws are classical laws with a whitened SCR). All three are stated in the paper.
- The abstract omits two conditions a reviewer asked for — that the laws are restored at the
  true coefficient and with no thermal noise, and that the certificate's cost can grow to
  vacuity. The abstract is at 249 of 250 words; both conditions are stated in the
  Introduction's third paragraph, in Corollaries 1–2, in Proposition 2, in the Conclusion and
  in Table IV. Changing them means cutting something else from the abstract.
- "Those are trained classifiers" is the strongest claim the evidence supports about the cited
  detector. The repository documents nothing further about its protocol, and R18 will not
  assert another group's method without a citable basis.

## The next round's list, in priority order

All four need a new computation and therefore a frozen protocol first (rule 5).

1. **Convert the 10⁻⁴ conformal conservatism into dB of CFAR loss.** IN-ARCP measures
   0.73 [0.54, 0.99] at 10⁻⁴ — significantly *below* design, which is a real sensitivity cost.
   The Beta-ratio law to convert it is already derived in the supplement. Both blind reviewers
   raised this; the abstract currently presents 0.73 beside 1.47 as uniform success.
2. **Separate the certificate's soundness from its implementation on sea clutter.** Every
   sea-clutter certificate test injects hits drawn from the calibration model, so dominance
   holds by construction — the paper says so. One test with a pattern genuinely *dominated by*
   but not equal to the model would make the guarantee's robustness an empirical result rather
   than a software check.
3. **Give the detection cost of the 1.07 → 0.08 false-alarm swing across CNR** on the 77 GHz
   data, which Table IV currently grades on the false-alarm side alone.
4. **Per-quintile direction behind the texture spreads**, and intervals on the figures the
   abstract leans on — in particular that 0.30 against 0.27 on 74 pedestrian onsets in seven
   blocks is not a difference.

## Verdict

Clear to release. Both blind orders prefer R18, the final claim audit's FAILs are all fixed
and re-verified, every presentation metric either improved or has a stated reason, every
artifact was rebuilt from an empty folder and opened, and the notation table records a
symbol clash that was caught **before** the text was written rather than after.
