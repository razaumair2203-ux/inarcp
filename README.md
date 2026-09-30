# IN-ARCP

**Innovation-Normalized Autoregressive Conformal Prediction** for independent scalar episodes.

IN-ARCP fits one zero-intercept AR(1) coefficient, computes a history-only innovation scale, and calibrates normalized prediction residuals on separate episodes. The name describes this model-specific instance of normalized split conformal prediction. It is not a claim that conformal calibration, innovation whitening, or Student prediction intervals are new.

Source: https://github.com/razaumair2203-ux/inarcp

## Research draft

The [current manuscript PDF](paper/manuscript.pdf) and [supplement PDF](paper/supplement.pdf)
are available in this repository. See [paper/README.md](paper/README.md) for
their version and status. The manuscript is a research draft, not a submitted
or accepted article. Its IEEE Access format is restored; both algorithms and the UML sequence diagram now appear in the main paper. [Template provenance](paper/TEMPLATE.md) and [implementation checks](docs/algorithm_traceability.md) are included.

The [implemented revision record](docs/revision_record_2026-09-28.md) explains the validated issues, changes and remaining limits. The [reproduction guide](reproducibility/README.md) includes the fresh 800-fit comparison, four complete fitted-mean checks, allocation study and every saved outcome. Original PDFs are archived separately; the former 4,800-fit headline is not reused.

The [R5 Overleaf ZIP](paper/releases/INARCP_Overleaf_IEEE_Access_2026-09-28_R5.zip) includes the official IEEE Access class and fonts. [R5 manuscript](paper/releases/INARCP_IEEE_Access_2026-09-28_R5.pdf): Algorithm 1 p.4, UML p.5, Algorithm 2 p.6. R5 revises the introduction, literature synthesis, contributions, scientific narrative and figures; see [the editorial revision record](docs/editorial_revision_R5.md).

## Install and use

```sh
python -m pip install .
python examples/basic_usage.py
python -m unittest discover -s tests -v
```

```python
from inarcp import INARCP

# H_train: (N, m); y_train: (N,)
# H_cal: (n, m); y_cal: (n,); H_test: (n_test, m)
model = INARCP(alpha=0.1, clip=0.98)
model.fit(H_train, y_train)
model.calibrate(H_cal, y_cal)
intervals = model.predict_interval(H_test)  # lower and upper endpoint columns
```

Each row must represent a separate episode. Split episodes before fitting/calibration; overlapping windows from one record are not automatically independent. A refit invalidates calibration. Histories must have at least two observations, a positive scale, and the same length in every split. The example is synthetic, not a validated sensor application.

## Definition and guarantees

For a fitted coefficient r and history h of length m,

```
s_r(h)^2 = ((1-r^2)*h[0]^2 + sum((h[j]-r*h[j-1])^2, j=1..m-1)) / m
score    = abs(y-r*h[-1]) / s_r(h)
k        = ceil((n+1)*(1-alpha))
interval = r*h[-1] +/- kth_calibration_score * s_r(h)
```

If k exceeds n, the interval is the whole real line. No interpolated quantile or arbitrary scale floor is used. Positive scaling of a complete calibration/test episode cancels from the score.

Coverage follows from exchangeability of standardized calibration/test episodes, conditional on training and episode scales. It averages over calibration and test histories, rather than guaranteeing coverage for each particular history. Different dynamics across calibration and test sets need not preserve coverage. The exact length analysis additionally assumes stationary, zero-mean Gaussian AR(1) episodes with a common coefficient. Training-scale heterogeneity affects the pooled coefficient estimate.

`oracle_mean_length` evaluates the Gaussian known-coefficient mean. `efficiency_terms` returns the leading fitting, calibration and rank-rounding contributions; these are asymptotic approximations without finite-sample remainder bounds. See [derivation](docs/method.md).

## Complex (I/Q) radar clutter episodes

`inarcp.clutter` holds the prediction discs of the radar-clutter paper (`paper/r11`). Rows are complex episodes; the history is the first m columns and the response is the last.

```python
from inarcp import ComplexINARCP, NoiseAwareINARCP, os_coverage
disc = ComplexINARCP(order=1, alpha=0.01).fit(X_train).calibrate(X_cal)            # RMS innovation scale
os_disc = ComplexINARCP(order=1, alpha=0.01, os_rank=8).fit(X_train).calibrate(X_cal)  # order-statistic scale
na_disc = NoiseAwareINARCP(order=4, alpha=0.1).fit(X_train).calibrate(X_cal)       # clutter + noise, AR(4)
center, radius = disc.predict_disc(H_test)            # exceedance |y - center| > radius is a detection
```

- `os_rank=k` normalizes by the k-th smallest innovation power. A persistent target is kept for `n_innovations_ - k` looks (m − k for order 1). This costs about 0.7 dB in theory for k = 8, m = 16 (2.0 dB measured on IPIX). It does not help gradually emerging targets or dwell integration, and it does not replace fast-time interference zeroing. `os_coverage(q, n, k)` is its exact law under pure AR(1) compound-Gaussian clutter.
- On IPIX, `NoiseAwareINARCP(order=4)` gives regions 0.891 [0.872, 0.905] times as wide as `ComplexINARCP(order=4)` when trained within the same session. Across days the RMS-scaled disc is the safer default.

`reproducibility/check_package_equivalence.py` checks that these classes reproduce the research code behind the paper's numbers.

## Revision scope

Version 0.2.0 adds `finite_calibration_mean_length` and `recommend_split`, executable scientific validation, complete new empirical results, and editable LaTeX manuscript/supplement sources. The allocation utility minimizes a leading approximation using prespecified planning parameters; it does not guarantee finite-sample optimality. At the tested total budget of 300, its candidates improve mean length by roughly 0.6% over an equal split.

The common-Gaussian comparisons show near parity with the fitted Student reference, shorter intervals than the specified invariant Ad-EffOrt implementation, and losses to native or nonlinear methods in some settings. All results and limitations are retained. No real-data application or broad state-of-the-art ranking is claimed.

## Prior work

- Lei et al., “Distribution-Free Predictive Inference for Regression,” JASA, 2018, [DOI](https://doi.org/10.1080/01621459.2017.1307116): normalized split-conformal construction.
- Dhillon et al., “On the Expected Size of Conformal Prediction Sets,” AISTATS, 2024, [paper](https://proceedings.mlr.press/v238/dhillon24a.html): expected-size analysis.
- Le Bars and Humbert, “On Volume Minimization in Conformal Regression,” ICML, 2025, [paper](https://proceedings.mlr.press/v267/bars25a.html): efficiency analysis and Ad-EffOrt; independent comparator implementation and exact settings are included in the reproduction study.

## License and provenance

MIT license applies to this repository's original code and documentation; it does not license the manuscript or supplement. NumPy and SciPy are separately licensed dependencies. The standalone implementation was prepared with OpenAI Codex assistance and checked against the research implementation and mathematical identities. No private career records, thesis files or employer documents are included. The Overleaf ZIP bundles unchanged official IEEE template/font dependencies under their own terms. Author metadata are preserved from the original draft. The author biographies and portrait in the current paper are restored from that original.
