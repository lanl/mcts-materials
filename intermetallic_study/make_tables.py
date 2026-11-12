"""SI tables from the new rankings: complete U ranking (Table S1) and literature-known RM6X6 compounds."""
import re
from pathlib import Path
import pandas as pd
H = Path(__file__).resolve().parent; W = H.parent
def tex(c):  # 'UTi6Sn6' -> 'UTi$_{6}$Sn$_{6}$'
    f, m, x = re.match(r'([A-Z][a-z]?)([A-Z][a-z]?)6([A-Z][a-z]?)6', c).groups(); return f"{f}{m}$_{{6}}${x}$_{{6}}$"

u = pd.read_csv(H / 'rankings/u_only_ranking.csv')
rows = [f"{int(r['rank'])} & {tex(r.compound)} & {r.e_above_hull:.4f} & {r.r_S:.4f} & {r.r_dos:.3f} & {r.reward:.3f} & {r.synthesized} \\\\" for _, r in u.iterrows()]
(H / 'tables/table_s1_rows.tex').write_text("\n".join(rows) + "\n")
print('Table S1:', len(rows), 'rows; reward range %.3f .. %.4f' % (u.reward.max(), u.reward.min()), '| bottom:', u.compound.iloc[-1])

full = pd.read_csv(H / 'rankings/full_ranking.csv').set_index('compound')
lit = []
for l in (H / 'data/experimental_compounds.txt').read_text().splitlines():
    m = re.match(r'\s*\d+\s+([A-Z][a-z]?)-([A-Z][a-z]?)-([A-Z][a-z]?)\s', l)
    if m: lit.append(f"{m[3]}{m[1]}6{m[2]}6")
lit = list(dict.fromkeys(lit))
d = full.loc[[c for c in lit if c in full.index]].copy()
d['has_hull'] = d.data_quality.eq('valid')
d = d.sort_values(['has_hull', 'rank'], ascending=[False, True])
rows = []
for c, r in d.iterrows():
    if r.has_hull:
        rows.append(f"{int(r['rank'])} & {tex(c)} & {r.e_above_hull:.4f} & {r.r_S:.4f} & {r.r_dos:.3f} & {r.reward:.3f} \\\\")
    else:
        rows.append(f"-- & {tex(c)} & -- & -- & {r.r_dos:.3f} & -- \\\\")
(H / 'tables/table_literature_rows.tex').write_text("\n".join(rows) + "\n")
print('literature compounds:', len(lit), 'listed,', int(d.has_hull.sum()), 'with hull; top-ranked:', d.index[0], int(d['rank'].iloc[0]))
print('literature with hull: ranks', sorted(d[d.has_hull]['rank'].astype(int).tolist()))
print('n in top 50 / top 100 of 1728:', int((d[d.has_hull]['rank'] <= 50).sum()), int((d[d.has_hull]['rank'] <= 100).sum()), ' max E_hull among lit:', round(d[d.has_hull].e_above_hull.max(), 4))
