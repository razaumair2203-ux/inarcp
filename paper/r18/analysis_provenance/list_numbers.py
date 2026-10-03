"""List hand-typed numbers in the manuscript body (outside display math and TikZ) with context, for the provenance audit."""
import re, sys
p = sys.argv[1] if len(sys.argv) > 1 else "manuscript/main.tex"
s = open(p, encoding="utf8").read()
body = s[s.index("\\begin{abstract}"):s.index("\\bibliographystyle")]
for env in ("equation", "align*", "multline", "gathered", "tikzpicture"):
    b, e = "\\begin{" + env + "}", "\\end{" + env + "}"
    while b in body:
        i = body.index(b); j = body.index(e, i) + len(e)
        body = body[:i] + " " + body[j:]
seen = set()
for m in re.finditer(r"(?<![A-Za-z\\{_^])\d[\d,.]*", body):
    ctx = body[max(0, m.start() - 55):m.end() + 25].replace("\n", " ")
    key = (m.group(0), ctx)
    if key in seen:
        continue
    seen.add(key)
    print(f"{m.group(0):>8s} | {ctx}")
