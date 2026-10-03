# IEEE Transactions on Aerospace and Electronic Systems — first fallback

**Why this is the first fallback.** TAES shares T-RS's template, review model, scope and
charging structure, so moving the paper costs one line. Checked against the AESS TAES
author-information page on 3 Oct 2026.

`main.tex` here is **generated** from `../../manuscript/main.tex` by
`../../analysis_provenance/make_journal_variants.py`. Do not edit it: edit the T-RS source and
regenerate, or the two will drift apart.

| Requirement | Status |
|---|---|
| Regular Paper or Correspondence | Regular Paper |
| Two columns, 10 pt, IEEE template, **PDF** at submission | ✓ identical IEEEtran journal class as T-RS |
| **No page limit**, US$200 per printed page beyond ten | **11 pages → US$200**, the same as T-RS |
| Single-anonymous review, ≥ 2 independent reviewers | ✓ |
| **AI-generated content disclosed in the Acknowledgments, naming the system and the affected sections.** "Failure to disclose AI-generated content is a policy violation subject to direct rejection" | ✓ unchanged from the T-RS version |
| Avoid "new"/"novel" in title and abstract | ✓ |
| Supplementary material is technical content and **must be provided for peer review** | ✓ the 33-page supplement, unchanged |
| Abstract word limit | Not specified by TAES. The abstract is 249 words, which satisfies the stricter T-RS limit |
| Survey papers handled by the Magazine editors | Not applicable |

## The only differences from the T-RS file

1. The running head: "Submitted to IEEE Transactions on Aerospace and Electronic Systems".
2. The header comment.

Everything else — title, authors, abstract, body, tables, figures, appendices, bibliography
style and the Code and Data Availability section — is identical, because TAES asks for the
same things.

## Before submitting to TAES rather than T-RS

- [ ] Rewrite the cover letter: `../../cover_letter_TRS.md` names T-RS and its scope. Change
      the addressee, the journal name and the fit paragraph.
- [ ] Reconsider the framing. TAES has a broader aerospace readership than T-RS, so the
      sea-clutter specificity may need one sentence of motivation in the Introduction that
      T-RS does not need.
- [ ] Check whether the paper has already been declined by T-RS. If so, say so in the cover
      letter and attach the reviews; AESS editors share a reviewer pool.

## Build

```
cd journal_formats/IEEE-TAES
pdflatex main && bibtex main && pdflatex main && pdflatex main
```

Verified on 3 Oct 2026: 11 pages, 0 overfull boxes, 0 undefined references.

## Source checked

AESS, TAES information for authors:
https://ieee-aess.org/publications/transactions-aes/author-information
