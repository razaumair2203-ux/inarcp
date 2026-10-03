# IEEE Transactions on Radar Systems — requirements, and how this paper meets them

**Primary venue.** Checked against the AESS author-information page for T-RS on 3 Oct 2026.
The formatted manuscript is the live package: `../../manuscript/main.pdf`.

| Requirement | This paper |
|---|---|
| Approved IEEE template, LaTeX or Word | ✓ IEEEtran journal class V1.8b, two columns, 10 pt |
| **No page limit**, but US$200 per printed page beyond ten | **11 pages → one page over, US$200.** A deliberate choice, approved 3 Oct 2026 |
| "Unnecessarily long manuscripts may receive unfavorable reviews" | 11 pages for a paper with four theorems, three datasets and 13 compared statistics is not long for this venue |
| Single-anonymous review, ≥ 2 reviewers, two-level prescreen | ✓ no anonymisation needed; authors and affiliations are on the title page |
| Abstract | ✓ 249 words, one paragraph, no citations, no equations |
| Avoid "new" and "novel" in the title and abstract | ✓ neither word appears in either |
| **AI-generated material disclosed in the Acknowledgment, naming the system and the affected sections** | ✓ "Anthropic Claude Code assisted with the derivations, simulations, analysis code and the preparation of the text in all sections; OpenAI Codex assisted earlier versions…". Non-disclosure risks direct rejection, so this is deliberately explicit |
| Supplementary material is technical content and must be supplied **for peer review** | ✓ 33-page supplement uploaded with the manuscript, not held back |
| Scope: radar signal processing, detection, CFAR, interference | ✓ core scope |
| Real measured data | ✓ three open datasets: IPIX X-band, NetRAD S-band, JKU 77 GHz FMCW |
| Code and data availability | ✓ a dedicated section, with the release tag and all three dataset DOIs |

## If you decide not to pay for page 11

Dropping to ten pages means removing roughly 300 words. The candidates, in the order the R18
audit would sacrifice them, are:

1. the cost-and-deployment clause of design rule 2 (about 40 words) — the detail lives in the
   supplement's cost section;
2. the second half of the operating-regime passage in Section VII-A, the range-cell re-onset
   mechanism (about 50 words) — also in the supplement;
3. the two-mechanism explanation of the model-law failures (about 45 words);
4. reverting Figures 2 and 3 to their R17 heights (1.75 and 1.6 in), which recovers about
   0.3 page.

Items 1–3 were each added in R18 because a blind reviewer asked for them or a claim audit
required them; item 4 was itself a finding (both blind reviewers noted that the smaller
figures were harder to read values off). Removing any of them is a real loss, which is why
the extra page was bought instead.

## What a T-RS reviewer is most likely to raise

Answers are prepared in
`../../../04_reviews/2026-10-03_R18_senior_review/SENIOR_REVIEW_R18.md`, under "Objections a
reviewer will raise that have no remedy available":

1. no real target with a real onset at sea — the dataset search is documented and exhausted;
2. two sea-clutter campaigns and one interference campaign, all open data;
3. several laws are classical laws with a whitened signal-to-clutter ratio — the contributions
   list says so and names the three results that are new.

## Sources checked

- AESS, T-RS author information: https://ieee-aess.org/publication/ieee-transactions-radar-systems/t-rs-author-info
- Submission system: https://ieee.atyponrex.com/journal/tradar-ieee
