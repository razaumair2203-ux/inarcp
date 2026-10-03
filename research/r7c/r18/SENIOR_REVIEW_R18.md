# Senior-reviewer audit of R17 against the 2026 body of knowledge

**Date:** 3 October 2026. **Subject:** `03_submission_IEEE-TRS/` at R17 (10 pages, 31-page supplement, tag `r17-trs-submission`).
**Posture:** adversarial. The reviewer assumed the paper is wrong until the saved outcomes said otherwise, and assumed every earlier audit had missed something.
**Target venue:** IEEE Transactions on Radar Systems, regular paper, single-anonymous review, minimum two reviewers, two-level prescreen.

## What this audit is not

It is not another prose round. R13–R17 already fixed prose, evidence levels, process leakage and the real-onset gap. Re-running those checks would be the regression that `CLAUDE.md` was written to stop. This audit asks one question only:

> **Which sentences, omissions or framings in R17 would cause a competent T-RS reviewer to ask for major revision or to reject, given what the field knows in 2026?**

Everything below is either a defect in the paper or a missing statement whose absence a reviewer will read as evasion. Items that are merely improvable are marked as such and were left alone.

## Method

1. Read the manuscript and supplement end to end as a radar reviewer, not as an editor.
2. For every quantitative claim, open the saved outcome file and check the number, the condition it was measured under, and the window it was averaged over.
3. Check the theory by hand: Propositions 1–4, Corollaries 1–4, Theorem 1 (eigenvalue inertia, the exponential-mixture identity, the monotonicity of `W`, the bound `T∞ ≤ √(m/(m−1))`).
4. Search the 2024–2026 literature for what a reviewer would demand as comparison or citation.
5. Compare the paper's own numbers against each other across sections, abstract, tables and conclusion.
6. Check the formal requirements of T-RS and of the two fallback venues.

Theory check result: **no error found.** The inertia argument in Appendix A is correct (Weyl plus Sylvester; `e_{m+1}^H M_q e_{m+1} = 1 > 0`), the mixture identity holds at any multiplicity, `b̄bᵀ` is Hermitian and rank one so `|bᵀX|² = |Y − aᵀH|²` as claimed, the OS law reduces to Rohling's, and `T∞² = mu/{(1−|r|²)+(m−1)u}` is increasing in `u = |1−re^{−jω}|²` with supremum `m/(m−1)`, so the bound and the `P_d → 0` conclusion are right. Numbers check result: **no arithmetic error found** in the macro-generated values; one hand-typed number (F9) and two documentation inconsistencies (F11) were found.

---

# Findings

Ordered by effect on acceptance. "Validated" means the reviewer opened the saved outcome and reproduced the reading.

---

## F1 — HIGH. The paper withholds its own matched comparison with the literature that dominates this benchmark

**The defect.** Section V-C ends:

> *Learned detectors report P_d = 0.91 at P_fa = 10⁻³ on IPIX with 1.024-s observations and a different evaluation [23].*

That is the only engagement with the 2024–2026 IPIX literature, and it quotes the competitor's number without the paper's own number at the same conditions. A reviewer who works on sea-clutter detection reads this as the authors declining to be compared.

**Why it matters in 2026.** The feature-based and learned sea-clutter detectors are the active line on this benchmark, and they report P_d ≈ 0.90 at P_fa = 10⁻³ with 0.512–1.024 s observations on these same 14 IPIX files. Any reviewer drawn from that community will ask the question in round one. Left unanswered, the paper's own target-cell numbers (P_d 0.22 over 8 pulses, 0.40 over 256) look like a 50-point deficit.

**What the repository already contains.** The comparison was *pre-specified*. `research/r7c/r12/PROTOCOL_R12.md:136`:

> **T4.** Descriptive: mean P-ANMF Pd at N = 1024, alpha = 1e-3, for comparison with long-observation detectors in the literature (no decision rule).

And the outcome, `supplement/data/r12_summary.txt:127,148`:

```
P-ANMF   conf  N=1024  Pd 0.409 (Pfa 0.0026)  [Pd 0.581]
T4 descriptive: P-ANMF N=1024 mean Pd at 1e-3: 0.409
```

**Validated.** 1024 pulses at the IPIX 1 kHz pulse repetition frequency is 1.024 s — exactly the literature's observation length. The paper's unsupervised, conformally thresholded detector reaches **P_d = 0.41 at a measured false-alarm rate of 2.6 × 10⁻³**, against the literature's 0.91 at 10⁻³.

**Assessment.** The gap is real and it is not a defect in the method. The three differences are substantive and all favour the learned detectors in a head-to-head on this dataset: they are *supervised on the same target in the same campaign*, so they learn that target's signature; their "controlled false-alarm rate" is an empirical operating point on the same recordings, with no finite-sample guarantee; and the paper's statistic is given no target training at all. The paper already states "We do not claim a more sensitive detector", so reporting the number is consistent with its own thesis and costs nothing except the appearance of caution.

**Remedy.** Replace the bare quotation with the matched pair and the reason it is not a like-for-like contest. Pre-specified, so not post hoc.

---

## F2 — HIGH. The condition under which the per-look onset gain exists is never stated, and the paper's own two measurements sit on opposite sides of it

**The defect.** The whitening gain requires the clutter to be correlated *at the look interval*. The paper measures that correlation on all three radars and reports the three values in three different sections, never together and never as a condition:

| Radar | Look interval | Measured correlation | Gain over power detection |
|---|---|---|---|
| IPIX, X-band | 1 ms (1 kHz PRF) | `\IpixAbsRMed` = 0.96 median | 7.0 dB over CA16, 10.6 dB over power OS |
| NetRAD, S-band | 1 ms (1 kHz PRF) | `\NetAbsRMin`–`\NetAbsRMax` = 0.97–0.98, at or near the 0.98 clamp | ≥ 12 dB over power OS |
| JKU, 77 GHz | 200 ms (frame rate) | `\PedR` = 0.12 median | none: 0.30 against 0.27 for a power clutter map |

**Why it matters.** A reviewer will put those rows side by side and ask the obvious question: the regime where the gain is large is pulse-to-pulse at 1 kHz, where a real target rarely *appears* within a 16-pulse history; the regime where onsets are physically common is scan-to-scan, where the paper's own measurement shows the clutter is nearly white and the gain is gone. Stated that baldly, it reads as a method that works where it is not needed. This is the single strongest objection available against the paper, and R17 supplied the evidence for it without joining it up.

**Validated.** Both halves are in the paper. `\PedR` = 0.12 and the parity result 0.30 vs 0.27 are in Section V-B; `\IpixAbsRMed` = 0.96 is in Section V-E; the NetRAD clamp sentence is in Section V-E. The R17 round record shows the parity was *predicted in advance* from Proposition 2 (protocol §4, "What theory predicts here"), so the paper understands the mechanism — it simply never states the envelope.

**Assessment, and why this is a strengthening rather than a wound.** Three facts, all already in the paper, close the objection:

1. **The horizon has a duration, and the paper never converts it.** At `m = 16`, `α = 10⁻²`, `m/q² = 3.0`, so `ℓ* < 4` looks and with `Δ = 8` the guarded horizon is about 12 looks. That is **about 12 ms at a 1 kHz pulse repetition frequency and about 2.4 s at a 5 Hz frame rate.** A reader cannot judge the result without that conversion, and the two numbers differ by a factor of 200.
2. **A radially moving target re-onsets in every range cell it enters.** Residence in one 15 m IPIX cell is `15/v` seconds, i.e. `15000/v` looks at 1 kHz. The detector gets its 12 looks on entry and is masked for the remainder, then the target crosses into the next cell and the history there is clean. So the per-look screen is, in effect, a detector of **range-cell transitions**, which is why it is sensitive to radially moving targets and blind both at the clutter Doppler and to targets parked in a cell.
3. **The look interval is therefore a design parameter with two opposing requirements**: long enough that onsets recur often relative to cell-crossing time, short enough that the clutter is still correlated at that lag. The paper's two datasets are the two extremes. Nothing in the paper tells a designer to measure `|r|` at the candidate look interval before choosing it — which is the one piece of advice that follows from all of this.

**Remedy.** Two sentences in Section VI-A converting the horizon to time and naming the condition, plus the measurement advice in design rule 1. Derived from quantities already in the paper (cell width, PRF, `ℓ*`, `Δ`); generated by `make_r18_outputs.py`; **no new empirical outcome is computed**, so `CLAUDE.md` rule 5 does not bite.

---

## F3 — MEDIUM-HIGH. The statistic the paper recommends for persistent targets is not constant-false-alarm-rate across clutter power, and the paper does not say so

**The defect.** Design rule 1 and Section V-C point the reader to the self-normalized whitened Doppler statistic (P-ANMF) for targets present throughout the history, because Proposition 3 rules out history normalization there. The paper reports that statistic's *pooled* false-alarm compliance (1.04 at 10⁻², 1.47 at 10⁻⁴) and never reports its behaviour across clutter power.

**Validated.** `supplement/data/r12_summary.txt`, Part L, texture-quintile spread (max/min of the measured false-alarm rate over quintiles of local clutter power):

| Statistic, conformal threshold | α = 10⁻² | α = 10⁻³ | α = 10⁻⁴ |
|---|---|---|---|
| IN-ARCP | 1.3 | 1.5 | 2.7 |
| CA16 power ratio | 1.1 | 1.1 | 1.3 |
| **P-ANMF, max over bins** | **4.4** | **9.9** | **23.2** |

So at 10⁻⁴ the recommended remedy's false-alarm rate varies 23-fold across quintiles of clutter power while its pooled rate looks compliant at 1.47. "Constant false alarm rate" is the property the whole paper is about; the statistic it recommends for the hardest case does not have it.

**Assessment.** This is not a contradiction of the theory — it is Corollary 2 operating on the statistic the paper recommends. The P-ANMF score is scale-invariant and therefore texture-pivotal in *pure* compound-Gaussian clutter, but with thermal noise the clutter-to-noise ratio varies across cells and the invariance is lost, which is exactly what Corollary 2 says and exactly what Section V-A already demonstrates for IN-ARCP on the 77 GHz data. The paper has the explanation and omits the observation. A reviewer who finds the number in the supplement will conclude the authors looked away.

**Remedy.** Report the spread in Section V-C and qualify design rule 1. One sentence and three numbers.

---

## F4 — MEDIUM. Why the model-based laws fail is asserted for two statistics and left open for the other nine, although the saved outcomes separate the mechanisms

**The defect.** Section V-A establishes the paper's central negative result — ten of eleven model-based laws exceed twice design at 10⁻⁴, by up to 60-fold — and offers a mechanism for only two cases: the residual bootstrap (innovation dependence) and the Kraut–Scharf law (fails even in simulated compound-Gaussian clutter, so not the tails). For the order-statistic law at 46-fold and Fisher's `g` at 50-fold, the paper says nothing. A reviewer will not accept a 60-fold failure as an unexplained empirical fact.

**Validated.** The same Part L table carries the diagnostic, in the texture-quintile spread of the *model-based* rules. At α = 10⁻³, where the per-quintile counts are large enough to trust:

| Model-based rule | P_fa/α | Texture-quintile spread |
|---|---|---|
| IN-ARCP, CA law | 1.02 | 1.4 |
| ANMF-SCM, Kraut–Scharf | 3.57 | 2.0 |
| ANMF-Tyler, fixed-point | 2.66 | 2.2 |
| **OS scale, OS law** | **8.34** | **4.0** |
| **P-ANMF max, Fisher's g** | **13.06** | **4.5** |
| Clipped, Gaussian simulation | 17.19 | 1.3 |

Two distinct mechanisms, cleanly separated: the order-statistic and maximum-DFT laws fail **where the clutter is strongest** (spread 4.0 and 4.5), while the clipped integrator's simulated threshold and the ANMF laws fail **nearly uniformly across clutter power** (1.3, 2.0, 2.2) — consistent with the paper's existing statement that Kraut–Scharf already fails 2.8–3.4-fold in simulated compound-Gaussian clutter.

**Assessment.** This converts the paper's biggest negative result from a measurement into an explanation, at a cost of two clauses, and it does not disturb any existing sentence. It also pre-empts the reviewer question "is this just the K-distribution tail?" with a measured answer: for two laws yes, for the others no.

**Remedy.** Two clauses in Section V-A, with a new macro.

---

## F5 — MEDIUM. The guard's headline number is measured only inside the window where the guard must help, and the paper does not state the window

**The defect.** The abstract and Section V-D give the guard's effect as a mean per-look detection probability rising from 0.24 to 0.82 for an injected persistent 10 dB target. The mean is over looks 1–8 and the guard is `Δ = 8` pulses, so the averaging window and the guard length are the same number. A reader naturally infers a durable gain; the mechanism gives a gain for exactly `Δ` looks.

**Validated.** `supplement/data/r14_summary.txt:11–19`, per-look P_d at 10 dB, looks 0 through 8:

```
random   g= 0: 0.88 0.71 0.64 0.50 0.08 0.01 0.00 0.00 0.00 | mean looks1-8 0.24
random   g= 8: 0.87 0.82 0.82 0.82 0.82 0.82 0.82 0.82 0.82 | mean looks1-8 0.82
random   g=16: 0.87 0.82 0.82 0.82 0.82 0.82 0.82 0.82 0.82 | mean looks1-8 0.82
```

Two readings follow. First, the measurement **stops at look 8**, so the post-guard decay that Corollary 4 predicts (horizon `Δ + ℓ*`) is predicted but not measured. Second, `Δ = 16` gives an identical 0.82 over the same window, so the window cannot distinguish the two guard lengths — the choice `Δ = 8` rests on its smaller onset cost (0.9 dB against 1.3 dB), which the paper does not say either.

**Assessment.** Not an overclaim: the Discussion already carries "A guard extends the horizon by only `Δ` looks", and the Conclusion already says "over the eight guarded looks". But the abstract and Section V-D give the number without its window, and the two sections that qualify it are pages away. A reviewer checking the figure will ask what happens at look 9. The honest answer — equation (6) at `ℓ − Δ`, not measured — should be in the sentence that states the number.

**Remedy.** Name the window where the number first appears, in the abstract and in Section V-D, word-neutral in the abstract. Add the `Δ = 8` versus `Δ = 16` justification in one clause.

---

## F6 — MEDIUM. Non-exchangeability is named as the paper's principal validity caveat, and the literature that quantifies it is in the bibliography but uncited

**The defect.** The paper's own evidence that exchangeability fails is in Section V-A — the one-bin P-ANMF runs at 1.10 [1.01, 1.19] times design at 10⁻², and the paper says this "exceed[s] sampling noise and suggest[s] that the calibration and test thirds of a session are not exactly exchangeable". The Discussion repeats that conformal validity "needs exchangeable calibration and test episodes, which holds only approximately within a session". Neither place cites any of the work that bounds what happens when exchangeability fails.

**Validated.** Both of the right citations are already in `references.bib` and absent from `main.bbl`:

- `barber2023` — Barber, Candès, Ramdas and Tibshirani, "Conformal prediction beyond exchangeability", *Ann. Statist.* 51(2), 2023. Bounds the coverage gap by a weighted total-variation term, which is exactly the quantity the paper's caveat leaves unbounded.
- `greco2010` — Greco, Stinco, Gini and Rangaswamy, "Impact of sea clutter nonstationarity on disturbance covariance matrix estimation and CFAR detector performance", *IEEE Trans. Aerosp. Electron. Syst.* 46(3), 2010. The radar-domain statement of the same problem, in the venue's own literature.

**Assessment.** A conformal-literate reviewer will notice the omission immediately and will read it as unfamiliarity with the field the paper borrows from. A radar reviewer will notice that the non-stationarity of sea clutter — a staple of this journal's literature — is treated as a novel caveat. Both are cheap to fix and both are credibility signals. `gibbs2021aci` (adaptive conformal inference) is cited in the supplement's baselines only; that is acceptable, since the paper's contamination result on gated ACI lives there.

**Remedy.** Cite both at the two sentences, with one clause saying what the non-exchangeable bound would require.

---

## F7 — MEDIUM. No cost, memory or deployment statement, in a journal that publishes radar *systems*

**The defect.** The paper claims the detector "takes the place of the range CFAR stage after range processing" (Fig. 1 caption) and gives three design rules, with no statement of arithmetic per cell, state per cell, or how much clean data a threshold needs. For T-RS this is a predictable prescreen and review question.

**It also under-sells the operational payoff.** The reason innovation normalization is worth the trouble operationally is that the score is pivotal, so **one threshold serves every range cell** — whereas a range CFAR re-derives its level from the neighbours of each cell and a clutter map stores a level per cell. The paper proves the pivotality, measures it (texture spread 1.3 at 10⁻², against 87.5 unnormalized and 9.8 for raw-RMS normalization) and never says what it buys.

**Validated, by derivation from the paper's own definitions.**
- Arithmetic: AR(`p`) whitening is `p` complex multiply-accumulates per cell per pulse; the scale is a sliding sum of `m` innovation powers (one add, one subtract, one magnitude-squared); the test is one comparison. So `O(p)` complex and `O(1)` real operations per cell per pulse — the same order as a sliding-window range CFAR.
- State: `m + Δ + p` complex samples per range cell — 25 words at `m = 16`, `Δ = 8`, `p = 1` — which range CFAR does not need and a clutter map does.
- Calibration: the paper's own rule is `≈ 3.15/α` episodes, i.e. about 31,500 at `α = 10⁻⁴`. Non-overlapping 17-pulse episodes over the 14 IPIX range cells make that **about 38 s of clean recording at 1 kHz**, and one scalar threshold per statistic to store.

**Assessment.** The three numbers above are arithmetic on quantities the paper already states. They turn an unanswered question into a short design rule and surface a strength that is currently buried in a texture-spread table.

**Remedy.** Extend design rule 2 with the state and calibration-data numbers; one clause on the single threshold.

---

## F8 — LOW-MEDIUM. The paper derives the CFAR loss and never calls it that

**The defect.** The supplement derives the expected detection probability under a conformally calibrated threshold as a ratio of Beta functions with exponent `γ = 1/(1+S)`, and Section IV-F points to it. That quantity is the **CFAR loss**, the standard figure of merit of this community, and the term appears nowhere in the paper. `watts2007cfarloss` is in the bibliography and uncited.

**Assessment.** Purely a vocabulary gap, but it is the vocabulary the reviewers use. Naming it connects the paper's calibration-size result to the literature a radar reviewer reads, and it costs six words and one reference.

**Remedy.** Name it in Section IV-F and cite `watts2007cfarloss`.

---

## F9 — LOW. One hand-typed result number, in breach of `CLAUDE.md` rule 4

`main.tex:280`: "both exceed their thresholds on the target cell at a rate of 0.0004 at `α = 10⁻³`". Not a macro. **Value verified correct** against `supplement/data/r12_summary.txt:146` (`IN1 Pd 0.0004`, `Clip-OS1 Pd 0.0004`). Every other result number in the body is macro-generated. **Remedy:** macro-ise.

---

## F10 — LOW. The supplement cites two sources by author name with no reference list

`supplement.tex` carries "Dewolf et al. report that estimated taxonomies mix up the true classes" and "Brockwell and Davis, *Time Series: Theory and Methods*, 1991" as inline prose. `dewolf2025` and `brockwell1991` are both in `references.bib`. A supplement submitted for peer review with an uncited attributed claim is an avoidable editorial flag. **Remedy:** give the supplement a short reference list. No page cost — the supplement has no limit.

---

## F11 — LOW, process. Top-level documentation still describes R16, and `_TO_DELETE/` is still in the tree

- Root `README.md` opens "➜ The latest paper is R16" and points at `INARCP_R16_manuscript_Overleaf.zip`, which no longer exists; the live Overleaf ZIPs are R17.
- The change log is still named `R16_CHANGES.md` at R17.
- `_TO_DELETE/` (12 directories of virtual environments, caches and LaTeX intermediates) is still at the root.

This is the drift that `CLAUDE.md` rule 10 exists to prevent, and the root README is the first thing any reader — including the next agent — opens. **Remedy:** rewrite the root README, rename the change log, archive the rest.

---

## F12 — LOW, accepted. Figure height

Figures 2 and 3 are 7.16 × 1.75 in and 7.16 × 1.6 in, at 8 pt axis labels and 6.3–6.8 pt legends. Legible — the R16 problem of 3–4 pt text is gone — but cramped for six-method detection curves. **Deliberately not changed.** Enlarging them costs page 11 and US$200, and `CLAUDE.md` rule 1 caps the paper at 10 pages. Recorded so the decision is visible, and listed as the first thing to spend a page on if the authors choose to pay for one.

---

# Checked and found sound — no action

These were examined because they are the obvious places for a paper like this to be wrong. They are not defects, and this section exists so that a later round does not re-open them.

| Checked | Verdict |
|---|---|
| **Abstract length** | 249 words against a 250 limit. The project's `metrics.py` reports 254 because it counts PDF line-break hyphenation artifacts ("in- dependent", "non- coherent") as separate tokens; rejoining them gives 249. Compliant, with **one word of headroom** — a hard constraint on any abstract edit. |
| **Propositions 1–4, Corollaries 1–4, Theorem 1** | Re-derived by hand. No error. Details at the head of this document. |
| **Unit independence** | 56 units = 14 sessions × 2 like-polarized channels × 2 third-assignments. Assignments 2 and 3 put different thirds in the test role, so **no test episode is used twice**, and pooling across units does not double-count. Dependence across channels and assignments is handled by the six-day cluster bootstrap, whose approximateness the paper states. Sound. |
| **"12 of 13 within 0.73–1.47" at 10⁻⁴** | Point estimates, as the table caption says; the widest interval (P-ANMF max, [0.75, 2.57]) is in the supplement. Honest, and the paper gives IN-ARCP's interval in the text. |
| **"10 of 11 model-based laws"** | Recounted: nine whitened statistics plus two ANMF laws; all fail except IN-ARCP's CA law at 1.92. Maximum 59.89 → "up to 60-fold". Correct. |
| **"53 outcomes, 13 not met, 4 without a verdict"** | Recounted across R12 (12/18), R14 (12/15), R15 (12/15), R17 (0/5 with 1 not met and 4 undecided): 53 = 36 + 13 + 4. Correct. |
| **Novelty against the 2026 conformal-radar literature** | Searched. Conformal prediction has been applied to railway-signal and runway *object* detection and to wireless-model calibration, not to CFAR thresholds on measured sea clutter. The niche is genuinely unoccupied; no priority problem. |
| **Build quality** | 10 pages, zero overfull boxes, zero undefined references, two mild underfull boxes (cosmetic). Supplement 31 pages, clean. |
| **T-RS formal compliance** | IEEEtran journal template; no page limit but US$200/page past 10, so 10 pages is a cost decision, not a requirement; single-anonymous; AI disclosure in the Acknowledgment naming the system and the affected sections — present and correct; "new"/"novel" absent from title and abstract. |
| **Squeeze hacks** | Nine, all ordinary IEEE table formatting (`\footnotesize`, `\scriptsize`, `tabcolsep`). No `\vspace{-}`, no `\resizebox` in the main text. Clean. |

---

# Objections a reviewer will raise that have no remedy available

These are not defects; they are the honest limits of the evidence. The paper already states all three. They are listed so the authors can answer them in a response letter without inventing anything.

1. **No real target with a real onset at sea.** `04_reviews/2026-10-02_R14-R15.../DATASETS_SCOUTED.md` and `ROUND_R17.md` record the search: SDRDSP is geoblocked from Pakistan and the IEEE DataPort copy lists no files; CSIR small-boat access is by request and the page 404s; the NetRAD release's trial log names a target recording ("the 14.42 files") that is not in the release; the IPIX targets are present throughout. The one real onset obtainable was the JKU walking person, and it was used. **Answer to give:** the search is documented, the gap is stated in the paper, and the required campaign is named in the Conclusion.
2. **Two sea-clutter campaigns, one interference campaign, all open data.** No in-house measurements. **Answer to give:** NetRAD was evaluated untouched under a protocol frozen before any statistic was computed, which is stronger than most single-campaign papers offer.
3. **Several laws are classical laws with a whitened signal-to-clutter ratio.** **Answer to give:** the contributions list already says so and names the three results that are new — the post-onset law with its horizon and guard, the OS law under persistence, and Theorem 1.

---

# Venue note

T-RS remains the right primary venue, and the page position is better than the package documentation assumed: **there is no page limit, only a US$200 per page overlength charge beyond ten printed pages.** The 10-page cap is therefore a cost decision the authors can revisit, not a rule. If one page were bought, F12 (figure height) is the first thing to spend it on.

Fallbacks, with 2026 facts checked:

| Venue | Length | Review | Cost | Note |
|---|---|---|---|---|
| **IEEE T-RS** (primary) | no limit; US$200/page past 10 | single-anonymous | traditional free; optional OA US$2,645 | AI disclosure in Acknowledgment, naming system and sections |
| **IEEE TAES** | no limit; US$200/page past 10 | single-anonymous | traditional free | Same scope and same AI policy. Template-compatible: IEEEtran two-column, 10 pt. Lowest-friction fallback. |
| **IET Radar, Sonar & Navigation** | no stated word limit | single-anonymous | **fully open access, APC US$2,600** (15% IET-member discount; waiver list by country) | Requires a graphical-abstract / contents entry of ≤ 80 words plus a representative figure, and a data-availability statement. The APC is mandatory, which materially changes the ranking against two free venues. |

---

# What was changed in R18, and what was deliberately not

**Implemented in the manuscript:** F1, F2, F3, F4, F5, F6, F7, F8, F9.
**Implemented in the supplement:** F2 (full arithmetic), F3, F10.
**Implemented in the repository:** F11.
**Recorded and not changed:** F12, and the three unanswerable objections.

Every main-text addition was paid for by a cut of at least equal size, as `CLAUDE.md` rule 1 requires; the cuts and the page/metric outcome are in `ROUND_R18.md`.
