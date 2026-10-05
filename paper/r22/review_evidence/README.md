# R22 independent review evidence

The original `r22-trs-submission` snapshot retains the signed scientific and fresh-Git reproduction evidence in this directory. Its checker pins the original R22 manuscript/PDF identities. Those historical reports certify that snapshot; they must not be read as a signature on later presentation files.

The final `r22-final-submission` review adds [final narrative, author and artifact evidence](final_submission/) and both anonymous presentation orders. The mathematical statements, proofs, saved outcomes, result tables and figure inputs are preserved. The final manuscript integrates dataset roles, relocates the complete migration outcome into Results and adds its matched motion-search reference. Both comparison orders prefer the final narrative. The independent final claim audit finds no material defect. The final fresh-Git check is a separate signed report added after its audited source commit.

For the historical check, archive `r22-trs-submission` and run the original `independent_release_check.py` on that archive. For the final check, archive `r22-final-submission` and run `final_submission/final_independent_release_check.py` on that archive:

```sh
git archive --format=zip --output=r22-final-review.zip r22-final-submission
python paper/r22/review_evidence/final_submission/final_independent_release_check.py --archive r22-final-review.zip --expected-commit COMMIT_SHA_FROM_GIT_REV_PARSE --work-dir NEW_EMPTY_REVIEW_DIRECTORY
```

Obtain the expected commit with `git rev-parse r22-final-submission^{commit}`. The output directory must not exist. Use the study Python dependencies, PyMuPDF, Matplotlib and working pdfLaTeX with the pinned IEEE support. Do not use Python `-O`; the checker uses assertions. It writes only disposable extracted copies and reports, fits no radar model and generates no new detector outcomes. It dynamically verifies the complete package manifest and pins unchanged scientific controls plus the final manuscript/supplement identities. Machine JSON absolute paths are historical audit locations, not installation requirements.

The cover letter remains a draft. These reviews do not certify author assent/declarations or journal acceptance.
