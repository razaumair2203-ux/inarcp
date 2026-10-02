#!/usr/bin/env bash
# Fetch the 14 monostatic (node 3) HH and VV NetRAD recordings of 9 June 2011 from the UCL Figshare archive
# (DOI 10.5522/04/32676582, CC BY-NC 4.0) by HTTP range requests, one zip member at a time, with CRC check.
cd "$(dirname "$0")/raw" || exit 1
for t in 1113_58 1118_34 1123_49 1128_12 1132_56 1139_49 1146_48 1446_21 1450_16 1457_22 1501_53 1508_24 1512_14 1518_58; do
  out="N3_${t}.mat"
  [ -f "$out.ok" ] && continue
  for try in 1 2 3; do
    python ../netrad_extract_member.py "NetRAD/N3/e11_06_09_${t}_P1_1_130000_S0_1_2047_node3_MF_refsig.mat" "$out" > "$out.log" 2>&1
    if grep -q "CRC ok" "$out.log"; then touch "$out.ok"; echo "$out ok"; break; fi
    echo "$out retry $try"
  done
done
sha256sum N3_*.mat > SHA256SUMS
echo done
