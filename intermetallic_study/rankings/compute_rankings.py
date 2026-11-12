"""Reference rankings with the band-pass reward: U-only (108) and full lanthanide+U (1728).
reward = exp(-tanh(120 (E_hull - E_THRES))) * r_DOS, E_THRES = 0.054 eV/atom, E_hull penalised (10 eV/atom) when no MP hull (Yb).
Mirrors postprocessing.rank_design_space (dedupe by composition, first = lowest E_hull row)."""
import re, sys
from pathlib import Path
import numpy as np, pandas as pd
from mcts_framework.intermetallic.dos_bandpass import BandpassDosRewardLookup
from mcts_framework.intermetallic.rewards import ehull_reward
from mcts_framework.intermetallic.evaluator import UnstablePenalty
H = Path(__file__).resolve().parent.parent
E_THRES = 0.054  # eV/atom: E_hull of UCr6Ge6, the least stable synthesized compound, on the GGA hull (no margin)
F = {'La','Ce','Pr','Nd','Pm','Sm','Eu','Gd','Tb','Dy','Ho','Er','Tm','Yb','Lu','U'}; G = {'Si','Ge','Sn','Pb'}
SYNTH = {'UNb6Sn6': 'Yes', 'UV6Sn6': 'Yes', 'UCr6Ge6': 'Yes', 'UCo6Ge6': 'Yes'}
FAILED = ['UTi6Sn6','UMn6Sn6','UMn6Ge6','UFe6Sn6','UV6Ge6','UNi6Ge6','UNi6Sn6','UCo6Sn6','UTi6Ge6','UTa6Sn6','UNb6Ge6',
          'UHf6Ge6','UHf6Si6','UPd6Sn6','UAg6Sn6','UCu6Sn6','UCu6Ge6']  # 17 attempted-unsuccessful, from manuscript Table S1

def parse(name):
    els = {e: int(c or 1) for e, c in re.findall(r'([A-Z][a-z]?)(\d*)', name)}
    if sorted(els.values()) != [1, 6, 6]: return None
    f = [e for e in els if e in F]; g = [e for e in els if e in G]; m = [e for e in els if e not in F | G]
    return (f[0], m[0], g[0]) if len(f) == len(g) == len(m) == 1 else None

lk = BandpassDosRewardLookup(H / 'data/rdos_bandpass_RE_U.csv')
d = pd.read_csv(H / 'data/mace_cache_v3_gga.csv')
d['t'] = d.name.map(parse); d = d[d.t.notna()].copy()
d['compound'] = d.t.map(lambda t: f'{t[0]}{t[1]}6{t[2]}6'); d['f'], d['M'], d['X'] = zip(*d.t)
d['e_hull_rank'] = np.where(d.data_quality.isin(['no_mp_data', 'error']), UnstablePenalty, d.e_above_hull)
d = d.sort_values('e_hull_rank').drop_duplicates('compound')
d['r_S'] = np.exp(d.e_hull_rank.map(lambda e: ehull_reward(e, E_THRES)))
d['r_dos'] = d.compound.map(lambda c: lk.get_reward(c))
d['e_peak'] = d.compound.map(lambda c: lk.peak_energy.get(f'{parse(c)[0]}-{parse(c)[2]}-{parse(c)[1]}', np.nan))
d['reward'] = d.r_S * d.r_dos
assert len(d) == 1728, len(d)
cols = ['compound', 'f', 'M', 'X', 'e_above_hull', 'data_quality', 'r_S', 'r_dos', 'e_peak', 'reward']
for label, sub in (('u_only', d[d.f == 'U']), ('full', d)):
    r = sub.sort_values('reward', ascending=False, kind='stable').reset_index(drop=True)
    r['rank'] = np.arange(1, len(r) + 1); r['percentile'] = 100 * (len(r) - r['rank']) / len(r)
    r['synthesized'] = r.compound.map(lambda c: SYNTH.get(c, 'No' if c in FAILED else '--'))
    r[cols + ['rank', 'percentile', 'synthesized']].to_csv(H / f'rankings/{label}_ranking.csv', index=False, float_format='%.6g')
    print(f'== {label}: {len(r)} compounds; reward max {r.reward.max():.3f}; stable (E_hull<E_THRES): {(r.e_above_hull[r.data_quality=="valid"]<E_THRES).sum()}')
    print(r.head(15)[['rank', 'compound', 'e_above_hull', 'r_S', 'r_dos', 'reward', 'synthesized']].to_string(index=False, float_format='%.4g'))
u = pd.read_csv(H / 'rankings/u_only_ranking.csv')
print('synthesized ranks:', u[u.synthesized == 'Yes'][['compound', 'rank']].values.tolist())
print('UCr6Sn6 (old start) rank:', int(u[u.compound == 'UCr6Sn6']['rank'].iloc[0]))
