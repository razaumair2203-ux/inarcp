# Submission package: IEEE Transactions on Radar Systems (Regular Paper), R11

Updated 30 Sep 2026, R10. This revision answers the external review of R9; every point was checked against the source (see the session record).

## R11 additions (30 Sep 2026, after a 2026 novelty check)
- **Order-statistic innovation normalization** (Corollary 3: the OS-CFAR law read as coverage), tested under the frozen `research/r7c/r11/PROTOCOL_R11.md`. Results are in `RESULTS_R11.md`: 2 of 11 expectations met.
  - **Kept:** it removes post-onset blindness for exactly m − k looks, as counted. At 10 dB, per-look Pd is 0.65–0.80 over 8 looks, against 0.002 for IN-ARCP. The cost is 2.0 dB (k = 8) or 0.3 dB (k = 12).
  - **Reported as negative:** it does not fix gradual emergence, the dwell, or real interference.
- **Real automotive interference** (JKU runs A and C): every per-cell normalization is masked by 5 dB. Fast-time zeroing restores sensitivity, and the conformal false-alarm rate holds at design after zeroing.
- **Not built:** an ACI corrupted-feedback remedy, because 2026 work exists (Wang–Zecchin–Simeone; Balachandran). It is cited instead.
- **Length:** the manuscript is now 12 pages (+US$400 at T-RS), and the abstract is 249 words.

## R10 changes relative to R9
- **New frozen study** (`research/r7c/r10/PROTOCOL_R10.md`, results in `RESULTS_R10.md`) with three parts:
  - classical detectors (PAMF-H, NPAMF, MTD-CA) at equal dwell Pfa;
  - gradual target emergence;
  - ACI under target contamination.
  - Three expectations failed (C2, A2, and R1's scripted check); all are reported.
- **Reframed** (new title): the disc's exceedance is a PAMF test with a calibrated threshold.
  - The classical PAMF matches its sensitivity, and gradual emergence defeats the per-look screen.
  - The paper claims an analysable, calibrated formulation, not a better detector.
- **Claims corrected:**
  - MAE instead of "within";
  - the second radar is reported on the false-alarm scale (1.07 to 0.08 times design);
  - "two radars" CFAR claim removed;
  - blindness limited to IN-ARCP;
  - "only conformal" removed;
  - the post-hoc JKU gain form is labelled as such;
  - "confirmatory" relabelled as a frozen-protocol evaluation, with a data-exposure table in the supplement.
- **Assumptions stated:**
  - the |r| ≤ 0.98 clamp (binding in 5/56 units);
  - Q ⪰ 0 in Prop. 1 (Weyl argument);
  - i.i.d. condition for the Beta law;
  - Mondrian bin edges estimated from the calibration sample;
  - the 999-score resolution limit at α = 0.001.
- **Robustness audit** (`r10/audit_existing.txt`):
  - exceedance dependence and a dependence-aware reference;
  - leave-one-day-out ranges;
  - per-day spread (3.5–13.8 dB);
  - NA-AR(4) convergence: 16/56 at the cap, with results insensitive to it (`na4_convergence.txt`).
- **Proofs of Props. 2 and 5 moved to the supplement** for length. The manuscript is 11 pages; the 11th page costs US$200 at T-RS.
- **SDRDSP:** the protocol was frozen before the data were obtained (`research/r7c/sdrdsp/PROTOCOL_SDRDSP.md`).
  - If the data do not arrive before submission, delete the "SDRDSP (pending)" row of the supplement's data-exposure table.

- **Primary target:** IEEE T-RS.
  - Guidelines: https://ieee-trs.org/author-information
  - Submit at https://ieee.atyponrex.com/journal/tradar-ieee
- **Backup:** IET Radar, Sonar & Navigation. It accepts free-format first submissions, so the same PDF works; use `declarations.md` for the IET statements.

## R8 history (kept for the record; its wording is superseded by the R10 corrections above)

| Addition | Evidence |
|---|---|
| **Detection of newly appearing targets.** Exact detection probability (Corollary 2); closed-form noise-limited whitening gains (Proposition 2); persistent-target blindness (Proposition 3) | Monte Carlo agreement to 3 decimals and 0.02 dB (`theory_checks_output.txt`) |
| **Real-data detection on IPIX.** Targets injected into 74,980 real test episodes, under a protocol frozen beforehand | Pfa at design (0.0099); +7.0 dB vs same-pulse power CFAR and +9.8 dB vs local power CFAR; exact law MAE 0.021. The noise-aware model adds 1–2 dB, and its plug-in breaks the Pfa budget. |
| **Second radar.** JKU 77 GHz FMCW, open data, 1.32 M episodes | Exact law predicts CNR-conditional coverage within 0.010; predicted loss in noise-dominated cells observed; unnormalized CP collapses (0.97 → 0.02) |
| **Reviewer baselines.** ACI (online) and a parametric K-texture ablation | ACI raises the worst transfer day 0.882 → 0.897 at no width cost. K-texture discs are 0.9% wider than NPMLE ones, with the same coverage. |
| **Negative results kept** | NA's CNR-flatness is only partial on static ground clutter; NA transfers worse across measurements than IN-ARCP; the magnitude of the J3 gain is not captured by the matched closed form |

All new numbers are LaTeX macros generated from saved outcomes (`analysis_provenance/make_r8_macros.py`). The four protocols and results sit in the repo under `research/r7c/{detection,baselines,jku}/`:
- `PROTOCOL_*.md` with its `.sha256`
- `RESULTS_*.md`

## Contents
| Path | What |
|---|---|
| `manuscript/main.pdf` | **Upload this.** 10 pages, IEEEtran journal, clean build (0 warnings), 241-word abstract |
| `manuscript/main.tex`, `references.bib`, `generated/`, `figures/` | Source. Build with pdflatex, bibtex, pdflatex, pdflatex. |
| `supplement/supplement.pdf` | **Upload as supplementary material** (7 pages): synthetic figure, Prop. 4 sketch, day-transfer table, hold-out, onset/dwell/theory tables, full result tables |
| `cover_letter_TRS.md` | Cover letter, updated for R9 |
| `declarations.md` | Data/code availability, conflicts, funding, CRediT, AI statements |
| `analysis_provenance/` | Scripts that produced every added number and figure (run with the repo `.venv`) |
| `final_stage_only/` | Biographies and portrait, for the final-files stage |

## BLOCKERS: the authors must do these before submitting
1. **AI disclosure.** Replace the bold bracket in the Acknowledgment with what you verified yourselves. Do not write a generic assurance.
2. **Check the mathematics yourselves**, in particular:
   - Appendix A (Prop. 1, now with Q ⪰ 0 and a Weyl-inequality step);
   - Appendix B (Cor. 2, Prop. 3);
   - the supplement proofs of Props. 2 and 5.
3. **Publish the code.** Everything is committed locally on branch `research/r7-clutter`, but it is **not pushed**.
   - Run `git push -u origin research/r7-clutter`.
   - Tag a release, e.g. `git tag v1.0-trs && git push origin v1.0-trs`.
   - Put the tag and commit into the Availability section (bold bracket) and the cover letter ([REPOSITORY TAG]).
4. **Co-authors.** Get consent, CRediT roles, affiliations (MathWorks clearance) and ORCID iDs.
5. **Confirm** the title (changed in R10), your e-mail, and the cover-letter statements marked [AUTHORS].
6. **Decide on length:** 12 pages (US$400) or cut (e.g. trim references, move Section VI-H detail to the supplement).

## Honest remaining risks
- Sea-clutter evidence is still one campaign (IPIX 1993). SDRDSP is pending, with a protocol frozen before download.
- The detection claims now stand against a classical PAMF, which matches the method. Reviewers may ask what remains new: the answer is the exact laws, calibration and the failure map, not sensitivity.
- The detection targets are injected, not real, and persistent targets are out of scope (proved).
- This is the right venue for the content. Acceptance is never guaranteed, but the standard objections are now answered:
  - "Only simulation": answered with two radars.
  - "No radar use": answered by the detection study.
  - "Missing online and parametric baselines": answered by ACI and the K-texture ablation.
  - "Theory not tied to data": answered, since the exact laws predict measured coverage and Pd.
