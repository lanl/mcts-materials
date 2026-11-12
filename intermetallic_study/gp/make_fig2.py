#!/usr/bin/env python3
"""Generate fig2_schematic.gp: the four MCTS phases (selection, expansion,
simulation, backpropagation) drawn as a small search tree above an excerpt of
the periodic table, in the palette of the results figures. Vector output,
Helvetica 10 pt, 6 x 4.6 in (double column)."""
from pathlib import Path

G = Path(__file__).resolve().parent
INK, MUTED = "#262626", "#8a8a8a"
TM_BLUE, GIV, LN, U_COL = "#3987e5", "#eb6834", "#1baf7a", "#262626"   # cell fills
HILITE = "#eb6834"                                                        # arrows / active nodes
NODE_OLD, NODE_SEL, NODE_NEW = "#cde2fb", "#3987e5", "#eb6834"
TM = [["Ti", "V", "Cr", "Mn", "Fe", "Co", "Ni", "Cu", "Zn"],
      ["Zr", "Nb", "Mo", "Tc", "Ru", "Rh", "Pd", "Ag", "Cd"],
      ["Hf", "Ta", "W", "Re", "Os", "Ir", "Pt", "Au", "Hg"]]
GIV_COL = ["Si", "Ge", "Sn", "Pb"]
LANTH = ["La", "Ce", "Pr", "Nd", "Pm", "Sm", "Eu", "Gd", "Tb", "Dy", "Ho", "Er", "Tm", "Yb", "Lu"]

# cell geometry (data units; each panel is 10 x 10)
CW, CH = 0.72, 0.78; TM_X0, TM_Y0 = 0.35, 4.55            # TM block top-left cell centre
GX = 8.9; GY0 = 5.35                                      # group-IV column
LW, LH = 0.62, 0.78; L_X0, L_Y0 = 0.35, 1.55              # lanthanide row
UX, UY = L_X0 + 3 * LW, 0.55                              # U below Nd

pos = {}
for r, row in enumerate(TM):
    for c, el in enumerate(row):
        pos[el] = (TM_X0 + c * CW, TM_Y0 - r * CH)
for r, el in enumerate(GIV_COL):
    pos[el] = (GX, GY0 - r * CH)
for c, el in enumerate(LANTH):
    pos[el] = (L_X0 + c * LW, L_Y0)
pos["U"] = (UX, UY)
size = {el: (CW, CH) for row in TM for el in row}
size.update({el: (CW, CH) for el in GIV_COL}); size.update({el: (LW, LH) for el in LANTH}); size["U"] = (LW, LH)
fill = {el: TM_BLUE for row in TM for el in row}
fill.update({el: GIV for el in GIV_COL}); fill.update({el: LN for el in LANTH}); fill["U"] = U_COL

obj = [1]
def cell(el, hilite=False):
    x, y = pos[el]; w, h = size[el]; obj[0] += 1
    border = f'fs solid 1.0 border lc rgb "{HILITE}" lw 2.2' if hilite else 'fs solid 1.0 border lc rgb "white" lw 0.6'
    return [f'set object {obj[0]} rect center {x},{y} size {w - 0.04},{h - 0.04} fc rgb "{fill[el]}" {border} front',
            f'set label {obj[0]} "{el}" at {x},{y} center tc rgb "white" font "Helvetica,10" front']

def table(hilites=(), arrows=()):
    out = []
    for el in pos: out += cell(el, el in hilites)
    for a, b in arrows:
        (x1, y1), (x2, y2) = pos[a], pos[b]; obj[0] += 1
        if abs(y1 - y2) < 1e-6:   # horizontal move: hop just above the row
            yy = y1 + size[a][1] / 2 + 0.22
            out.append(f'set arrow {obj[0]} from {x1},{yy} to {x2},{yy} head filled size 0.22,20 lc rgb "{HILITE}" lw 2.2 front')
        else:                      # vertical move: hop just right of the column
            xx = max(x1, x2) + size[a][0] / 2 + 0.22
            out.append(f'set arrow {obj[0]} from {xx},{y1} to {xx},{y2} head filled size 0.22,20 lc rgb "{HILITE}" lw 2.2 front')
    return out

# tree geometry
ROOT = (5.0, 9.5); KIDS = [(2.9, 8.2), (5.0, 8.2), (7.1, 8.2)]; GKIDS = [(4.1, 6.9), (5.9, 6.9)]
def node(xy, color, shape="circle", ring=False):
    x, y = xy; obj[0] += 1
    if shape == "circle":
        return [f'set object {obj[0]} circle at {x},{y} size 0.36 fc rgb "{color}" fs solid 1.0 border lc rgb "{INK if ring else "white"}" lw {1.6 if ring else 0.8} front']
    return [f'set object {obj[0]} rect center {x},{y} size 0.66,0.6 fc rgb "{color}" fs solid 1.0 border lc rgb "{INK if ring else "white"}" lw {1.6 if ring else 0.8} front']

def edge(a, b, color=MUTED, dashed=False, arrow=False, lw=1.2):
    obj[0] += 1
    head = "head filled size 0.22,20" if arrow else "nohead"
    return [f'set arrow {obj[0]} from {a[0]},{a[1]} to {b[0]},{b[1]} {head} lc rgb "{color}" lw {lw}{" dt 2" if dashed else ""} front']

def panel(letter, title, tree, hilites, arrows, extra=()):
    out = [f'set title "({letter}) {title}" left offset -2,-0.7 tc rgb INK']
    out += tree + table(hilites, arrows) + list(extra)
    out.append("plot NaN notitle")
    out.append(f"unset for [i=2:{obj[0]}] object i; unset for [i=2:{obj[0]}] label i; unset for [i=2:{obj[0]}] arrow i; unset label 900")
    return out

lines = ['load "style.gp"', 'eval DOUBLE(6, 6.2)', 'set output "out/Fig2.pdf"',
         'set multiplot layout 2,2 margins 0.01,0.99,0.01,0.96 spacing 0.02,0.06',
         'unset border; unset tics; unset grid; unset key; set size ratio -1', 'set xrange [-0.3:10.1]; set yrange [-0.1:10.3]']

# (a) selection: descend from the root to the child with the highest UCB (UCr6Sn6 -> UMn6Sn6)
tree_a = node(ROOT, NODE_SEL, ring=True)
for k in KIDS: tree_a += edge(ROOT, k)
tree_a += node(KIDS[0], NODE_OLD, "rect") + node(KIDS[1], NODE_SEL, "rect", ring=True) + node(KIDS[2], NODE_OLD, "rect")
tree_a += edge((ROOT[0] - 0.02, ROOT[1] - 0.4), (KIDS[1][0] - 0.02, KIDS[1][1] + 0.35), HILITE, arrow=True, lw=2.2)
lines += panel("a", "Selection", tree_a, ["Cr", "Mn", "Sn", "U"], [("Cr", "Mn")])
# (b) expansion: a new child by one substitution (UMn6Sn6 -> UFe6Sn6)
tree_b = node(ROOT, NODE_OLD)
for k in KIDS: tree_b += edge(ROOT, k)
tree_b += node(KIDS[0], NODE_OLD, "rect") + node(KIDS[1], NODE_SEL, "rect") + node(KIDS[2], NODE_OLD, "rect")
tree_b += edge(KIDS[1], GKIDS[0]) + edge(KIDS[1], GKIDS[1], HILITE, lw=2)
tree_b += node(GKIDS[0], NODE_OLD) + node(GKIDS[1], NODE_NEW, ring=True)
lines += panel("b", "Expansion", tree_b, ["Mn", "Fe", "Sn", "U"], [("Mn", "Fe")])
# (c) simulation: evaluate the new node and roll out random substitutions (Fe->Co, Sn->Ge, U->Nd)
tree_c = node(ROOT, NODE_OLD)
for k in KIDS: tree_c += edge(ROOT, k)
tree_c += node(KIDS[0], NODE_OLD, "rect") + node(KIDS[1], NODE_SEL, "rect") + node(KIDS[2], NODE_OLD, "rect")
tree_c += edge(KIDS[1], GKIDS[0]) + edge(KIDS[1], GKIDS[1]) + node(GKIDS[0], NODE_OLD) + node(GKIDS[1], NODE_NEW, ring=True)
chain = [(7.1, 6.9), (8.3, 6.9), (9.5, 6.9)]
prev = GKIDS[1]
for p in chain:
    tree_c += edge((prev[0] + 0.38, prev[1]), (p[0] - 0.38, p[1]), HILITE, dashed=True, arrow=True, lw=1.8) + node(p, "white", ring=True); prev = p
tree_c += [f'set label 900 "rollout" at 8.3,7.55 center tc rgb "{HILITE}" font "Helvetica,10" front']
lines += panel("c", "Simulation", tree_c, ["Fe", "Co", "Sn", "Ge", "U", "Nd"], [("Fe", "Co"), ("Sn", "Ge"), ("U", "Nd")])
# (d) backpropagation: the value flows back to the root
tree_d = node(ROOT, NODE_SEL, ring=True)
for k in KIDS: tree_d += edge(ROOT, k)
tree_d += node(KIDS[0], NODE_OLD, "rect") + node(KIDS[1], NODE_SEL, "rect", ring=True) + node(KIDS[2], NODE_OLD, "rect")
tree_d += edge(KIDS[1], GKIDS[0]) + edge(KIDS[1], GKIDS[1]) + node(GKIDS[0], NODE_OLD) + node(GKIDS[1], NODE_NEW, ring=True)
tree_d += edge((GKIDS[1][0] - 0.25, GKIDS[1][1] + 0.3), (KIDS[1][0] + 0.25, KIDS[1][1] - 0.35), HILITE, arrow=True, lw=2.2)
tree_d += edge((KIDS[1][0] + 0.1, KIDS[1][1] + 0.35), (ROOT[0] + 0.1, ROOT[1] - 0.4), HILITE, arrow=True, lw=2.2)
lines += panel("d", "Backpropagation", tree_d, ["Fe", "Sn", "U"], [])
lines.append("unset multiplot")
(G / "fig2_schematic.gp").write_text("\n".join(lines) + "\n")
print("wrote fig2_schematic.gp with", obj[0], "objects")
