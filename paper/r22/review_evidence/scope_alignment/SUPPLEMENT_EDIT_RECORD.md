# Bounded supplement scope alignment

5 October 2026. Writer record, not independent certification. Only two supplement sentences were revised through `03_submission_IEEE-TRS/analysis_provenance/final_submission_edits.json`; the existing `make_additional_validation.py` generator regenerated `supplement/supplement.tex`.

## Sentence 1: opening scope

**Before:** This supplement supports the paper's conditional laws and measured calibration results.

**After:** This supplement provides proofs of the paper's conditional laws and supporting results on calibration, target visibility, interference and real targets.

**Reason:** The previous opening named only laws and calibration even though the supplement also contains substantial visibility, interference and real-target evidence. The replacement describes existing content rather than adding a new contribution or validation claim.

**Evidence:** Supplement proof and numerical-verification sections; false-alarm calibration tables; post-onset and long-trajectory sections; pulse-interference certificates and real JKU interference; real IPIX target, JKU pedestrian and camera-associated UW pedestrian sections. The independent scope-audit action plan identifies this opening as an optional, bounded alignment.

**Preservation:** All qualifications about frozen outcomes, prospective extensions, data exposure, internal study labels, failed conditions and post-hoc choices remain unchanged. No assertion of universal validation, target superiority or independent confirmation was added.

## Sentence 2: remaining onset gap

**Before:** None establishes independent maritime onset performance.

**After:** None establishes detection performance at independently timed onsets of real targets in correlated clutter.

**Reason:** The missing evidence concerns target timing and the correlated-clutter regime. Restricting it to a maritime setting needlessly narrowed the statistical problem and obscured the existing ground-scene tests.

**Evidence:** The surrounding JKU pedestrian section retains its failed confirmatory event-support condition and radar-derived labels. The UW section reports weak frame-lag correlation, imperfect camera association and an empty primary clean-entry set. The real IPIX target is continuously present; injected trajectories have known timing. These findings support the specific remaining gap without removing completed real-target tests.

**Preservation:** The gap remains explicit. Descriptive pedestrian results, intervals, failed condition, secondary endpoints and all numerical values remain unchanged. Historical source descriptions and genuine sea-specific dataset labels were retained.

## Writer verification

- The regenerated supplement is exactly the baseline text with these two literal replacements; no other supplement-source difference exists.
- The wrapper's ten incidental output files remain byte-identical: `r22_macros.tex`, the two copied figures, `additional_validation_provenance.json`, the frozen proof fragment and five frozen table fragments.
- Neither generator nor any frozen source/input, result macro, table cell, proof or figure was edited. No radar fitting/scoring or new outcome computation was performed.
- No main manuscript, metadata, PDF or ZIP was changed by this writer.
- The editorial JSON now includes both replacements, so later regeneration retains the corrected scope.

Root will perform the final package compilation, page inspection and independent last-edit claim review.
