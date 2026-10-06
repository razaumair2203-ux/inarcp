# R22 title, contribution and endpoint review — 6 October 2026

The author approved **Innovation-Normalized Radar Detection in Compound-Gaussian Clutter: Self-Masking Analysis and False-Alarm Control** and targeted abstract clarifications. The author requested a fresh check of contribution completeness, limitation balance and technical ambiguity in results. This is a bounded R22 presentation revision, not a new scientific study or R23. Software remains 0.3.0.

The pre-edit release is preserved with verified hashes at `99_archive/paper_versions/R22_before_title_endpoint_clarity_2026-10-06/`. Baseline public commit: `f47d3f5a208f1ce12d28373ce37bd5d42c5ce4d8`. All earlier release tags and signed reports remain unchanged. The current presentation tag is `r22-clarity-submission`.

## Contribution completeness and scope

The existing three-item contribution structure is complete and is retained:

| Contribution | Evidence and qualification |
|---|---|
| Post-onset detection and self-masking | Rank-one detection law, OS counterpart and visibility horizon quantify contamination of the cell's own history. Guard delay is conditional on the stated model; neither the law nor the measured long trajectories establish indefinite target visibility. |
| Conformal calibration application and measured validation | Established split-conformal theory supplies calibration requirements. IPIX/NetRAD comparisons establish improved, imperfect measured tail calibration, with explicit NetRAD failures at nominal 10^-4. The paper does not claim to invent conformal prediction. |
| Interference false-alarm theorem | A worst-case bound and conformal threshold control false-alarm probability for arbitrary interference amplitudes under exchangeability and clutter-independent hit positions dominated by the calibration hit model. This theorem does not guarantee detection sensitivity. |

Recovery of classical CFAR laws, Gaussian quadratic-form coverage and noise-dependent whitening gains support the analysis. The 48-look, idealized migration, measured-interference and camera-associated experiments establish useful regimes and boundaries; they are validation findings, not additional detector inventions. The one-pulse PAMF equivalence and classical foundations remain explicit.

## Limitations and balance

No evidence warrants removing or adding a blanket limitation. The manuscript retains exact-law model conditions, exchangeability and hit-pattern conditions, finite guard benefit, far-tail failures, sensitivity costs and vacuous certificates, poor unknown-time migration acquisition, and the missing independent real-target onset validation in correlated clutter. Radar-derived JKU labels and descriptive UW camera association remain distinguished from independently verified radar onset.

There is no meaningful numerical quota between contribution and limitation statements: claims, assumptions and unsuccessful operating conditions are different objects. The introduction has three explicit contribution items; the discussion separately explains theoretical conditions, real-onset/deep-tail validation gaps and migration. Relevant boundaries also remain beside their results and in the conclusion. Their repeated placement serves distinct functions and does not imply equal research weight. The paper should foreground the established result and state each condition where it changes interpretation.

IEEE guidance asks for a self-contained abstract of at most 250 words and a clear account of novelty/context; it supplies no contribution-to-limitation ratio. Sources consulted: [IEEE Author Center](https://journals.ieeeauthorcenter.ieee.org/create-your-ieee-journal-article/create-the-text-of-your-article/structure-your-article/) and [T-RS author information](https://ieee-aess.org/publication/ieee-transactions-radar-systems/t-rs-author-info). No numerical editorial ratio is inferred from their silence.

## Changes and supporting evidence

- Title and running header now name the self-masking analysis and the controlled false-alarm quantity. The supplement, draft letter, metadata and current documentation agree.
- Abstract false-alarm ratios explicitly name the probability; the 10 dB reference is SCR. Eventual self-masking replaces the vague collapse endpoint. The certificate's guaranteed quantity is false-alarm probability.
- The sparse measured-interference penalty is extra SCR at 50% detection against the same clipped integrator with a clean-data threshold on the same interfered run. Saved sparse-C/no-mitigation values are 14.52 minus 8.11 dB overall (6.41, reported 6.4) and 10.40 minus 7.29 dB on hit-free segments (3.11, reported 3.1).
- Main captions distinguish design per-look false-alarm probability and SCR. The Hann/PAMF comparison names the detection criterion and clutter-matched versus random-Doppler comparator. Supplementary guard detection columns specify alpha=0.01; JKU columns define the rate ratio and SCR50 with its dB unit.
- Guard onset costs explicitly use Pd=0.5; unrounded saved differences 0.887334 and 1.245531 dB retain the existing 0.9 and 1.2 dB reports.
- Migration exposure is 4,256 **test windows per condition**, not 4,256 successful acquisitions. Acquisition means any strict exceedance over the full search; local acquisition requires an exceeding bin within 6 m of the trajectory. These definitions match `run_migration.py:event_records` and its evaluation-only local mask. All original outcomes remain unchanged.

The ordered supplementary editorial overlay makes these changes regeneration-safe without altering pinned compact-base inputs, proof fragments or scientific code. `EDIT_RECORD.json`, `FINAL_PRECISION_RECORD.json` and `PAGE_BUDGET_RECORD.json` preserve exact changes and reasons.

## Verification

The final main build has **11 pages and a 248-word rendered abstract**; the supplement has **27 pages**. Both standalone source ZIPs compile after fresh extraction, with no errors, overfull boxes or unresolved references. The cover remains a one-page draft requiring author factual confirmations; no journal submission was made.

Both anonymous comparison orders favor the clarified text. Follow-up reviews resolve the guard-cost and acquisition/local-event questions. The separate last-edit endpoint/claim audit traces changed quantities to saved outcomes and method definitions. Its conclusions, plus the independent fresh-archive reproduction/visual report, certify their own final snapshots and are linked separately when attached.

The unchanged regression tools report body word counts 6,961 to 6,999 (+38), mean prose sentence length unchanged at 21.2, and the structural metric's sentences over 40 words reduced from 3.4% to 2.8%. The abstract's Flesch score falls from 15.5 to 11.2 because precise multi-syllable quantity labels replace compressed shorthand; its mean sentence length changes only 18.4 to 18.6. The prose tool's over-35-word share rises 10.5% to 10.7%, and numeric density is slightly higher because Pd=0.5/50% is now explicit. These bounded tradeoffs are accepted for endpoint precision, supported by both independent reader comparisons. No squeeze settings, figures, table count, citation list or mathematical environment was added.

The new independent checker preserves all earlier frozen scientific gates and saved-result checks, and adds baseline proof/equation/numerical/figure preservation, exact metadata expansion, source-ZIP identity, full-title consistency, current 11/27/1-page builds and the <=250-word abstract requirement. Historic checks remain immutable. Pending author confirmations, ORCIDs and live-portal fields remain as documented; artifact checks do not certify author assent.
