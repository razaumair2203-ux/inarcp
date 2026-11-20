"""Independent, small simulation audit of the claims that the public package can test.

This is not a reproduction of the manuscript's learned-comparator experiments.
Run: python examples/audit_simulation.py --repetitions 400 --output audit.csv
"""
import argparse
import csv
import math

import numpy as np
from scipy.stats import t

from inarcp import INARCP, history_scale


def episodes(rng, n, m, rho=0.8):
    x = rng.normal(size=(n, m + 1))
    for j in range(1, m + 1):
        x[:, j] = rho * x[:, j - 1] + math.sqrt(1 - rho**2) * x[:, j]
    return x[:, :-1], x[:, -1]


def bounds(center, scale, threshold):
    return np.column_stack((center - threshold * scale, center + threshold * scale))


def measurement(interval, truth):
    return (float(np.mean((truth >= interval[:, 0]) & (truth <= interval[:, 1]))),
            float(np.mean(interval[:, 1] - interval[:, 0])))


def run(seed=20260928, repetitions=400, n_train=1000, n_cal=199, n_test=500,
        m=4, alpha=0.1):
    """Return one row per independent model fit, scenario and method.

    Paired methods share the same generated episodes. Calibration and test
    episodes are independently generated; there is no overlap or tuning.
    """
    rng = np.random.default_rng(seed)
    rows = []
    for repetition in range(repetitions):
        train_h, train_y = episodes(rng, n_train, m)
        cal_h, cal_y = episodes(rng, n_cal, m)
        test_h, test_y = episodes(rng, n_test, m)
        model = INARCP(alpha=alpha).fit(train_h, train_y).calibrate(cal_h, cal_y)
        rho = model.rho_
        center_cal = rho * cal_h[:, -1]
        rms_cal = np.sqrt(np.mean(cal_h**2, axis=1))
        rank = math.ceil((n_cal + 1) * (1 - alpha))
        if rank > n_cal:
            raise ValueError("Finite-length comparison needs a finite conformal rank.")
        raw_scores = np.abs(cal_y - center_cal) / rms_cal
        raw_q = np.partition(raw_scores, rank - 1)[rank - 1]
        global_q = np.partition(np.abs(cal_y - center_cal), rank - 1)[rank - 1]
        for scenario, h, y in (("same", test_h, test_y),
                               ("whole_scale_x2", 2 * test_h, 2 * test_y),
                               ("future_only_x2", test_h, 2 * test_y)):
            center = rho * h[:, -1]
            methods = {
                "IN-ARCP": model.predict_interval(h),
                "AR+raw_RMS": bounds(center, np.sqrt(np.mean(h**2, axis=1)), raw_q),
                "AR+global": bounds(center, np.ones(len(h)), global_q),
                "equal_fit_Student": bounds(center, history_scale(h, rho),
                                             t.ppf(1 - alpha / 2, m)),
            }
            for method, interval in methods.items():
                coverage, length = measurement(interval, y)
                rows.append(dict(repetition=repetition, scenario=scenario,
                                 method=method, coverage=coverage, length=length))
    return rows


def summarize(rows):
    """Aggregate by fitted repetition, not by individual test observation."""
    out = []
    for scenario in sorted({r["scenario"] for r in rows}):
        for method in sorted({r["method"] for r in rows}):
            subset = [r for r in rows if r["scenario"] == scenario and r["method"] == method]
            cov = np.array([r["coverage"] for r in subset])
            length = np.array([r["length"] for r in subset])
            se = cov.std(ddof=1) / math.sqrt(len(cov)) if len(cov) > 1 else math.nan
            out.append((scenario, method, cov.mean(), 1.96 * se, length.mean()))
    return out


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--seed", type=int, default=20260928)
    parser.add_argument("--repetitions", type=int, default=400)
    parser.add_argument("--n-train", type=int, default=1000)
    parser.add_argument("--n-cal", type=int, default=199)
    parser.add_argument("--n-test", type=int, default=500)
    parser.add_argument("--m", type=int, default=4)
    parser.add_argument("--output", default="audit.csv")
    args = parser.parse_args()
    result = run(args.seed, args.repetitions, args.n_train,
                 args.n_cal, args.n_test, args.m)
    with open(args.output, "w", newline="") as stream:
        writer = csv.DictWriter(stream, fieldnames=result[0].keys())
        writer.writeheader()
        writer.writerows(result)
    for item in summarize(result):
        print("%s %-18s coverage %.4f +/- %.4f length %.4f" % item)
