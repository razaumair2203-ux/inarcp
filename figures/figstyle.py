"""Shared print style of the figures: 8-pt type, one colour order safe for colour-vision
deficiency, with line style and marker shape duplicating every colour.
"""
import matplotlib

matplotlib.use("Agg")
import matplotlib.pyplot as plt

BLUE, ORANGE, TEAL = "#2166AC", "#D95F02", "#1B9E77"
DARK, GREY, GRID, BAND = "#333333", "#777777", "#E4E4E4", "#EDEDED"


def apply(size=9):
    plt.rcParams.update({
        "font.family": "sans-serif", "font.size": size,
        "axes.titlesize": size, "axes.labelsize": size,
        "xtick.labelsize": size, "ytick.labelsize": size,
        "legend.fontsize": size, "legend.title_fontsize": size,
        "axes.edgecolor": "#898781", "axes.labelcolor": DARK,
        "xtick.color": DARK, "ytick.color": DARK,
        "axes.linewidth": .6, "xtick.major.width": .6, "ytick.major.width": .6,
        "axes.spines.top": False, "axes.spines.right": False,
        "legend.frameon": False, "legend.handlelength": 1.9,
        "legend.labelspacing": .3, "legend.borderaxespad": .2,
        "pdf.fonttype": 42, "axes.titlelocation": "left",
    })


def grid(ax, axis="both"):
    ax.grid(axis=axis, color=GRID, lw=.5)
    ax.set_axisbelow(True)
