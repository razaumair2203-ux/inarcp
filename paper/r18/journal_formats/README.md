# The manuscript in each venue's format

One source of truth. `../manuscript/main.tex` is the paper; the other two files here are
**generated** from it by `../analysis_provenance/make_journal_variants.py`. Editing a generated
file is how the versions drift apart, so edit the T-RS source and run the generator.

```
cd 03_submission_IEEE-TRS
python analysis_provenance/make_journal_variants.py
cd journal_formats/IEEE-TAES && pdflatex main && bibtex main && pdflatex main && pdflatex main
cd ../IET-RSN      && pdflatex main && bibtex main && pdflatex main && pdflatex main
```

| Folder | Venue | Layout | Length | Cost | Built and checked |
|---|---|---|---|---|---|
| `IEEE-TRS/` | **IEEE Trans. Radar Systems** (primary) | IEEEtran journal, 2 col, 10 pt | **11 pages** | free + **US$200** overlength | the live package; 0 overfull, 0 undefined |
| `IEEE-TAES/` | IEEE Trans. Aerospace and Electronic Systems | identical | 11 pages | free + US$200 overlength | ✓ 3 Oct 2026; 0 overfull, 0 undefined |
| `IET-RSN/` | IET Radar, Sonar & Navigation | single column, A4 | 21 pages | **open access, APC ≈ US$2,600** | ✓ 3 Oct 2026; 0 overfull, 0 undefined, 0 errors |

`IEEE-TRS/` holds no copy of the manuscript, only its guidelines: `CLAUDE.md` rule 10 allows
one live version, and the T-RS format *is* that version.

Each folder's `GUIDELINES.md` lists that venue's requirements with the paper's status against
each, the things only the authors can supply (ORCID, CRediT, competing interests), and what
else would have to change before submitting there.

## The order to try them, and why

1. **T-RS.** Core scope, single-anonymous, free to publish, and the venue the paper was
   written for.
2. **TAES.** Same template, same review model, same charges, broader readership. Moving costs
   a running head and a new cover letter.
3. **IET RSN.** Same scope, but every accepted paper pays an APC of about US$2,600, and the
   paper needs a graphical-abstract entry, a data-availability statement, author
   contributions and a transfer into the publisher's own template. Worth it only if both IEEE
   venues decline, and only after checking whether a country waiver applies.

The full venue assessment, including what a reviewer at each is likely to raise, is in
`../../04_reviews/2026-10-03_R18_senior_review/SENIOR_REVIEW_R18.md` and
`../../04_reviews/2026-10-02_R14-R15_improvement_and_confirmation/VENUE_FIT.md`.
