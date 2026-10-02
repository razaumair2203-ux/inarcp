#!/usr/bin/env bash
# Convert NetRAD recordings as they arrive, then run R15 on all 28 units.
cd "$(dirname "$0")"
PY=../../../.venv/Scripts/python.exe
while true; do
  n=$(ls ../data/netrad/raw/*.mat.ok 2>/dev/null | wc -l)
  $PY netrad.py
  [ "$n" -ge 14 ] && [ "$(ls ../data/netrad/proc/*.npz 2>/dev/null | wc -l)" -ge 14 ] && break
  sleep 60
done
INARCP_GPU=1 $PY run_r15_netrad.py --workers 12 > run_r15_netrad.log 2>&1
echo "run exit $?"
