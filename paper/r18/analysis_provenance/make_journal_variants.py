"""Generate the venue-specific manuscript variants from the live T-RS source.

There is one source of truth, `manuscript/main.tex` (CLAUDE.md rule 10). This script derives
the other two venues' files from it, so a change to the paper never has to be made twice.

  journal_formats/IEEE-TRS/    -> a pointer to the live package; no copy is made
  journal_formats/IEEE-TAES/   -> IEEEtran journal, identical layout; running head and
                                  submission note changed
  journal_formats/IET-RSN/     -> single-column A4, IEEEtran commands stubbed out, plus the
                                  four front-matter items IET requires that IEEE does not

Run from 03_submission_IEEE-TRS/:   python analysis_provenance/make_journal_variants.py
Then build each variant in its own folder (pdflatex, bibtex, pdflatex, pdflatex).
"""
import os
import re
import shutil

HERE = os.path.dirname(os.path.abspath(__file__))
PKG = os.path.dirname(HERE)
SRC = os.path.join(PKG, "manuscript")
OUT = os.path.join(PKG, "journal_formats")

main = open(os.path.join(SRC, "main.tex"), encoding="utf-8").read()
PRE, AFTER = main.split("\\begin{document}", 1)


def copy_support(dest):
    """Copy the files a build needs: bibliography, generated macros and tables, figures."""
    os.makedirs(dest, exist_ok=True)
    shutil.copy2(os.path.join(SRC, "references.bib"), dest)
    g = os.path.join(dest, "generated")
    os.makedirs(g, exist_ok=True)
    for f in os.listdir(os.path.join(SRC, "generated")):
        if f.endswith(".tex"):
            shutil.copy2(os.path.join(SRC, "generated", f), g)
    fd = os.path.join(dest, "figures")
    os.makedirs(fd, exist_ok=True)
    for x in ("fig_theory_row.pdf", "fig_detection.pdf"):
        shutil.copy2(os.path.join(SRC, "figures", x), fd)


# ========================================================================= IEEE TAES
taes = os.path.join(OUT, "IEEE-TAES")
copy_support(taes)
t = main
SUBS_TAES = [
    (
        "\\markboth{Submitted to IEEE Transactions on Radar Systems}",
        "\\markboth{Submitted to IEEE Transactions on Aerospace and Electronic Systems}",
    ),
    (
        "% IEEE Transactions on Radar Systems -- Regular Paper (IEEEtran journal template).",
        "% IEEE Transactions on Aerospace and Electronic Systems -- Regular Paper.\n"
        "% GENERATED from ../../manuscript/main.tex by analysis_provenance/"
        "make_journal_variants.py.\n"
        "% Do not edit here: edit the T-RS source and regenerate. TAES uses the same IEEEtran\n"
        "% journal template, the same single-anonymous review and the same US$200/page charge\n"
        "% beyond ten printed pages, so only the running head and this note differ.",
    ),
]
for old, new in SUBS_TAES:
    assert t.count(old) == 1, (old[:60], t.count(old))
    t = t.replace(old, new, 1)
open(os.path.join(taes, "main.tex"), "w", encoding="utf-8").write(t)
print("wrote", os.path.join(taes, "main.tex"))

# ========================================================================= IET RSN
iet = os.path.join(OUT, "IET-RSN")
copy_support(iet)

inputs = "\n".join(re.findall(r"^\\input\{generated/[^}]+\}", PRE, re.M))

IET_PRE = """% IET Radar, Sonar & Navigation -- single-column variant.
% GENERATED from ../../manuscript/main.tex by analysis_provenance/make_journal_variants.py.
% Do not edit here: edit the T-RS source and regenerate.
%
% NOT THE PUBLISHER'S CLASS FILE. IET/Wiley do not distribute a LaTeX class that could be
% validated offline, and IET accepts a manuscript in any legible format for peer review.
% This file reproduces IET's STATED requirements: single column, an unstructured abstract,
% keywords, numbered sections, a numeric reference list, and the four front-matter statements
% IET requires and IEEE does not. Before submitting, transfer the body into the official IET
% template from the journal's Author Guidelines page.
\\documentclass[11pt,a4paper]{article}
\\usepackage[margin=2.3cm]{geometry}
\\usepackage[T1]{fontenc}
\\usepackage{amsmath,amssymb,amsthm,booktabs,array,graphicx}
\\usepackage{cite,xurl,enumitem}
\\usepackage[hidelinks]{hyperref}
\\usepackage{tikz}
\\usetikzlibrary{positioning,arrows.meta}
\\usepackage{setspace}
\\onehalfspacing
%% the T-RS tables are set for a 3.4 in column; shrink any that overrun the single-column width
\\usepackage{adjustbox}
\\let\\TRStabular\\tabular \\let\\endTRStabular\\endtabular
\\renewenvironment{tabular}[2][c]{%
  \\begin{adjustbox}{max width=\\textwidth}\\TRStabular[#1]{#2}}%
  {\\endTRStabular\\end{adjustbox}}
\\graphicspath{{figures/}}
\\newtheorem{proposition}{Proposition}
\\newtheorem{corollary}{Corollary}
\\newtheorem{theorem}{Theorem}
\\newcommand{\\PP}{\\mathbb{P}}
%% ---- IEEEtran commands the article class does not provide ----
\\providecommand{\\IEEEPARstart}[2]{\\textbf{\\large #1}#2}
\\renewcommand{\\markboth}[2]{}
\\providecommand{\\bstctlcite}[1]{}
\\providecommand{\\MakeLowercase}[1]{#1}
\\newenvironment{IEEEkeywords}{\\par\\medskip\\noindent\\textbf{Keywords: }}{\\par}
\\providecommand{\\appendices}{\\par\\medskip\\setcounter{section}{0}%
  \\renewcommand{\\thesection}{Appendix \\Alph{section}}}
%% single column: the starred float environments are the unstarred ones
\\newenvironment{tablestar}{\\begin{table}}{\\end{table}}
\\newenvironment{figurestar}{\\begin{figure}}{\\end{figure}}
__INPUTS__
\\begin{document}
\\sloppy
"""
IET_PRE = IET_PRE.replace("__INPUTS__", inputs)

body = AFTER

AUTHOR_BLOCK = """\\author{Muhammad Umair Raza\\thanks{%
$^{1}$Department of Avionics Engineering, College of Aeronautical Engineering, National
University of Sciences and Technology (NUST), Risalpur, Pakistan.
$^{2}$MathWorks, Natick, MA, USA.
$^{3}$National Disaster Management Authority (NDMA), Islamabad, Pakistan.
Correspondence: M. U. Raza, \\texttt{uraza@cae.nust.edu.pk}.}$^{,1}$
\\and Sohail Ahmed$^{2}$ \\and Ammad Ahmed$^{3}$}
\\date{}
"""

n = len(re.findall(r"\\author\{.*?\}\}\s*\n", body, flags=re.S))
assert n == 1, f"author block matches {n} times"
body = re.sub(r"\\author\{.*?\}\}\s*\n", lambda _m: AUTHOR_BLOCK, body, count=1, flags=re.S)

# starred floats -> the environments defined above (article has no table*/figure*)
for a, b in (("{table*}", "{tablestar}"), ("{figure*}", "{figurestar}")):
    body = body.replace("\\begin" + a, "\\begin" + b).replace("\\end" + a, "\\end" + b)

IET_FRONT = """
\\noindent\\rule{\\textwidth}{0.4pt}

\\paragraph{Table-of-contents entry (graphical-abstract text, 62 words).}
Constant-false-alarm-rate laws assume independent exponential samples, which correlated sea
clutter does not provide. Whitening each range cell along slow time and normalizing by the
cell's own innovation power restores those laws, and a conformal threshold calibrated on
measured clutter holds the false-alarm rate where model-based laws fail by up to sixty-fold.
A slow-time guard delays a persistent target's self-masking, and clipped integration can be
certified against pulsed interference of any power.
\\emph{Representative figure: Fig.~\\ref{fig:chain}, the detector in the receive chain.}

\\paragraph{Data availability statement.}
All three datasets are openly available and none were generated by the authors: IPIX from
McMaster University \\cite{ipixweb}, NetRAD from University College London
\\cite{netrad2026}, and the 77~GHz FMCW data from Zenodo \\cite{jku2026}. The analysis code,
the hashed protocols, the saved outcomes and the figure scripts are at
\\url{https://github.com/razaumair2203-ux/inarcp}, release tag \\texttt{r18-trs-submission}.

\\paragraph{Author contributions.}
To be completed by the authors on submission, using the CRediT taxonomy; see
\\texttt{declarations.md} in the submission package.

\\paragraph{Conflict of interest.}
S. Ahmed is employed by MathWorks. The authors declare no other competing interest.

\\noindent\\rule{\\textwidth}{0.4pt}
\\medskip
"""

assert body.count("\\section{Introduction}") == 1
body = body.replace(
    "\\section{Introduction}", IET_FRONT + "\n\\section{Introduction}", 1
)

open(os.path.join(iet, "main.tex"), "w", encoding="utf-8").write(IET_PRE + body)
print("wrote", os.path.join(iet, "main.tex"))

# ========================================================================= T-RS pointer
trs = os.path.join(OUT, "IEEE-TRS")
os.makedirs(trs, exist_ok=True)
open(os.path.join(trs, "THIS_IS_THE_LIVE_PACKAGE.md"), "w", encoding="utf-8").write(
    "# IEEE T-RS: the live package, not a copy\n\n"
    "The T-RS-formatted manuscript **is** `../../manuscript/main.tex` and\n"
    "`../../manuscript/main.pdf`. Nothing is duplicated here, because `CLAUDE.md` rule 10\n"
    "allows only one live version of the paper.\n\n"
    "- Manuscript: `../../manuscript/main.pdf`\n"
    "- Supplement: `../../supplement/supplement.pdf`\n"
    "- Files to upload: `../../UPLOAD_TRS/`\n"
    "- Overleaf: `../../overleaf/`\n"
    "- Requirements checked against the journal: `GUIDELINES.md` in this folder\n"
)
print("wrote", os.path.join(trs, "THIS_IS_THE_LIVE_PACKAGE.md"))
