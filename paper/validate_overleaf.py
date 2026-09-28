"""Compile the delivered ZIP in isolation and compare rendered reference pages."""
from pathlib import Path
import hashlib
import json
import os
import re
import subprocess
import tempfile
import zipfile
import fitz


ROOT = Path(__file__).resolve().parent
RELEASE = "2026-09-28_R6"


def digest(data):
    return hashlib.sha256(data).hexdigest()


def main():
    archive = ROOT / "releases" / f"INARCP_Overleaf_IEEE_Access_{RELEASE}.zip"
    result = {"release": RELEASE, "archive_sha256": digest(archive.read_bytes()),
              "validation": "Fresh local TeX Live extraction; not a hosted Overleaf run"}
    with tempfile.TemporaryDirectory(prefix="inarcp-overleaf-check-") as temporary:
        folder = Path(temporary)
        with zipfile.ZipFile(archive) as package:
            assert package.testzip() is None
            for name in package.namelist():
                assert not Path(name).is_absolute() and ".." not in Path(name).parts
            package.extractall(folder)
        entries = (folder / "PACKAGE_SHA256SUMS").read_text().splitlines()
        for line in entries:
            expected, name = line.split("  ", 1)
            assert digest((folder / name).read_bytes()) == expected, name
        result["verified_package_files"] = len(entries)
        assert (folder / "main.tex").read_bytes() == (ROOT / "manuscript.tex").read_bytes()
        assert not (folder / ".ieee-template").exists()
        # Force regeneration to prove the editable diagram is part of the build.
        (folder / "figures/sequence_diagram.pdf").unlink()
        environment = os.environ.copy()
        for key in ["TEXINPUTS", "TFMFONTS", "T1FONTS", "ENCFONTS", "TEXFONTMAPS", "BSTINPUTS"]:
            environment.pop(key, None)
        result["documents"] = {}
        for name, reference in [("main", "manuscript"), ("supplement", "supplement")]:
            process = subprocess.run(
                ["latexmk", "-pdf", "-interaction=nonstopmode", "-halt-on-error", f"{name}.tex"],
                cwd=folder, env=environment, stdout=subprocess.PIPE, stderr=subprocess.STDOUT,
                text=True, timeout=120)
            if process.returncode:
                raise RuntimeError(process.stdout[-8000:])
            log = (folder / f"{name}.log").read_text()
            failures = re.findall(r"^.*(?:Overfull|undefined|Warning|referenced but does not exist).*$", log, re.M)
            assert not failures, failures
            built = fitz.open(folder / f"{name}.pdf")
            original = fitz.open(ROOT / f"{reference}.pdf")
            assert not built.is_repaired and len(built) == len(original), (name, len(built), len(original), built.is_repaired, original.is_repaired, (folder / f"{name}.pdf").stat().st_size, (ROOT / f"{reference}.pdf").stat().st_size)
            raster_hashes = []
            for a, b in zip(built, original):
                assert a.rect == b.rect
                assert a.get_text() == b.get_text()
                # Compare every page at 96 dpi, including color and layout.
                pa = a.get_pixmap(matrix=fitz.Matrix(4/3, 4/3), alpha=False)
                pb = b.get_pixmap(matrix=fitz.Matrix(4/3, 4/3), alpha=False)
                assert pa.samples == pb.samples, f"Rendered mismatch in {name}, page {a.number+1}"
                raster_hashes.append(digest(pa.samples))
            item = {"pages": len(built), "text_and_render_match_reference": True,
                    "page_raster_sha256_at_96dpi": raster_hashes, "build_warnings": failures}
            if name == "main":
                targets = {"algorithm_1": "Algorithm 1 IN-ARCP", "uml_figure_1": "UML sequence of",
                           "algorithm_2": "Algorithm 2 Prespecified"}
                item["content_pages"] = {label: [i+1 for i, p in enumerate(built) if text in p.get_text()]
                                         for label, text in targets.items()}
                assert all(len(pages) == 1 for pages in item["content_pages"].values()), item["content_pages"]
            result["documents"][name] = item
        result["editable_diagram_rebuilt"] = (folder / "figures/sequence_diagram.pdf").stat().st_size > 0
    output = ROOT / "releases/overleaf_validation_R5.json"
    output.write_text(json.dumps(result, indent=2) + "\n")
    print("Fresh ZIP build verified:", {name: item["pages"] for name, item in result["documents"].items()})
    print("Content locations:", result["documents"]["main"]["content_pages"])


if __name__ == "__main__":
    main()
