# IN-ARCP

Innovation-normalized autoregressive conformal prediction for scalar episodes and complex radar clutter.

The current radar manuscript studies how whitening and normalization affect false alarms, target self-masking and integration under pulsed interference. The per-look statistic is a history-normalized one-pulse parametric adaptive matched filter (PAMF). The work develops its post-onset detection law and visibility horizon, a slow-time guard, the order-statistic counterpart and a conformal certificate for bounded integration. It does not claim to introduce whitening or split conformal prediction.

## Current radar manuscript: R22

**Innovation-Normalized Detection in Compound-Gaussian Clutter: Exact Laws, Conformal Thresholds and Certified Integration under Pulsed Interference**

| Read or reproduce | File |
|---|---|
| Manuscript | [PDF](paper/r22/UPLOAD_TRS/INARCP_R22_Manuscript.pdf) |
| Technical supplement | [PDF](paper/r22/UPLOAD_TRS/INARCP_R22_Supplementary_Material.pdf) |
| Editable manuscript | [Overleaf ZIP](paper/r22/UPLOAD_TRS/INARCP_R22_manuscript_Overleaf.zip) |
| Editable supplement | [Overleaf ZIP](paper/r22/UPLOAD_TRS/INARCP_R22_supplement_Overleaf.zip) |
| Sources, saved inputs and build instructions | [R22 package](paper/r22/README.md) |

R22 is a research draft prepared for IEEE Transactions on Radar Systems, not an accepted article. Tag **`r22-scope-submission`** identifies the bounded 5 October 2026 scope alignment; earlier `r22-final-submission` and `r22-trs-submission` tags are preserved. Software remains **0.3.0**, released 30 September 2026. The alignment represents the existing sea and ground evidence more evenly without changing mathematical claims, outcomes or figure inputs. Three hash-registered studies extend persistent-target trajectories to 48 looks, test continuous range migration with unknown crossing time, and evaluate camera-labelled pedestrian recordings. [Protocols, results and reproduction instructions](research/r7c/r22/README.md) are provided.

Earlier R21 tags and artifacts are preserved. Its additive `r21-trs-submission-metadata1` tag corrects only artifact manifest paths and release documentation; its scientific artifacts retain their original hashes.

The theory applies to the stated statistical models, rather than exclusively to sea clutter. Exact AR innovation laws require the true coefficient, a common episode texture and no thermal noise. Conformal calibration requires exchangeable episodes. The interference certificate requires a dominating hit model independent of the clean clutter. Measured evidence uses IPIX and NetRAD sea clutter, JKU 77 GHz ground-clutter/interference recordings, and three UW camera-labelled pedestrian records. Longer guards extend the useful interval for abrupt injected onsets, followed by collapse. Guarded IN-ARCP acquires poorly in the idealized continuous-migration study. The UW records have weak inter-frame correlation and no eligible primary clean entries; their presence-association results do not validate correlated-clutter onset detection. The paper reports both gains and failures and does not establish universal detector superiority.

## Install and check

```sh
python -m pip install .
python -m unittest discover -s tests -v
python reproducibility/check_package_equivalence.py
```

The last command compares the reusable complex-episode implementation with the corresponding research implementations. It does not reproduce every radar experiment.

## Complex radar episodes

Each row of `X_train` or `X_cal` is a complex episode: a fixed-length history followed by the tested sample. `H_test` contains histories of the same length.

```python
from inarcp import ComplexINARCP, NoiseAwareINARCP

disc = ComplexINARCP(order=1, alpha=0.01).fit(X_train).calibrate(X_cal)
os_disc = ComplexINARCP(order=1, alpha=0.01, os_rank=8).fit(X_train).calibrate(X_cal)
na_disc = NoiseAwareINARCP(order=4, alpha=0.1).fit(X_train).calibrate(X_cal)

center, radius = disc.predict_disc(H_test)
# A sample y exceeds the prediction disc when abs(y - center) > radius.
```

`os_rank=k` uses the k-th smallest history innovation power instead of its mean. Its persistence behavior depends on the threshold and target Doppler; the strong-target collapse condition is stated in the R21 paper. It is not a blanket guarantee of detection for `m-k` looks. `os_coverage` evaluates the pure AR(1) compound-Gaussian law; `exact_coverage` evaluates the Gaussian quadratic-form law for a specified covariance, linear center and quadratic scale. The guarded and certified dwell experiments are implemented in [the research code](research/r7c/), beyond this prediction-disc API. The package's AR(1) fit is unclamped least squares; the research experiments clamp its magnitude at 0.98. Use the study implementation for exact experimental settings.

Split complete episodes before fitting and calibration. Overlapping windows from a record are not automatically exchangeable. Refitting invalidates the previous calibration; changing deployment dynamics can invalidate it too. A history-scale method also needs a positive scale and consistent history lengths.

## Scalar API and earlier research

The original scalar API remains available:

```python
from inarcp import INARCP

model = INARCP(alpha=0.1, clip=0.98)
model.fit(H_train, y_train)
model.calibrate(H_cal, y_cal)
intervals = model.predict_interval(H_test)
```

The earlier scalar manuscript, **Innovation-Normalized Conformal Prediction for Autoregressive Episodes: Training and Calibration Costs**, is retained with its [reproduction guide](reproducibility/README.md), [method derivation](docs/method.md), [validation record](docs/revision_record_2026-09-28.md) and [historical paper files](paper/README.md). Its IEEE Access sources and synthetic comparisons belong to that earlier study. `oracle_mean_length`, `finite_calibration_mean_length`, `efficiency_terms` and `recommend_split` remain part of the API; the fitting/split approximations do not guarantee finite-sample optimality.

Normalized split conformal prediction builds on [Lei et al. (2018)](https://doi.org/10.1080/01621459.2017.1307116). The scalar efficiency study also relates to [Dhillon et al. (2024)](https://proceedings.mlr.press/v238/dhillon24a.html) and [Le Bars and Humbert (2025)](https://proceedings.mlr.press/v267/bars25a.html). Radar-specific foundations and recent related work are cited in the current R22 manuscript.

## License and provenance

The MIT license covers the repository's original software and documentation, excluding manuscript/supplement text, figures and PDFs. External datasets, official IEEE template assets and software dependencies retain their own terms. Dataset fetch instructions and saved outcomes are under `research/r7c`; the repository does not redistribute the full raw radar recordings. See [CITATION.cff](CITATION.cff) for software citation metadata.

Development and manuscript preparation used Anthropic Claude Code and OpenAI Codex assistance. The manuscript specifies the extent of that assistance in its Acknowledgment. The authors remain responsible for checking the methods, results and text.
