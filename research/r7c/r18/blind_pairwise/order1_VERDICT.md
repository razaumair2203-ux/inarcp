# Blind pairwise review, order 1 (A = R17, B = R18)

**Reviewer did not know which was which.** Reported **P(B better) = 0.85**, i.e.
**P(R18 better) = 0.85.** With order 2's 0.70, both presentation orders favour R18.
(R17's own round scored 0.68/0.68 against R16.1.)

## What it credited to R18

- The abstract scoping the guard's 0.82 to its averaging window — "the largest single
  difference" — and "Only the first eight looks were measured" as a limitation stated at the
  claim.
- The whole operating-regime passage: "this is the referee's first question, and B puts the
  unflattering answer in its own text." It re-derived every number (8 + 3.7 = 11.7; 11.7 ms;
  11.7 × 200 ms = 2.34 s; 15/10 × 1000 = 1500; 11.7/1500 = 0.78%) and found them consistent.
- The matched learned-detector comparison: "A different evaluation" is a brush-off ...
  Volunteering a losing matched comparison is exactly what a reviewer wants."
- The P-ANMF non-pivotality caveat, the non-exchangeability citations, the deployment cost,
  the CFAR-loss naming, and the enlarged figures' tick labelling ("A's figures are harder to
  read values off").
- It verified R18's new numbers independently: "B's new numbers (11.7 looks, 12 ms, 2.3 s,
  1,500 looks, 0.8%, 31,500, 38 s, 25 samples) all check out."

## Defects in R18, all fixed in R18.1

Items marked **both** were independently found by the order-2 reviewer as well.

| # | Objection | Fix applied |
|---|---|---|
| xi **both** | Dropping "injected-interference" makes the NetRAD abstract claim false; contradicted by R18's own Table III row (certified P_d = 0.04) and Table IV grade F | Qualifier restored, paid for elsewhere in the abstract |
| xii **both** | "ours on neither" — the paper's own Related Work says a conformal threshold is an *empirical* threshold plus a finite-sample law, so the claim contradicts the paper's own characterization | Rewritten to claim only what is true: no target data, and a finite-sample law |
| xiii **both** | The Δ = 8 versus Δ = 16 conclusion is one-sided. Sharper than order 2: by Corollary 4, Δ = 16 moves the horizon to ≈ 19.7 looks — nearly doubling the visibility window for 0.4 dB — and R18's own Discussion argues horizon length is the binding limitation. "Cheaper" was being used to mean "better" | Rewritten to state both sides and declare no winner. This was an internal inconsistency R18 introduced against its own F2 argument |
| xiv | **"Fail where the clutter is strongest" is not established by a max/min spread.** The spread says the rate varies with texture; it does not say which quintile is worst — it could be driven by the lowest. The per-quintile values are not in the saved output, so the direction cannot be checked without a new run | Directional claim removed: the text now says only that the rate depends strongly on clutter power. Labelled exploratory |
| xv **both** | "One threshold for every cell" overstates the measured pivotality: the spreads are 2.7 at 10⁻⁴ on IPIX and 2.40 on NetRAD, so a single shared threshold does not hold the per-cell rate at the rates the paper cares about | Rewritten as approximate, with the 10⁻⁴ spread quoted in the same clause |
| xvi **both** | The 38 s calibration figure is the i.i.d. bound and is the number a reader will quote | "at least about 38 s", and the calibration ranking stated as offline |
| 11, 12 | Cutting "The per-look score is a one-pulse PAMF test" from the Introduction, and the clutter-map citations, "were the wrong things to cut": the PAMF sentence "is the sentence that makes the novelty claim credible" | Both restored |

## Pre-existing defects it found in both versions — fixed where cheap and exact

| # | Objection | Disposition |
|---|---|---|
| i | **The Kraut–Scharf inference is a non sequitur as worded.** "fails 2.8–3.4-fold even in simulated compound-Gaussian clutter, so the SCM failure need not stem from the clutter tails" — simulated compound-Gaussian clutter *is* heavy-tailed, so a failure there is consistent with the tails being the cause. Called "the clearest logical error in either version" | **Fixed.** The simulation is compound-Gaussian (supplement, V7 rows), so the sound inference is that the failure is already present *under the model* and need not come from any departure of real clutter from it. Reworded to say exactly that |
| v | "The certificate holds on sea clutter" (Conclusion) is not supported as the authors themselves describe the experiment: every sea-clutter certificate test has the hit model correct by construction — "this checks the implementation and the cost, not robustness" — and the one test with a real hit pattern gives P_d = 0.04 | **Fixed.** The Conclusion now scopes the claim to where the hit model dominates the pattern, and names the injected-hit basis |
| iii | The abstract's "12 of 13" lets a reader assume the exception is marginal; it is 0.03, i.e. 33× conservative. Worse, Table IV grades that row **W** although its caption says grades follow the worst case | **Fixed in Table IV**, which now names the exception and carries a split grade. The abstract is at 249 of 250 words and the body states 0.03 with its mechanism, so the abstract is left as is |
| vii | κ ≈ 9 in design rule 3 is a post-hoc selection whose pre-specified rule held in only 17 of 56 units; labelled correctly where reported and silently unlabelled where recommended | **Fixed**: the design rule now carries the post-hoc label |
| x | Two values for the same CAloc gain, 9.8 dB and 9.9 dB, distinguished only by an opaque "in this comparison" | **Fixed**: "in the ramp comparison" |
| xix | Cutting "This blindness was seen during development" loses candor about what pre-specification bought | **Resolved differently.** That sentence is process text, which `CLAUDE.md` rule 2 bars from the manuscript, and the supplement's data-exposure table already records the development check. The overclaim the reviewer objects to is the word "confirms": changed to "measures", which claims no confirmatory weight without narrating process |
| ii | The abstract's "restores these laws" omits that this holds at the true coefficient and with ν = 0 | **Considered, not changed.** The abstract is at the word limit. The condition is stated in the Introduction's third paragraph, in Corollaries 1–2, in Proposition 2 and in the Conclusion's first clause. Recorded |
| iv | The abstract does not say the certificate can be vacuous | **Considered, not changed.** Same word limit; the abstract carries "Injected bursts defeat every remedy tested", the Conclusion says "at a cost that grows to vacuity", and Table IV grades all four cases. Recorded |
| vi | The abstract's 23-fold comparator is the unremediated baseline, while blanking reaches P_d 0.78 within 1.21× design at the same hit rate | **Adequately covered in the body**, which states the blanking numbers two sentences from the certificate's 0.64. Comparing a remedy against the unremediated baseline in an abstract is standard. Recorded |
| viii | Table IV grades a 1.07 → 0.08 false-alarm swing across CNR as "P" with no detection cost given | **Deferred.** The P_d cost is not in the saved outcomes; quantifying it is a new analysis needing a frozen protocol (rule 5). Top-three item for the next round |
| ix | "in its main run" concedes other runs exist without saying what they showed | The supplement reports the independent re-check. Recorded |

## Items both reviewers deferred to a future round

1. Convert the 10⁻⁴ conformal conservatism (IN-ARCP 0.73 [0.54, 0.99]) into dB of CFAR loss
   using the Beta-ratio law the paper already derives, instead of presenting 0.73 beside 1.47
   as uniform success.
2. Test the certificate on sea clutter with a hit pattern genuinely *dominated by* but not
   equal to the calibration model, so that robustness is separated from implementation.
3. Give the detection cost of the 1.07 → 0.08 CNR swing, and the per-quintile direction
   behind the texture spreads.
4. Add intervals to the figures the abstract leans on, and note that 0.30 against 0.27 on 74
   pedestrian onsets is not a difference.

All four need new computation and therefore a frozen protocol first.
