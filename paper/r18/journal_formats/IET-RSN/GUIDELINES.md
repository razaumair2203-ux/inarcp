# IET Radar, Sonar & Navigation — second fallback

Checked against the journal's Wiley author-guidelines and open-access pages on 3 Oct 2026.

## Read this first: the cost changed the ranking

**IET RSN is now fully open access, with a mandatory article processing charge of about
US$2,600** (£2,060 / €2,380). Every accepted paper pays it. IET members get 15% off when the
submitting author is a member, and corresponding authors in countries on Wiley's waivers and
discounts list may pay nothing — Pakistan's eligibility should be checked before this venue is
chosen, because the corresponding author is at NUST.

Against that, T-RS and TAES both publish free under the traditional model and charge only
US$200 for the eleventh page. **This venue costs roughly thirteen times more than the T-RS
overlength charge**, so it should be a considered choice, not a default third try.

## This is not the publisher's class file

IET and Wiley do not distribute a LaTeX class that could be validated offline. `main.tex` here
is a **single-column A4 rendering** that satisfies IET's *stated* structural requirements and
is legible for peer review, which is all IET asks of a submission. It:

- stubs out the IEEEtran-only commands (`\IEEEPARstart`, `\markboth`, `\bstctlcite`,
  `\appendices`, the `IEEEkeywords` environment, the starred float environments);
- rebuilds the title block, since `\thanks` inside `\author` is IEEEtran-specific;
- shrinks any table that overruns the single-column width, because the T-RS tables are set for
  a 3.4-inch column;
- adds the four front-matter items IET requires and IEEE does not (below).

**Before submitting, transfer the body into the official template from the journal's author
guidelines page.** Verified on 3 Oct 2026: 21 pages, 0 overfull boxes, 0 undefined references,
0 errors.

`main.tex` is **generated** from `../../manuscript/main.tex` by
`../../analysis_provenance/make_journal_variants.py`. Do not edit it: edit the T-RS source and
regenerate.

| Requirement | Status |
|---|---|
| Single editable document, Word or LaTeX | ✓ `main.tex` plus `generated/`, `figures/`, `references.bib` |
| Unstructured abstract | ✓ 249 words. IET states no numeric limit |
| Keywords | ✓ |
| Sections: abstract, introduction, methods, results, conclusions | ✓ all present, numbered |
| **Table-of-contents entry: title, authors, ≤ 80 words or three sentences, and a representative figure** | ✓ drafted at 62 words in the front matter, pointing at Fig. 1, the receive-chain diagram |
| **Data availability statement**, per Wiley's data-sharing policy | ✓ drafted in the front matter: all three datasets are open and third-party, with the code repository and release tag |
| **AI disclosure.** "The IET does not recognize AI tools as authors… If AI tools were used in the preparation of any part of the paper, this should be clearly disclosed, and authors take full responsibility" | ✓ the Acknowledgment names the systems, the affected sections and the authors' responsibility. IET's wording is satisfied by the IEEE-form disclosure already in the paper |
| Author contributions | ⚠ **drafted as a placeholder.** The authors must supply CRediT roles; see `../../declarations.md` |
| Conflict of interest | ✓ drafted: S. Ahmed is employed by MathWorks |
| ORCID | ⚠ **authors to supply** |
| Open access APC | ⚠ about US$2,600, mandatory. Check the waiver list |

## What else would need doing before this submission

- [ ] Transfer into the official IET template.
- [ ] Rewrite the cover letter for IET; the present one is addressed to T-RS.
- [ ] Decide the APC question, including the waiver check, **before** submitting.
- [ ] Reference style: the file still uses `IEEEtran.bst`, which is numeric and close to IET
      house style but not identical. The official template will set this.
- [ ] Re-check the figures at single-column width. Figures 2 and 3 were drawn for a 7.16-inch
      double-column span and are reflowed here; they will want redrawing at the single-column
      width rather than scaling.

## Sources checked

- Author guidelines: https://ietresearch.onlinelibrary.wiley.com/hub/journal/17518792/homepage/author-guidelines
- Open access and APC: https://ietresearch.onlinelibrary.wiley.com/hub/journal/17518792/homepage/open-access
