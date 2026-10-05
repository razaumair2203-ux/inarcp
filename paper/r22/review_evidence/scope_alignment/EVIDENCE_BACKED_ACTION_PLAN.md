# R22 hook, scope and narrative: diagnosis and bounded action plan

5 October 2026. This is the requested assessment before rewriting. The manuscript, supplement, uploads, numerical inputs and public Git snapshot have not been changed. All 139 active release-artifact hashes still match the published baseline; see [identity check](UNCHANGED_BASELINE_CHECK.json).

## Decision

The author's objection is supported. The abstract reports numerical evidence only from the two sea-clutter families, and the conclusion again names only those families. Substantive ground-scene tests are in the body but disappear from the opening and closing empirical account. The previous pass improved the introduction and methods without fixing this imbalance. Its earlier final-review verdict did not resolve this framing requirement.

There is also a specific underlying ambiguity: Discussion says “Transfer of calibration findings to other clutter types remains untested.” The paper already reports JKU ground-data coverage, false-alarm and CNR checks. The unestablished transfer is the deep-tail result, particularly calibration at 10^-4 beyond IPIX/NetRAD. The limitation needs that endpoint, rather than a blanket statement which can erase the non-sea checks in the reader's understanding.

The issue is bounded. The title, motivation, contribution structure, model, analytical sequence, four-family methods and detailed results are already general or appropriately dataset-specific. No evidence supports treating the whole manuscript as a failed sea-only rewrite. Those mature passages need no change.

## The hook to preserve

The paper explains and quantifies when a radar cell's own whitened history helps detection, when a persistent or gradually entering target contaminates that reference, and how pulsed corruption affects integration. Its post-onset rank-one law, visibility horizon and OS analysis make the detection interval calculable; a guard delays contamination. A separate worst-case conformal certificate gives an amplitude-independent false-alarm bound under its hit-position and exchangeability conditions. Measurements test the predictions, costs and boundaries across sea clutter and ground scenes, leading to specific choices about look interval, history/guard, calibration and interference mitigation.

The main proposed analytical novelty lies in the post-onset/horizon/OS analysis and the pulse-interference certificate in the stated form. Whitening/PAMF, classical CA/OS laws and split-conformal ranks remain acknowledged foundations. More datasets strengthen the measured design evidence; they do not automatically create additional novel laws. This scope review does not replace the earlier literature-priority audit.

Three different levels must remain visible:

1. **Physical-source-independent statistical theory.** No sea variable enters the mathematics. The exact innovation laws retain Gaussian speckle, true AR whitening, a common texture over the relevant span and their noise conditions. “Arbitrary texture distribution” does not mean arbitrary textured process.
2. **Diverse empirical evaluation.** IPIX, NetRAD, JKU and UW actually test different endpoints and regimes. The paper should give that breadth appropriate prominence.
3. **Endpoint-specific operational evidence.** These datasets do not all validate every model assumption or establish superiority in every setting. The certificate has a broader clean-distribution domain than the AR law, but still needs exchangeability and independent, dominated hit positions.

## What the tests contribute to the narrative

| Evidence | Purpose and verified strength | Boundary that must remain explicit |
|---|---|---|
| Synthetic model checks | Check the exact coverage/detection formulas, post-onset/horizon behavior, OS counterpart and certificate implementation | Mathematical truth comes from the proofs; simulation checks their calculation under the specified model |
| IPIX X-band sea clutter | Strong measured onset sensitivity and far-tail calibration evidence; guards, ramps and injected-hit tests; fully persistent real target | Development exposure, dependence and known injected timing; the real target is continuously present |
| NetRAD S-band sea clutter | Initially unused-data test with refitted thresholds; guard and matched-hit findings reproduce; higher correlation and native flagged-pulse boundaries | Not frozen-threshold transfer; five statistics exceed twice design at 10^-4; later studies reuse exposed recordings |
| JKU 77 GHz reference and real interference | Tests thermal-noise/CNR effects and real interfering chirps; sparse certificate has a measured control/cost tradeoff; fast-time excision is useful | Uneven CNR support and a post-hoc gain comparison; real masks do not prove theorem assumptions; dense certification is nearly vacuous |
| JKU real walking person | Real radar-derived onset events after mitigation; descriptive sensitivity and background comparisons | Seven event blocks, same-radar labels and weak frame-to-frame correlation; no confirmatory onset-superiority claim |
| UW camera-labelled pedestrians | Detector-external presence evidence, whole-record roles, background checks and support sensitivities | All correlation gates fail, primary clean entries are absent, camera depth/timing uncertain; no precise radar-onset validation |
| Long injected trajectories | Extends guard evidence to 48 looks, including measured null rates and eventual self-masking | Finite delay, not indefinite target visibility or new real trajectories |
| Unknown-time continuous migration | Tests acquisition beyond known onset; complete 24-condition grid and measured null/localization outcomes | Guarded acquisition is poor; idealized response is not a measured hardware response |

These tests are valuable because they distinguish the conditions that produce a gain, the cost of control and the conditions that call for a different detector or mitigation. The manuscript should communicate this contribution confidently and specifically. It should not present all tests as successes of the exact no-noise law or merely advertise a number of datasets.

## Whole-paper disposition and proposed actions

Line locators refer to the current `03_submission_IEEE-TRS/manuscript/main.tex`. These are proposed changes, not applied edits.

| Location | Diagnosis | Action/status |
|---|---|---|
| Title, line 39 | Already general and consistent with the actual analytical contribution | **Keep** |
| Abstract, line 50 | Only sea datasets appear in the measured account; repeated numerical detail consumes the space that should represent complementary tests | **Required framing correction:** foreground the mechanism/contribution and include sea/ground test roles plus a meaningful non-sea finding. Fund this through selective compression of repeated sea-specific detail |
| Keywords, line 54 | Sea clutter is a legitimate empirical keyword | **Author choice, not a defect.** Do not remove it merely to appear more general |
| Introduction/contributions, lines 58–68 | General three-problem motivation, acknowledged PAMF lineage, bounded novelty and explicit four-family roadmap already work | **Keep.** No fourth “broad validation” contribution bullet or generic diversity paragraph |
| Related Work, lines 71–75 | The needed classical, conformal, interference and motion-search context is already integrated | **Keep.** This scope correction does not require new citation padding or a new literature section |
| Model/laws, lines 77–259 | Source independence and distinct statistical conditions are explicit | **Keep all equations, notation, assumptions and proofs** |
| Experimental Design, lines 263–275 | All four families and their processing/exposure are identified | **Keep**, including accurate sea labels for the two marine recordings |
| Results, lines 290–348 | Already contains non-sea CNR, real interference, pedestrians, persistent targets, guards and migration | **Keep results and their classification.** No rearrangement or repetition solely to prove breadth |
| Table IV, lines 354–379 | Its 16 claims have support; the generic ground/interference labels obscure which dataset supplies a row | **Small precision/navigation improvements:** name UW and JKU in the relevant labels; provide compact evidence pointers to the appropriate main/supplement sections or saved outputs. Keep measured outcomes and numerical cells |
| Discussion bridge, line 383 | Generic summary does not fully interpret the complementary tests | **Replace rather than append:** link correlation at the actual look lag, CNR, reference contamination and hit structure to the design findings |
| Discussion transfer limit, line 387 | Too broad for the already reported ground-data calibration/noise checks | **Clarify specifically:** calibration down to 10^-4 has not been established beyond the two sea-clutter families. Preserve that real limitation |
| Design rule, line 393 | “Both radars” refers to IPIX/NetRAD, although four families now appear | **Tiny contextual correction:** identify IPIX/NetRAD. Keep the concrete rule and costs |
| Conclusion, line 399 | Ground-scene evidence disappears from the synthesis | **Required closing alignment:** include what noise, real interference and real-pedestrian tests establish and the resulting design choices; retain the independently timed correlated-onset and measured-response gaps |
| Supplement opening, line 22 | Supports more than laws/calibration: visibility and interference/real-target evidence are substantial | **Optional small alignment:** describe those existing roles in the opening sentence |
| Supplement pedestrian ending, line 738 | Residual “independent maritime onset performance” states an unnecessarily environment-specific remaining gap | **Small consistency correction:** identify independent real-target onset performance in correlated clutter; retain historical data descriptions and failed endpoints |
| Cover letter, availability and declarations | Already name all four families and preserve author/data facts | **Keep facts and synchronize only where affected** |

A physical sea/ground categorization must not replace the relevant statistical regime. In particular, JKU chirp-level noise/interference tests differ from JKU/UW frame-to-frame pedestrian tests. Their observed weak frame-lag correlation is not a claim that all 77 GHz or all ground clutter is weakly correlated.

## Abstract and word-budget strategy

The current abstract has 246 rendered words. Appending a dataset list is not an acceptable solution. A revised abstract should use its existing space for:

- the source-neutral detector problem and principal analytical contribution;
- the essential exact-law and certificate conditions;
- the purpose-based breadth of measured tests;
- representative numerical evidence of the strongest gains/control;
- the main operational boundaries.

Keep a quantitatively strong calibration anchor, a guard/sensitivity anchor and a qualified interference result. Avoid reproducing every matched injected-hit and guard value for both sea radars when those detailed comparisons are already in the tables. Ground evaluation must appear through what it tests and establishes, not just through provider names. The real sparse-interference false-alarm result and its sensitivity cost are available in existing generated macros; no new number is needed.

The Discussion and Conclusion changes should replace their existing synthesis. Table pointers must be economical and paid for by removing actual repetition elsewhere. Preserve 11 pages, native figure sizes and readable tables. No figure redesign, new result grid or additional study is required by this diagnosis.

## Wording safeguards

Each changed sentence must have a recorded reason, evidence source and preservation constraint. Use terms that name the mechanism or measured endpoint. Keep the distinctions between per-look detection, within-window acquisition and camera presence association; nominal versus measured false alarms; fitted versus true models; injected versus real targets; and initial unseen data versus later reuse.

“Diverse evaluation” is supported; “validated in every clutter type” is not. More forceful language cannot erase weak pedestrian correlation, an undefined clean-entry endpoint, migration failure, burst costs or refitted calibration. Conversely, broad limitations must not erase completed non-sea experiments. These are acceptance criteria for proposed wording, not accusations that all such errors currently exist.

## Implementation and verification gate

This audit-and-plan stage is complete. Article editing has not begun. If the plan is implemented, keep it within R22 and preserve all existing immutable public tags. Use a concrete sentence-level change record rather than a general rewrite.

After the last edit:

1. Check all formal mathematics, result macros, table cells, figures, saved outcomes and study controls against this baseline. No scientific outcome or protocol changes are part of this scope.
2. Reconcile the abstract/conclusion/captions with the supporting main and supplementary tables; distinguish figures whose complete supporting grids live in the repository.
3. Synchronize metadata, affected companion summaries and both Overleaf containers. Regenerate supplementary prose through the existing editorial layer rather than altering locked proof inputs.
4. Compile within the 11-page budget and 150–250-word abstract range; inspect all PDFs and build both ZIPs from empty directories.
5. Compare presentation metrics, explicitly justify any tradeoff, and obtain independent last-edit claim/scope reviews and anonymous comparisons in both orders. The scope rubric must explicitly require the abstract, conclusion and empirical synthesis to represent the complementary non-sea tests.
6. Promote/publish only after those checks, maintaining one live package and an unchanged archived/published baseline.

This stage requires no new radar computation, external-model dispatch, new literature claim, author fact or permission to change the science.

## Independent supporting reviews

- [Whole-paper section map](CURRENT_SCOPE_AND_NARRATIVE_AUDIT.md)
- [Formal assumptions, proof and empirical evidence matrix](HOOK_AND_EVIDENCE_MATRIX.md)
- [Selective reader-impact and sentence targets](SELECTIVE_READER_IMPACT_AUDIT.md)
- [Unchanged manuscript/artifact baseline](UNCHANGED_BASELINE_CHECK.json)

All three internal independent reviews agree on the principal diagnosis: abstract and closing synthesis underrepresent non-sea evaluation; most of the body already conveys the broader model and test scope. None supplies a reason for a wholesale rewrite or a new contribution claim.
