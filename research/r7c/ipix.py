"""IPIX Dartmouth 1993 stare files: loading, McMaster preprocessing, episode construction.

Source: https://soma.ece.mcmaster.ca/ipix/dartmouth/datasets.html (free research use; cite the
site). Preprocessing follows the McMaster 'auto' recipe (cdfhowto.html / ipixload.m):
per range bin and channel, remove the mean and standard deviation of I and Q separately, then
remove the I/Q phase imbalance: sin(beta) = 2<I,Q>/N (after standardisation),
I_rot = (I - Q sin beta)/sqrt(1 - sin^2 beta).
Range bins listed as primary/secondary target bins on the site, plus one guard bin on each
side, are excluded from clutter-only episodes (1-based table converted to 0-based).
"""
import os
import numpy as np
from scipy.io import netcdf_file

RAW = os.path.join(os.path.dirname(__file__), "data", "raw")

# file number -> (file stem, date, 1-based secondary target bins lo:hi, primary)
FILES = {
    17: ("19931107_135603_starea", "1993-11-07", (8, 11), 9),
    18: ("19931107_141630_starea", "1993-11-07", (8, 11), 9),
    19: ("19931107_145028_starea", "1993-11-07", (7, 9), 8),
    25: ("19931108_213827_starea", "1993-11-08", (6, 8), 7),
    26: ("19931108_220902_starea", "1993-11-08", (6, 8), 7),
    30: ("19931109_191449_starea", "1993-11-09", (6, 8), 7),
    31: ("19931109_202217_starea", "1993-11-09", (6, 9), 7),
    40: ("19931110_001635_starea", "1993-11-10", (5, 8), 7),
    54: ("19931111_163625_starea", "1993-11-11", (7, 10), 8),
    280: ("19931118_023604_stareC0000", "1993-11-18", (7, 10), 8),
    283: ("19931118_035737_stareC0000", "1993-11-18", (8, 12), 10),
    310: ("19931118_162155_stareC0000", "1993-11-18", (6, 9), 7),
    311: ("19931118_162658_stareC0000", "1993-11-18", (6, 9), 7),
    320: ("19931118_174259_stareC0000", "1993-11-18", (6, 9), 7),
}
NRANGE = 14


def _preprocess(I, Q):
    I = (I - I.mean(0)) / I.std(0)
    Q = (Q - Q.mean(0)) / Q.std(0)
    # McMaster: sin(beta) = 2 (I,Q)/A^2, A^2 = mean squared amplitude (= 2 after standardisation)
    sb = 2 * np.mean(I * Q, axis=0) / np.mean(I ** 2 + Q ** 2, axis=0)
    I = (I - Q * sb) / np.sqrt(1 - sb ** 2)
    return I + 1j * Q, np.degrees(np.arcsin(sb))


def load(number, keep="clutter", guard=1):
    """Return dict with complex arrays z[pol] of shape (131072, nbins) and bin indices.
    keep='clutter': exclude target secondary bins +/- guard; keep='target': primary bin only."""
    stem, date, (lo, hi), prim = FILES[number]
    f = netcdf_file(os.path.join(RAW, stem + ".cdf"), "r", mmap=False)
    A = f.variables["adc_data"][:].astype(np.float64)
    A = np.where(A < 0, A + 256, A)          # stored as signed bytes; data are unsigned ADC counts
    gi = lambda k: int(f.variables[k].getValue())
    iI, iQ = gi("adc_like_I"), gi("adc_like_Q")
    if keep == "clutter":
        excl = set(range(lo - 1 - guard, hi + guard))   # 0-based, inclusive guard
        bins = [b for b in range(NRANGE) if b not in excl]
    else:
        bins = [prim - 1]
    out = dict(number=number, date=date, bins=bins, z={}, imbalance_deg={})
    for tx in range(A.shape[1]):
        z, imb = _preprocess(A[:, tx, :, iI], A[:, tx, :, iQ])
        out["z"][f"like{tx}"] = z[:, bins]
        out["imbalance_deg"][f"like{tx}"] = imb[bins]
    f.close()
    return out


def episodes(z, t0, t1, m, stride):
    """Episodes of m+1 consecutive pulses from every bin, starts in [t0, t1-m-1] every `stride`.
    Returns X (n, m+1) and the start index and bin of each row."""
    starts = np.arange(t0, t1 - m, stride)
    idx = starts[:, None] + np.arange(m + 1)[None, :]
    E = z[idx]                                   # (S, m+1, B)
    S, _, B = E.shape
    X = np.transpose(E, (0, 2, 1)).reshape(S * B, m + 1)
    return X, np.repeat(starts, B), np.tile(np.arange(B), S)
