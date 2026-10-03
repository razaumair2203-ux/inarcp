"""Prose-quality KPIs per manuscript version (complements 04_reviews/2026-10-01_regression_audit/scripts/metrics.py).
Text is taken from the PDF body (before REFERENCES), with words hyphenated at line breaks rejoined.
Usage: python prose_metrics.py R07 R09 R12 R13 R15   (PDFs in ./versions)"""
import re, sys, os, json, statistics as st
import fitz

V = os.path.join(os.path.dirname(os.path.abspath(__file__)), "versions")
VAGUE = r"\b(various|several|some|certain|relatively|fairly|quite|somewhat|rather|significant(?:ly)?|substantial(?:ly)?|considerabl[ey]|appropriate(?:ly)?|suitabl[ey]|essentially|basically|generally|typically|largely|mostly|often|aspects?|issues?|things?|etc)\b"
DANGLING = r"(?:^|[.!?]\s+)(This|These|That|It|Such)\s+(is|are|was|were|gives|yields|shows|means|makes|holds|follows|has|have|can|may|does|explains|keeps|costs|matters)\b"
PASSIVE = r"\b(is|are|was|were|be|been|being)\s+(\w+ly\s+)?\w+(ed|en|wn|lt|pt|nt)\b"
NOMINAL = r"\b\w{4,}(tion|tions|ment|ments|ness|ity|ities|ance|ence)\b"
CONNECT = r"^(However|Therefore|Thus|Hence|Because|Since|In contrast|By contrast|Conversely|First|Second|Third|Finally|Moreover|Consequently|As a result|Instead|Yet|But|So|This is why|To|Unlike|Like|Both|Neither|Where|When|Once|After|Before|If)\b"
STOP = set("the a an of to in and or for on at by with from as is are was were be been that this these those it its their our we which whose than then there here not no but if into over under per each every all both can may only also more most less such between within without".split())


def body(pdf):
    t = "\n".join(p.get_text() for p in fitz.open(pdf))
    t = re.split(r"\n\s*REFERENCES\s*\n", t)[0]
    t = re.sub(r"(?<=[a-z])-\n(?=[a-z])", "", t)
    # R18: strip the running head and page number before sentence splitting. Without this a
    # page break inside a sentence splices "SUBMITTED TO ... <n>" into it, which inflates the
    # long-sentence counts and makes them depend on where content happens to fall on a page.
    t = re.sub(r"SUBMITTED TO IEEE TRANSACTIONS ON [A-Z ]+\s*\d*", " ", t)
    t = re.sub(r"RAZA et al\.:[^\n]*", " ", t)
    return t


def paragraphs(t):
    # PDF paragraphs: blank-line separated blocks are unreliable; use lines ending a sentence followed by an indented/capital start
    blocks = [re.sub(r"\s+", " ", b).strip() for b in re.split(r"(?<=[.:])\n(?=[A-Z])", t)]
    return [b for b in blocks if len(b.split()) >= 40]


def sentences(t):
    flat = re.sub(r"\s+", " ", t)
    flat = re.sub(r"\b(e\.g|i\.e|cf|Fig|Figs|Eq|Sec|vs|et al|Prop|Cor|Thm|Ref|no|vol|pp)\.", lambda m: m.group(0).replace(".", "§"), flat)
    ss = [s.strip() for s in re.split(r"(?<=[.!?])\s+(?=[A-Z(\[])", flat)]
    return [s for s in ss if len(re.findall(r"[A-Za-z]{2,}", s)) >= 4]


def content(p):
    return {w for w in re.findall(r"[a-z][a-z\-]{3,}", p.lower()) if w not in STOP}


def main():
  out = {}
  for v in sys.argv[1:]:
      t = body(os.path.join(V, v + ".pdf"))
      ss = sentences(t)
      words = re.findall(r"[A-Za-z][A-Za-z\-']+", t)
      W = len(words)
      lens = [len(s.split()) for s in ss]
      ps = paragraphs(t)
      coh = [len(content(a) & content(b)) / max(1, len(content(a) | content(b))) for a, b in zip(ps, ps[1:])]
      nums = [len(re.findall(r"(?<![A-Za-z])[−-]?\d+(?:\.\d+)?", s)) for s in ss]
      r = dict(
          words=W, sentences=len(ss),
          sent_len_mean=round(st.mean(lens), 1), sent_len_sd=round(st.pstdev(lens), 1),
          pct_sent_gt35=round(100 * sum(l > 35 for l in lens) / len(lens), 1),
          vague_per_1000w=round(1000 * len(re.findall(VAGUE, t, re.I)) / W, 1),
          dangling_this_it_per_100s=round(100 * len(re.findall(DANGLING, re.sub(r"\s+", " ", t))) / len(ss), 1),
          passive_pct_sent=round(100 * sum(bool(re.search(PASSIVE, s)) for s in ss) / len(ss), 1),
          nominal_per_100w=round(100 * len(re.findall(NOMINAL, t, re.I)) / W, 1),
          connective_start_pct=round(100 * sum(bool(re.match(CONNECT, s)) for s in ss) / len(ss), 1),
          parens_per_sent=round(sum(s.count("(") for s in ss) / len(ss), 2),
          semicolon_colon_per_sent=round(sum(s.count(";") + s.count(":") for s in ss) / len(ss), 2),
          numbers_per_sent=round(st.mean(nums), 2),
          pct_sent_ge4_numbers=round(100 * sum(n >= 4 for n in nums) / len(ss), 1),
          para_cohesion_jaccard=round(st.mean(coh), 3) if coh else None,
      )
      out[v] = r
  keys = list(next(iter(out.values())))
  print("metric".ljust(28) + "".join(k.rjust(8) for k in out))
  for k in keys:
      print(k.ljust(28) + "".join(str(out[v][k]).rjust(8) for v in out))
  json.dump(out, open(os.path.join(os.path.dirname(V), "prose_metrics.json"), "w"), indent=1)


if __name__ == '__main__':
    main()
