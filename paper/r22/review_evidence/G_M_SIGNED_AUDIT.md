# Independent R22-G outcomes and R22-M pre-execution audit

**Decision:** G passes independent numerical audit. M passes final protocol/configuration/implementation review; no material blocker to executing its registered idealized study was found. No change to the G scientific calculation or final M settings is needed.

Signed 5 October 2026 by `/root/r22_validation_audit`, independent internal review agent. The auditor authored none of these experimental runners, protocols or summary code, and applied the Evidence-First standard. Detailed evidence is in `INDEPENDENT_AUDIT.md`.

**G:** Frozen protocol `0ba0aafcaa0a9b254c10ab6a4da4ba19c8c203f851e43295bd6351979a01a012` matches every one of the 84 exact expected outcome identities. Source/code hashes, integer count bounds, seeds, support indexing, and denominator geometry pass. Independent source-array recomputation reproduces all 84 fits and 252 calibration thresholds; maximal errors are 5.56e-16 and 1.15e-14. Test totals are 236,440 IPIX and 1,075,080 NetRAD episodes.

Without importing the aggregator, the auditor reconstructed all 18 numerical summary families, all guard differences and intervals, crossings/rebounds, registered expectations, and all 180 CSV rows. Stored summaries are numerically identical. The 10,000 paired cluster resamples use the six IPIX days or fourteen NetRAD recording identities, retain all member units, and divide by the resampled actual episode denominator.

Verified random-Doppler, 10 dB, looks 9–16 guard16-minus-guard0 mean differences are 0.8182689054 [0.7554229760,0.8717852451] for IPIX and 0.9212237694 [0.8990574250,0.9426072230] for NetRAD. G1–G4 all meet their registered criteria. Maximum partial-domain G2 MAE is .00223777/.00222416; maximum late-window G4 probability is 6.02690e-5/3.80204e-5. The evidence supports delayed self-masking followed by collapse. It does not establish sustained-detection superiority or acquisition false-alarm control for G.

**M:** Final protocol SHA-256 is `7d6a800b9e8e7b20db42aa6898ed5961adb01034ccf02889d3e408f1debdd02c`; runner is `36e1f2163234a5de948d431b2a6928a461c46fe964d0d8f7ef9af1a8224afbcd`; configuration is `45039d372a5825bbe8d7f1902b372bca8a3041ebbe3193dda5c10dfd9d1265b2`. `MIGRATION_FREEZE.json` and both imported dependency hashes validate.

Independent fabricated-array checks verify scalar IN/CA/OS histories, coherent-bank/ANMF normalization, endpoint support, physical raw-amplitude gain normalization, velocity-linked Doppler, on-centre SCR, and local masks. All detectors calibrate the same three-bin×1,024-look acquisition search. The sole material draft correction—largest rather than second-largest calibration maximum at n152–160, alpha=.01—is resolved and documented. Ideal finite-rank resolution and measured dependent-window null rates are distinguished. Serial preparation and disjoint prepared-cache scoring preserve the scientific settings and freeze gate.

M is explicitly an ideal zero-phase sinc sensitivity study on reused measured clutter. Its PSF is not a verified NetRAD hardware response, and it supplies no real-target validation. This clearance covers design and implementation before outcomes, not M result certification. R review is separate and pending.
