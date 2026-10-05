# Blind pairwise review: first, then second

Recommendation: **choose second**. The second manuscript strengthens the scientific argument by measuring the delayed collapse beyond the original eight-look window and by testing, and reporting failure on, continuous migration. Its additional real-target checks remain descriptive and do not claim operational onset validation. The core contribution, mathematical presentation, and main calibration results are already mature in both manuscripts. **No change is needed to those mature parts on the evidence available here. No material defect was identified in either PDF.**

## Scope and evidence

For the original blind review, I read all 11 pages of first before opening second, then read all 11 pages of second. I also visually inspected every rendered page of both PDFs, including all figures, tables, equations, appendices, and references. After the final page-8 wording clarification, I reloaded first and then second in the same order, reread both page-8 passages, and visually checked second's updated page 8. The hashes below identify the final PDFs checked. I did not inspect an identity mapping, revision history, other manuscript sources, supplements, code, protocols, or raw outcomes. Release-tag chronology played no role in the judgment.

PDF hashes read for this review:

- first: `7218d385aa9cd618b3c0946883216018833ec8262c3e0cdb2a7da1fb45a4d504`
- second: `3cac39ba29a0f16f5a387d1679de9e25c68025742f20765b5d972b95e01ef67e`

This is a manuscript-level scientific and presentation review. Reported measurements can be checked for internal consistency and appropriate interpretation here; their reproducibility and correspondence to raw outcomes require the separate audit. Bibliographic authenticity was not independently verified.

## Scientific narrative and contribution

Both manuscripts have a clear three-part hook: recovering useful classical laws in whitened units, quantifying self-masking after target onset, and calibrating robust integration against pulsed interference. They explicitly acknowledge the one-pulse PAMF equivalence and attribute sensitivity gain to whitening rather than to conformal calibration. That prevents a familiar detector construction from being presented as wholly new. The contribution claims are concentrated on the post-onset laws, the visibility horizon, and the interference certificate, with the classical laws and split-conformal machinery properly framed as foundations (pp. 1–5).

First gives a coherent argument and openly states that its guard evidence ends at look eight (p. 8). Its discussion also warns that migration need not provide a clean reference history (p. 9). Those are appropriate limitations, not defects that require rewriting.

Second provides a more complete scientific arc. The 48-look trajectories directly address whether a guard extends visibility or solves persistence. Figure 3b and Section VI-C show the former, and the text explicitly rejects indefinite persistent-target detection. Section IV-D also distinguishes partial contamination from a fully target-filled history, supplying the corresponding history energy. The migration experiment then tests the practical concern that first could only discuss: a continuously entering range response can contaminate the reference before the target reaches its peak. The very low reported acquisition rates are useful negative evidence rather than an inconvenient result being hidden.

This added evidence does not change the paper into a demonstrated operational detector. Second says that externally timed clean onsets in correlated clutter and a measured range response remain necessary. That is the correct boundary for the evidence described.

## Calibration of assertions and limitations

Both PDFs distinguish the true-model, common-texture, zero-thermal-noise laws from empirical performance with fitted coefficients. They distinguish exchangeability-based marginal validity from the independence assumptions needed for the conditional Beta calculation. Non-overlap is explicitly said to be insufficient, and observed rate excess is linked cautiously to nonstationarity. These qualifications are substantive and adequately visible (Sections III-A, IV-F, VI-A, VII-A).

The interference certificate states clutter-independent hit positions and inclusion-order dominance rather than merely a matching hit rate. Both manuscripts explain why matched independent injected hits test implementation and cost, why bursts violate the independent-hit assumptions, and why a matched certificate can become useless for detection. The conclusion does not conceal the 10^-3 or burst-related failures.

Second handles the added evidence responsibly:

- The longer-guard gain concerns mean per-look detection on specified looks, with paired cluster intervals; it is not treated as a guarantee of sustained acquisition.
- The camera-labelled walks establish presence rather than precise native-bin radar onset; low correlation and absence of eligible primary entries are explicit.
- The migration study specifies an acquisition-level design and reports the measured null-rate imbalance. P-ANMF superiority is described as a higher point estimate, without unsupported significance language.
- The unavailable complex range response and idealized sinc injection are explicit, so the migration result supports a boundary under the tested response model, not a universal field-performance statement.

The main reported numbers agree across the abstract, results, and summary tables where the same comparison is retained. The second Table IV carefully states that the persistent-target guard comparison is now 0 to 16, whereas the ramp comparison remains 0 to 8. I found no internally contradictory numerical assertion that warrants a necessary correction.

## Notation, Table IV, and figures

The notation is usable in both versions: fitted `r` and true `rho`, onset at look zero, score versus squared score, guard length, per-look versus dwell tests, and hit versus exceedance are distinguished. The quadratic-form construction and rank-one proof are readable; I found no evident sign or dimension error in the displayed laws. This does not substitute for numerical or symbolic verification of the underlying implementation.

Table IV is usable in both PDFs. The two-column format gives the measured result beside the relevant test, and the bold phrases guide scanning without replacing quantitative evidence. Second adds two important boundaries and labels eventual self-masking directly. Its caption states design defaults and changes in guard comparison, and both captions warn that equal nominal designs can have different measured false-alarm rates. Second is a little denser, but no text is clipped or unusably crowded; it remains a good summary rather than a pass/fail scoreboard.

Figures 1 and 2 are clear in both PDFs. Figure 1 explicitly retains the latest sample as predictor input even with a guard, avoiding a potentially consequential interpretation error. Figure 2 makes the Doppler-dependent horizon and interference calibration behavior visible. First Figure 3b is effective for its short Doppler comparison. Second Figure 3b is more persuasive for the persistence claim: separate guard curves, measured versus model lines, and uncertainty bands show the delayed collapse and subsequent low sensitivity. The full 48-look axis is justified by that scientific purpose. No figure redesign is necessary.

## Abstract and optional editorial choices

First's abstract already delivers the mechanism, numerical calibration advantage, guard effect, and certificate limitations. Second retains that impact and adds the two most consequential findings: measured delayed collapse and poor migration detection. The abstract is dense in both; reducing its numerical load would be an author choice, not a scientific correction.

An optional precision edit in second would change “Measured trajectories” to “Injected-target trajectories” in the abstract, making the source of that evidence explicit in the same sentence. The body and Figure 3 caption already establish it, so the present wording is not a material overclaim. Likewise, first's explicit description of hashed protocols as internal records is useful transparency; retaining those few words in second would be optional because second does not claim an external registry and refers readers to the supplement for exposure and deviations.

## Final judgment

The final second-PDF clarification names the relevant long-dwell statistic and result directly: at 1,024 pulses, P-ANMF has a measured false-alarm rate of 2.6 times design. The surrounding text retains the descriptive status of the literature comparison because training and evaluation protocols differ, and states that the i.i.d. Beta law cannot guarantee control for these non-exchangeable windows. This is precise and renders cleanly; it removes an avoidable ambiguity without changing the result or the scientific conclusion. Both final PDFs remain 11 pages.

Choose second for its stronger measurement of the central guard mechanism and its more concrete operating boundaries. This is a substantive evidence improvement, with only a modest increase in presentation density. First remains scientifically coherent; the preference does not rest on manufacturing a defect in it. No mandatory manuscript correction follows from this blind PDF comparison. Raw-outcome verification remains separate.
