# IN-ARCP: innovation-normalized radar detection with conformal thresholds

Code and figure scripts for

M. U. Raza et al., "Innovation-Normalized Radar Detection in Compound-Gaussian Clutter: Self-Masking
Analysis and False-Alarm Control," submitted to IEEE Transactions on Radar Systems.

## Contents
- `paper/`: the manuscript and its Supplementary Material as currently submitted to IEEE Transactions on
  Radar Systems. This is the authors' submitted version, not the published article.
- `inarcp/`: Python package (IN-ARCP score, AR whitening, split-conformal thresholds) with `tests/` and `examples/`.
- `figures/`: scripts that draw Figs. 1-3 of the paper and the supplementary figures from the saved inputs in
  `figures/inputs/` (no simulation or data fitting).

Analysis plans and saved study outputs are available from the authors on request.

## Data
Raw radar recordings are not redistributed; obtain them from their providers:
- IPIX (McMaster University, Dartmouth 1993): https://soma.ece.mcmaster.ca/ipix/dartmouth/datasets.html
- NetRAD (UCL Figshare, doi:10.5522/04/32676582, CC BY-NC 4.0)
- JKU 77 GHz FMCW network data (Zenodo, doi:10.5281/zenodo.21933926)
- 5.8 GHz land-clutter recordings (Zenodo, doi:10.5281/zenodo.3451408, CC BY-SA 4.0)
- UWB foliage set (Zenodo, doi:10.5281/zenodo.10815247, CC BY-NC-SA 4.0)
- UW 77 GHz records (IEEE DataPort, doi:10.21227/xm40-jx59)

## Use
`pip install -e .` then `pytest tests`; `python examples/basic_usage.py`. Figures: `python figures/fig1_theory.py`
(and the other scripts), output in `figures/out/`. `SHA256SUMS` lists every file of the release.

## Licence
The code is released under the MIT licence (see `LICENSE`). The radar data keep their providers' terms.
