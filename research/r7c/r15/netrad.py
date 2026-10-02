"""NetRAD (UCL/UCT, False Bay, 9 June 2011) node-3 monostatic recordings: loading and preprocessing (PROTOCOL_R15.md, Section 0).

Source: UCL Research Data Repository, DOI 10.5522/04/32676582 (CC BY-NC 4.0); fetched by data/netrad/fetch_netrad.sh.
Clutter cells: the providers' node-3 'bins with clutter cell' (NR_Range_Selection_June9.m), 1-based -> 0-based.
Preprocessing: drop trailing all-zero pulses; per clutter cell remove the complex mean and scale to unit mean power.
Hit mask: a pulse is hit when more than 10% of its 1024 range bins exceed ten times the bin's median power over the file.
Usage: python netrad.py   (converts every downloaded recording to data/netrad/proc/<tag>.npz; prints shapes only)
"""
import os, sys
import numpy as np

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
RAW = os.path.join(ROOT, "data", "netrad", "raw")
PROC = os.path.join(ROOT, "data", "netrad", "proc")

# tag -> (polarization, 1-based inclusive clutter bins)
FILES = {
    "1113_58": ("HH", 530, 630), "1118_34": ("HH", 430, 530), "1123_49": ("HH", 430, 530), "1128_12": ("HH", 400, 470),
    "1132_56": ("HH", 370, 440), "1139_49": ("HH", 360, 420), "1146_48": ("HH", 330, 380),
    "1446_21": ("VV", 541, 641), "1450_16": ("VV", 441, 541), "1457_22": ("VV", 401, 481), "1501_53": ("VV", 391, 461),
    "1508_24": ("VV", 381, 441), "1512_14": ("VV", 361, 401), "1518_58": ("VV", 321, 361),
}
HIT_FACTOR, HIT_FRACTION = 10.0, 0.10


def _read(tag):
    from scipy.io import loadmat
    D = loadmat(os.path.join(RAW, f"N3_{tag}.mat"), variable_names=["Data_matched"])["Data_matched"]
    return np.asarray(D)


def convert(tag):
    out = os.path.join(PROC, f"{tag}.npz")
    if os.path.exists(out):
        return out
    D = _read(tag)                                         # (pulses, 1024)
    nz = np.flatnonzero(np.any(D != 0, axis=1))
    T = int(nz[-1]) + 1 if len(nz) else 0
    dropped = D.shape[0] - T
    D = D[:T]
    P = np.abs(D) ** 2
    med = np.median(P, axis=0)
    hit = np.mean(P > HIT_FACTOR * med[None, :], axis=1) > HIT_FRACTION
    pol, lo, hi = FILES[tag]
    bins = np.arange(lo - 1, hi)                           # 1-based lo..hi inclusive -> 0-based lo-1..hi-1
    z = D[:, bins].astype(np.complex128)
    z = z - z.mean(0)
    z = z / np.sqrt(np.mean(np.abs(z) ** 2, 0))
    os.makedirs(PROC, exist_ok=True)
    tmp = out + ".tmp.npz"
    np.savez(tmp, z=z, bins=bins, hit=hit, dropped=dropped, raw_shape=np.array(D.shape), pol=pol)
    os.replace(tmp, out)
    print(f"{tag} {pol}: raw {D.shape[0] + dropped}x{D.shape[1]}, dropped {dropped} trailing zero pulses, clutter cells {len(bins)}", flush=True)
    return out


def load(tag):
    d = np.load(os.path.join(PROC, f"{tag}.npz"))
    return dict(z=d["z"], bins=list(d["bins"]), hit=d["hit"], pol=str(d["pol"]), dropped=int(d["dropped"]))


if __name__ == "__main__":
    tags = sys.argv[1:] or [t for t in FILES if os.path.exists(os.path.join(RAW, f"N3_{t}.mat.ok"))]
    for t in tags:
        convert(t)
