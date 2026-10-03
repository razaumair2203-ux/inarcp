"""Fill cover_letter_template.md with the manuscript's generated macros, so the letter quotes exactly the paper's numbers.
Usage: python make_cover_letter.py   ->  ../cover_letter_TRS.md"""
import os, re
HERE = os.path.dirname(os.path.abspath(__file__))
GEN = os.path.join(HERE, "..", "manuscript", "generated")
M = {}
for f in os.listdir(GEN):
    if f.endswith("_macros.tex"):
        M.update(re.findall(r"\\newcommand\{\\(\w+)\}\{([^}]*)\}", open(os.path.join(GEN, f), encoding="utf8").read()))
t = open(os.path.join(HERE, "cover_letter_template.md"), encoding="utf8").read()
keys = re.findall(r"\{(\w+)\}", t)
missing = [k for k in keys if k not in M]
assert not missing, missing
out = re.sub(r"\{(\w+)\}", lambda m: M[m.group(1)].replace("$", ""), t)
open(os.path.join(HERE, "..", "cover_letter_TRS.md"), "w", encoding="utf8").write(out)
print("cover letter written;", len(keys), "macros filled")
