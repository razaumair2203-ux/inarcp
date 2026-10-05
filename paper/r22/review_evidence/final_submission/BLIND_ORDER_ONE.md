# Independent anonymous comparison ? blind order one

Recommendation: **second.pdf**, by a modest but meaningful advantage in evidence framing and narrative organization. Both manuscripts are mature. I found no material technical or presentation defect in either PDF that requires correction within this PDF-only review. No further change is needed to the second PDF for the review criteria assessed here.

Reviewer signature: `/root/r22_final_blind_order_one`, independent anonymous manuscript reviewer, 2026-10-05.

## Inputs and completion record

- `first.pdf` ? SHA-256: `3cac39ba29a0f16f5a387d1679de9e25c68025742f20765b5d972b95e01ef67e`; 11 pages.
- `second.pdf` ? SHA-256: `6d2e9fa29c49bebd7fea059369824f6af9c912de7712d726b850f68509d8e1c7`; 11 pages.
- First PDF: pages **1, 2, 3, 4, 5, 6, 7, 8, 9, 10, 11** read and visually inspected as rendered page images.
- Second PDF: pages **1, 2, 3, 4, 5, 6, 7, 8, 9, 10, 11** read and visually inspected as rendered page images.
- Author-roster size was excluded from the assessment. No identity mapping, named manuscript versions, parent-directory contents, source files, supplementary files, empirical reruns, or external sources were inspected. Rendering and text extraction used only the two supplied PDFs. This review assesses the evidence and argument presented in them; it does not independently authenticate their empirical outputs or cited sources.

## Concrete reasons for the preference

1. **The second PDF states the model-to-measurement gap more precisely at the point of motivation.** On page 1 it says that covariance and AR-whitening detectors restore scale invariance under their model assumptions, and that this does not establish far-tail accuracy in measured clutter. This directly separates a theoretical property from the empirical problem addressed. The first PDF's introduction reaches the same general motivation, but its longer wording about thresholds from Gaussian laws or simulation is less exact about this distinction. Both appropriately acknowledge the one-pulse PAMF connection rather than representing whitening gain as a new detector gain.

2. **The second PDF's early contribution claims agree more immediately with the qualified results.** Its calibration contribution on page 1 says that thresholds improve measured tail calibration over the tested model laws and explicitly retains NetRAD failures at 10^-4. The first PDF's contribution on page 2 says that the thresholds "hold the rate" to the respective levels; its later results and discussion supply the qualifications, so this is not an overall material misrepresentation. The second is nevertheless easier to read accurately on first encounter. Similarly, its abstract calls the 48-look trajectories "Injected-target trajectories," whereas the first calls them "Measured trajectories." Figure 3 and the body in both PDFs identify the injected targets, but the second removes that early ambiguity.

3. **The second PDF establishes the diverse data roles before using their results.** Its page 2 overview explains sea-clutter tail calibration, injected reference-contamination tests, JKU real interference and pedestrian returns, and UW external camera labels. Page 6 includes a dedicated camera-labelled-pedestrian methods paragraph with whole-record roles and screened clutter masks. The first supplies the UW context mainly when the result appears on page 7. The second therefore makes the external-label result feel like part of the experimental design, while preserving the limitation that camera presence labels do not establish precise native-bin radar onset.

4. **The second PDF gives the migration study a coherent results-to-discussion sequence.** Page 2 relates the migration question to motion-aware coherent integration; page 9 places the numerical acquisition result in Results subsection VI-F. Discussion then interprets the contamination mechanism and guard limitation. The first introduces the numerical migration experiment inside Discussion on page 9. Its conclusion is sound, but the second's sequence makes the negative result easier to assess as evidence before reading its interpretation.

## Shared strengths and boundaries

The exact onset, persistence, OS and integration laws on pages 3?5 are presented with explicit model conditions. Theorem 1 identifies exchangeability, clutter-independent hit positions and inclusion-order dominance; the adjacent text correctly says that a hit-rate bound alone is insufficient. The results on pages 6?9 distinguish approximate calibration from a proved guarantee, report non-exchangeability, identify matched injected-hit tests as implementation/cost checks, and retain the burst, low-rate saturation, real-target and continuous-migration failures. The conclusion in both versions preserves these boundaries. These mature passages should stay.

Equations are legible in both rendered PDFs, including the eigenvalue coverage law, rank-one detection law and visibility horizon. Figure 1 makes the retained latest predictor sample and separated scale window clear. Figure 2's caption distinguishes closed forms from the Monte Carlo-only interference panel. Figure 3 explicitly labels injected targets, measured versus fitted-law trajectories, weighting and exploratory status. Tables I?III identify rates, designs, detector families and hit conditions; Table IV clearly separates calibration, sensitivity and failure mechanisms and warns that equal nominal designs can yield different measured false-alarm rates. I found no clipping, overlap or unreadable mathematical or caption content. Dense compact tables and the long abstract are acceptable at this stage, not necessary corrections.

The preference is thus for the second PDF's clearer and more consistent presentation of substantially shared scientific content. It is not a claim of a newly validated empirical advantage, nor a request for additional experiments or numerical improvement.
