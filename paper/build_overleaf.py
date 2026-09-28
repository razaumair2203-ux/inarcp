"""Package the current manuscript and verified official IEEE dependencies.

Run from any directory after compiling manuscript.pdf and supplement.pdf.
The ZIP is self-contained; no dependency is fetched during an Overleaf build.
"""
from pathlib import Path
import hashlib
import json
import shutil
import zipfile
import fitz


ROOT = Path(__file__).resolve().parent
RELEASE = "2026-09-28_R6"


def digest(data):
    return hashlib.sha256(data).hexdigest()


def main():
    manuscript = fitz.open(ROOT / "manuscript.pdf")
    supplement = fitz.open(ROOT / "supplement.pdf")
    locations = {}
    for label, needle in [("Algorithm 1", "Algorithm 1 IN-ARCP"),
                          ("UML Figure 1", "FIGURE 1. UML sequence"),
                          ("Algorithm 2", "Algorithm 2 Prespecified")]:
        pages = [i + 1 for i, p in enumerate(manuscript) if needle in p.get_text()]
        assert len(pages) == 1, (label, pages)
        locations[label] = pages[0]
    location_text = "; ".join(f"{k} p.{v}" for k, v in locations.items())
    provenance = json.loads((ROOT / "template_provenance.json").read_text())
    contents = {}
    for name, expected in provenance["files"].items():
        data = (ROOT / ".ieee-template" / name).read_bytes()
        if digest(data) != expected:
            raise ValueError(f"Official template dependency mismatch: {name}")
        contents[name] = data
    source_names = ["manuscript.tex", "supplement.tex", "references.bib",
                    "algorithm_inarcp.tex", "algorithm_split.tex",
                    "author_biographies.tex", "sequence_diagram.tex",
                    "sequence_figure.tex", "results_section.tex",
                    "template_provenance.json"]
    for name in source_names:
        contents["main.tex" if name == "manuscript.tex" else name] = (ROOT / name).read_bytes()
    for folder in ["generated", "figures"]:
        for path in sorted((ROOT / folder).iterdir()):
            if path.suffix in {".tex", ".pdf", ".png"}:
                contents[path.relative_to(ROOT).as_posix()] = path.read_bytes()
    rc = (ROOT / "latexmkrc").read_text()
    # Root-level assets make the Overleaf project portable without a hidden cache.
    contents["latexmkrc"] = ("@default_files = ('main.tex');\n" +
        rc.replace('"./.ieee-template//:"', '"./:"')).encode()
    contents["README_OVERLEAF.txt"] = f"""IN-ARCP — IEEE Access — {RELEASE}

Upload this ZIP using Overleaf > New Project > Upload Project.
Select main.tex as Main document and pdfLaTeX as Compiler, then Recompile.
Expected: {len(manuscript)} manuscript pages; {location_text}.
Select supplement.tex to compile the {len(supplement)}-page supplementary document.

The official IEEE Access class and its fonts are included unchanged, verified
against the ZIP downloaded from IEEE's website on 28 September 2026.
See template_provenance.json for the official source and every dependency hash.

Edit main.tex for the article, algorithm_inarcp.tex / algorithm_split.tex for
the pseudocode, and sequence_diagram.tex for the UML. latexmkrc rebuilds the
diagram as a vector PDF automatically before compiling the article.

The compiled/ folder contains reference PDFs under distinct revision names.
Those are not the output of your new Overleaf build; download that from its PDF
viewer. No main.pdf is bundled, avoiding a stale output with the same filename.

Repository source: https://github.com/razaumair2203-ux/inarcp
R5 revises the scientific narrative, literature synthesis and figure presentation.
main.tex is byte-identical to paper/manuscript.tex at package creation.
This archive is an importable project, not an existing hosted Overleaf project.

Template/font rights and notices remain with their respective owners. The
repository MIT software license does not relicense those files or the paper.
No journal submission or acceptance is represented by this research draft.
""".encode()
    contents["validation/algorithm_description_checks.json"] = (
        ROOT.parent / "reproducibility/results/algorithm_description_checks.json").read_bytes()
    releases = ROOT / "releases"
    releases.mkdir(exist_ok=True)
    for source, label in [("manuscript.pdf", "INARCP_IEEE_Access"),
                          ("supplement.pdf", "INARCP_Supplement")]:
        name = f"{label}_{RELEASE}.pdf"
        shutil.copyfile(ROOT / source, releases / name)
        contents[f"compiled/{name}"] = (ROOT / source).read_bytes()
    contents["PACKAGE_SHA256SUMS"] = "".join(
        f"{digest(data)}  {name}\n" for name, data in sorted(contents.items())).encode()
    destination = releases / f"INARCP_Overleaf_IEEE_Access_{RELEASE}.zip"
    with zipfile.ZipFile(destination, "w", zipfile.ZIP_DEFLATED, compresslevel=9) as archive:
        for name, data in sorted(contents.items()):
            info = zipfile.ZipInfo(name, date_time=(2026, 9, 28, 12, 0, 0))
            info.compress_type = zipfile.ZIP_DEFLATED
            info.external_attr = 0o100644 << 16
            archive.writestr(info, data)
    print(f"Created {destination.name}: {len(contents)} files, {destination.stat().st_size} bytes")


if __name__ == "__main__":
    main()
