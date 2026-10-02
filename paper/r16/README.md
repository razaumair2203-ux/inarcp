# Submission package: IEEE Transactions on Radar Systems, Regular Paper (R16.1, 2 Oct 2026)

**This folder holds the only live version of the paper.** Every earlier version is in `../99_archive/paper_versions/`, each with a note on why it was retired.

**Title:** *Innovation-Normalized Detection in Compound-Gaussian Clutter: Exact Laws, Conformal Thresholds and Certified Integration under Pulsed Interference*

## Upload this
**`UPLOAD_TRS/`** holds exactly the files to upload to https://ieee.atyponrex.com/journal/tradar-ieee. See `UPLOAD_TRS/UPLOAD_GUIDE.md` for which file goes in which field.

## Contents
| Item | Where |
|---|---|
| Manuscript | `manuscript/main.pdf`: 10 pages, abstract of about 249 words (limit 250). Clean build: 0 warnings, 0 overfull boxes, 0 undefined references |
| Supplement | `supplement/supplement.pdf`: 30 pages, clean build |
| Overleaf | `overleaf/INARCP_R16.1_manuscript_Overleaf.zip` and `overleaf/INARCP_R16.1_supplement_Overleaf.zip`. Each was compiled from an empty folder and verified |
| Radar block diagram of the technique | `docs/technique_flow.pdf` |
| What changed from R15, and why | `R16_CHANGES.md` (R16, its figure revision, and R16.1) |
| Notation (one meaning per symbol) | `SYMBOLS.md` |
| Checks behind this version | `../04_reviews/2026-10-02_R16_prose_benchmark/` (prose benchmark of all versions, blind panels, claim audits) and `../04_reviews/2026-10-02_R14-R15_improvement_and_confirmation/` (theorems, venue, R14/R15 studies) and `../04_reviews/2026-10-02_R16.1_evidence_levels/` (R16.1 evidence-level edits: metrics, blind pairwise, claim audits) |

## Journal requirements (checked on 2 Oct 2026, ieee-trs.org author information)
| Requirement | Status |
|---|---|
| IEEE template (IEEEtran journal, LaTeX) | ✓ IEEEtran V1.8b |
| 10 free pages; US$200 per page beyond 10 | ✓ 10 pages |
| AI use disclosed in the Acknowledgment, naming the system and the sections with AI-generated content | ✓ |
| Abstract of 150–250 words, one paragraph, with no references | ✓ |
| No "new" or "novel" in the title or abstract | ✓ |
| Real measured data | ✓ three open datasets: IPIX, NetRAD and JKU 77 GHz |
| Open access | Optional (US$2,645 for 2025 submissions); traditional publication is free |

## Code release (done)
The R14 and R15 studies were committed and pushed to `research/r7-clutter`, and the release tag **`r16-trs-submission`** was pushed. R16.1 is released under the tag **`r16.1-trs-submission`** (created and pushed with the R16.1 commit), which is the one now cited in Code and Data Availability and in the cover letter. The NetRAD raw data (about 28 GB) is git-ignored; `research/r7c/data/netrad/fetch_netrad.sh` fetches it again.

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
cd analysis_provenance && python make_r14_outputs.py && python make_r15_outputs.py && python make_fig_theory_row.py && python make_fig_detection.py && python make_supp_sections.py && python make_verification_macros.py && python make_cover_letter.py
cd ../manuscript && pdflatex main && bibtex main && pdflatex main && pdflatex main
cd ../supplement && pdflatex supplement && pdflatex supplement     (after the manuscript, for its cross-references)
```

## Known weaknesses a reviewer may raise
Table IV of the paper maps these openly.
- **Data.** There are two sea-clutter campaigns and one interference campaign, all open data, with no in-house measurements. The IPIX evaluation reuses recordings that were seen during development; NetRAD's recordings were not.
- **Injected targets.** Apart from the IPIX reference target, every real-data detection result uses targets injected into real clutter with known timing. No real target with a real onset confirms the positive detection results yet.
- **NetRAD at 10⁻⁴.** Five statistics exceed twice design there. An exploratory analysis ties part of this to rare wideband events.
- **Bursts.** Bursty interference defeats every remedy tested.
- **Hit model.** A certificate is only as good as its hit model, and it is nearly vacuous on NetRAD's frequent flagged pulses.
- **Classical laws.** Several laws are classical laws with a whitened SCR. The new results are:
  - the post-onset law, with its horizon and the guard;
  - the OS law under persistence;
  - Theorem 1.
