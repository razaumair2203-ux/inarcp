"""Build the two Overleaf containers from an empty folder, compile each one, and only then
write the ZIPs (CLAUDE.md rule 7).

The pinned IEEEtran.cls (V1.8b) and IEEEtran.bst (1.14) are carried over from the previous
container, which is the only copy of those exact versions in this tree.

Usage, from 03_submission_IEEE-TRS/:   python analysis_provenance/make_overleaf_zips.py
"""
import os
import re
import shutil
import subprocess
import sys
import tempfile
import zipfile
from pathlib import Path

HERE = os.path.dirname(os.path.abspath(__file__))
PKG = os.path.dirname(HERE)
OVER = os.path.join(PKG, "overleaf")
TAG = "R21"
# The pinned official IEEE class files, kept in the package so this script does not depend on
# an archived artifact. Extracted once from the R17 container in R18.
PINNED = os.path.join(OVER, "pinned")

UPLOAD = os.path.join(PKG, "UPLOAD_TRS")
os.makedirs(UPLOAD, exist_ok=True)
MAN_ZIP = os.path.join(UPLOAD, f"INARCP_{TAG}_manuscript_Overleaf.zip")
SUP_ZIP = os.path.join(UPLOAD, f"INARCP_{TAG}_supplement_Overleaf.zip")

MAN_README = f"""# IN-ARCP manuscript, Overleaf container ({TAG})

Upload as **New Project -> Upload Project**. Then **Menu**: Compiler **pdfLaTeX**, Main
document **main.tex**, TeX Live newest. **Recompile** gives **11 pages**.

- Every result number is a macro in `generated/*.tex`, produced from saved outcomes by the
  scripts in `analysis_provenance/` of the project repository. Never type a result into
  `main.tex`; change it at its source and regenerate.
- The paper is 11 pages by decision, not by accident: T-RS charges US$200 for each page past
  ten, and page 11 was bought in R18 for the operating-regime passage, the cost design rule
  and larger Figures 2 and 3. Do not let it reach 12.
- Do not shrink a figure with `width=` to make room. That is how R16 came to print its
  figures at 3-4 pt. Figures 2 and 3 are drawn at their final print size with readable labels by `make_fig_theory_row.py` and `make_fig_detection.py`.
- `IEEEtran.cls` (V1.8b) and `IEEEtran.bst` (1.14) are pinned copies of the official IEEE
  files. Leave them in place.
- Fig. 1 is TikZ inside `main.tex`; Overleaf's TeX Live has what it needs.
- When you are done, **Menu -> Download -> Source** and put `main.tex` back in
  `manuscript/` of the package. That folder is the single live copy.
"""

SUP_README = f"""# IN-ARCP supplementary material, Overleaf container ({TAG})

Upload as a **separate** project. Main document **supplement.tex**. The page count is checked by this build script.

The supplement reads the paper's equation, appendix and proposition numbers from
`manuscript_main.aux`, which is included here. If you renumber anything in the manuscript:

1. recompile the manuscript project;
2. download its `main.aux` from **Logs and output files**;
3. upload it here as `manuscript_main.aux`.

The compact supplement contains the supporting proofs and readable result tables.
Its full-output index points to the frozen repository; original terminal dumps are
not required to typeset this PDF. The local package documents table provenance and
the compact-source generator. Preserve the uncertainty intervals and disclosures.
"""


def run(cmd, cwd):
    if cmd[0] == "pdflatex":
        cmd = [cmd[0], "--disable-installer", *cmd[1:]]
    result = subprocess.run(cmd, cwd=cwd, capture_output=True, shell=False)
    if result.returncode:
        detail = (result.stdout + result.stderr).decode("utf-8", errors="replace")
        raise RuntimeError(f"Build failed in {cwd}: {detail[-2000:]}")
    return result


def remove_build_temp(directory):
    """Only delete this script's freshly created build directories under OS temp."""
    target = Path(directory).resolve()
    temp_root = Path(tempfile.gettempdir()).resolve()
    if target.parent != temp_root or not target.name.startswith(("verify_", "overleaf_man_", "overleaf_sup_")):
        raise RuntimeError(f"Refusing to remove unexpected path: {target}")
    shutil.rmtree(target)


def pages(pdf):
    import pymupdf
    with pymupdf.open(pdf) as d:
        return d.page_count


def log_ok(log, label):
    t = open(log, encoding="utf-8", errors="replace").read()
    over = len(re.findall(r"Overfull", t))
    undef = len(re.findall(r"undefined", t))
    errs = len(re.findall(r"^!", t, re.M))
    print(f"    {label}: overfull {over}, undefined {undef}, errors {errs}")
    return errs == 0 and undef == 0 and over == 0


# ------------------------------------------------------------------ pinned IEEE class files
pinned = {}
for n in ("IEEEtran.cls", "IEEEtran.bst"):
    pinned[n] = open(os.path.join(PINNED, n), "rb").read()

# ------------------------------------------------------------------ manuscript container
print("manuscript container")
tmp = tempfile.mkdtemp(prefix="overleaf_man_")
src = os.path.join(PKG, "manuscript")
shutil.copy2(os.path.join(src, "main.tex"), tmp)
shutil.copy2(os.path.join(src, "main.bbl"), tmp)
shutil.copy2(os.path.join(src, "references.bib"), tmp)
os.makedirs(os.path.join(tmp, "generated"))
for f in sorted(os.listdir(os.path.join(src, "generated"))):
    if f.endswith(".tex"):
        shutil.copy2(os.path.join(src, "generated", f), os.path.join(tmp, "generated", f))
os.makedirs(os.path.join(tmp, "figures"))
for f in ("fig_theory_row.pdf", "fig_detection.pdf"):
    shutil.copy2(os.path.join(src, "figures", f), os.path.join(tmp, "figures", f))
for n, b in pinned.items():
    open(os.path.join(tmp, n), "wb").write(b)
open(os.path.join(tmp, "README_OVERLEAF.md"), "w", encoding="utf-8").write(MAN_README)

for _ in range(3):
    run(["pdflatex", "-interaction=nonstopmode", "main.tex"], tmp)
ok_man = log_ok(os.path.join(tmp, "main.log"), "compile")
p_man = pages(os.path.join(tmp, "main.pdf"))
print(f"    pages {p_man}")
assert p_man == 11, f"Manuscript page cap exceeded: {p_man}"

# ------------------------------------------------------------------ supplement container
print("supplement container")
tmp2 = tempfile.mkdtemp(prefix="overleaf_sup_")
ssrc = os.path.join(PKG, "supplement")
# Include exactly the sources/figures read by the compact document. Unused R19
# generated sections and terminal-log inputs remain in the local evidence package.
pending = ["supplement.tex"]
included = set()
while pending:
    name = pending.pop()
    if name in included:
        continue
    included.add(name)
    full = os.path.join(ssrc, name)
    body = open(full, encoding="utf-8").read()
    target = os.path.join(tmp2, name)
    os.makedirs(os.path.dirname(target), exist_ok=True)
    shutil.copy2(full, target)
    for child in re.findall(r"\\input\{([^}]+)\}", body):
        pending.append(child if child.endswith(".tex") else child + ".tex")
    for figure in re.findall(r"\\includegraphics(?:\[[^\]]*\])?\{([^}]+)\}", body):
        name_pdf = figure if figure.endswith(".pdf") else figure + ".pdf"
        figure_target = os.path.join(tmp2, name_pdf)
        os.makedirs(os.path.dirname(figure_target), exist_ok=True)
        shutil.copy2(os.path.join(ssrc, name_pdf), figure_target)
shutil.copy2(os.path.join(src, "main.aux"), os.path.join(tmp2, "manuscript_main.aux"))
# the container is flat, so the external-document reference must point at the local copy
st = open(os.path.join(tmp2, "supplement.tex"), encoding="utf-8").read()
st = st.replace(r"\externaldocument[M-]{../manuscript/main}",
                r"\externaldocument[M-]{manuscript_main}")
open(os.path.join(tmp2, "supplement.tex"), "w", encoding="utf-8").write(st)
open(os.path.join(tmp2, "README_OVERLEAF.md"), "w", encoding="utf-8").write(SUP_README)

for _ in range(2):
    run(["pdflatex", "-interaction=nonstopmode", "supplement.tex"], tmp2)
ok_sup = log_ok(os.path.join(tmp2, "supplement.log"), "compile")
p_sup = pages(os.path.join(tmp2, "supplement.pdf"))
print(f"    pages {p_sup}")

if not (ok_man and ok_sup):
    print("A container failed to compile cleanly. Nothing written.")
    sys.exit(1)

# ------------------------------------------------------------------ write the ZIPs
SKIP = (".aux", ".log", ".out", ".fls", ".fdb_latexmk", ".blg", ".synctex.gz", ".pdf")


def write_zip(path, root, keep_pdf_dirs=()):
    n = 0
    with zipfile.ZipFile(path, "w", zipfile.ZIP_DEFLATED) as z:
        for base, _dirs, files in os.walk(root):
            for f in sorted(files):
                rel = os.path.relpath(os.path.join(base, f), root).replace("\\", "/")
                ext = os.path.splitext(f)[1]
                if ext == ".pdf" and not any(rel.startswith(d) for d in keep_pdf_dirs):
                    continue
                if ext in SKIP and ext != ".pdf":
                    if not (f == "manuscript_main.aux"):
                        continue
                z.write(os.path.join(base, f), rel)
                n += 1
    return n


n1 = write_zip(MAN_ZIP, tmp, keep_pdf_dirs=("figures/",))
# the supplement's figures sit at its root, so keep root-level PDFs there
with zipfile.ZipFile(SUP_ZIP, "w", zipfile.ZIP_DEFLATED) as z:
    for base, _dirs, files in os.walk(tmp2):
        for f in sorted(files):
            rel = os.path.relpath(os.path.join(base, f), tmp2).replace("\\", "/")
            ext = os.path.splitext(f)[1]
            if f in ("supplement.pdf",):
                continue
            if ext in (".log", ".out", ".fls", ".fdb_latexmk", ".blg", ".synctex.gz"):
                continue
            if ext == ".aux" and f != "manuscript_main.aux":
                continue
            z.write(os.path.join(base, f), rel)
n2 = len(zipfile.ZipFile(SUP_ZIP).namelist())

print(f"wrote {MAN_ZIP} ({n1} entries)")
print(f"wrote {SUP_ZIP} ({n2} entries)")

# ------------------------------------------------------------------ verify by re-extracting
print("verifying both ZIPs by extracting into empty folders and compiling")
for zp, mainfile, want, runs in ((MAN_ZIP, "main.tex", p_man, 3),
                                 (SUP_ZIP, "supplement.tex", p_sup, 2)):
    v = tempfile.mkdtemp(prefix="verify_")
    with zipfile.ZipFile(zp) as z:
        z.extractall(v)
    for _ in range(runs):
        run(["pdflatex", "-interaction=nonstopmode", mainfile], v)
    pdf = os.path.join(v, mainfile.replace(".tex", ".pdf"))
    got = pages(pdf)
    base = os.path.basename(zp)
    ok = log_ok(os.path.join(v, mainfile.replace(".tex", ".log")), base)
    print(f"    {base}: {got} pages (expected {want}) {'OK' if got == want and ok else 'MISMATCH'}")
    remove_build_temp(v)

remove_build_temp(tmp)
remove_build_temp(tmp2)
