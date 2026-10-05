"""R22 long guard trajectories, with the R14 score and fixed clean calibration.

Empirical entry points require the frozen R22 protocol hash. Mathematical and
indexing helpers are data-independent and can be checked before registration.
No fitting is performed here: the caller supplies the training-third AR(1) fit.
"""
from __future__ import annotations

from dataclasses import dataclass
import hashlib
from pathlib import Path
import math
import sys
import json
import os
import time
import platform

import numpy as np

HERE = Path(__file__).resolve().parent
ROOT = HERE.parent
sys.path.insert(0, str(ROOT))
from methods import conformal_quantile


@dataclass(frozen=True)
class GuardSettings:
    m: int = 16
    guards: tuple[int, ...] = (0, 8, 16)
    max_look: int = 48
    onset: int = 32
    calibration_length: int = 41
    calibration_stride: int = 41
    test_stride: int = 81
    alphas: tuple[float, ...] = (0.01,)
    detection_alpha: float = 0.01
    scr_db: tuple[float, ...] = (10.0, 20.0)
    onset_scr_db: tuple[float, ...] = ()
    batch_size: int = 4096
    texture_half: int = 1024
    law_draw_limit: int = 2000
    windows: tuple[tuple[int, int], ...] = ((1, 8), (9, 16), (17, 24), (25, 32), (41, 48))

    @property
    def segment_length(self):
        return self.onset + self.max_look + 1

    def validate(self):
        if self.m < 2 or not self.guards or any(g < 0 for g in self.guards):
            raise ValueError("m >= 2 and nonnegative guards are required")
        if self.onset < self.m + max(self.guards):
            raise ValueError("onset must leave enough pre-onset history")
        if self.max_look < 0 or self.calibration_length <= self.onset:
            raise ValueError("invalid look range or calibration segment length")
        if min(self.calibration_stride, self.test_stride, self.batch_size) <= 0:
            raise ValueError("strides and batch_size must be positive")
        if self.detection_alpha not in self.alphas:
            raise ValueError("detection_alpha must have a registered clean threshold")
        if any(not 0 < a < 1 for a in self.alphas):
            raise ValueError("alphas must lie in (0, 1)")


def require_frozen(protocol_sha: str, protocol_path: Path | None = None):
    """Require the caller's registration hash, protocol bytes, and saved hash to agree."""
    path = Path(protocol_path) if protocol_path else HERE / "PROTOCOL_R22_G.md"
    saved = path.with_suffix(".sha256")
    if not protocol_sha or not path.is_file() or not saved.is_file():
        raise RuntimeError("Empirical R22 outcomes require a frozen protocol and hash")
    actual = hashlib.sha256(path.read_bytes()).hexdigest()
    if actual != protocol_sha or saved.read_text().split()[0] != protocol_sha:
        raise RuntimeError("R22 protocol hash mismatch; no outcomes computed")
    return actual


def _geometry(length, onset, looks, guards, m):
    looks = np.asarray(looks, dtype=int)
    guards = np.asarray(guards, dtype=int)
    t = onset + looks
    a = t[None, :] - guards[:, None] - m
    if (looks < 0).any() or (guards < 0).any() or (a < 0).any():
        raise ValueError("all tested and scale indices must be nonnegative")
    if not len(looks) or not len(guards) or t.max() >= length or t.min() < 1:
        raise ValueError("segment does not contain the requested tests")
    return t, a


def _scale_sums(sample_power, innovation_power, a, m, r):
    # innovation_power[:, j] is the innovation at sample j+1. For a window
    # a..a+m-1, internal innovations are a+1..a+m-1, i.e. powers a..a+m-2.
    prefix = np.column_stack((np.zeros(len(sample_power)), np.cumsum(innovation_power, axis=1)))
    return ((1 - abs(r) ** 2) * sample_power[:, a]
            + prefix[:, a + m - 1] - prefix[:, a])


def guard_scores(segments, r, *, onset=32, looks=range(49), guards=(0, 8, 16), m=16):
    """Exact R14 squared score, returned as (guard, segment, look).

    The scale is rebuilt from each window, including its stationary first-sample
    term. Using a globally computed first innovation for that term is incorrect.
    """
    segments = np.asarray(segments)
    if segments.ndim != 2 or not np.isfinite(r) or abs(r) >= 1:
        raise ValueError("2D segments and a finite stable AR(1) coefficient required")
    t, a = _geometry(segments.shape[1], onset, looks, guards, m)
    ep = abs(segments[:, 1:] - r * segments[:, :-1]) ** 2
    scale = _scale_sums(abs(segments) ** 2, ep, a, m, r)
    if (scale <= 0).any():
        raise FloatingPointError("nonpositive innovation scale")
    return np.transpose(m * ep[:, t - 1][..., None] / np.transpose(scale, (0, 2, 1)), (2, 0, 1))


def score_polynomials(segments, target, r, *, onset=32, looks=range(49), guards=(0, 8, 16), m=16):
    """Coefficients for exact scores of segments + c*target (real c).

    Return numerator (3, segment, look) and denominator (3, guard, segment,
    look), in ascending powers of c. This avoids repeating complex filtering
    for each SCR and retains the same Swerling draw across every guard and SCR.
    """
    segments, target = np.asarray(segments), np.asarray(target)
    if target.shape != segments.shape or segments.ndim != 2:
        raise ValueError("target and segment shapes must agree")
    t, a = _geometry(segments.shape[1], onset, looks, guards, m)
    ec = segments[:, 1:] - r * segments[:, :-1]
    et = target[:, 1:] - r * target[:, :-1]
    pp = (abs(segments) ** 2, 2 * np.real(np.conj(segments) * target), abs(target) ** 2)
    ep = (abs(ec) ** 2, 2 * np.real(np.conj(ec) * et), abs(et) ** 2)
    num = np.stack([m * x[:, t - 1] for x in ep])
    den = np.stack([np.transpose(_scale_sums(x, y, a, m, r), (1, 0, 2))
                    for x, y in zip(pp, ep)])
    return num, den


def evaluate_polynomials(numerator, denominator, scr_linear):
    c = math.sqrt(scr_linear)
    num = numerator[0] + c * numerator[1] + scr_linear * numerator[2]
    den = denominator[0] + c * denominator[1] + scr_linear * denominator[2]
    if (den <= 0).any():
        raise FloatingPointError("nonpositive target-contaminated innovation scale")
    return num[None, ...] / den


def target_energies(profile, r, scr_linear, *, onset=32, looks=range(49), guards=(0, 8, 16), m=16):
    """Whitened target energies for an arbitrary complex profile at every look.

    Profile can be (time,) or (draw,time), with unit SCR scaling before the
    Swerling CN(0,1) amplitude. The stationary, noise-free true-AR(1) model
    gives innovation variance P*(1-|r|^2). This is not a fitted real-data law.
    """
    profile = np.atleast_2d(profile)
    if not np.isfinite(r) or abs(r) >= 1 or scr_linear < 0:
        raise ValueError("stable coefficient and nonnegative SCR required")
    t, a = _geometry(profile.shape[1], onset, looks, guards, m)
    ep = abs(profile[:, 1:] - r * profile[:, :-1]) ** 2
    sw = scr_linear / (1 - abs(r) ** 2)
    e0 = sw * ep[:, t - 1]
    eh = sw * np.transpose(_scale_sums(abs(profile) ** 2, ep, a, m, r), (1, 0, 2))
    return e0, eh


def rank_one_probability(e0, eh, beta, m=16):
    """Exact marginal detection law for independent unit clutter innovations.

    e0 and eh broadcast; beta is the squared score threshold divided by m.
    This remains valid at full scale contamination if energies are calculated
    from the actual window. It does not establish an acquisition-probability law.
    """
    e0, eh = np.broadcast_arrays(np.asarray(e0, float), np.asarray(eh, float))
    if beta <= 0 or m < 1 or (e0 < 0).any() or (eh < 0).any():
        raise ValueError("positive threshold and nonnegative energies required")
    b = 1 + e0 - beta * (1 + eh)
    c = beta * (1 + e0 + eh)
    disc = np.sqrt(b * b + 4 * c)
    # The alternate root avoids catastrophic cancellation for strong histories.
    lp = np.array((b + disc) / 2, copy=True)
    np.divide(2 * c, disc - b, out=lp, where=b < 0)
    lm = -c / lp
    return np.exp(np.log(lp) - np.log(lp - lm) - (m - 1) * np.log1p(beta / lp))


def abrupt_profile(omega, length=81, onset=32):
    t = np.arange(length) - onset
    return (t[None, :] >= 0) * np.exp(1j * np.atleast_1d(omega)[:, None] * t[None, :])


def segment_starts(block, length, stride):
    """Preserve R14's exclusive final start (rather than changing its sampling)."""
    return np.arange(block[0], block[1] - length, stride, dtype=int)


def segment_layout(z, block, length, stride):
    st = segment_starts(block, length, stride)
    return np.repeat(st, z.shape[1]), np.tile(np.arange(z.shape[1]), len(st))


def local_power(z, starts, bins, length, half=1024):
    """R14 texture proxy, excluding the entire segment, with native file length.

    This reproduces run_study.texture_proxy(..., m=length-1, half=1024),
    including its file-edge clipping. It avoids mutable run_study.T globals.
    """
    pp = abs(z) ** 2
    cs = np.vstack((np.zeros((1, z.shape[1])), np.cumsum(pp, axis=0)))
    lo = np.clip(starts - half, 0, len(z))
    hi = np.clip(starts + length + half, 0, len(z))
    tot = cs[hi, bins] - cs[lo, bins] - (cs[starts + length, bins] - cs[starts, bins])
    return tot / (hi - lo - length)


def _batches(z, starts, bins, length, batch_size):
    ix = np.arange(length)
    for a in range(0, len(starts), batch_size):
        b = min(a + batch_size, len(starts))
        yield a, b, z[starts[a:b, None] + ix[None, :], bins[a:b, None]]


def run_guard_study(z, r, calibration_block, test_block, seed, *, protocol_sha,
                    settings=GuardSettings(), protocol_path=None):
    """Calibrate once, then retain null and target marginal/acquisition counts.

    Count arrays are integers and denominators are saved; recording/day cluster
    aggregation is deliberately left to the R22 reporting infrastructure. No
    sample independence or acquisition false-alarm guarantee is asserted.
    """
    require_frozen(protocol_sha, protocol_path)
    settings.validate()
    cfg = settings
    kw = dict(onset=cfg.onset, looks=range(cfg.max_look + 1), guards=cfg.guards, m=cfg.m)
    cs, cb = segment_layout(z, calibration_block, cfg.calibration_length, cfg.calibration_stride)
    ts, tb = segment_layout(z, test_block, cfg.segment_length, cfg.test_stride)
    if not len(cs) or not len(ts):
        raise ValueError("both calibration and test blocks require full segments")
    cal = np.empty((len(cfg.guards), len(cs)))
    for a, b, seg in _batches(z, cs, cb, cfg.calibration_length, cfg.batch_size):
        cal[:, a:b] = guard_scores(seg, r, **{**kw, "looks": (0,)})[:, :, 0]
    q = np.array([[conformal_quantile(row, alpha) for alpha in cfg.alphas] for row in cal])
    if not np.isfinite(q).all():
        raise ValueError("calibration count cannot resolve a registered alpha")
    n, nl, ng = len(ts), cfg.max_look + 1, len(cfg.guards)
    null_look = np.zeros((ng, len(cfg.alphas), nl), dtype=np.int64)
    null_acq = np.zeros_like(null_look)
    null_window_acq = np.zeros((ng, len(cfg.alphas), len(cfg.windows)), dtype=np.int64)
    target_look = np.zeros((3, len(cfg.scr_db), ng, nl), dtype=np.int64)
    target_acq = np.zeros_like(target_look)
    target_window_acq = np.zeros((3, len(cfg.scr_db), ng, len(cfg.windows)), dtype=np.int64)
    onset_counts = np.zeros((len(cfg.onset_scr_db), ng), dtype=np.int64)
    rng = np.random.default_rng(seed)
    amp = np.sqrt(.5) * (rng.standard_normal(n) + 1j * rng.standard_normal(n))
    omegas = (rng.uniform(-np.pi, np.pi, n), np.full(n, np.angle(r)),
              np.full(n, np.angle(r) + np.pi))
    powers = local_power(z, ts, tb, cfg.segment_length, cfg.texture_half)
    if not np.isfinite(powers).all() or (powers <= 0).any():
        raise FloatingPointError("invalid local power for target injection")
    amplitude = np.sqrt(powers) * amp
    threshold = q[:, cfg.alphas.index(cfg.detection_alpha)]
    for a, b, seg in _batches(z, ts, tb, cfg.segment_length, cfg.batch_size):
        clean = guard_scores(seg, r, **kw)
        for j in range(len(cfg.alphas)):
            dec = clean > q[:, j, None, None]
            null_look[:, j] += dec.sum(axis=1)
            null_acq[:, j] += np.maximum.accumulate(dec, axis=2).sum(axis=1)
            for wi, (lo, hi) in enumerate(cfg.windows):
                null_window_acq[:, j, wi] += dec[:, :, lo:hi + 1].any(axis=2).sum(axis=1)
        for di, om in enumerate(omegas):
            u = abrupt_profile(om[a:b], cfg.segment_length, cfg.onset)
            base = amplitude[a:b, None] * u
            num, den = score_polynomials(seg, base, r, **kw)
            for si, sdb in enumerate(cfg.scr_db):
                sc = evaluate_polynomials(num, den, 10 ** (sdb / 10))
                dec = sc > threshold[:, None, None]
                target_look[di, si] += dec.sum(axis=1)
                target_acq[di, si] += np.maximum.accumulate(dec, axis=2).sum(axis=1)
                for wi, (lo, hi) in enumerate(cfg.windows):
                    target_window_acq[di, si, :, wi] += dec[:, :, lo:hi + 1].any(axis=2).sum(axis=1)
            if di == 0:
                for si, sdb in enumerate(cfg.onset_scr_db):
                    sc = evaluate_polynomials(num[:, :, :1], den[:, :, :, :1], 10 ** (sdb / 10))
                    onset_counts[si] += (sc[:, :, 0] > threshold[:, None]).sum(axis=1)
    # The registered plug-in law uses each guard's actual calibration threshold.
    # Plugging in r from real data is exploratory and ignores thermal noise,
    # fit error, texture variation within the segment, and non-AR dependence.
    beta = threshold[:, None, None] / cfg.m
    law = np.zeros((3, len(cfg.scr_db), ng, nl))
    law_n = min(n, cfg.law_draw_limit)
    for di, om in enumerate(omegas):
        for a in range(0, law_n, cfg.batch_size):
            b = min(a + cfg.batch_size, law_n)
            u = abrupt_profile(om[a:b], cfg.segment_length, cfg.onset)
            e0, eh = target_energies(u, r, 1.0, **kw)
            for si, sdb in enumerate(cfg.scr_db):
                s = 10 ** (sdb / 10)
                # Each guard has a different beta, so evaluate the scalar-threshold
                # formula guard by guard without changing the registered draws.
                for gi in range(ng):
                    law[di, si, gi] += rank_one_probability(s * e0, s * eh[gi], float(beta[gi, 0, 0]), cfg.m).sum(axis=0) / law_n
    return dict(guard_null_look_counts=null_look, guard_null_acquisition_counts=null_acq,
                guard_target_look_counts=target_look, guard_target_acquisition_counts=target_acq,
                guard_null_window_acquisition_counts=null_window_acq,
                guard_target_window_acquisition_counts=target_window_acq,
                guard_windows=np.asarray(cfg.windows),
                guard_onset_counts=onset_counts, guard_thresholds_squared=q,
                guard_law_ideal_plugin=law, guard_law_beta=beta,
                guard_law_n_draws=law_n,
                guard_n_calibration=len(cs), guard_n_test=n,
                guard_looks=np.arange(nl), guard_guards=np.asarray(cfg.guards),
                guard_alphas=np.asarray(cfg.alphas), guard_scr_db=np.asarray(cfg.scr_db),
                guard_onset_scr_db=np.asarray(cfg.onset_scr_db),
                guard_dopplers=np.asarray(("random", "matched", "opposite")),
                guard_test_starts=ts, guard_test_bins=tb,
                guard_random_omega=omegas[0], guard_swerling_amplitude=amp,
                guard_texture_power=powers, guard_seed=seed)


def file_sha256(path):
    h = hashlib.sha256()
    with Path(path).open("rb") as f:
        for chunk in iter(lambda: f.read(1024 * 1024), b""):
            h.update(chunk)
    return h.hexdigest()


def native_blocks(length):
    b1, b2 = length // 3, 2 * length // 3
    return {"A": (0, b1 - 2000), "B": (b1, b2 - 2000), "C": (b2, length)}


def _source_manifest():
    from ipix import FILES as IF
    sys.path.insert(0, str(ROOT / "r15"))
    from netrad import FILES as NF
    sources = {}
    for radar, folder, names in (
        ("IPIX", ROOT / "data" / "raw", {str(num): row[0] + ".cdf" for num, row in IF.items()}),
        ("NetRAD", ROOT / "data" / "netrad" / "raw", {tag: f"N3_{tag}.mat" for tag in NF})):
        registry = folder / "SHA256SUMS"
        recorded = {line.split()[-1].lstrip("*"): line.split()[0] for line in registry.read_text().splitlines() if line.strip()}
        for rec, name in names.items():
            raw = folder / name
            entry = dict(raw_path=str(raw), raw_bytes=raw.stat().st_size,
                         raw_mtime_ns=raw.stat().st_mtime_ns, raw_sha256=recorded[name],
                         identity_registry=str(registry), identity_registry_sha256=file_sha256(registry))
            if radar == "IPIX":
                actual = file_sha256(raw)
                if actual != recorded[name]:
                    raise RuntimeError(f"Raw IPIX identity mismatch: {name}")
                entry["raw_identity_check"] = "fresh SHA-256 matches saved registry"
            else:
                log = raw.with_suffix(".mat.log")
                if not raw.with_suffix(".mat.ok").exists() or "CRC ok" not in log.read_text():
                    raise RuntimeError(f"Missing verified extraction evidence for {name}")
                proc = ROOT / "data" / "netrad" / "proc" / f"{rec}.npz"
                entry.update(raw_identity_check="prior extraction CRC-ok/.ok and saved SHA-256; raw not rehashed",
                             extraction_log_sha256=file_sha256(log), processed_path=str(proc),
                             processed_bytes=proc.stat().st_size, processed_sha256=file_sha256(proc))
            sources[f"{radar}|{rec}"] = entry
    return sources


def _run_native_job(args):
    radar, rec, pol, rot, protocol_sha, source, code_sha, out_dir = args
    require_frozen(protocol_sha)
    cfg = GuardSettings()
    out = Path(out_dir) / f"g_{radar.lower()}_{rec}_{pol}_rot{rot}.npz"
    if out.exists():
        with np.load(out, allow_pickle=False) as old:
            if str(old["protocol_sha256"]) != protocol_sha or str(old["code_sha256"]) != code_sha:
                raise RuntimeError(f"Resume artifact has a different registration or implementation: {out}")
            return str(out), "resumed", float(old["seconds"])
    from ipix import load as iload, episodes, FILES as IF
    from methods import fit_ols, innovation_scale
    t0 = time.perf_counter()
    if radar == "IPIX":
        d = iload(int(rec)); z = d["z"][pol]
        bins = d["bins"]; day = IF[int(rec)][1]
        cluster = day
        previous = ROOT / "study" / "results" / "r14" / f"u_{rec}_{pol}_rot{rot}.npz"
    else:
        sys.path.insert(0, str(ROOT / "r15"))
        from netrad import load as nload
        d = nload(rec); z = d["z"]; bins = d["bins"]
        day = "2011-06-09"; cluster = rec
        previous = ROOT / "study" / "results" / "r15" / f"n_{rec}_rot{rot}.npz"
    roles = {2: ("B", "C", "A"), 3: ("C", "A", "B")}[rot]
    bl = native_blocks(len(z)); tr, ca, te = (bl[b] for b in roles)
    xtr, _, _ = episodes(z, *tr, cfg.m, 256)
    r = fit_ols(xtr)
    with np.load(previous, allow_pickle=False) as prev:
        oldr = complex(*prev["r"])
    r_error = abs(r - oldr)
    if r_error > 1e-14:
        raise RuntimeError(f"Training fit differs from R14/R15 for {out.name}: {r_error}")
    seed_string = f"R22|G|{radar}|{rec}|{pol}|{rot}"
    seed = int(hashlib.sha256(seed_string.encode()).hexdigest()[:8], 16)
    res = run_guard_study(z, r, ca, te, seed, protocol_sha=protocol_sha, settings=cfg)
    # Auditable direct score agreement on a fixed first-segment subset, not a
    # sample-dependent numerical check or selection rule.
    st, bi = segment_layout(z, te, cfg.segment_length, cfg.test_stride)
    xx = z[st[:10, None] + np.arange(cfg.segment_length), bi[:10, None]]
    fast = guard_scores(xx, r)
    direct = np.stack([np.column_stack([
        abs(xx[:, cfg.onset + l] - r * xx[:, cfg.onset + l - 1]) ** 2 /
        innovation_scale(xx[:, cfg.onset + l - g - cfg.m:cfg.onset + l - g], r) ** 2
        for l in range(cfg.max_look + 1)]) for g in cfg.guards])
    numerical_error = float(np.max(abs(fast - direct)))
    if not np.allclose(fast, direct, rtol=1e-11, atol=1e-11):
        raise RuntimeError(f"Direct score verification failed for {out.name}")
    res.update(r=np.array((r.real, r.imag)), radar=radar, recording=rec, polarization=pol,
               rotation=rot, day=day, cluster=cluster, native_bins=np.asarray(bins),
               native_T=len(z), native_B=z.shape[1], train_block=np.asarray(tr),
               calibration_block=np.asarray(ca), test_block=np.asarray(te),
               guard_seed_string=seed_string, protocol_sha256=protocol_sha, code_sha256=code_sha,
               source_identity_json=json.dumps(source, sort_keys=True),
               old_training_fit_absolute_error=r_error, direct_score_max_absolute_error=numerical_error,
               seconds=time.perf_counter() - t0)
    temp = out.with_suffix(".tmp.npz")
    np.savez_compressed(temp, **res)
    os.replace(temp, out)
    return str(out), "saved", res["seconds"]


def main():
    import argparse
    from concurrent.futures import ProcessPoolExecutor, wait, FIRST_COMPLETED
    from ipix import FILES as IF
    sys.path.insert(0, str(ROOT / "r15"))
    from netrad import FILES as NF
    ap = argparse.ArgumentParser(description=__doc__)
    ap.add_argument("--workers", type=int, default=4)
    ap.add_argument("--radar", choices=("IPIX", "NetRAD", "both"), default="both")
    args = ap.parse_args()
    if not 1 <= args.workers <= 8:
        ap.error("workers must be between 1 and 8")
    proto = HERE / "PROTOCOL_R22_G.md"
    protocol_sha = proto.with_suffix(".sha256").read_text().split()[0]
    require_frozen(protocol_sha)
    code_sha = file_sha256(__file__)
    out = ROOT / "study" / "results" / "r22_guard"
    out.mkdir(parents=True, exist_ok=True)
    print("R22-G source identities: verifying small IPIX files and hashing NetRAD processed files", flush=True)
    sources = _source_manifest()
    scripts = (__file__, HERE / "test_guard_study.py", ROOT / "ipix.py", ROOT / "methods.py", ROOT / "r15" / "netrad.py")
    manifest = dict(protocol_sha256=protocol_sha, started=time.strftime("%Y-%m-%d %H:%M:%S"),
                    python=sys.version, numpy=np.__version__, platform=platform.platform(),
                    workers=args.workers, settings=GuardSettings().__dict__, sources=sources,
                    code_sha256={str(p): file_sha256(p) for p in scripts}, output_directory=str(out),
                    requested_radar=args.radar)
    manifest_path = HERE / "R22_G_run_manifest.json"
    manifest_path.write_text(json.dumps(manifest, indent=2), encoding="utf-8")
    jobs = []
    if args.radar in ("IPIX", "both"):
        jobs += [("IPIX", str(rec), pol, rot) for rec in IF for pol in ("like0", "like1") for rot in (2, 3)]
    if args.radar in ("NetRAD", "both"):
        jobs += [("NetRAD", rec, row[0], rot) for rec, row in NF.items() for rot in (2, 3)]
    started = time.perf_counter(); done = 0; failures = []
    with ProcessPoolExecutor(max_workers=args.workers) as ex:
        pending = {ex.submit(_run_native_job, (*job, protocol_sha, sources[f"{job[0]}|{job[1]}"], code_sha, str(out))): job for job in jobs}
        while pending:
            finished, _ = wait(pending, timeout=30, return_when=FIRST_COMPLETED)
            if not finished:
                print(f"heartbeat: {done}/{len(jobs)} complete, {len(pending)} pending, elapsed {time.perf_counter() - started:.0f}s", flush=True)
            for future in finished:
                job = pending.pop(future)
                try:
                    path, status, seconds = future.result()
                    done += 1
                    print(f"{done}/{len(jobs)} {status} {Path(path).name} {seconds:.2f}s", flush=True)
                except Exception as error:
                    failures.append(dict(job=job, error=repr(error)))
                    print(f"FAILED {job}: {error!r}", flush=True)
    manifest.update(completed=done, failures=failures, finished=time.strftime("%Y-%m-%d %H:%M:%S"),
                    elapsed_seconds=time.perf_counter() - started)
    manifest_path.write_text(json.dumps(manifest, indent=2), encoding="utf-8")
    if failures:
        raise SystemExit(f"{len(failures)} units failed; see {manifest_path}")
    print(f"COMPLETE {done}/{len(jobs)} units; manifest {manifest_path}", flush=True)


if __name__ == "__main__":
    main()
