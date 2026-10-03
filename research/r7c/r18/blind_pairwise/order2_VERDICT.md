# Blind pairwise review, order 2 (A = R18, B = R17)

**Reviewer did not know which was which.** Reported P(B better) = 0.30, i.e.
**P(R18 better) = 0.70.**

## It found no arithmetic or internal-consistency error in either version

It independently re-derived and confirmed: ℓ* = 1 + 3.0 − 1/1.93² = 3.73 at the opposite
Doppler; m/q² = 3.0 at m = 16 and P_fa = 0.01; K_eff = 64/45.3 = 1.41; T∞ ≤ √(16/15) = 1.033
against q̂ = 2.31; and the R18 arithmetic: 11.7 looks → 12 ms at 1 kHz, 2.3 s at 200 ms
frames, and 11.7/1500 = 0.8%. Its closing words: "I found **no arithmetic or
internal-consistency error** in either version. The problems are all claim-framing problems."

## FAIL it found in R18 — accepted, and it is one R18 introduced

**The abstract word-saving cut broke a true sentence.** To pay for naming the guard's
averaging window, R18 had shortened

> "the guard and the **injected-interference** certificate behave as on IPIX"  (R17)

to

> "the guard and the certificate behave as on IPIX"  (R18)

The reviewer: *"False as written. On NetRAD the only certificate test against the radar's own
anomalous pulses is reported by A itself as vacuous: Table III ... and Table IV grades it
'NetRAD flagged pulses, certified — F — P_d 0.04'. A certificate that detects nothing does
not 'behave as on IPIX'."*

Correct, and exactly the failure mode `CLAUDE.md` was written against — "local fixes left the
abstract out of step with the tables". The qualifier is restored in R18.1 and paid for
elsewhere in the abstract.

## WEAK items in R18 text — all accepted and fixed in R18.1

| Item | Reviewer's objection | Fix |
|---|---|---|
| "ours on neither" | IN-ARCP's threshold *is* an empirical quantile; the real distinction is the finite-sample law, so the sentence claims something flattering the method does not have | Rewritten to claim only the finite-sample law |
| "so Δ = 8 is the cheaper choice" | The window is looks 1–8, the interval most favourable to Δ = 8 and least informative about Δ = 16, and the preference is not labelled as resting on it | Rewritten: the looks measured "do not favour the longer guard" |
| "about 38 s of clean recording" | 3.15/α is the i.i.d. bound, which the paper itself calls a lower bound under dependence; the memorable number is the optimistic one | "at least about 38 s" |
| "one threshold for every cell" | Reads as the opposite of what is meant (one *per* cell rather than one *shared*), and the cost omits ranking the calibration scores | "one threshold shared by all cells ... the calibration scores are ranked once, offline" |
| "over its eight guarded looks from 0.24 to 0.82" | The 0.24 baseline is measured *without* a guard, so those looks are not guarded looks | "over the first eight looks after onset" — correct for both arms, same length |

## Shared objections, pre-existing in both versions

Recorded, not all actionable in this round.

| # | Objection | Disposition |
|---|---|---|
| S4 | "The Gaussian threshold of IN-ARCP gives the same sensitivity at a similar false-alarm rate" is true at α = 10⁻² and misleading as a general statement, since the same law runs at 1.92× design at 10⁻⁴ | **Fixed in R18.1**: the design rate is now stated |
| S5 | IN-ARCP conformal at 10⁻⁴ is 0.73 [0.54, 0.99] — significantly *below* design, a real CFAR loss never converted into dB, while the abstract presents the 0.73–1.47 band as a success | **Accepted, deferred.** Converting it needs a new computation, which `CLAUDE.md` rule 5 requires a frozen protocol for. It is the top item for the next round, recorded in `ROUND_R18.md` |
| S1 | The abstract's "certifies ... of any power" lists the theorem's extra conditions but not exchangeability, which the Results measure failing at 10⁻² | **Known, deliberate.** The abstract is at 249 of 250 words; "conformal threshold" carries the exchangeability setting, and Theorem 1 and the Discussion state it explicitly. Recorded rather than changed |
| S2 | The certificate's independent evidence is one favourable case (77 GHz sparse) against three failures (77 GHz dense, NetRAD flagged pulses, bursts) | The abstract carries "Injected bursts defeat every remedy tested", Table IV grades all four, and the body says the IPIX injected hits "check the implementation and the cost, not robustness". Adequate once the A1 qualifier is restored |
| S3 | "the sensitivity comes from whitening, not from the order statistic" changes two things at once; the whitened-OS arm exists in Table I and is not invoked | Accepted; a precise fix needs the whitened-OS first-look number, which is a new extraction. Deferred with S5 |
| S6 | "12 of 13 within 0.73–1.47" and "5 of 13 above twice design" are selected-extremum statements over 13 statistics × 3 rates × 2 datasets with no selection accounting | Structural; the intervals are in the supplement and the direction reverses between datasets, which the paper states. Recorded |

## Differences the reviewer credited to R18

Decisively: the learned-detector comparison ("A improves, decisively ... B is evasive; A is
self-damaging and credible"), and the operating-regime budget ("this is the paper's central
operational limitation, quantified by the authors against their own interest, and it answers
the question every radar reviewer will ask"). Substantially: the texture-spread caveat
against the paper's own fallback statistic ("B moves it to the Supplement, which is burying
it"). Also credited: the two-mechanism explanation of the model-law failures, the
non-exchangeability citations, "Only the first eight looks were measured", naming the CFAR
loss, the look-interval design rule, and the enlarged figures' tick labelling.
