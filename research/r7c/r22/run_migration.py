"""Gated idealized range-response/unknown-acquisition experiment on raw NetRAD clutter.

No real data are read or fitted without MIGRATION_FREEZE.json matching the protocol,
configuration and this script. --check-mechanics uses only deterministic fabricated arrays.
See migration_feasibility.md: this is not verified hardware-PSF or real-target validation.
"""
from __future__ import annotations

import argparse
import hashlib
import json
import os
from pathlib import Path
import sys
import time
import uuid

import numpy as np
from numpy.lib.stride_tricks import sliding_window_view
from scipy.io import loadmat

HERE = Path(__file__).resolve().parent
ROOT = HERE.parent
sys.path.insert(0, str(ROOT))
sys.path.insert(0, str(ROOT / "r15"))
from methods import conformal_quantile, fit_ols  # existing scalar/fit implementations
from netrad import FILES

C_LIGHT = 299792458.0
ROTATIONS = {2: ("B", "C", "A"), 3: ("C", "A", "B")}


def sha(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as stream:
        for chunk in iter(lambda: stream.read(1024 * 1024), b""):
            digest.update(chunk)
    return digest.hexdigest()


def require_frozen(config_path: Path, freeze_path: Path) -> dict:
    if not freeze_path.exists():
        raise RuntimeError("No MIGRATION_FREEZE.json: real-data computation is prohibited.")
    record = json.loads(freeze_path.read_text(encoding="utf-8"))
    protocol = (freeze_path.parent / record["protocol_file"]).resolve()
    for key, path in (("protocol_sha256", protocol), ("config_sha256", config_path),
                      ("runner_sha256", Path(__file__).resolve())):
        if record.get(key) != sha(path):
            raise RuntimeError(f"Frozen hash mismatch: {key}")
    dependencies = {name: sha(ROOT / name) for name in ("methods.py", "r15/netrad.py")}
    if record.get("dependency_sha256") != dependencies:
        raise RuntimeError("Frozen hash mismatch: imported existing method/loader source")
    return record


def validate_config(cfg: dict) -> None:
    if cfg["search_bins"] != 3:
        raise ValueError("This runner implements a fixed three-native-bin acquisition region.")
    m, k = cfg["history"], cfg["coherent_dwell"]
    required = max(max(cfg["guards"]) + m,
                   cfg["coherent_guard"] + m + k - 1,
                   cfg["self_normalized_dwell"])
    if cfg["prefix"] < required:
        raise ValueError("Prefix cannot support all reference histories and sliding dwells.")
    if not 1 <= cfg["os_rank"] <= m:
        raise ValueError("OS rank outside the history.")
    if cfg["doppler_bins"] < max(k, cfg["self_normalized_dwell"]):
        raise ValueError("Doppler grid must have at least the longest dwell's frequencies.")
    if not 0 <= cfg["crossing_look_min"] < cfg["crossing_look_max_exclusive"] <= cfg["search_looks"]:
        raise ValueError("Crossing-time interval outside the search.")
    if any(rotation not in ROTATIONS for rotation in cfg["rotations"]):
        raise ValueError("Only previously defined rotations 2 and 3 are supported.")
    if not 0 < cfg["alpha_acquisition"] < 1:
        raise ValueError("Acquisition alpha outside (0,1).")
    if any(not 0 < fraction <= 1 for fraction in cfg["effective_bandwidth_fractions"]):
        raise ValueError("Idealized bandwidth fraction outside (0,1].")


def blocks(total: int, gap: int) -> dict:
    one, two = total // 3, 2 * total // 3
    return {"A": (0, one - gap), "B": (one, two - gap), "C": (two, total)}


def native_groups(bins: np.ndarray, count: int) -> np.ndarray:
    if np.any(np.diff(bins) != 1):
        raise ValueError("Provider clutter region must contain contiguous native bins.")
    centers = np.rint(np.linspace(1, len(bins) - 2, count)).astype(int)
    groups = centers[:, None] + np.array([-1, 0, 1])[None, :]
    if len(np.unique(groups)) != groups.size:
        raise ValueError("Index-only selected groups overlap.")
    return groups


def read_raw(tag: str) -> dict:
    """Existing R15 transform; retain raw per-bin gains for a common physical target."""
    path = ROOT / "data" / "netrad" / "raw" / f"N3_{tag}.mat"
    raw = loadmat(path, variable_names=["Data_matched"])["Data_matched"]
    nz = np.flatnonzero(np.any(raw != 0, axis=1))
    total = int(nz[-1]) + 1 if len(nz) else 0
    pol, low, high = FILES[tag]
    bins = np.arange(low - 1, high)  # MATLAB 1-based to stored 0-based
    selected = np.array(raw[:total, bins], dtype=np.complex128, copy=True)
    raw_shape = raw.shape
    del raw
    means = selected.mean(axis=0)
    selected -= means
    gains = np.sqrt(np.mean(np.abs(selected) ** 2, axis=0))
    if np.any(gains <= 0) or not np.isfinite(gains).all():
        raise ValueError("Invalid fixed bin normalization gains.")
    selected /= gains
    return dict(z=selected, gains=gains, means=means, bins=bins, pol=pol,
                raw_shape=raw_shape, dropped=raw_shape[0] - total,
                raw_path=path, raw_sha256=sha(path))


def read_prepared(tag: str, cache_root: Path, record: dict) -> dict:
    directory = cache_root / tag
    with np.load(directory / "metadata.npz", allow_pickle=False) as packed:
        metadata = json.loads(str(packed["metadata_json"]))
        if metadata["freeze"] != record:
            raise RuntimeError(f"Prepared raw-bin cache has a different freeze: {tag}")
        arrays = {name: packed[name].copy() for name in ("gains", "means", "bins")}
    path = directory / "z.npy"
    if sha(path) != metadata["z_sha256"]:
        raise RuntimeError(f"Prepared raw-bin cache content hash mismatch: {tag}")
    return dict(z=np.load(path, mmap_mode="r", allow_pickle=False), **arrays,
                pol=metadata["pol"], raw_shape=tuple(metadata["raw_shape"]),
                dropped=metadata["dropped"], raw_path=Path(metadata["raw_path"]),
                raw_sha256=metadata["raw_sha256"])


def prepare_raw(tag: str, cache_root: Path, record: dict) -> None:
    """Run serially after freezing, before parallel scorers: bounded raw-load concurrency."""
    directory = cache_root / tag
    if (directory / "metadata.npz").exists():
        read_prepared(tag, cache_root, record)
        print(f"Verified prepared cache {tag}", flush=True)
        return
    directory.mkdir(parents=True, exist_ok=True)
    if (directory / "z.npy").exists():
        raise RuntimeError(f"Incomplete existing cache {tag}; do not silently overwrite it.")
    data = read_raw(tag)
    temporary = directory / "z.tmp.npy"
    np.save(temporary, data["z"], allow_pickle=False)
    metadata = dict(freeze=record, pol=data["pol"], raw_shape=data["raw_shape"],
                    dropped=data["dropped"], raw_path=str(data["raw_path"]),
                    raw_sha256=data["raw_sha256"], z_sha256=sha(temporary))
    os.replace(temporary, directory / "z.npy")
    save_atomic(directory / "metadata.npz",
                dict(metadata_json=np.array(json.dumps(metadata, sort_keys=True)),
                     gains=data["gains"], means=data["means"], bins=data["bins"]))
    print(f"Prepared {tag}: {data['z'].shape[0]} pulses, {data['z'].shape[1]} native bins", flush=True)


def training_rows(z: np.ndarray, block: tuple, m: int, stride: int) -> np.ndarray:
    starts = np.arange(block[0], block[1] - m, stride)
    indices = starts[:, None] + np.arange(m + 1)[None, :]
    return z[indices].transpose(0, 2, 1).reshape(-1, m + 1)


def geometry(z: np.ndarray, block: tuple, groups: np.ndarray, cfg: dict) -> dict:
    length = cfg["prefix"] + cfg["search_looks"]
    starts = np.arange(block[0], block[1] - length + 1, length)
    win_starts = np.repeat(starts, len(groups))
    group_index = np.tile(np.arange(len(groups)), len(starts))
    if not len(win_starts):
        raise ValueError("Recording split too short for a complete acquisition window.")
    return dict(starts=win_starts, groups=groups[group_index], group_index=group_index)


def windows(z: np.ndarray, geo: dict, rows: np.ndarray, cfg: dict) -> np.ndarray:
    times = geo["starts"][rows, None] + np.arange(cfg["prefix"] + cfg["search_looks"])[None, :]
    return z[times[:, :, None], geo["groups"][rows, None, :]]


def local_raw_power(z: np.ndarray, gains: np.ndarray, block: tuple,
                    geo: dict, cfg: dict) -> np.ndarray:
    """Clutter power outside the complete episode; all intervals stay in its split."""
    length, half = cfg["prefix"] + cfg["search_looks"], cfg["proxy_half_window"]
    power = np.abs(z) ** 2
    cumulative = np.vstack([np.zeros((1, z.shape[1])), power.cumsum(axis=0)])
    starts = geo["starts"]
    low, high = np.maximum(starts - half, block[0]), np.minimum(starts + length + half, block[1])
    central = geo["groups"][:, 1]
    sums = (cumulative[high, central] - cumulative[low, central]
            - cumulative[starts + length, central] + cumulative[starts, central])
    denominator = high - low - length
    if np.any(denominator <= 0):
        raise ValueError("No surrounding clutter available for a split-contained SCR proxy.")
    result = sums / denominator * gains[central] ** 2
    if not np.isfinite(result).all() or np.any(result <= 0):
        raise ValueError("Invalid surrounding clutter power; do not silently drop windows.")
    return result


def history_power(segment: np.ndarray, starts: np.ndarray, m: int, r: complex) -> tuple:
    hist = sliding_window_view(segment, m, axis=1)[:, starts, :, :]
    raw_power = np.abs(hist) ** 2
    innovative = ((1 - abs(r) ** 2) * raw_power[..., 0]
                  + np.sum(np.abs(hist[..., 1:] - r * hist[..., :-1]) ** 2, axis=-1)) / m
    return raw_power, innovative


def score_arrays(segment: np.ndarray, r: complex, cfg: dict) -> dict:
    """All methods output scores at the identical look endpoints, without timing oracle."""
    m, k = cfg["history"], cfg["coherent_dwell"]
    endpoint = cfg["prefix"] + np.arange(cfg["search_looks"])
    numerator = np.abs(segment[:, endpoint, :] - r * segment[:, endpoint - 1, :]) ** 2
    raw_numerator = np.abs(segment[:, endpoint, :]) ** 2
    tiny = np.finfo(float).tiny
    scores = {}
    for guard in cfg["guards"]:
        raw_hist, scale = history_power(segment, endpoint - guard - m, m, r)
        scores[f"IN-G{guard}"] = numerator / np.maximum(scale, tiny)
        scores[f"CA-G{guard}"] = raw_numerator / np.maximum(raw_hist.mean(axis=-1), tiny)
        order = np.partition(raw_hist, cfg["os_rank"] - 1, axis=-1)[..., cfg["os_rank"] - 1]
        scores[f"OS{cfg['os_rank']}-G{guard}"] = raw_numerator / np.maximum(order, tiny)
    # Steady-state target steering: d(omega)*exp(i*omega*j). d cancels exactly in
    # normalized matched-filter power, leaving DFT-bank energy / K. No step-onset
    # first-dwell steering and no target Doppler are provided.
    innovation = segment[:, 1:, :] - r * segment[:, :-1, :]
    dwell = sliding_window_view(innovation, k, axis=1)[:, endpoint - k, :, :]
    spectrum = np.fft.fft(dwell, n=cfg["doppler_bins"], axis=-1)
    coherent = np.max(np.abs(spectrum) ** 2, axis=-1) / k
    del spectrum
    _, scale = history_power(segment, endpoint - k + 1 - cfg["coherent_guard"] - m, m, r)
    scores[f"PAMF-H1-K{k}-G{cfg['coherent_guard']}"] = coherent / np.maximum(scale, tiny)
    # Persistent-target comparator: current-dwell energy rather than historical
    # energy normalizes the same coherent Doppler search. This explicitly named
    # N16 AR(1) variant is not the existing AR(4), K8 R12 implementation.
    n = cfg["self_normalized_dwell"]
    self_dwell = sliding_window_view(innovation, n, axis=1)[:, endpoint - n, :, :]
    self_spectrum = np.fft.fft(self_dwell, n=cfg["doppler_bins"], axis=-1)
    self_energy = np.sum(np.abs(self_dwell) ** 2, axis=-1)
    scores[f"P-ANMF1-N{n}"] = np.max(np.abs(self_spectrum) ** 2, axis=-1) / np.maximum(n * self_energy, tiny)
    return scores


def maxima_over_search(segment: np.ndarray, r: complex, cfg: dict) -> dict:
    return {name: score.max(axis=(1, 2)) for name, score in score_arrays(segment, r, cfg).items()}


def seed_for(tag: str, rotation: int, namespace: str) -> int:
    text = f"{namespace}|{tag}|{rotation}".encode()
    return int.from_bytes(hashlib.sha256(text).digest()[:8], "little")


def target_draws(n: int, tag: str, rotation: int, cfg: dict) -> dict:
    rng = np.random.default_rng(seed_for(tag, rotation, cfg["seed_namespace"]))
    amp = (rng.standard_normal(n) + 1j * rng.standard_normal(n)) / np.sqrt(2)
    crossing = rng.integers(cfg["crossing_look_min"], cfg["crossing_look_max_exclusive"], n)
    return dict(amplitude=amp, crossing=crossing)


def target_response(geo: dict, rows: np.ndarray, gains: np.ndarray, raw_power: np.ndarray,
                    draws: dict, speed: float, fraction: float, scr_db: float, cfg: dict) -> tuple:
    time_index = np.arange(cfg["prefix"] + cfg["search_looks"]) - cfg["prefix"]
    crossing = draws["crossing"][rows]
    # Coordinates relative to each group's central native-bin center; unknown
    # absolute provider node-zero offset cancels in the range differences.
    target_position = speed * (time_index[None, :] - crossing[:, None]) / cfg["look_rate_hz"]
    native_position = cfg["native_bin_spacing_m"] * np.array([-1, 0, 1])
    delta_range = native_position[None, None, :] - target_position[:, :, None]
    bandwidth = cfg["nominal_bandwidth_hz"] * fraction
    psf = np.sinc(2 * bandwidth * delta_range / C_LIGHT)
    doppler = -2 * cfg["carrier_hz"] * speed / C_LIGHT
    carrier_phase = np.exp(2j * np.pi * doppler * time_index / cfg["look_rate_hz"])
    amplitude = np.sqrt(10 ** (scr_db / 10) * raw_power[rows]) * draws["amplitude"][rows]
    transformed_gain = gains[geo["groups"][rows]]
    target = amplitude[:, None, None] * psf * carrier_phase[None, :, None] / transformed_gain[:, None, :]
    local = np.abs(delta_range[:, cfg["prefix"]:, :]) <= cfg["native_bin_spacing_m"]
    return target, local


def event_records(scores: dict, thresholds: dict, local: np.ndarray | None = None) -> dict:
    out = {}
    for name, score in scores.items():
        decisions = score > thresholds[name]
        any_by_look = decisions.any(axis=2)
        acquired = any_by_look.any(axis=1)
        first = np.where(acquired, any_by_look.argmax(axis=1), -1)
        event = dict(any=acquired.astype(np.uint8), first_look=first)
        if local is not None:
            local_by_look = (decisions & local).any(axis=2)
            local_acquired = local_by_look.any(axis=1)
            event["local"] = local_acquired.astype(np.uint8)
            event["first_local_look"] = np.where(local_acquired, local_by_look.argmax(axis=1), -1)
            # A declaration is the highest scoring native bin among those that
            # exceed at the first acquisition endpoint. Every detector uses this
            # same fixed bin-selection rule; ties follow np.argmax's native order.
            best = score[np.arange(len(score)), np.maximum(first, 0)].argmax(axis=1)
            event["first_is_local"] = (acquired & local[np.arange(len(score)), np.maximum(first, 0), best]).astype(np.uint8)
        out[name] = event
    return out


def collect_maxima(z: np.ndarray, geo: dict, r: complex, cfg: dict) -> dict:
    out = {}
    for lo in range(0, len(geo["starts"]), cfg["batch_windows"]):
        rows = np.arange(lo, min(lo + cfg["batch_windows"], len(geo["starts"])))
        values = maxima_over_search(windows(z, geo, rows, cfg), r, cfg)
        for name, value in values.items():
            if not np.isfinite(value).all():
                raise ValueError(f"Nonfinite {name} score maxima; report the failure, not selected windows.")
            out.setdefault(name, []).append(value)
    return {name: np.concatenate(parts) for name, parts in out.items()}


def save_atomic(path: Path, arrays: dict) -> None:
    tmp = path.with_name(path.name + ".tmp.npz")
    np.savez_compressed(tmp, **arrays)
    os.replace(tmp, path)


def run_unit(data: dict, tag: str, rotation: int, cfg: dict, record: dict, outdir: Path,
             job_id: str) -> None:
    path = outdir / f"migration_{tag}_rot{rotation}.npz"
    if path.exists():
        raise FileExistsError(f"Refusing to replace prior outcomes: {path}")
    started_utc = time.strftime("%Y-%m-%dT%H:%M:%SZ", time.gmtime())
    z, gains, bins = data["z"], data["gains"], data["bins"]
    split = blocks(len(z), cfg["split_gap"])
    train, calibration, test = (split[name] for name in ROTATIONS[rotation])
    r = fit_ols(training_rows(z, train, cfg["history"], cfg["train_stride"]))
    if not np.isfinite(r):
        raise ValueError("Nonfinite AR coefficient; do not silently replace the unit.")
    groups = native_groups(bins, cfg["groups_per_recording"])
    gc, gt = geometry(z, calibration, groups, cfg), geometry(z, test, groups, cfg)
    calibration_maxima = collect_maxima(z, gc, r, cfg)
    threshold = {name: conformal_quantile(value, cfg["alpha_acquisition"])
                 for name, value in calibration_maxima.items()}
    clean_maxima = collect_maxima(z, gt, r, cfg)
    raw_power = local_raw_power(z, gains, test, gt, cfg)
    draws = target_draws(len(gt["starts"]), tag, rotation, cfg)
    output = dict(native_bins=bins, native_groups=bins[groups], gains=gains, means=data["means"],
                  test_starts=gt["starts"], test_group_index=gt["group_index"],
                  crossing_look=draws["crossing"], target_amplitude=draws["amplitude"],
                  raw_proxy_power=raw_power, ar1_coefficient=np.array(r),
                  calibration_starts=gc["starts"], calibration_group_index=gc["group_index"])
    for name in threshold:
        output[f"threshold|{name}"] = np.array(threshold[name])
        output[f"calibration_maxima|{name}"] = calibration_maxima[name]
        output[f"null_maxima|{name}"] = clean_maxima[name]
        output[f"null_acquisition|{name}"] = (clean_maxima[name] > threshold[name]).astype(np.uint8)
    conditions = [(speed, fraction, scr) for speed in cfg["radial_speeds_m_s"]
                  for fraction in cfg["effective_bandwidth_fractions"] for scr in cfg["scr_db"]]
    for speed, fraction, scr in conditions:
        collection = {}
        for lo in range(0, len(gt["starts"]), cfg["batch_windows"]):
            rows = np.arange(lo, min(lo + cfg["batch_windows"], len(gt["starts"])))
            segment = windows(z, gt, rows, cfg)
            injection, local = target_response(gt, rows, gains, raw_power, draws, speed, fraction, scr, cfg)
            scores = score_arrays(segment + injection, r, cfg)
            if any(not np.isfinite(value).all() for value in scores.values()):
                raise ValueError("Nonfinite target scores; do not silently count them as misses.")
            events = event_records(scores, threshold, local)
            for name, event in events.items():
                for endpoint, values in event.items():
                    collection.setdefault((name, endpoint), []).append(values)
        condition = f"speed{speed:g}|band{fraction:g}|scr{scr:g}"
        for (name, endpoint), parts in collection.items():
            output[f"target|{condition}|{name}|{endpoint}"] = np.concatenate(parts)
    manifest = dict(tag=tag, rotation=rotation, execution_job_id=job_id, started_utc=started_utc,
                    finished_utc=time.strftime("%Y-%m-%dT%H:%M:%SZ", time.gmtime()),
                    freeze=record, config=cfg, splits=split, raw_shape=data["raw_shape"],
                    raw_sha256=data["raw_sha256"], raw_filename=data["raw_path"].name,
                    dropped=data["dropped"], calibration_windows=len(gc["starts"]),
                    test_windows=len(gt["starts"]), numpy_version=np.__version__,
                    conformal_rank=int(np.ceil((len(gc["starts"]) + 1) * (1 - cfg["alpha_acquisition"]))),
                    iid_rank_tail_mass=float((len(gc["starts"]) + 1 - np.ceil((len(gc["starts"]) + 1) * (1 - cfg["alpha_acquisition"]))) / (len(gc["starts"]) + 1)))
    output["manifest_json"] = np.array(json.dumps(manifest, sort_keys=True))
    save_atomic(path, output)
    print(f"Saved {path.name}: {len(gt['starts'])} acquisition windows", flush=True)


def check_mechanics(cfg: dict) -> None:
    """Shape/index/physics checks only; no random fit, calibration or detection rates."""
    validate_config(cfg)
    t = np.arange(cfg["prefix"] + cfg["search_looks"])
    base = (1 + t[:, None] / 10000) * np.exp(0.13j * t[:, None]) * np.array([1, 2, 3])[None, :]
    segment = base[None, :, :]
    r = 0.5 + 0.2j
    arrays = score_arrays(segment, r, cfg)
    assert all(array.shape == (1, cfg["search_looks"], 3) for array in arrays.values())
    test_endpoint = cfg["prefix"] + 3
    history = segment[0, test_endpoint - cfg["guards"][0] - cfg["history"]:test_endpoint - cfg["guards"][0], 1]
    scale = ((1 - abs(r) ** 2) * abs(history[0]) ** 2 + np.sum(abs(history[1:] - r * history[:-1]) ** 2)) / cfg["history"]
    manual = abs(segment[0, test_endpoint, 1] - r * segment[0, test_endpoint - 1, 1]) ** 2 / scale
    np.testing.assert_allclose(arrays[f"IN-G{cfg['guards'][0]}"][0, 3, 1], manual)
    k = cfg["coherent_dwell"]
    dwell = segment[0, test_endpoint - k + 1:test_endpoint + 1, 1] - r * segment[0, test_endpoint - k:test_endpoint, 1]
    frequencies = 2 * np.pi * np.arange(cfg["doppler_bins"]) / cfg["doppler_bins"]
    manual_bank = abs(np.exp(-1j * frequencies[:, None] * np.arange(k)[None, :]) @ dwell) ** 2 / k
    _, pamf_scale = history_power(segment, np.array([test_endpoint - k + 1 - cfg["coherent_guard"] - cfg["history"]]), cfg["history"], r)
    name = f"PAMF-H1-K{k}-G{cfg['coherent_guard']}"
    np.testing.assert_allclose(arrays[name][0, 3, 1], manual_bank.max() / pamf_scale[0, 0, 1])
    n = cfg["self_normalized_dwell"]
    self_dwell = segment[0, test_endpoint - n + 1:test_endpoint + 1, 1] - r * segment[0, test_endpoint - n:test_endpoint, 1]
    manual_self = abs(np.exp(-1j * frequencies[:, None] * np.arange(n)[None, :]) @ self_dwell) ** 2 / (n * np.sum(abs(self_dwell) ** 2))
    np.testing.assert_allclose(arrays[f"P-ANMF1-N{n}"][0, 3, 1], manual_self.max())
    for name, values in score_arrays(segment * (3 - 2j), r, cfg).items():
        np.testing.assert_allclose(values, arrays[name])
    geo = dict(groups=np.array([[0, 1, 2]]))
    draws = dict(amplitude=np.ones(1, complex), crossing=np.array([300]))
    target, local = target_response(geo, np.array([0]), np.array([1., 2., 4.]), np.array([5.]), draws, 5., 1., 10., cfg)
    at_crossing = cfg["prefix"] + 300
    np.testing.assert_allclose(abs(target[0, at_crossing, 1]) ** 2 * 4, 50.)
    assert local.shape == (1, cfg["search_looks"], 3)
    assert local[0, 300].all()
    # An alarm at the last search look is included; no post-onset gate suppresses it.
    fake = np.zeros((2, cfg["search_looks"], 3)); fake[0, -1, 2] = 2
    events = event_records({"fake": fake}, {"fake": 1.}, np.ones_like(fake, bool))["fake"]
    assert events["first_look"].tolist() == [cfg["search_looks"] - 1, -1]
    assert events["first_is_local"].tolist() == [1, 0]
    print("Deterministic fabricated-array mechanics passed. No real samples or detection rates computed.")


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--config", type=Path, default=HERE / "migration_config_draft.json")
    parser.add_argument("--freeze", type=Path, default=HERE / "MIGRATION_FREEZE.json")
    parser.add_argument("--output", type=Path, default=HERE / "migration_outcomes")
    parser.add_argument("--check-mechanics", action="store_true")
    parser.add_argument("--tags", nargs="+", help="Frozen-list subset for disjoint parallel recording jobs")
    parser.add_argument("--prepared-cache", type=Path, default=HERE / "migration_prepared")
    parser.add_argument("--prepare-only", action="store_true", help="Serial raw-bin cache preparation after freezing; no detector fitting/scoring")
    parser.add_argument("--require-prepared", action="store_true", help="Never fall back to a full raw MAT load")
    args = parser.parse_args()
    cfg = json.loads(args.config.read_text(encoding="utf-8"))
    validate_config(cfg)
    if args.check_mechanics:
        check_mechanics(cfg)
        return
    record = require_frozen(args.config, args.freeze)
    tags = args.tags or cfg["tags"]
    if len(tags) != len(set(tags)) or any(tag not in cfg["tags"] for tag in tags):
        raise ValueError("--tags must be a unique subset of the complete frozen recording list.")
    if args.prepare_only:
        for tag in tags:
            prepare_raw(tag, args.prepared_cache, record)
        return
    args.output.mkdir(parents=True, exist_ok=True)
    job_id = uuid.uuid4().hex
    for tag in tags:
        # Loading/scaling is intentionally below the freeze gate.
        if (args.prepared_cache / tag / "metadata.npz").exists():
            data = read_prepared(tag, args.prepared_cache, record)
        elif args.require_prepared:
            raise RuntimeError(f"No prepared cache for {tag}; parallel raw loading is prohibited.")
        else:
            data = read_raw(tag)
        for rotation in cfg["rotations"]:
            run_unit(data, tag, rotation, cfg, record, args.output, job_id)
        del data


if __name__ == "__main__":
    main()
