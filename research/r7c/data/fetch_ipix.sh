#!/bin/sh
# Fetch IPIX Dartmouth 1993 stare files + documentation pages. Terms: free research use,
# cite https://soma.ece.mcmaster.ca/ipix/ and inform the McMaster group of results.
set -e
B=https://soma.ece.mcmaster.ca/ipix/dartmouth
cd "$(dirname "$0")/raw"
curl -s -m 120 -o datasets.html $B/datasets.html
curl -s -m 120 -o cdfhowto.html $B/cdfhowto.html
for f in 19931107_135603_starea 19931107_141630_starea 19931107_145028_starea 19931108_213827_starea \
         19931108_220902_starea 19931109_191449_starea 19931109_202217_starea 19931110_001635_starea \
         19931111_163625_starea 19931118_023604_stareC0000 19931118_035737_stareC0000 \
         19931118_162155_stareC0000 19931118_162658_stareC0000 19931118_174259_stareC0000; do
  [ -s $f.cdf ] || curl -s -m 1200 --retry 3 -o $f.cdf $B/data/$f.cdf
  echo "$f $(stat -c %s $f.cdf)"
done
sha256sum *.cdf *.html > SHA256SUMS
