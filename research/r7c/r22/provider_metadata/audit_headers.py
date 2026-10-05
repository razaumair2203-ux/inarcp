"""Read acquisition headers only; never load ADC/Data_matched samples or fit a model."""
from pathlib import Path
import hashlib
import json

from scipy.io import netcdf_file, whosmat

HERE = Path(__file__).resolve().parent
ROOT = HERE.parents[1]


def serial(value):
    if isinstance(value, bytes):
        return value.decode("utf-8", errors="replace")
    if isinstance(value, dict):
        return {key: serial(item) for key, item in value.items()}
    if hasattr(value, "tolist"):
        return value.tolist()
    return value


ipix = []
for path in sorted((ROOT / "data" / "raw").glob("*.cdf")):
    with netcdf_file(path, "r", mmap=False) as file:
        variables = {}
        for name in ("PRF", "RF_frequency", "Pulse_length", "range"):
            var = file.variables[name]
            variables[name] = dict(value=serial(var[:] if var.shape else var.getValue()),
                                   attributes=serial(var._attributes))
        ipix.append(dict(filename=path.name, dimensions=file.dimensions,
                         tx_polarization=serial(file._attributes["TX_polarization"]),
                         metadata=variables))
netrad = []
for path in sorted((ROOT / "data" / "netrad" / "raw").glob("*.mat")):
    netrad.append(dict(filename=path.name, bytes=path.stat().st_size,
                       variables=[dict(name=name, shape=shape, matlab_class=kind)
                                  for name, shape, kind in whosmat(path)]))
sources = {path.name: hashlib.sha256(path.read_bytes()).hexdigest()
           for path in HERE.iterdir() if path.suffix in (".m", ".xlsx", ".json")
           and path.name != "METADATA_AUDIT.json"}
result = dict(contains_detector_outcomes=False, contains_new_sample_fits=False,
              source_archive="https://ndownloader.figshare.com/files/65710497",
              source_metadata_sha256=sources, ipix=ipix, netrad=netrad)
(HERE / "METADATA_AUDIT.json").write_text(json.dumps(result, indent=2), encoding="utf-8")
print(f"Audited headers for {len(ipix)} IPIX and {len(netrad)} NetRAD recordings; no sample outcomes.")
