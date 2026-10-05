# Anonymous pairwise verdict

**Preference: first.** Confidence is high for this comparative scope/narrative judgment. The first manuscript is mature and needs no change for the requested scope implementation. The second remains technically coherent, but its abstract and conclusion underrepresent the complementary ground-scene evidence already present in its body. This preference is about the meaning of those measurements, not the number of datasets or the proportion of positive findings.

## Sources and review boundary

| Source | Pages | SHA-256 |
|---|---:|---|
| `first.pdf` | 11 | `61b371062d4ef7fac4be1f6040ce487bb3b2982780111ea1fc1005a705209f64` |
| `second.pdf` | 11 | `6d2e9fa29c49bebd7fea059369824f6af9c912de7712d726b850f68509d8e1c7` |

Reviewed the assigned PDFs and text extractions only. Read the mathematical and experimental body and compared the differing passages. Inspected rendered pages 1, 3, 7, 8, 9 and 10, including side-by-side views of the changed summary pages. No mapping, source manuscript, version history, other review, external review dispatch or new study was inspected. The source manuscripts were not edited. This is an internal evidence-to-narrative certification, not an independent reproduction of the data or a full external literature audit.

## Specific comparison evidence

The table compares second to first; it does not infer their chronological order.

| Location | Second | First | Evidence and reader impact |
|---|---|---|---|
| Abstract, p. 1 | Gives additional matched independent-hit results: IPIX detection 0.64 and NetRAD false-alarm ratio 0.08/detection 0.92. Omits the 77 GHz results. | Explicitly identifies sea clutter and 77 GHz ground scenes as tests of calibration, visibility, noise and interference. Reports sparse real-interference control at 0.54 times design with a 6.4 dB cost, fast-time zeroing, and little pedestrian whitening advantage at weak frame correlation. | Sections VI-A/B/D, pp. 7-8, support these statements. VI-D explicitly says the matched injected hits check implementation and cost, rather than robustness. The first abstract therefore conveys what the complementary measurements establish and the operational choice they motivate, while preserving the sea-clutter findings. |
| Conclusion, p. 9 | Summarizes IPIX/NetRAD, extended trajectories, poor migration and certificate sensitivity costs for bursts/frequent hits. | Also summarizes noise-dependent JKU calibration, real-interference control and cost, restoration of clean-reference rates by excision, and weak-correlation JKU/UW pedestrian checks. | These are substantive findings in the unchanged body, rather than extra dataset mentions. They connect the noise caveat to measured calibration and the certificate to a practical interference alternative. The first conclusion better represents the actual manuscript. |
| Discussion VII-A, p. 9 | Says transfer of calibration findings to other clutter types remains untested. | Says calibration down to 10^-4 remains unestablished beyond the two sea-clutter datasets, and identifies ground-scene tests as complementary. | VI-A already measures 77 GHz coverage versus CNR and false-alarm behavior at 10^-2; it does not establish 10^-4 ground-scene calibration. The first wording states that precise unestablished boundary. The second's broader statement can obscure the lower-rate ground-scene calibration evidence that was actually collected. |
| Table IV, p. 10 | Uses generic row labels for real ground targets and real 77 GHz interference; removes the supplementary evidence map from the caption. | Names UW camera-associated pedestrians and JKU real interference and retains supplementary table/section locators. | The numerical outcomes are unchanged. The first gives clearer attribution and a shorter route to the supporting evidence. This is supporting readability/traceability evidence, not a separate fatal defect in the second. |

## Mathematical hook and evidence calibration

The shared body is coherent and needs no rewriting for this comparison. The introduction links whitening and innovation normalization to classical laws, then separates tail calibration, contamination of a cell's own history, and corrupted test/reference pulses. Section III-A states common episode texture, and the guarded/dwell span it must cover. Sections IV-A/C/D distinguish onset gain from post-onset target energy entering the reference. The guard moves the scale window while retaining the latest predictor sample (Fig. 1), so it delays contamination without rescuing targets near clutter Doppler. The horizon in Corollary 4, the fully contaminated limit in Proposition 3 and the 48-look collapse in Fig. 3b consistently describe a finite benefit.

Theorem 1 is explicitly conditional: exchangeable clean episodes, clutter-independent hit positions and inclusion-order dominance by the calibration mask law. Its history-zeroing/dwell-maximizing bound covers arbitrary interference amplitudes; it does not remove those assumptions. The discussion explicitly says measured agreement or an empirical mask does not prove them. The body also distinguishes marginal conformal validity from the independent-score Beta calculations, and says non-overlap alone does not validate independence. Neither version materially weakens these qualifications.

Both versions retain substantial negative evidence: NetRAD failures at 10^-4 after threshold refitting; little benefit at clutter Doppler; eventual history self-masking; descriptive real-target results without informative external onsets at strongly correlated lags; a burst-matched certificate that detects no target; and very low acquisition under idealized continuous migration. The first does not become falsely reassuring by including the ground scenes: its abstract also reports the measured sensitivity cost and weak-correlation limitation. Its conclusion retains the need for independently timed real-target onsets in correlated clutter and a measured range response.

Verified here are the passages, numerical consistency with the supplied body/tables, shared assumptions and layouts. The comparative reader impact is a reasoned judgment. Generalization, exchangeability and real-mask dominance remain uncertainties already acknowledged by the manuscripts; the supplied PDFs do not independently establish them.

## Material defects and readability

**First: no material defect found within the requested comparison; no change needed.** The body, concise summaries and captions are already mature. The complementary measurements are presented with their limitations rather than as universal validation.

**Second: a bounded narrative defect.** Its abstract/conclusion narrow the apparent empirical scope to sea clutter and matched injected hits, despite the ground-scene evidence in the same body; its broad transfer statement is less accurate than the first's explicit 10^-4 boundary. This does not invalidate its mathematical results or its experimental body.

Both remain 11 pages with comparable typography and readable, dense two-column layouts. The changed passages do not produce visible clipping, overlap or a significant space/readability penalty. Figure 1 explains the guarded scale and retained predictor; Figure 3 states injection, aggregation, exploratory fitted-law comparison and intervals; Table II clearly identifies injected interference; Tables III/IV retain failure conditions as well as gains. No material layout defect was found in the inspected pages. Minor alternative phrasing or caption preferences do not warrant further edits.
