"""Readable vector figures from the independently audited R22-G aggregate only."""
from pathlib import Path
import hashlib
import json
import numpy as np
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt

HERE = Path(__file__).resolve().parent
SUMMARY = HERE / 'R22_G_SUMMARY.json'
OUT = HERE / 'presentation'
OUT.mkdir(exist_ok=True)
D = json.loads(SUMMARY.read_text(encoding='utf-8'))
plt.rcParams.update({'font.family': 'sans-serif', 'font.size': 9,
    'axes.spines.top': False, 'axes.spines.right': False,
    'axes.linewidth': .6, 'legend.frameon': False, 'pdf.fonttype': 42})
COLORS = ['#333333', '#2166AC', '#D95F02']

def panel(ax, radar, scr):
    d = D['radars'][radar]
    looks = np.array(d['looks'])
    si = d['scr_db'].index(scr)
    di = d['dopplers'].index('random')
    for gi, (guard, color) in enumerate(zip(d['guards'], COLORS)):
        empirical = np.array(d['target_per_look_probability'])[di, si, gi]
        interval = np.array(d['target_per_look_interval'])[di, si, gi]
        predicted = np.array(d['ideal_plugin_per_look_probability'])[di, si, gi]
        ax.fill_between(looks, interval[:, 0], interval[:, 1], color=color, alpha=.10, lw=0)
        ax.plot(looks, empirical, color=color, lw=1.7, label=f'$\\Delta={guard}$')
        ax.plot(looks, predicted, '--', color=color, lw=1., alpha=.9)
    ax.set(xlim=(-.5, 48.5), ylim=(-.015, 1.02), xticks=np.arange(0, 49, 8),
        xlabel='Look after onset $\\ell$', ylabel='Per-look $P_{\\rm d}$')
    ax.grid(axis='y', color='#e2e2e2', lw=.5)
    ax.set_title(f'{radar}, SCR {scr} dB', fontsize=9)

fig, axes = plt.subplots(2, 2, figsize=(7.16, 5.15))
for row, scr in enumerate((10, 20)):
    for col, radar in enumerate(('IPIX', 'NetRAD')):
        panel(axes[row, col], radar, scr)
        axes[row, col].legend(loc='upper right', fontsize=9, handlelength=1.7,
                             title='Slow-time guard', title_fontsize=9)
fig.tight_layout(pad=.35, h_pad=1.5, w_pad=1.2)
fig.savefig(OUT / 'fig_guard_extension.pdf')
fig.savefig(OUT / 'fig_guard_extension.png', dpi=200)
plt.close(fig)

OLD_INPUT = HERE.parents[2] / 'paper/r21/analysis_provenance/fig_detection_r21.json'
old = json.loads(OLD_INPUT.read_text(encoding='utf-8'))
fig, (a, b) = plt.subplots(1, 2, figsize=(7.16, 2.65))
scr = np.array(old['scr_db'])
for name, color, style, label in [('CAloc', '#777777', ':', 'CAloc'),
    ('CA16', '#333333', '--', 'CA16'), ('NA4', '#D95F02', '-.', 'NA-AR(4)'),
    ('IN1', '#2166AC', '-', 'IN-ARCP')]:
    a.plot(scr, old['panel_a'][f'{name}|0.01|pd'], style, color=color, lw=1.5, label=label)
a.plot(scr, old['panel_a']['IN1|0.01|pred'], 'o', color='#2166AC', ms=3.8,
       mfc='white', mew=.9, label='Law (Cor. 2)')
h, labels = a.get_legend_handles_labels()
order = [3, 4, 2, 1, 0]
a.legend([h[i] for i in order], [labels[i] for i in order], loc='lower right',
         fontsize=9, handlelength=1.8, labelspacing=.3, borderaxespad=.2)
a.set(xlim=(-5.5, 25.5), ylim=(-.02, 1.02), xlabel='SCR (dB)', ylabel='$P_{\\rm d}$')
a.set_title('(a) Target in the tested pulse', fontsize=9)
a.grid(color='#e2e2e2', lw=.5)
panel(b, 'IPIX', 10)
b.set_title('(b) Persistent target, SCR 10 dB', fontsize=9)
b.legend(loc='upper right', fontsize=9, handlelength=1.7, title='Slow-time guard', title_fontsize=9)
fig.tight_layout(pad=.35, w_pad=1.2)
fig.savefig(OUT / 'fig_detection_r22.pdf')
fig.savefig(OUT / 'fig_detection_r22.png', dpi=200)
plt.close(fig)
(OUT / 'guard_figure_provenance.json').write_text(json.dumps({
    'summary_sha256': hashlib.sha256(SUMMARY.read_bytes()).hexdigest(),
    'unchanged_panel_a_source_sha256': hashlib.sha256(OLD_INPUT.read_bytes()).hexdigest(),
    'styles': 'Solid: empirical; dashed: fitted-model prediction; shaded: 95% cluster interval.',
    'size_inches': {'main': [7.16, 2.65], 'supplement': [7.16, 5.15]},
    'font_points': 9}, indent=2)+'\n', encoding='utf-8')
print('Two vector figures generated from audited saved arrays; no new outcomes.')
