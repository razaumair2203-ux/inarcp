# Migration runner mechanics, before real-data outcomes

The deterministic `python run_migration.py --check-mechanics` check passed. It uses a fabricated complex exponential with a deterministic amplitude envelope, and does not fit, calibrate, or compute detection rates. Checks cover:

- identical 1024-look endpoint and three-bin score shapes for all eight methods;
- direct scalar guarded innovation-history score versus vectorized score;
- direct 64-frequency matched-filter bank versus FFT implementation;
- direct 16-innovation normalized coherent bank versus P-ANMF1-N16;
- invariance to a common nonzero complex scale;
- raw target peak SCR through unequal bin-normalization gains;
- inclusion of the final search endpoint and explicit no-acquisition sentinel.

A separate fabricated four-by-three complex cache round-trip passed, including refusal of changed freeze metadata, refusal of missing freeze metadata, and refusal of modified cached sample contents. The temporary directory was resolved and verified to remain inside `r22` before removal. No real samples were loaded by those checks.

A fabricated sixteen-window timing probe of all eight score functions took 0.453 s. This is a resource estimate only, not a real-data result. The native-recording header audit and public archive directory read are saved in `provider_metadata/`. They contain acquisition metadata and source hashes, no detector outcomes or new sample fits.

The root independent auditor separately checked scalar score calculations, physical gain normalization, signed Doppler/range consistency and prefix support. Its required correction of the planning quantile description was accepted: the finite calibration threshold is the largest maximum, with ideal rank tail mass `1/(n+1)`. The planned n range was additionally corrected to 152–160 after including the split gaps and 40-pulse prefix. These are conditional planning counts rather than measured outcomes.

No protocol freeze record was created by this sub-agent, and no new real-data threshold, false-alarm rate or target outcome has been computed. Root freezes the final M protocol/configuration/runner before authorizing execution. The independent audit of the added cache/parallel-subset paths is still required.
