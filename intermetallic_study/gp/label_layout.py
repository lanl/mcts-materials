#!/usr/bin/env python3
"""Rank labels with leader lines for the two scatter figures, laid out from the data.
Fig 4 (uranium): points with r_DOS < 0.1 overlap -> labels in a column to their right, ordered
by E_hull; other points get adjacent labels in the plot command. Fig 6 inset (lanthanides):
labels in a top row (E_hull >= split) and a bottom row, each ordered by r_DOS."""
import re
from pathlib import Path
import numpy as np
G = Path(__file__).resolve().parent


def replace_block(path, lines, anchor_regex):
    s = path.read_text().splitlines()
    s = [l for l in s if not re.match(r"set (label|arrow) (3\d|4\d|5\d|6\d|7\d) ", l)]
    i = [k for k, l in enumerate(s) if re.search(anchor_regex, l)][-1]   # last match (the inset of Fig 6)
    path.write_text("\n".join(s[:i + 1] + lines + s[i + 1:]) + "\n")


# ---- Fig 4
d = np.loadtxt(G / "data/fig4_mcts_top15.dat")
cl = d[d[:, 0] < 0.1]; cl = cl[np.argsort(-cl[:, 1])]
X = 0.115; top, step = 0.40, 0.085
lines = []
for k, (x, y, r) in enumerate(cl):
    ly = top - k * step; r = int(r)
    lines += [f'set label {30 + r} "{r}" at {X:.3f}, {ly:.3f} left font FONT tc rgb INK front',
              f'set arrow {30 + r} from {X - 0.004:.3f}, {ly:.3f} to {x:.4f}, {y:.4f} nohead lc rgb MUTED lw 0.7 back']
# near-coincident points outside the cluster: no inline label; leader-line labels to either side
rest = d[d[:, 0] >= 0.1]; pairs = []
for i in range(len(rest)):
    for j in range(i + 1, len(rest)):
        if abs(rest[i, 0] - rest[j, 0]) < 0.012 and abs(rest[i, 1] - rest[j, 1]) < 0.03:
            pairs.append((rest[i], rest[j]))
excl = []
for a, b in pairs:
    a, b = sorted((a, b), key=lambda t: t[0])             # a left, b right
    for (x, y, r), lx, ly, al in ((a, a[0] - 0.03, a[1] + 0.06, "right"), (b, b[0] + 0.03, b[1] + 0.06, "left")):
        r = int(r); excl.append(r)
        lines += [f'set label {30 + r} "{r}" at {lx:.3f}, {ly:.3f} {al} font FONT tc rgb INK front',
                  f'set arrow {30 + r} from {lx + (0.004 if al == "right" else -0.004):.3f}, {ly - 0.01:.3f} to {x:.4f}, {y:.4f} nohead lc rgb MUTED lw 0.7 back']
gp = G / "fig4_scatter_u.gp"; t = gp.read_text()
cond = "$1 > 0.1" + "".join(f" && $3 != {r}" for r in excl)
t = re.sub(r"\(\$1 > 0\.1( && \$3 != \d+)* \? sprintf", f"({cond} ? sprintf", t); gp.write_text(t)
replace_block(G / "fig4_scatter_u.gp", lines, r"^set key ")
print("fig4 cluster ranks:", [int(r) for r in cl[:, 2]], "| paired:", excl)

# ---- Fig 6 inset
d = np.loadtxt(G / "data/fig9_mcts_top15.dat")
x0, x1, y0, y1, split = 1.37, 1.95, 0.0, 0.085, 0.03
YT, YB = 0.078, 0.005
lines = []
for row, sel, ly, dy in (("top", d[:, 1] >= split, YT, -0.004), ("bot", d[:, 1] < split, YB, 0.004)):
    pts = d[sel]; pts = pts[np.argsort(pts[:, 0])]
    xs = np.linspace(x0 + 0.03, x1 - 0.03, len(pts))
    for lx, (x, y, r) in zip(xs, pts):
        r = int(r)
        lines += [f'set label {50 + r} "{r}" at {lx:.3f}, {ly:.4f} center font FONT tc rgb INK front',
                  f'set arrow {50 + r} from {lx:.3f}, {ly + dy:.4f} to {x:.4f}, {y:.4f} nohead lc rgb MUTED lw 0.7 back']
p = G / "fig9_scatter_full.gp"; s = p.read_text()
s = re.sub(r"set xrange \[1\.35:1\.97\]; set yrange \[-0\.017:0\.041\]; set xtics 1\.4,0\.2,1\.8 offset 0,0\.4; set ytics 0,0\.02 offset 0\.4,0",
           f"set xrange [{x0}:{x1}]; set yrange [{y0}:{y1}]; set xtics 1.4,0.2,1.8 offset 0,0.4; set ytics 0,0.02 offset 0.4,0", s)
s = re.sub(r"set object 2 rect from [^\n]* fc", f'set object 2 rect from {x0}, {y0} to {x1}, {y1} fc', s)
p.write_text(s)
replace_block(p, lines, r"^set arrow 1 from graph 0, first 0 to graph 1, first 0 nohead lc rgb INK lw 1 dt 2$")
print("fig9 inset rows written")
