# Final R22 narrative and evidence-scope audit

Signed: `/root/r22_final_narrative_audit`, independent internal read-only reviewer, 2026-10-05. The reviewer did not write or edit the manuscript, supplement, scientific runners or saved outcomes. This report assesses the currently published R22 text and the signed scientific reviews. It does not independently rerun the science, certify author identities, or certify a later edited PDF.

## Judgment

R22 is already a coherent, mature paper. Its hook is not a wholly new per-look detector or a claim of universal detector superiority. The one-pulse PAMF equivalence and classical whitening benefit are stated. The contribution is the post-onset law and visibility boundary, their order-statistic counterpart, and the score-specific interference certificate, assembled with measured calibration and sensitivity evidence. The introduction, contribution list, mathematical development, Table IV and conclusion largely agree. No broad rewrite, additional contribution bullet, new figure, or repetition of the negative results is needed.

The new studies are already integrated, not merely appended without analysis. Long-trajectory results appear in Results, Figure 3b and Supplementary Figure S6, with the full-contamination energy distinguished from the partial-history law. Camera-associated real targets appear in Results and have a complete supplement section, source/method citations, all primary backgrounds and all fixed sensitivities. Migration has a complete supplementary method/results section and a quantitative main-text discussion, including all 24 conditions, measured null ratios, unavailable hardware response and the reference-contamination mechanism. The main improvement available is to put its main quantitative result in Results before interpreting it in Discussion.

Existing 2023–2026 conformal, learned radar, rank-CFAR and sieve-bootstrap references already contextualize the modern methodological comparison. The extensions do not automatically require another generic literature paragraph. The camera study's UW dataset and RAMP-CNN label-method citations are present; the NetRAD provider and original campaign paper are present. Add a new citation only if a new scientific comparison or methodological claim is introduced. Counting recent references is not evidence of novelty.

## Evidence breadth and its limits

| Evidence | Defensible description | Description to avoid |
| --- | --- | --- |
| IPIX | X-band measured textured sea clutter; acquisition in 1993; six recording dates; development exposure disclosed; additional rotations do not constitute an untouched campaign | A new independent data campaign for each rotation or protocol |
| NetRAD | S-band measured sea clutter; acquisition on 9 June 2011; public dataset release cited as 2026; untouched before its initial protocol; thresholds refitted on its designated calibration data | Newly acquired 2026 field data; frozen-threshold transfer; independent campaigns for later reused long-trajectory/migration tests |
| JKU | 76–77 GHz FMCW data; real interference, clean reference, and a real walking-person recording; frame-level onset results descriptive | Real target onset evidence in strongly correlated textured sea clutter; unspecified new acquisition dates inferred from the 2026 publication |
| UW | Three 2019 same-day 77 GHz raw-ADC records; dataset release cited as 2022; detector-external camera labels; training correlation 0.020–0.039; no primary clean entries | Strongly correlated clutter, independently verified native-bin onset, or useful clean-entry detection probability |
| Long trajectories | Injected known-onset persistent targets on measured IPIX/NetRAD clutter, all guards tested through look 48; supported delay followed by collapse | New real targets or indefinite persistent-target detection |
| Continuous migration | Fixed unknown-crossing search, continuous physical trajectory and idealized sinc response injected into reused measured NetRAD clutter; all 24 conditions retained | Measured hardware response or a universal field-performance ranking |

The breadth is valuable because the tests address different failure mechanisms. It cannot be summarized as successful validation across many independent real-target datasets. Publication year, acquisition year, development exposure, signal realism and endpoint validity are different dimensions.

The signed audits verify guard gains of 0.818 and 0.921 over looks 9–16, eventual collapse, migration acquisition 0.004464–0.030075 with P-ANMF's higher point estimates in all 24 conditions, and camera presence association 0.283469 versus guarded CA's 0.288979. Those are existing results; no new number should be typed into the main prose in place of its generated macro.

## Selective proposed edits

Only items 1–2 below are factual/context corrections. Items 3–4 improve important claim or section precision. Items 5–10 are optional selective polish; choose them only if the final layout and abstract word budget permit. This list is not an instruction to rewrite every passage.

1. **Supplement, “Unmet expectations”: historical count scope.** “Of the 53 outcomes predicted for the last four studies” now reads as if it covers the newly added extensions. Those 53 concern R12, R14, R15 and R17. Replace the opening with:

   > Each expected value was written down before the outcome was computed. For the earlier R12, R14, R15 and R17 protocols, thirteen of 53 expected outcomes were not met and four were left without a verdict. The additional long-trajectory, migration and camera studies report their outcomes in their own sections.

   Trace: the four existing bullets and counts (18 + 15 + 15 + 5), with the new G/M/R sections separately retained. This does not change a verdict.

2. **Supplement, “The operating regime of the per-look screen”: arithmetic and newly stale scope.** The paper now uses four dataset families, whereas the passage says “the paper's three radars.” Also, 1 ms versus 200 ms is a factor of 200, not three orders of magnitude. Replace the first sentences with:

   > Corollary~\ref{M-cor:horizon} gives the visibility horizon in looks. Its physical duration depends on look spacing: the three radar settings compared below span 1 to 200 ms. At $m=16$ and $P_{\rm fa}=10^{-2}$ the horizon is 3.7 looks at the opposite Doppler on IPIX and negative at the clutter Doppler, so with the $\Delta=8$ guard a strong persistent target is kept for at most $\Delta+\ell^{\ast}=11.7$ looks there.

   Trace: the immediately following existing table. Keep UW outside this table unless its corresponding guarded horizon is actually derived and qualified; no new numerical row is required.

3. **Main introduction, calibration contribution: “hold the rate.”** The current statement can sound like guaranteed exact measured control across every statistic. Replace the second sentence of that contribution with:

   > On IPIX and NetRAD, these thresholds improve measured tail calibration over the tested model-based laws; NetRAD retains failures at $10^{-4}$.

   The first sentence about the known finite-sample law remains. The quantitative 12/13 and 13/13 results remain in the abstract and Results. Trace: Table I, Table III, the signed claim audit, and the explicit exchangeability boundary.

4. **Main migration result: place the main observation in Results.** Relocate the existing quantitative paragraph beginning “With unknown crossing time” from Discussion to the end of the NetRAD Results subsection, without changing its numbers or assumptions. Keep in Discussion its last mechanism sentence, expanded only enough to read independently:

   > Continuous range migration can contaminate the normalization history before the target peak arrives; the measured acquisition failures show that a guard does not ensure a clean history.

   The preceding discussion paragraphs already explain the operational gap. The relocated paragraph retains the idealized response and measured null rates. A new subsection is optional; no new literature paragraph is required simply because the result moves.

5. **Main introduction, first problem: unsupported broad literature generalization.** Instead of saying Gaussian or simulated tail accuracy on real clutter is “rarely measured,” use the more precise statement:

   > Adaptive covariance and AR-whitening detectors restore scale invariance under their model assumptions (Section~\ref{sec:related}), but this does not establish the accuracy of model-based thresholds in the far tail of measured clutter.

   This is a logical distinction already demonstrated by the paper, rather than an unquantified assessment of the whole literature.

6. **Main introduction, validation roadmap: connect the tests to their purposes and acknowledge the camera addition.** Replace the existing sentence beginning “We test the framework” with:

   > We evaluate calibration and target visibility on X-band IPIX and S-band NetRAD sea clutter; NetRAD was unused in development and its thresholds are refitted. Longer trajectories and unknown-timing migration test the limits of a clean reference history. Real-interference and real-target checks use 77~GHz FMCW data, including camera-labelled UW walks. Comparisons include PAMF, ANMF, power detectors, certified trimming and pulse blanking.

   Retain the next two sentences identifying the shared PAMF gain and the conditional framework contribution. This adds a small amount of text and should be traded against redundant phrases, not obtained by shrinking figures. Trace: Experimental Design, data-exposure table, new Results and G/M/R audits.

7. **Abstract evidence category.** Change only “Measured trajectories follow delayed collapse” to “Injected-target trajectories follow delayed collapse.” This identifies the source of the evidence immediately. It is optional because Figure 3 and the body already specify the injection; it was also independently suggested in the prior blind review.

8. **Abstract final sentence: name the detector and actual endpoint.** Replace “The guarded screen poorly detects idealized continuous migration” with:

   > Guarded IN-ARCP poorly acquires continuously migrating targets under idealized range responses.

   This identifies acquisition, rather than an undefined “screen,” and preserves the response-model limit. It is a small optional clarity edit; the abstract is already near its word limit.

9. **Supplement operating-regime prose: measured difference versus confirmatory inference.** Replace “which is descriptive and not a difference” with:

   > The difference is descriptive; seven event blocks do not support a confirmatory superiority claim.

   The existing 0.30 versus 0.27 estimates are a difference. Failed E1 limits the inference drawn from it. Trace: R17's seven blocks, minimum eight-block criterion, and the retained descriptive result.

10. **Supplement real IPIX target section: remove an inaccurate rhetorical contrast.** Replace “The value of P-ANMF here is a calibrated short-dwell threshold, not sensitivity” with:

    > Conformal P-ANMF retains sensitivity to the persistent target without history self-masking; its calibration degrades at the longest tested windows.

    Trace: preserved target table, conformal detection 0.22–0.40 over 8–256 pulses, measured clutter ratios 1.1–1.5, and ratio 2.6 at 1,024 pulses. This does not assert universal superiority or ideal false-alarm control. The current contrast conceals a useful distinction between history-normalized and dwell-normalized detectors.

## Passages requiring no change

- Title: coherent and accurate; renaming it merely to advertise the additional checks is unnecessary.
- The three contribution headings and their mathematical content: mature and appropriately distinguish established foundations from this paper's new law and certificate.
- Main self-masking/long-trajectory result: precisely defines the 9–16-look gain, paired intervals, eventual collapse and null rates.
- Main camera paragraph and its supplementary primary/sensitivity tables: appropriately describe presence, weak correlation and the empty clean-entry endpoint. Do not relabel presence association as detection probability.
- Table IV: clear measured advantages and boundaries; a binary pass/fail redesign would erase differences between calibration, sensitivity, assumption failure and inconclusive evidence.
- Main conclusion: already balances supported theory/calibration/guard behavior with migration and operational-validation limits. A generic claim of broad validation or another positive summary sentence would add little.
- Proofs, formulas, symbols, generated outcomes, figure data and frozen protocols: this prose pass provides no reason to modify them.

The author additions requested by the user must be synchronized separately in the manuscript, supplement and submission artifacts, using authenticated identities and affiliations. This review does not infer assent, contribution statements, ORCIDs or declarations.

## Reviewed identities and limits

- Main source SHA-256: `672391d80749913f886acf9c961e05f14c5e329c4fe2fb68881da120287d81d1`.
- Main PDF SHA-256: `3cac39ba29a0f16f5a387d1679de9e25c68025742f20765b5d972b95e01ef67e`.
- Supplement source SHA-256: `18ee8cc71102a5fda1583ac69c26915843fa4c4170baed0dcbb5d4c8bd03a9f8`.
- Supplement PDF SHA-256: `00bf644133df2e2f0603d5fd63e11785004b0321b8de194798061ca7343d1258`.

Sources read: the full main source; complete supplementary source in segmented reads and targeted new/method/operating-regime sections; bibliography entries; R22 integrated numerical claim audit; M/R signed outcome audit; release review; both final blind reviews. Raw-outcome verification and all-page PDF rendering remain covered by the preceding signed independent audits, not repeated or claimed by this narrative review. A final post-edit read, compilation/page-count check and targeted visual check remain necessary if the parent applies any edits.

Signed: `/root/r22_final_narrative_audit`, 2026-10-05.
