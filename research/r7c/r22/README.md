# R22 reproduction

Run the commands below from the repository root in a complete R22 clone. Python 3.12 was used for the registered runs; numerical versions are recorded in `research/r7c/requirements.lock.txt` and the execution manifests. Install the research environment with:

```sh
python -m pip install -r research/r7c/requirements.lock.txt
```

The public saved results support rebuilding figures, numerical macros and tables without downloading radar records. Recomputing detector outcomes also requires the provider records and local intermediates described below. New runs preserve the registered conditions, including their failures: G uses synthetic targets with known onset on exposed clutter; M uses an idealized range response and unknown crossing time on exposed NetRAD clutter; R tests detector-external camera association, with failed correlation gates and no primary clean-entry units.

## Verify the public snapshot

`REPRODUCTION_MANIFEST.json` records exact repository-relative byte hashes for the R22 scientific sources, frozen controls, saved public results and presentation inputs. Historical unfrozen prerequisite sources/inputs have a separate LF-normalized hash map for portable checking. This normalization is never applied to a frozen M/R dependency or gate. The manifest supplements the original registration records; it does not replace or amend a protocol. From the repository root:

```sh
python -c "import hashlib,json,pathlib; d=json.loads(pathlib.Path('research/r7c/r22/REPRODUCTION_MANIFEST.json').read_text()); assert all(hashlib.sha256(pathlib.Path(p).read_bytes()).hexdigest()==h for p,h in d['sha256'].items()); assert all(hashlib.sha256(pathlib.Path(p).read_bytes().replace(b'\r\n',b'\n')).hexdigest()==h for p,h in d['normalized_lf_sha256'].items()); print('R22 exact-byte and historical LF hashes match')"
```

Preserve the repository's `.gitattributes`. The M and R gates hash imported `methods.py` bytes; M also hashes `r15/netrad.py`. Their existing line endings are part of those identities. G's runtime gate checks its protocol against `PROTOCOL_R22_G.sha256`; its run manifest and this public manifest additionally identify the implementation and dependencies. M checks `MIGRATION_FREEZE.json` against protocol, configuration, runner and both imported sources. R checks `UW_FREEZE.json` against protocol, configuration, runner, `methods.py` and the fixed provider-member registry. Do not edit frozen controls to make a changed run pass.

## Rebuild R22 presentation from saved results

The complete paper package must be present at `paper/r22/`. Run these two commands in this order:

```sh
python research/r7c/r22/make_guard_figures.py
python paper/r22/analysis_provenance/make_additional_validation.py
```

The first reads `R22_G_SUMMARY.json` and the inherited `paper/r21/analysis_provenance/fig_detection_r21.json`, then writes the two vector figures and previews under `research/r7c/r22/presentation/`. The second reads the saved G/M/R summaries, generates `manuscript/generated/r22_macros.tex`, copies the R22 figures into the paper, and rebuilds the supplement through the preserved compact generator followed by the R22 additions. Its local `additional_sections.py`, `make_compact_supplement.py`, `compact_inputs/` and `supplement_reference_insertions.json` are required. Neither command fits or scores radar data.

See [the paper reproduction guide](../../../paper/r22/analysis_provenance/R22_REPRODUCTION.md) for typesetting and inherited inputs. `make_fig_detection.py` or `make_compact_supplement.py` alone regenerates inherited R21 presentation content; it does not produce the final R22 figure/supplement. Use the final two-command chain above after any inherited presentation regeneration. Regenerated PDF bytes can vary with fonts, library versions and metadata; snapshot byte verification and numerical/source reproduction are separate checks.

The public R report and all 168 method/record/association/endpoint rows can also be regenerated directly from the saved JSON, without a provider download:

```sh
python research/r7c/r22/summarize_uw.py --input research/r7c/r22/R22_R_SUMMARY.json --output-dir research/r7c/r22
```

This unfrozen postprocessor verifies the input's companion `.json.sha256`, copies its JSON bytes unchanged and writes `R22_R_RESULTS.md`, `R22_R_METHOD_RECORD_COUNTS.csv` and the copied summary/checksum. It may replace those derived outputs. Its real CLI accepts `--input` and `--output-dir`; the defaults are the original local `study/results/r22/R/uw_outcomes.json` and `r22/`, respectively.

## Fabricated mechanics checks

These commands require no provider data and compute no empirical outcomes:

```sh
python -m unittest discover -s research/r7c/r22 -p test_guard_study.py -v
python research/r7c/r22/run_migration.py --check-mechanics
python research/r7c/r22/analyze_migration.py --check-mechanics
python research/r7c/r22/run_uw.py --mechanics
python -m unittest discover -s research/r7c/r22 -p test_download_uw.py -v
```

## Provider data and a separate scientific rerun

Use a separate clone or working copy for raw reruns, preserving the published summaries. Raw records, converted clutter arrays and per-window NPZ files are excluded from the public release. Fetch scripts and runners write local registries, logs and results; these newly generated execution files need not have the original timestamps or byte identities.

IPIX needs all 14 CDF files enumerated in `research/r7c/ipix.py`, under `research/r7c/data/raw/`, with `SHA256SUMS`. The provider is [McMaster's Dartmouth IPIX collection](https://soma.ece.mcmaster.ca/ipix/dartmouth/datasets.html); follow its research-use and attribution terms. NetRAD needs all 14 node-3 HH/VV matched-filter MAT files enumerated in `research/r7c/r15/netrad.py`, under `research/r7c/data/netrad/raw/`, named `N3_<tag>.mat`. G additionally requires each extraction `.mat.ok` marker, `.mat.log` containing `CRC ok`, the raw `SHA256SUMS`, and converted `data/netrad/proc/<tag>.npz`. The [UCL provider dataset](https://doi.org/10.5522/04/32676582) is CC BY-NC 4.0; retain provider attribution and terms. The range extractor selects members of the provider archive rather than downloading the full archive.

For IPIX/NetRAD acquisition, the supplied shell scripts require a POSIX environment with Bash, curl and GNU coreutils. Create the destination directories first; then run:

```sh
python -c "from pathlib import Path; [Path(p).mkdir(parents=True,exist_ok=True) for p in ['research/r7c/data/raw','research/r7c/data/netrad/raw']]"
bash research/r7c/data/fetch_ipix.sh
bash research/r7c/data/netrad/fetch_netrad.sh
python research/r7c/r15/netrad.py
```

The NetRAD extractor also needs `curl` on Python's process PATH. On Windows use a suitable POSIX environment for the shell scripts, or obtain the same named records and verified registries from the providers. The historical `r15/pipeline_r15.sh` embeds a workspace-specific Python path; the explicit Python commands below avoid that dependency.

### G: known-onset long guard trajectories

The existing G runner compares each newly fitted AR coefficient with the corresponding earlier local R14/R15 result. A fresh raw-data reproduction therefore needs these excluded intermediates:

- `study/results/r14/u_<IPIX number>_<like0 or like1>_rot<2 or 3>.npz`: all 56 units;
- `study/results/r15/n_<NetRAD tag>_rot<2 or 3>.npz`: all 28 units.

Regenerate them with the earlier frozen runners, retaining the complete research source tree and their original protocols. These commands rerun the earlier studies as prerequisites, not just a fit-only shortcut:

```sh
python research/r7c/r14/run_r14_ipix.py --workers 2
python research/r7c/r15/run_r15_netrad.py --workers 2
python research/r7c/r22/guard_study.py --workers 4 --radar both
python research/r7c/r22/analyze_guard.py
```

G writes 84 local `g_*.npz` files to `research/r7c/study/results/r22_guard/`. It resumes an existing unit only when its saved protocol and runner hashes match; a mismatch fails. It rewrites `R22_G_run_manifest.json`. `analyze_guard.py` has no argument parser: it requires all 84 local NPZs and the complete manifest, and writes the three public `R22_G_*` summary/count/table files beside the source. It does not read the public unit-count JSON as a replacement for the local NPZs. The shipped summaries are the inputs needed for presentation reproduction.

### M: idealized continuous migration and unknown timing

M reads the original matched-filter MAT files, keeping observed pulses, and prepares its own mean/gain-normalized clutter cache. It does not use the R15 hit mask to filter null data. In the separate scientific rerun copy:

```sh
python research/r7c/r22/run_migration.py --prepare-only --prepared-cache research/r7c/study/results/r22_migration/cache
python research/r7c/r22/run_migration.py --require-prepared --prepared-cache research/r7c/study/results/r22_migration/cache --output research/r7c/study/results/r22_migration
python research/r7c/r22/analyze_migration.py --input research/r7c/study/results/r22_migration --output research/r7c/study/results/r22_migration/recomputed_summary
```

Prepare raw caches serially. The scoring command above processes the complete fixed cohort serially from those caches; optional parallel execution uses at most four disjoint `--tags` subsets with `--require-prepared`, as specified in the protocol. There is no `--workers` option for M. Every scoring unit refuses an existing output file, and the analyzer refuses existing summary destinations. The alternate summary directory avoids overwriting the published `summary/`. The analyzer requires all 28 units, 24 conditions and eight methods; a subset is not a complete reproduction.

Native spacing is 6 m, while the two sinc responses are explicitly idealized 22.5/45 MHz sensitivity cases. These injections do not reproduce a measured hardware PSF or constitute real-target validation. Calibration/search definitions, finite ranks, measured null rates and all unfavorable conditions remain in the saved summaries.

### R: camera-associated UW pedestrians

The public fixed member registry is sufficient for selective acquisition; no private ZIP catalog is needed:

```sh
python research/r7c/r22/download_uw.py --plan
python research/r7c/r22/download_uw.py
python research/r7c/r22/run_uw.py
python research/r7c/r22/summarize_uw.py --output-dir research/r7c/study/results/r22/R/recomputed_summary
```

The downloader uses standard-library HTTP range requests, verifies the frozen registry and every selected member's CRC/SHA, reuses correct local files and writes receipts only inside ignored `research/r7c/data/UW_R22/`. It acquires the three fixed records' raw ADC frames and camera labels. Provider availability is required; attribution and the documented CC BY 4.0 dataset terms are in [UW_ATTRIBUTION.md](UW_ATTRIBUTION.md).

R writes to the fixed local directory `research/r7c/study/results/r22/R/`; it has no output-directory option and refuses a nonempty directory. The immutable public copy is `R22_R_SUMMARY.json`, outside that directory, with complete tables in `R22_R_METHOD_RECORD_COUNTS.csv` and `R22_R_RESULTS.md`. The explicit fresh postprocessing destination above preserves that published copy during a scientific rerun. The R22 paper generator reads the shipped public summary directly. Camera presence association does not supply exact radar-return onsets, and the failed correlation/clean-entry gates remain part of the result.

The real CLIs and their options can be inspected with `--help` on `guard_study.py`, `run_migration.py`, `analyze_migration.py`, `run_uw.py`, `download_uw.py` and `summarize_uw.py`. The summary and figure scripts without argument parsers are run without invented flags.
