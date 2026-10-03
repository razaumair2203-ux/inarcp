# Submission package: IEEE Transactions on Radar Systems, Regular Paper (R18, 3 Oct 2026)

**This folder holds the only live version of the paper.** Every earlier version is in `../99_archive/paper_versions/`, each with a note on why it was retired.

**Title:** *Innovation-Normalized Detection in Compound-Gaussian Clutter: Exact Laws, Conformal Thresholds and Certified Integration under Pulsed Interference*

## Upload this
**`UPLOAD_TRS/`** holds exactly the files to upload to https://ieee.atyponrex.com/journal/tradar-ieee. See `UPLOAD_TRS/UPLOAD_GUIDE.md` for which file goes in which field.

## Contents
| Item | Where |
|---|---|
| Manuscript | `manuscript/main.pdf`: **11 pages**, abstract 249 words (limit 250). Clean build: 0 warnings, 0 overfull boxes, 0 undefined references. T-RS has no page limit but charges US$200 per page past ten, so expect a US$200 overlength charge; page 11 was approved on 3 Oct 2026 |
| Supplement | `supplement/supplement.pdf`: 37 pages, clean build. T-RS requires it **with the submission, for peer review** |
| Overleaf | `overleaf/INARCP_R18_manuscript_Overleaf.zip` and `overleaf/INARCP_R18_supplement_Overleaf.zip`. Each was built in an empty folder, compiled there, then re-extracted into another empty folder and recompiled |
| Radar block diagram of the technique | `docs/technique_flow.pdf` |
| What changed, and why | `CHANGES.md`, newest first (R18, R17, R16.1, R16) |
| The paper in each venue's format | `journal_formats/`: T-RS (primary), TAES, IET RSN, each with its own `GUIDELINES.md` |
| Notation (one meaning per symbol) | `SYMBOLS.md` |
| Checks behind this version | **`../04_reviews/2026-10-03_R18_senior_review/`** (the senior-reviewer audit against the 2026 body of knowledge: twelve findings in `SENIOR_REVIEW_R18.md`, what changed in `ROUND_R18.md`, the two blind pairwise reviews, the adversarial claim audit and the metrics), `../04_reviews/2026-10-02_R16_prose_benchmark/` (prose benchmark of all versions, blind panels, claim audits) and `../04_reviews/2026-10-02_R14-R15_improvement_and_confirmation/` (theorems, venue, R14/R15 studies), `../04_reviews/2026-10-02_R16.1_evidence_levels/` (R16.1 evidence-level edits) and `../04_reviews/2026-10-03_R17_real_onsets/` (R17: integration rounds, metrics, and summaries of the blind-pairwise reviews and claim audits in `ROUND_R17.md`) |

## Journal requirements (checked on 2 Oct 2026, ieee-trs.org author information)
| Requirement | Status |
|---|---|
| IEEE template (IEEEtran journal, LaTeX) | ✓ IEEEtran V1.8b |
| No page limit; US$200 per printed page beyond 10 | ⚠ **11 pages → US$200.** Approved 3 Oct 2026 |
| AI use disclosed in the Acknowledgment, naming the system and the sections with AI-generated content | ✓ |
| Abstract of 150–250 words, one paragraph, no references | ✓ 249 words, one word of headroom |
| No "new" or "novel" in the title or abstract | ✓ |
| Real measured data | ✓ three open datasets: IPIX, NetRAD and JKU 77 GHz |
| Open access | Optional (US$2,645 for 2025 submissions); traditional publication is free |

## Code release (done)
R18 is released under the tag **`r18-trs-submission`**, which is the tag cited in Code and Data Availability, the cover letter and `declarations.md`. The earlier tags `r12-trs-submission`, `r16-trs-submission`, `r16.1-trs-submission` and `r17-trs-submission` are also pushed and remain valid for those versions. The NetRAD raw data (about 28 GB) is git-ignored; `research/r7c/data/netrad/fetch_netrad.sh` fetches it again.

## Only the authors can do these
- [ ] Read the whole PDF once. Check in particular the proofs in the Appendices: Theorem 1, Proposition 4 and Corollary 4.
- [ ] Complete `declarations.md`: CRediT roles, ORCID iDs, conflict of interest (S. Ahmed is employed by MathWorks) and funding.
- [ ] Confirm the AI statement in the Acknowledgment, and the NetRAD acknowledgment that the dataset licence asks for.

## Folder contents
| Path | What |
|---|---|
| `manuscript/` | `main.tex`, `references.bib`, `generated/` (every number as a macro, plus generated tables), `figures/`, `main.pdf`, `main.bbl`, and `main.aux` (the supplement reads the paper's labels from it) |
| `supplement/` | `supplement.tex`, the generated sections, the tables, the figures, `data/` (saved result summaries) and `supplement.pdf` |
| `overleaf/` | the two Overleaf ZIPs; see `overleaf/HOW_TO_USE.md` |
| `analysis_provenance/` | the scripts that turn saved outcomes into `generated/*.tex`, the supplement sections and the cover letter; run them with the repository's `.venv` |
| `docs/` | the signal-chain diagram (`technique_flow.pdf` and `.tex`) |
| `UPLOAD_TRS/` | the files for the journal's submission system |
| `final_stage_only/` | author biographies and portrait, needed only after acceptance |

## Rebuild locally
```
cd analysis_provenance
python make_r14_outputs.py && python make_r15_outputs.py && python make_r17_outputs.py
python make_r18_outputs.py && python make_r18_supp.py && python make_supp_verbatim.py
python make_fig_theory_row.py && python make_fig_detection.py
python make_supp_sections.py && python make_verification_macros.py && python make_cover_letter.py
cd ../manuscript && pdflatex main && bibtex main && pdflatex main && pdflatex main
cd ../supplement && pdflatex supplement && pdflatex supplement     (after the manuscript, for its cross-references)
cd .. && python analysis_provenance/make_cover_letter_pdf.py
python analysis_provenance/make_journal_variants.py    (the TAES and IET files)
python analysis_provenance/make_overleaf_zips.py       (both containers, built and verified in empty folders)
```

## Known weaknesses a reviewer may raise
Table IV of the paper maps these openly.
- **Data.** There are two sea-clutter campaigns and one interference campaign, all open data, with no in-house measurements. The IPIX evaluation reuses recordings that were seen during development; NetRAD's recordings were not.
- **Real targets.** Apart from the IPIX reference target and one walking person at 77 GHz, every real-data detection result uses targets injected into real clutter with known timing. The pedestrian test (R17) is descriptive. Its onsets fell in 7 distinct five-frame blocks, fewer than the 8 required, and on them IN-ARCP only matched a power clutter map (0.30 against 0.27, which on 74 onsets in seven blocks is not a difference). No real target with a real onset at sea has been tested.
- **Sensitivity against the learned detectors on this benchmark.** At the literature's observation length of 1,024 pulses the paper's self-normalized statistic reaches P_d = 0.41 at 2.6 x 10^-3 against a reported 0.91 at 10^-3. The paper reports this and says why the comparison is not like for like; it does not claim a more sensitive detector.
- **Operating regime.** The per-look gain needs clutter still correlated at the look interval, and physically frequent onsets need a look interval long enough for targets to cross range cells. The paper's two radars sit at the extremes of that trade-off, and nothing in the evidence covers the middle.
- **NetRAD at 10⁻⁴.** Five statistics exceed twice design there. An exploratory analysis ties part of this to rare wideband events.
- **Bursts.** Bursty interference defeats every remedy tested.
- **Hit model.** A certificate is only as good as its hit model, and it is nearly vacuous on NetRAD's frequent flagged pulses.
- **Classical laws.** Several laws are classical laws with a whitened SCR. The new results are:
  - the post-onset law, with its horizon and the guard;
  - the OS law under persistence;
  - Theorem 1.
