"""R18 edit pass 4: split the three sentences over 40 words that R18 introduced.

The R18 metrics showed pct_sent_over_40w rising 7.0 -> 7.7% and sent_len_mean 25.8 -> 26.1.
Diffing the over-40-word sentence sets against R17 isolated exactly three new ones, all mine
(F6, F2, F3). Splitting them also lowers numbers per sentence, the other regressed metric.
CLAUDE.md rule 6 forbids shipping a presentation regression without a stated reason; this
removes the part of it that is avoidable.
"""
import os
import sys

PKG = r"c:/Users/DELL/Downloads/MS thess/03_submission_IEEE-TRS"
MAIN = os.path.join(PKG, "manuscript", "main.tex")

EDITS = [
    (
        "F6 sentence: 43 words -> 28 + 21",
        r"not exactly exchangeable, as the non-stationarity of sea clutter implies \cite{greco2010}; bounding the coverage gap it leaves would need a budget for the drift between them \cite{barber2023}.",
        r"not exactly exchangeable, as the non-stationarity of sea clutter implies \cite{greco2010}. Bounding the coverage gap that leaves would need a budget for the drift between the thirds \cite{barber2023}.",
    ),
    (
        "F2 sentence: 47 words -> 24 + 34",
        r"The per-look screen therefore needs a look interval short enough that the clutter is still correlated at that lag, where its gain lives, and long enough that a target re-enters range cells often, since it onsets again in each new cell (\CellLooksRef{} looks in a 15~m cell at \CellSpeedRef~m/s, of which \DutyRef\% are visible).",
        r"The per-look screen therefore needs a look interval short enough that the clutter is still correlated at that lag, where its gain lives. It also needs one long enough for targets to re-enter range cells often, since a target onsets again in each new cell (\CellLooksRef{} looks in a 15~m cell at \CellSpeedRef~m/s, of which \DutyRef\% are visible).",
    ),
    (
        "F3 sentence: 44 words -> 17 + 31",
        r"above the design $10^{-3}$, and it is the least pivotal of the thirteen: the texture-quintile spread of its rate is",
        r"above the design $10^{-3}$. It is also the least pivotal of the thirteen statistics: the texture-quintile spread of its rate is",
    ),
]

src = open(MAIN, encoding="utf-8").read()
fail = []
for name, old, new in EDITS:
    n = src.count(old)
    if n != 1:
        fail.append(f"  {name}: pattern occurs {n} times")
        continue
    src = src.replace(old, new, 1)

if fail:
    print("FAILED, nothing written:")
    print("\n".join(fail))
    sys.exit(1)

open(MAIN, "w", encoding="utf-8").write(src)
print(f"applied {len(EDITS)} edits to {MAIN}")
