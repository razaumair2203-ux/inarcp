"""Regression metrics across manuscript versions (PDF text for prose, LaTeX source for structure)."""
import re, sys, json, os, fitz

S = os.path.dirname(os.path.abspath(__file__))
V = os.path.join(S, "versions")


def syllables(w):
    w = w.lower()
    w = re.sub(r"[^a-z]", "", w)
    if not w:
        return 0
    if len(w) <= 3:
        return 1
    w = re.sub(r"(?:[^laeiouy]es|ed|[^laeiouy]e)$", "", w)
    w = re.sub(r"^y", "", w)
    return max(1, len(re.findall(r"[aeiouy]{1,2}", w)))


def pdf_body(pdf):
    d = fitz.open(pdf)
    txt = "\n".join(p.get_text() for p in d)
    pages = d.page_count
    # R18: strip the running head and page number before sentence splitting. Without this
    # a page break inside a sentence splices "SUBMITTED TO ... <n>" into it, which inflates
    # the long-sentence counts and makes the count depend on where content happens to fall.
    txt = re.sub(r"SUBMITTED TO IEEE TRANSACTIONS ON [A-Z ]+\s*\d*", " ", txt)
    txt = re.sub(r"RAZA et al\.:[^\n]*", " ", txt)
    # cut references and everything after
    m = re.search(r"\n\s*REFERENCES\s*\n", txt)
    body = txt[: m.start()] if m else txt
    # abstract
    am = re.search(r"(?:Abstract\s*[—–-]+|ABSTRACT)\s*(.*?)(Index Terms|INDEX TERMS|Keywords)", body, re.S)
    abstract = am.group(1) if am else ""
    return pages, body, abstract


def prose_sentences(text):
    t = re.sub(r"-\n", "", text)
    t = re.sub(r"\s+", " ", t)
    sents = re.split(r"(?<=[a-z0-9\)\]])[.?!]\s+(?=[A-Z])", t)
    out = []
    for s in sents:
        words = re.findall(r"[A-Za-z][A-Za-z\-']+", s)
        # drop math-heavy fragments: require mostly words
        toks = s.split()
        if len(words) >= 5 and len(words) / max(1, len(toks)) > 0.6:
            out.append((s, words))
    return out


def readability(text):
    ss = prose_sentences(text)
    nw = sum(len(w) for _, w in ss)
    nsy = sum(syllables(x) for _, w in ss for x in w)
    nsent = len(ss)
    complex_w = sum(1 for _, w in ss for x in w if syllables(x) >= 3)
    asl = nw / max(1, nsent)
    fre = 206.835 - 1.015 * asl - 84.6 * nsy / max(1, nw)
    fog = 0.4 * (asl + 100 * complex_w / max(1, nw))
    long40 = sum(1 for _, w in ss if len(w) > 40) / max(1, nsent)
    return dict(sentences=nsent, mean_sentence_words=round(asl, 1), flesch=round(fre, 1), fog=round(fog, 1),
                pct_sent_over_40w=round(100 * long40, 1))


def read_tex(k):
    files = {"R07": ["R07.tex", "R07_body.tex"], "R12a": ["R12a.tex", "R12a_laws.tex"], "R12": ["R12.tex", "R12_laws.tex"],
             "R13": ["R13.tex", "R13_laws.tex"]}.get(k, [k + ".tex"])
    src = open(os.path.join(V, files[0]), encoding="utf8", errors="replace").read()
    if len(files) > 1 and os.path.exists(os.path.join(V, files[1])):
        sub = open(os.path.join(V, files[1]), encoding="utf8", errors="replace").read()
        src = re.sub(r"\\input\{sec_(?:body|laws)(?:\.tex)?\}", lambda _m: sub, src)
    src = re.sub(r"(?<!\\)%.*", "", src)  # strip comments
    body = src.split("\\begin{document}", 1)[-1]
    body = body.split("\\appendices", 1)[0]
    body = body.split("\\section*{Code", 1)[0]
    return src, body


HEDGE = r"\b(not|only|although|whereas|however|but|plausibly|consistent with|untested|exploratory|post hoc|need not|approximately|barely|nearly|partly|partially|mildly|modest)\b"
PROCESS = r"\b(R ?(?:7|8|9|10|11|12)|frozen|protocol|expectations?|development|pre-?specified|confirmatory)\b"
CODES = r"\(\s*[LAJTIC][0-9]\s*\)|\b[LAJ][1-4]\b(?=[\),])"
METHODS = ["IN-ARCP", "NA-AR", "NA ", "PAMF", "NPAMF", "ANMF", "P-ANMF", "CA16", "CAloc", "OS-CFAR", "OS score", "MTD", "ACI",
           "Mondrian", "Tyler", "Fisher", "bootstrap", "clipped", "binary integra", "non-coherent integra", "zeroing", "perceptron",
           "raw-RMS", "K-texture", "gradient-boosted"]


def tex_metrics(src, body):
    m = {}
    m["theorem_like"] = len(re.findall(r"\\begin\{(proposition|corollary|theorem|lemma)\}", body))
    m["figures_main"] = len(re.findall(r"\\begin\{figure\*?\}", body))
    m["tables_main"] = len(re.findall(r"\\begin\{table\*?\}", body))
    m["sections"] = len(re.findall(r"\\section\{", body))
    m["subsections"] = len(re.findall(r"\\subsection\{", body))
    m["numbered_eqs"] = len(re.findall(r"\\label\{eq:", body))
    m["macros_numbers_used"] = len(re.findall(r"\\[A-Z][A-Za-z]{3,}(?![A-Za-z{])", body))
    paras = [p for p in re.split(r"\n\s*\n", body) if len(re.findall(r"[A-Za-z]{3,}", p)) > 30 and "\\begin{table" not in p]
    lens = [len(re.findall(r"\S+", p)) for p in paras]
    m["mean_paragraph_words"] = round(sum(lens) / max(1, len(lens)))
    m["max_paragraph_words"] = max(lens) if lens else 0
    m["squeeze_hacks"] = len(re.findall(r"\\vspace\{-|\\footnotesize|\\scriptsize|\\resizebox|\\looseness|tabcolsep", body))
    m["acronyms_distinct"] = len(set(re.findall(r"\b[A-Z][A-Z0-9]{1,}(?:-[A-Z0-9]+)*\b", re.sub(r"\\[A-Za-z]+", "", body))))
    m["methods_named"] = sum(1 for x in METHODS if x in body)
    return m


def title_of(src):
    t = re.search(r"\\title\{(.*?)\}\s*\n", src)
    if not t:
        t = re.search(r"pdftitle=\{(.*?)\}", src)
    return t.group(1) if t else ""


out = {}
for k in sys.argv[1:]:
    pdf = os.path.join(V, k + ".pdf")
    pages, body, abstract = pdf_body(pdf)
    src, tbody = read_tex(k)
    words = len(re.findall(r"[A-Za-z][A-Za-z\-']+", body))
    nums = len(re.findall(r"(?<![A-Za-z])[−-]?\d+(?:\.\d+)?", body))
    low = body.lower()
    r = dict(pages=pages, body_words=words)
    r.update(readability(body))
    r["abstract_words"] = len(re.findall(r"\S+", abstract))
    r["abstract_numbers"] = len(re.findall(r"(?<![A-Za-z])\d+(?:\.\d+)?", abstract))
    ra = readability(abstract)
    r["abstract_mean_sentence_words"] = ra["mean_sentence_words"]
    r["abstract_flesch"] = ra["flesch"]
    r["numbers_per_100w"] = round(100 * nums / words, 1)
    r["hedges_per_1000w"] = round(1000 * len(re.findall(HEDGE, low)) / words, 1)
    r["process_jargon_hits"] = len(re.findall(PROCESS, body, re.I))
    r["expectation_codes"] = len(re.findall(CODES, body))
    r["new_novel_in_title_abstract"] = len(re.findall(r"\b(new|novel)\b", (title_of(src) + " " + abstract).lower()))
    t = title_of(src)
    r["title_words"] = len(t.split())
    r.update(tex_metrics(src, tbody))
    out[k] = r

keys = list(next(iter(out.values())).keys())
print("metric".ljust(30) + "".join(k.rjust(8) for k in out))
for key in keys:
    print(key.ljust(30) + "".join(str(out[k][key]).rjust(8) for k in out))
json.dump(out, open(os.path.join(S, "metrics.json"), "w"), indent=1)
