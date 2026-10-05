# UW dataset attribution and public reproduction

The source-derived camera class/track summaries, training means/gains and associated dataset summaries in `R22_R_SUMMARY.json` and `R22_R_METHOD_RECORD_COUNTS.csv` use the University of Washington dataset under **Creative Commons Attribution 4.0 International (CC BY 4.0)**. These files contain our registered processing/assessment of the source; raw records are not bundled.

Dataset citation: Xiangyu Gao, Guanbin Xing, Youchen Luo, Sumit Roy and Hui Liu (2022), *Raw ADC Data of 77GHz MMWave radar for Automotive Object Detection*, IEEE DataPort, [DOI 10.21227/xm40-jx59](https://doi.org/10.21227/xm40-jx59). Author order here follows the saved [primary DataCite registry metadata](https://api.datacite.org/dois/10.21227/xm40-jx59), reproduced as `provider_metadata/UW_DATACITE.json`. The [primary dataset page](https://ieee-dataport.org/documents/raw-adc-data-77ghz-mmwave-radar-automotive-object-detection) identifies `Automotive.zip` and CC BY 4.0 in its dataset JSON-LD. [License terms](https://creativecommons.org/licenses/by/4.0/).

The provider's [public raw release](https://github.com/Xiangyu-Gao/Raw_ADC_radar_dataset_for_automotive_object_detection) links the same archive and documents 128 samples, 255 chirps, 4 receivers and 2 transmitters. The DataCite abstract erroneously describes a different 12-transmitter/16-receiver carry-object recording; it is not the source for our waveform or archive identification. The author repository's MIT statement applies to its tool; dataset attribution follows the DOI's CC BY 4.0 terms.

Camera annotation provenance: Xiangyu Gao, Guanbin Xing, Sumit Roy and Hui Liu (2021), *RAMP-CNN: A Novel Neural Network for Enhanced Automotive Radar Object Recognition*, IEEE Sensors Journal 21(4), 5119–5132, [DOI 10.1109/JSEN.2020.3036047](https://doi.org/10.1109/JSEN.2020.3036047). [Author paper, Sections IV-C and VI-A](https://arxiv.org/html/2011.08981v2), describes synchronized camera object/depth estimates and manual calibration. Unquantified depth and manual-correction error prevent treating every label as precise independent native-bin onset truth.

## Reproduction from a fresh clone

Run commands from the repository root. The public frozen manifest contains every selected archive member's HTTP offset, compressed size, CRC32, canonical relative destination and SHA256; the large original ZIP catalog/private review folder is unnecessary.

```powershell
python research/r7c/r22/download_uw.py --plan
python research/r7c/r22/download_uw.py
python research/r7c/r22/run_uw.py
```

Acquisition verifies the frozen manifest's hash against `UW_FREEZE.json`, downloads only the three fixed records' raw ADC and all camera labels, and verifies every member's CRC32 and SHA256. Existing correct members are reused. It never rewrites `UW_SOURCE_MANIFEST.json`; a separate receipt is written inside ignored `data/UW_R22/download_receipts/`. It requests approximately 1.35 GB and extracts approximately 2.81 GB. Source availability remains dependent on the provider.

`run_uw.py` verifies its frozen scientific code/config/source identities. It refuses to overwrite any previous Part R output/audit files. In a fresh clone, the immutable public result copy is `R22_R_SUMMARY.json`, outside the guarded run output directory; it is byte-identical to the original outcome JSON with SHA256 `305b6c6fcd0e2c54a97d647ecff8019797e950a939321f7359f94f3bbbd08147`.

The public result reports all registered failures: every aggregate-correlation gate failed, primary clean-entry denominators were zero, and background exceedance did not meet every registered descriptive bound. It does not establish whitening/onset superiority. [Complete result tables](R22_R_RESULTS.md) and [all 168 method/record/association/endpoint rows](R22_R_METHOD_RECORD_COUNTS.csv) preserve this interpretation.

Fabricated acquisition checks require no provider download:

```powershell
python -m unittest discover -s research/r7c/r22 -p test_download_uw.py -v
```
