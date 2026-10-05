# Rebuilding the compact supplement

For R22 run **`make_additional_validation.py`**, which calls the inherited compact
generator, then integrates the three registered studies, their complete tables
and the extended-guard figure. Running the inherited generator alone drops the
R22 evidence. See [R22 reproduction instructions](R22_REPRODUCTION.md).

The inherited `make_compact_supplement.py` uses preserved, hash-checked R19 text fragments in
`compact_inputs/` and the frozen JSON files under `research/r7c` in a full repository
clone. It also works in this workspace. It transforms saved results into readable
tables; it does not rerun radar experiments or bootstrap uncertainty.

The current Overleaf archives contain every input needed for typesetting and do
not require numerical generators. Compile the manuscript first and the supplement
twice when working locally; the standalone supplement archive carries the final
manuscript cross-reference file. Both archives are in `../UPLOAD_TRS/`.

Old raw-log layout generators remain in the archived packages. They must not
overwrite this compact source. Complete numerical logs remain indexed in the
supplement and available in the public repository. Existing proof text is retained.

`make_r18_outputs.py` obtains the sixteen-pulse guard onset cost from unrounded
saved R14 endpoints: 1.2 dB. See `GUARD_ROUNDING_CORRECTION.json`.
