# Blind pairwise review — presentation order two

Read order: **first**, then **second**. I read all 11 pages of each PDF, including references and appendices, and visually inspected all 22 rendered pages. I did not inspect mappings, other manuscripts, outcome files, protocols, or existing reviews. Visible release identifiers were disregarded; the recommendation uses only the presented manuscript content.

| Presented PDF | Pages | SHA-256 |
| --- | ---: | --- |
| first | 11 | `3cac39ba29a0f16f5a387d1679de9e25c68025742f20765b5d972b95e01ef67e` |
| second | 11 | `7218d385aa9cd618b3c0946883216018833ec8262c3e0cdb2a7da1fb45a4d504` |

## Decision

**Keep first.** The preference is substantive, principally about the evidence supporting the operating boundaries. Both manuscripts are mature and have the same credible central contribution. No broad rewrite, new contribution claim, or figure/table redesign is needed. The localized clarification identified on the initial read is now resolved; no mandatory issue remains from this review. No further change is needed on the reviewed manuscript dimensions.

First directly shows that a guard delays, but does not prevent, self-masking. Its 48-look Fig. 3b compares guards of 0, 8 and 16 pulses, with measured trajectories, fitted-law trajectories using the same episode weighting, and cluster intervals. Section VI-C reports paired gains over looks 9–16 on both sea-clutter radars and explicitly states that every guard subsequently loses sensitivity. Second appropriately admits that its real-clutter measurements stop at look 8, but its guarded plateau cannot demonstrate the later collapse or distinguish the longer guards. First closes that particular evidential gap.

First also replaces second's illustrative migration/horizon calculation with an actual, explicitly idealized migration experiment (Section VII-A). It reports acquisition of 0.004–0.030 across 24 conditions, lower than P-ANMF in every condition, and reports the unequal measured null-rate ratios. This is useful negative evidence rather than an operational success claim. The unavailable measured complex range response and use of sinc responses are stated. Its conclusion correctly keeps measured range response and externally timed, correlated-clutter onsets as outstanding operational requirements.

## Scientific narrative and contribution

Both manuscripts organize the argument well: exact laws under an ideal innovation model; contamination by persistent targets; calibration on actual clutter; and conditional certification under pulse hits. Both identify the per-look statistic with a one-pulse PAMF and explicitly attribute sensitivity gain to whitening. They do not present conformal ranks or the established CA/OS laws as new inventions. The claimed contribution is the post-onset law and horizon, the persistence treatment, and the interference certificate assembled with measured calibration evidence.

The mathematical narrative is internally coherent at the level reviewed. The quadratic-form result, rank-one post-onset reduction, and order-statistic worst-case bound support the stated mechanisms. First's added full-history energy expression and restriction of the shifted horizon to partial contamination make the transition to eventual collapse clearer. This is a manuscript assessment, not an independent theorem, literature-novelty, or implementation audit.

The conclusions follow the evidence described. Calibration results concern measured null rates; step/ramp sensitivity concerns injected targets with known timing; matched independent hits check the implementation and detection cost; real interference remains empirical. Both distinguish false-alarm control from useful detection. Neither matched-hit agreement nor observed masks are claimed to prove hit-model dominance or exchangeability. First's additional failure cases narrow the operational conclusion appropriately.

## Claim and limitation calibration

Both manuscripts state the true AR coefficient, common episode texture, and no-thermal-noise conditions for the classical innovation laws. They separately state exchangeability for marginal conformal validity and independence for the conditional Beta calculation. They acknowledge session nonstationarity, IPIX development exposure, sparse expected tail events, six-cluster uncertainty, refitted NetRAD thresholds, remaining NetRAD failures at 10^-4, certificate vacuity under bursts, and the different protocols of target-trained literature.

First strengthens the real-target boundary with camera-labelled walks that provide no eligible correlated clean entries and no demonstrated whitening advantage. It correctly treats these as inconclusive for the intended regime. These results support a boundary, not evidence that the detector is generally inferior in correlated sea clutter.

Second has a transparency advantage in two places: its protocol paragraph states that the hashed record is internal and gives the unmet/no-verdict counts; its guard paragraph says the 0.9 dB onset cost exceeded the advance allowance. First retains the numerical onset cost and points to supplementary failures/deviations, but summarizes those disclosures more generally. Retaining a short explicit statement of failed predictions would be useful if space allows. This is an editorial preference, not a reason to reject first or a mandatory request to restore all removed detail.

## Abstract, notation, Table IV, and figures

**Abstract:** Both convey theoretical conditions, practical gains, tail failures and burst sensitivity costs. First is slightly denser, but its 48-look validation and final migration warning materially improve the reader's understanding of the scope. Second's opening explanation of a predictable number of looks is a little more immediately explanatory; this is a minor wording preference. No abstract rewrite is required on scientific grounds.

**Notation:** The roles of fitted r versus true rho, onset look 0, pulse guard Delta, amplitude threshold q versus squared score threshold, and nominal alpha versus measured Pfa are clear. Fig. 1 explicitly preserves the latest predictor sample inside the guard, avoiding a common misunderstanding. I found no notation defect that changes the reported conclusion. The short label “IN” in first's migration row can be expanded for convenience, but its intended detector is clear from the text.

**Table IV:** Both are readable, compact, and useful. Bold outcome phrases separate empirical advantages from failure mechanisms. First improves the persistent-target row by stating the 9–16-look interval, guard 0-to-16 comparison, and eventual collapse. Its caption correctly distinguishes this comparison from the ramp guard and states the migration SCR levels. The added migration and real-ground-target rows make the boundaries more complete without making the table unusable. No redesign is needed.

**Figures:** Fig. 1 is legible and captures the processing/indexing relationship. Fig. 2 has readable axes, distinctive styles/markers and a clear design line. The zero-event markers are explained rather than represented as measured positive probabilities. Fig. 3a is readable in both. First's Fig. 3b is the better scientific display of guard duration and subsequent failure; its caption identifies the dashed exploratory law and interval shading. Second's Fig. 3b retains a more detailed Doppler comparison within the initial eight looks, an honest tradeoff, but the text still reports the Doppler failure in first. No clipping, missing legend, or unreadable figure defect was found.

## Localized clarification — closed on final check

**Initial finding, first, Section VI-C, page 8:** After reporting measured clutter-rate ratios of 1.1 and 1.5 for 8–256-pulse P-ANMF and a general sentence about a supplementary long-dwell literature comparison, the initial PDF said that the measured false-alarm rate exceeded twice design without locally identifying its statistic/window. Second supplied the 1,024-pulse comparison and its 2.6-times-design rate.

**Final finding:** First now states, “At 1,024 pulses, P-ANMF has a measured false-alarm rate of 2.6 times design,” before the qualification about the i.i.d. Beta law. The referent is explicit, the distinct 8–256-pulse rates remain clear, and the paragraph renders legibly. This fully resolves the requested context repair. It does not alter the scientific recommendation.

## Final check and hash history

After notification of the targeted replacement, I checked first before second again. I reread the extracted text of all 11 pages of first, checked the updated page 8 render, inspected second's page 8, and reviewed a word-wrap-normalized text diff spanning all pages of the current pair. Availability-tag differences were excluded from the judgment. No additional substantive change was found against the prior reading. Second is byte-identical to the initial reviewed PDF. Both remain 11 pages.

The hash table above identifies the final pair reviewed. First's initial-read SHA-256 was `e772394b6d2a7b462640e19e2c2f5efe9c407373b4eb2ed3ec6fcf9cc979b20b`; its final SHA-256 is `3cac39ba29a0f16f5a387d1679de9e25c68025742f20765b5d972b95e01ef67e`. Second's SHA-256 remains `7218d385aa9cd618b3c0946883216018833ec8262c3e0cdb2a7da1fb45a4d504`. This follow-up was a manuscript-context check, not a new raw-data audit or a search for additional criticism.

## Evidence boundary

Verified here: what each PDF states, the rendered figures/tables, their internal argumentative consistency, page counts and hashes. Reasonable inference: first offers a stronger evidential account of delayed collapse and the migration boundary. Not verified here: raw outcome values, sampling implementation, protocol timing, supplementary results, authentic source contents, or reproducibility of the new experiments. Those require a separate artifact audit. No manuscript was edited.
