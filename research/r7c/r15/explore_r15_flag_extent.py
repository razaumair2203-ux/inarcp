"""EXPLORATORY (post hoc, after a blind review asked whether the NetRAD 'hits' could be sea spikes): range extent of the
flagged pulses. For each HH recording with flagged pulses, report how many of the 1024 range bins exceed ten times their
median in a flagged pulse, and what fraction of those bins lie outside the providers' clutter window.
Output: explore_r15_flag_extent_output.txt"""
import os, sys
HERE = os.path.dirname(os.path.abspath(__file__)); sys.path.insert(0, HERE)
import numpy as np
from netrad import FILES, _read, HIT_FACTOR, HIT_FRACTION

out = ["EXPLORATORY. Flagged pulses: number of range bins above 10x their median, and share of them outside the clutter window"]
for tag, (pol, lo, hi) in FILES.items():
    if pol != "HH":
        continue
    D = _read(tag); P = np.abs(D) ** 2; med = np.median(P, 0)
    exc = P > HIT_FACTOR * med[None, :]
    flag = exc.mean(1) > HIT_FRACTION
    win = np.zeros(D.shape[1], bool); win[lo - 1:hi] = True
    n_exc = exc[flag].sum(1); n_out = exc[flag][:, ~win].sum(1)
    # unflagged pulses with any exceedance inside the window (candidate sea spikes) for contrast
    spk = (~flag) & exc[:, win].any(1)
    n_spk = exc[spk].sum(1)
    out.append(f"{tag} HH: flagged {flag.mean():.4f} of pulses; elevated bins per flagged pulse median {np.median(n_exc):.0f} "
               f"(5-95%: {np.percentile(n_exc, 5):.0f}-{np.percentile(n_exc, 95):.0f}) of {D.shape[1]}, outside the {win.sum()}-bin window "
               f"{np.median(n_out / n_exc):.2f} (median share); unflagged pulses with an elevated window bin: elevated bins median {np.median(n_spk) if spk.any() else 0:.0f}")
    print(out[-1], flush=True)
open(os.path.join(HERE, "explore_r15_flag_extent_output.txt"), "w", encoding="utf8").write("\n".join(out) + "\n")
