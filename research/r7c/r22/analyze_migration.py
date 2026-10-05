"""Preregistered complete-cohort R22-M aggregation; publish aggregates, not raw-bin caches.

All 28 units, 24 conditions and eight methods are required. Recording bootstrap
resamples retain both rotations and every acquisition of each selected record.
--check-mechanics uses fabricated aggregate counts only.
"""
from __future__ import annotations

import argparse
import csv
import hashlib
import json
from pathlib import Path
import sys

import numpy as np

HERE = Path(__file__).resolve().parent
sys.path.insert(0, str(HERE))
import run_migration as runner

BOOTSTRAP_REPLICATES = 10000
BOOTSTRAP_SEED = int(hashlib.sha256(b"R22|M|bootstrap").hexdigest()[:8], 16)
METRICS = ("any", "local", "first_is_local")


def conditions(cfg):
    return [(float(speed), float(fraction), float(scr))
            for speed in cfg["radial_speeds_m_s"]
            for fraction in cfg["effective_bandwidth_fractions"] for scr in cfg["scr_db"]]


def condition_name(condition):
    speed, fraction, scr = condition
    return f"speed{speed:g}|band{fraction:g}|scr{scr:g}"


def method_names(cfg):
    result = []
    for guard in cfg["guards"]:
        result.extend((f"IN-G{guard}", f"CA-G{guard}", f"OS{cfg['os_rank']}-G{guard}"))
    result.extend((f"PAMF-H1-K{cfg['coherent_dwell']}-G{cfg['coherent_guard']}",
                   f"P-ANMF1-N{cfg['self_normalized_dwell']}"))
    return result


def scalar_count(values, n, label):
    values = np.asarray(values)
    if values.shape != (n,) or not np.isin(values, (0, 1)).all():
        raise ValueError(f"Invalid saved binary outcomes: {label}")
    return int(values.sum())


def bootstrap_weights(records, replicates=BOOTSTRAP_REPLICATES, seed=BOOTSTRAP_SEED):
    rng = np.random.default_rng(seed)
    draws = rng.integers(0, records, size=(replicates, records))
    weights = np.zeros((replicates, records), dtype=np.int64)
    for index in range(records):
        weights[:, index] = np.sum(draws == index, axis=1)
    return weights


def cluster_rates(counts, denominators, weights):
    """Pool acquisition counts, preserving recording-level dependence on resampling."""
    counts = np.asarray(counts)
    denominator = weights @ np.asarray(denominators)
    if np.any(denominator <= 0):
        raise ValueError("Bootstrap acquisition denominator is zero.")
    flat = counts.reshape(counts.shape[0], -1)
    return ((weights @ flat) / denominator[:, None]).reshape((len(weights),) + counts.shape[1:])


def check_mechanics():
    denominators = np.array([20, 40, 80])
    counts = np.array([[1, 2], [6, 8], [20, 30]])
    weights = np.array([[1, 1, 1], [3, 0, 0], [0, 2, 1], [0, 0, 3]])
    result = cluster_rates(counts, denominators, weights)
    expected = np.array([[27/140, 40/140], [1/20, 2/20], [32/160, 46/160], [20/80, 30/80]])
    np.testing.assert_allclose(result, expected)
    np.testing.assert_allclose(result[:, 1] - result[:, 0], expected[:, 1] - expected[:, 0])
    draw_weights = bootstrap_weights(14)
    assert draw_weights.shape == (10000, 14) and np.all(draw_weights.sum(axis=1) == 14)
    np.testing.assert_array_equal(draw_weights, bootstrap_weights(14))
    print("Fabricated episode-weighting, paired differences and seeded recording-bootstrap checks passed.")


def read_complete_cohort(directory, cfg, freeze):
    methods, conds = method_names(cfg), conditions(cfg)
    if len(methods) != 8 or len(conds) != 24 or len(cfg["tags"]) != 14:
        raise ValueError("R22-M requires its complete frozen eight-method, 24-condition, 14-record cohort.")
    expected = [directory / f"migration_{tag}_rot{rotation}.npz"
                for tag in cfg["tags"] for rotation in cfg["rotations"]]
    missing = [path.name for path in expected if not path.exists()]
    extras = sorted(path.name for path in directory.glob("migration_*.npz") if path not in expected)
    if missing or extras:
        raise ValueError(f"Incomplete or unexpected cohort; missing={missing}; extra={extras}")
    unit_metadata, unit_counts, null_counts = [], [], []
    cluster_n = np.zeros(14, dtype=np.int64)
    cluster_null = np.zeros((14, len(methods)), dtype=np.int64)
    cluster_target = np.zeros((14, len(conds), len(methods), len(METRICS)), dtype=np.int64)
    timing_totals = np.zeros((len(conds), len(methods), 6), dtype=np.int64)
    for tag_index, tag in enumerate(cfg["tags"]):
        for rotation in cfg["rotations"]:
            path = directory / f"migration_{tag}_rot{rotation}.npz"
            with np.load(path, allow_pickle=False) as packed:
                manifest = json.loads(str(packed["manifest_json"]))
                if manifest["freeze"] != freeze or manifest["config"] != cfg:
                    raise ValueError(f"Frozen source/configuration mismatch: {path.name}")
                if manifest["tag"] != tag or manifest["rotation"] != rotation:
                    raise ValueError(f"Saved identity mismatch: {path.name}")
                n, nc = int(manifest["test_windows"]), int(manifest["calibration_windows"])
                if n <= 0 or nc <= 0:
                    raise ValueError("Empty saved acquisition cohort.")
                rank = int(np.ceil((nc + 1) * (1 - cfg["alpha_acquisition"])))
                tail_mass = (nc + 1 - rank) / (nc + 1)
                if manifest["conformal_rank"] != rank or not np.isclose(manifest["iid_rank_tail_mass"], tail_mass):
                    raise ValueError(f"Saved calibration-rank mismatch: {path.name}")
                coefficient = complex(packed["ar1_coefficient"])
                if not np.isfinite(coefficient):
                    raise ValueError(f"Nonfinite saved fit: {path.name}")
                crossing = np.asarray(packed["crossing_look"])
                if crossing.shape != (n,) or np.any(crossing < cfg["crossing_look_min"]) or np.any(crossing >= cfg["crossing_look_max_exclusive"]):
                    raise ValueError(f"Invalid saved target crossing times: {path.name}")
                common = dict(unit_id=f"{tag}_rot{rotation}", tag=tag,
                              polarization=runner.FILES[tag][0], rotation=rotation)
                unit_metadata.append(dict(**common, source_npz_filename=path.name,
                                          source_npz_sha256=runner.sha(path), source_npz_bytes=path.stat().st_size,
                                          raw_filename=manifest["raw_filename"], raw_sha256=manifest["raw_sha256"],
                                          raw_shape=manifest["raw_shape"], dropped_padding=manifest["dropped"],
                                          execution_job_id=manifest["execution_job_id"],
                                          n_calibration=nc, n_test=n, conformal_rank=rank,
                                          iid_rank_tail_mass=tail_mass,
                                          ar1_real=coefficient.real, ar1_imag=coefficient.imag))
                cluster_n[tag_index] += n
                for method_index, method in enumerate(methods):
                    threshold = float(packed[f"threshold|{method}"])
                    cal = packed[f"calibration_maxima|{method}"]
                    test = packed[f"null_maxima|{method}"]
                    if cal.shape != (nc,) or test.shape != (n,) or not np.isfinite(cal).all() or not np.isfinite(test).all() or not np.isfinite(threshold):
                        raise ValueError(f"Invalid saved fit/calibration/null maxima: {path.name}/{method}")
                    actual_threshold = runner.conformal_quantile(cal, cfg["alpha_acquisition"])
                    if threshold != actual_threshold:
                        raise ValueError(f"Saved threshold does not equal its fixed rank: {path.name}/{method}")
                    null = packed[f"null_acquisition|{method}"]
                    nh = scalar_count(null, n, method)
                    if not np.array_equal(null, test > threshold):
                        raise ValueError(f"Null flags disagree with saved maxima: {path.name}/{method}")
                    cluster_null[tag_index, method_index] += nh
                    null_counts.append(dict(**common, method=method, n_calibration=nc,
                                            conformal_rank=rank, iid_rank_tail_mass=tail_mass,
                                            threshold=threshold, n_test=n, null_hits=nh))
                    for condition_index, condition in enumerate(conds):
                        name = condition_name(condition)
                        stem = f"target|{name}|{method}|"
                        events = {metric: packed[stem + metric] for metric in METRICS}
                        counts = [scalar_count(events[metric], n, f"{name}/{method}/{metric}") for metric in METRICS]
                        first, first_local = packed[stem + "first_look"], packed[stem + "first_local_look"]
                        if first.shape != (n,) or first_local.shape != (n,):
                            raise ValueError(f"Invalid saved timing arrays: {path.name}/{name}/{method}")
                        if not np.array_equal(first >= 0, events["any"].astype(bool)) or not np.array_equal(first_local >= 0, events["local"].astype(bool)):
                            raise ValueError("Acquisition indicators and first-look sentinels disagree.")
                        if np.any(first >= cfg["search_looks"]) or np.any(first_local >= cfg["search_looks"]) or np.any(first < -1) or np.any(first_local < -1):
                            raise ValueError("Saved acquisition times outside the prescribed search.")
                        if np.any(events["local"] > events["any"]) or np.any(events["first_is_local"] > events["local"]):
                            raise ValueError("Saved local event cannot exceed the acquisition event.")
                        local_mask = events["local"].astype(bool)
                        if np.any(first_local[local_mask] < first[local_mask]):
                            raise ValueError("A local declaration cannot precede the first declaration.")
                        first_is_local = events["first_is_local"].astype(bool)
                        if np.any(first_local[first_is_local] != first[first_is_local]):
                            raise ValueError("First-local classification disagrees with first declaration time.")
                        local_delay = first_local[local_mask] - crossing[local_mask]
                        timing = np.array([int(first[first >= 0].sum()), int(first_local[local_mask].sum()),
                                           int(local_delay.sum()), int((local_delay < 0).sum()),
                                           int((local_delay == 0).sum()), int((local_delay > 0).sum())])
                        timing_totals[condition_index, method_index] += timing
                        cluster_target[tag_index, condition_index, method_index] += counts
                        speed, fraction, scr = condition
                        unit_counts.append(dict(**common, condition=name, radial_speed_m_s=speed,
                                                bandwidth_fraction=fraction, effective_bandwidth_hz=cfg["nominal_bandwidth_hz"]*fraction,
                                                scr_db=scr, method=method, n_test=n,
                                                any_hits=counts[0], local_hits=counts[1], first_local_hits=counts[1],
                                                first_is_local_hits=counts[2], first_acquisition_look_sum=int(timing[0]),
                                                first_local_look_sum=int(timing[1]), first_local_delay_sum=int(timing[2]),
                                                first_local_before_crossing=int(timing[3]),
                                                first_local_at_crossing=int(timing[4]), first_local_after_crossing=int(timing[5])))
    return methods, conds, unit_metadata, unit_counts, null_counts, cluster_n, cluster_null, cluster_target, timing_totals


def write_csv(path, rows):
    with path.open("w", encoding="utf-8", newline="") as stream:
        writer = csv.DictWriter(stream, fieldnames=list(rows[0]))
        writer.writeheader()
        writer.writerows(rows)


def analyze(directory, output, cfg, freeze):
    (methods, conds, metadata, unit_counts, null_counts, cluster_n,
     cluster_null, cluster_target, timing) = read_complete_cohort(directory, cfg, freeze)
    weights = bootstrap_weights(len(cfg["tags"]))
    bootstrap_null = cluster_rates(cluster_null, cluster_n, weights)
    bootstrap_target = cluster_rates(cluster_target, cluster_n, weights)
    n = int(cluster_n.sum())
    null_hits, target_hits = cluster_null.sum(axis=0), cluster_target.sum(axis=0)
    null_ci = np.quantile(bootstrap_null, (0.025, 0.975), axis=0)
    target_ci = np.quantile(bootstrap_target, (0.025, 0.975), axis=0)
    null_summary, condition_summary, paired = [], [], []
    alpha = cfg["alpha_acquisition"]
    for method_index, method in enumerate(methods):
        rate = float(null_hits[method_index] / n)
        null_summary.append(dict(method=method, acquisitions=n, null_hits=int(null_hits[method_index]),
                                 acquisition_false_alarm_probability=rate,
                                 cluster_ci_lower=float(null_ci[0, method_index]), cluster_ci_upper=float(null_ci[1, method_index]),
                                 nominal_alpha=alpha, false_alarm_ratio=rate/alpha,
                                 ratio_ci_lower=float(null_ci[0, method_index]/alpha), ratio_ci_upper=float(null_ci[1, method_index]/alpha),
                                 M2_within_half_to_twice_design=bool(0.5 <= rate/alpha <= 2),
                                 calibration_count_min=min(item["n_calibration"] for item in metadata),
                                 calibration_count_max=max(item["n_calibration"] for item in metadata),
                                 iid_rank_tail_mass_min=min(item["iid_rank_tail_mass"] for item in metadata),
                                 iid_rank_tail_mass_max=max(item["iid_rank_tail_mass"] for item in metadata)))
    guarded = methods.index("IN-G8")
    for condition_index, condition in enumerate(conds):
        name = condition_name(condition)
        speed, fraction, scr = condition
        common = dict(condition=name, radial_speed_m_s=speed, bandwidth_fraction=fraction,
                      effective_bandwidth_hz=cfg["nominal_bandwidth_hz"]*fraction, scr_db=scr)
        for method_index, method in enumerate(methods):
            row = dict(**common, method=method, acquisitions=n)
            for metric_index, metric in enumerate(METRICS):
                row[f"{metric}_hits"] = int(target_hits[condition_index, method_index, metric_index])
                row[f"{metric}_probability"] = float(target_hits[condition_index, method_index, metric_index]/n)
                row[f"{metric}_cluster_ci_lower"] = float(target_ci[0, condition_index, method_index, metric_index])
                row[f"{metric}_cluster_ci_upper"] = float(target_ci[1, condition_index, method_index, metric_index])
            local_hits = row["local_hits"]
            row.update(first_local_hits=local_hits, first_acquisition_look_sum=int(timing[condition_index, method_index, 0]),
                       first_local_look_sum=int(timing[condition_index, method_index, 1]),
                       first_local_delay_sum=int(timing[condition_index, method_index, 2]),
                       mean_first_local_delay_looks=float(timing[condition_index, method_index, 2]/local_hits) if local_hits else None,
                       first_local_before_crossing=int(timing[condition_index, method_index, 3]),
                       first_local_at_crossing=int(timing[condition_index, method_index, 4]),
                       first_local_after_crossing=int(timing[condition_index, method_index, 5]))
            condition_summary.append(row)
            if method_index == guarded:
                continue
            for metric_index, metric in enumerate(METRICS):
                differences = bootstrap_target[:, condition_index, guarded, metric_index] - bootstrap_target[:, condition_index, method_index, metric_index]
                low, high = np.quantile(differences, (0.025, 0.975))
                point = float((target_hits[condition_index, guarded, metric_index] - target_hits[condition_index, method_index, metric_index])/n)
                paired.append(dict(**common, endpoint=metric, endpoint_role="primary" if metric == "any" else "secondary",
                                   reference_method="IN-G8", comparator_method=method, acquisitions=n,
                                   probability_difference=point, cluster_ci_lower=float(low), cluster_ci_upper=float(high)))
    expected_rows = len(metadata)*len(conds)*len(methods)
    if len(metadata) != 28 or len(unit_counts) != expected_rows or len(paired) != 24*7*3:
        raise ValueError("Incomplete preregistered report topology.")
    if not all(np.isfinite(item["probability_difference"]) for item in paired):
        raise ValueError("A fixed paired comparison cannot be estimated.")
    summary = dict(protocol="R22-M", freeze=freeze, config=cfg,
                   analysis_sha256=runner.sha(Path(__file__).resolve()),
                   bootstrap=dict(replicates=BOOTSTRAP_REPLICATES, seed=BOOTSTRAP_SEED,
                                  seed_source="first eight SHA-256 hex characters of R22|M|bootstrap, interpreted base16",
                                  clusters=cfg["tags"], retained_within_cluster="both rotations and all acquisition windows",
                                  intervals="descriptive paired recording-cluster percentile 95% intervals",
                                  sample_policy="episode-weighted pooled counts; same bootstrap weights for every method/condition/endpoint"),
                   reporting_scope="Idealized continuous range-response/timing sensitivity on reused measured clutter; no real-target or verified hardware-PSF validation",
                   publication_policy="Only aggregate counts/metadata and source hashes; no per-window raw provider samples, means/gains or power proxies exported",
                   checks=dict(M1_all_28_units_complete_finite=True,
                               M2_methods_within_half_to_twice_design=sum(item["M2_within_half_to_twice_design"] for item in null_summary),
                               M2_total_methods=len(methods), M3_all_fixed_paired_comparisons_estimable=True),
                   acquisition_windows=n, condition_count=len(conds), method_count=len(methods),
                   recording_window_counts={tag:int(value) for tag,value in zip(cfg["tags"],cluster_n)},
                   units=metadata, null_results=null_summary, condition_results=condition_summary, paired_results=paired)
    output.mkdir(parents=True, exist_ok=True)
    destinations = [output/name for name in ("migration_unit_counts.csv", "migration_unit_null.csv", "migration_conditions.csv",
                                            "migration_null.csv", "migration_paired.csv", "migration_summary.json", "RESULTS_R22_M.md")]
    if any(path.exists() for path in destinations):
        raise FileExistsError("Refusing to replace previously saved migration summaries.")
    for path, rows in zip(destinations[:5], (unit_counts, null_counts, condition_summary, null_summary, paired)):
        write_csv(path, rows)
    destinations[5].write_text(json.dumps(summary, indent=2, allow_nan=False), encoding="utf-8")
    lines = ["# R22-M complete fixed-cohort results", "", f"All 28 units, 24 conditions and eight methods completed; {n} acquisition windows per method/condition.",
             "", "This is idealized range-response/timing sensitivity on measured NetRAD clutter, not measured hardware-PSF or real-target validation.",
             "All four signed speeds, both bandwidths and all three SCRs are retained in the linked CSV/JSON outputs.", "",
             "M1: met. M3: met. M2 is evaluated below at the nominal acquisition design probability 0.01.", "",
             "| Method | Null hits / acquisitions | False-alarm ratio | Recording-cluster 95% ratio interval | M2 met |",
             "|---|---:|---:|---:|---|"]
    for item in null_summary:
        lines.append(f"| {item['method']} | {item['null_hits']} / {n} | {item['false_alarm_ratio']:.4f} | [{item['ratio_ci_lower']:.4f}, {item['ratio_ci_upper']:.4f}] | {'yes' if item['M2_within_half_to_twice_design'] else 'no'} |")
    lines.extend(["", "The calibration threshold is the largest acquisition maximum. Actual calibration sizes/ranks and ideal i.i.d. rank tail masses are in migration_unit_null.csv. Dependence and distribution shift require the measured null rates above; nominal thresholds do not establish equal realized false-alarm rates.",
                  "", "The primary endpoint is any threshold crossing in the complete three-bin, 1024-look search. Local and first-is-local outcomes are evaluation summaries. An acquisition during a target window may include a background alarm.",
                  "", "The table below retains all conditions. Each cell is IN-G8 probability minus the corresponding comparator probability, with a paired recording-cluster interval in migration_paired.csv. Local probabilities and timing counts are separately retained in migration_conditions.csv.",
                  "", "| Speed (m/s) | Bandwidth (MHz) | SCR (dB) | IN-G8 any | IN-G8 local | IN-G8 − IN-G0 any | IN-G8 − P-ANMF1-N16 any |", "|---:|---:|---:|---:|---:|---:|---:|"])
    for condition in conds:
        name = condition_name(condition)
        gr = next(item for item in condition_summary if item["condition"] == name and item["method"] == "IN-G8")
        diff0 = next(item for item in paired if item["condition"] == name and item["endpoint"] == "any" and item["comparator_method"] == "IN-G0")
        diffa = next(item for item in paired if item["condition"] == name and item["endpoint"] == "any" and item["comparator_method"] == "P-ANMF1-N16")
        lines.append(f"| {condition[0]:g} | {cfg['nominal_bandwidth_hz']*condition[1]/1e6:g} | {condition[2]:g} | {gr['any_probability']:.4f} | {gr['local_probability']:.4f} | {diff0['probability_difference']:+.4f} | {diffa['probability_difference']:+.4f} |")
    lines.extend(["", "Uncertainty uses 10,000 resamples of the 14 complete recordings, retaining both rotations and all their acquisition windows. All recordings belong to one campaign day; these intervals do not establish generalization across independent days or radar systems.",
                  "", "No speed, width, SCR, null filtering, steering direction or timing endpoint was retuned. Comparisons at nominal alpha must be read beside each method's measured false-alarm rate. Outputs include source NPZ hashes and aggregate per-unit counts; provider raw-bin caches and per-window raw provider values remain local.", ""])
    destinations[6].write_text("\n".join(lines), encoding="utf-8")
    print(json.dumps(dict(units=28, acquisition_windows=n, conditions=24, methods=8,
                          M2_methods_met=summary["checks"]["M2_methods_within_half_to_twice_design"], output=str(output)), indent=2))


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--input", type=Path, default=runner.ROOT/"study"/"results"/"r22_migration")
    parser.add_argument("--output", type=Path, default=runner.ROOT/"study"/"results"/"r22_migration"/"summary")
    parser.add_argument("--config", type=Path, default=HERE/"migration_config_draft.json")
    parser.add_argument("--freeze", type=Path, default=HERE/"MIGRATION_FREEZE.json")
    parser.add_argument("--check-mechanics", action="store_true")
    args = parser.parse_args()
    if args.check_mechanics:
        check_mechanics()
        return
    cfg = json.loads(args.config.read_text(encoding="utf-8"))
    freeze = runner.require_frozen(args.config, args.freeze)
    analyze(args.input, args.output, cfg, freeze)


if __name__ == "__main__":
    main()
