# Uploading to IEEE Transactions on Radar Systems (R18, 3 Oct 2026)

**Submission site:** https://ieee.atyponrex.com/journal/tradar-ieee
**Manuscript type:** Regular Paper.
**Length:** 11 printed pages. T-RS sets **no page limit**; it charges **US$200 for each page
beyond ten**, so expect a **US$200 overlength charge**. Page 11 was a deliberate decision in
R18, approved by the authors, and it carries the operating-regime passage, the
cost-and-deployment design rule and the enlarged Figures 2 and 3.

## The three files in this folder

| File | Field in the submission system | Checked |
|---|---|---|
| `INARCP_TRS_Manuscript.pdf` | Main document | 11 pages; byte-identical to `../manuscript/main.pdf`; opens; 0 overfull boxes, 0 undefined references, 0 warnings |
| `INARCP_TRS_Supplementary_Material.pdf` | Supplementary material, **for peer review** | 37 pages; byte-identical to `../supplement/supplement.pdf`; opens; clean build |
| `Cover_Letter.pdf` | Cover letter. If the system offers a text box instead, paste the text of `../cover_letter_TRS.md` | 2 pages; opens; quotes the paper's own macros, so its numbers cannot drift from the tables |

T-RS states that supplementary material is technical content and **must** be provided for peer
review at submission, not after acceptance. Upload it with the manuscript.

## Metadata to paste into the forms

- **Title:** Innovation-Normalized Detection in Compound-Gaussian Clutter: Exact Laws,
  Conformal Thresholds and Certified Integration under Pulsed Interference
- **Abstract:** copy from the PDF. **249 words** against the 250-word limit — one word of
  headroom, so do not add to it in the form.
- **Keywords:** compound-Gaussian clutter, conformal prediction, constant false alarm rate,
  pulse integration, pulsed interference, sea clutter
- **Authors:** Muhammad Umair Raza (corresponding author, NUST), Sohail Ahmed (MathWorks),
  Ammad Ahmed (NDMA). **ORCID iDs: [AUTHORS TO SUPPLY]**
- **Funding and competing interests:** see `../declarations.md`. S. Ahmed is employed by
  MathWorks — declare this. **[AUTHORS TO COMPLETE]**
- **Open access:** optional (US$2,645). Traditional publication is free.

## Things only the authors can do before you press submit

- [ ] Read the whole 11-page PDF once, in particular the Appendix proofs (Theorem 1,
      Proposition 4, Corollary 4).
- [ ] Complete `../declarations.md`: CRediT roles, ORCID iDs, competing interests, funding.
- [ ] Confirm the AI-use statement in the Acknowledgment. T-RS requires the AI system to be
      named and the affected sections identified; the current wording names Anthropic Claude
      Code and OpenAI Codex and says "all sections". Confirm that this is what you want to
      state, because a disclosure that is wrong in either direction is a policy problem.
- [ ] Confirm the NetRAD acknowledgment that the dataset licence asks for.
- [ ] Accept the US$200 overlength charge, or ask for the 10-page variant (see
      `../journal_formats/IEEE-TRS/GUIDELINES.md` for what would have to come out).

## Only at the final-files stage, after acceptance

- LaTeX source: `../overleaf/INARCP_R18_manuscript_Overleaf.zip`
- Author biographies and portrait: `../final_stage_only/`

## Provenance of this folder

Rebuilt from an empty folder on 3 Oct 2026 after the R18 round. Each PDF was opened and its
page count and content checked, and the two copies were verified byte-identical to their
sources. The previous (R17) bundle is in
`../../99_archive/paper_versions/R17_senior-review-superseded_2026-10-03/`.
