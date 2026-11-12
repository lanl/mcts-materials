#!/usr/bin/env python3
"""Numbers for the reviewer points on the stability reward (v3: MP2020-corrected GGA/GGA+U hull,
E_thres = 0.07 eV/atom). Writes stability_checks.json and prints a summary.

1. Hull change: old mixed hull (v2 rankings, E_thres 0.05) vs consistent hull (v3 rankings,
   E_thres 0.054), and the pure hull effect at a fixed threshold of 0.05.
2. MACE vs DFT: stable/unstable agreement (E_hull < E_thres) with DFT formation energies placed
   on the same hull (lanthanides f in core, U f in valence; flagged DFT outliers excluded), and
   the reward ranking with DFT instead of MACE formation energies.
"""
import json, os
from pathlib import Path
import numpy as np, pandas as pd
from scipy.stats import spearmanr

H = Path(__file__).resolve().parent; S = H.parent; V2 = Path(os.environ.get("OLD_STUDY", S / "data/old_study"))   # rankings of the earlier, mixed-hull study (section 1 only)
E_THRES = 0.054
rS = lambda e, t=E_THRES: np.exp(-np.tanh(120 * (np.asarray(e) - t)))
h = pd.read_csv(H / "hull_check.csv").set_index("compound")
v3 = {k: pd.read_csv(S / f"rankings/{k}_ranking.csv").set_index("compound") for k in ("u_only", "full")}
v2 = {k: pd.read_csv(V2 / f"rankings/{k}_ranking.csv").set_index("compound") for k in ("u_only", "full")}
out = {}


def compare(a, b, label):
    """a, b: reward Series on the same index (a = reference)."""
    ra = a.rank(ascending=False); rb = b.rank(ascending=False)
    top = lambda s, k: set(s.sort_values(ascending=False).index[:k])
    res = {"n": int(len(a)), "spearman": float(spearmanr(a, b).correlation),
           "top15_overlap": len(top(a, 15) & top(b, 15)), "top50_overlap": len(top(a, 50) & top(b, 50)),
           "best_ref": a.idxmax(), "best_ref_new_rank": int(rb[a.idxmax()]), "best_new": b.idxmax(), "best_new_ref_rank": int(ra[b.idxmax()])}
    out[label] = res
    print(f"{label:55s} n={res['n']:4d} Spearman {res['spearman']:.3f}  top-15 {res['top15_overlap']:2d}/15  top-50 {res['top50_overlap']:2d}/50  "
          f"#1 {res['best_ref']} -> {res['best_ref_new_rank']}; new #1 {res['best_new']} (was {res['best_new_ref_rank']})")
    return res


print("== 1. hull change")
for sp in ("u_only", "full"):
    a = v2[sp].reward; b = v3[sp].reward.reindex(a.index)
    compare(a, b, f"{sp}: v2 (mixed hull, 0.05) vs v4 (GGA hull, 0.054)")
    idx = v3[sp].index
    pure = pd.Series(rS(h.loc[idx, "e_hull_gga"].fillna(10), 0.05) * v3[sp].r_dos.values, index=idx)
    compare(v2[sp].reward.reindex(idx), pure, f"{sp}: hull effect only (both at E_thres 0.05)")
valid = h[h.dq == "valid"]
d = valid.e_hull_gga - valid.e_hull_cache
out["ehull_shift"] = {"median_meV": float(1000 * d.median()), "mad_meV": float(1000 * d.abs().median()),
                      "p05_meV": float(1000 * d.quantile(.05)), "p95_meV": float(1000 * d.quantile(.95)),
                      "flips_at_0.05": int(((valid.e_hull_cache < .05) != (valid.e_hull_gga < .05)).sum()), "n": int(len(valid))}
print("E_hull shift GGA - old:", {k: round(v, 1) if isinstance(v, float) else v for k, v in out["ehull_shift"].items()})
u2, u3 = v2["u_only"], v3["u_only"]
syn = ["UCr6Ge6", "UV6Sn6", "UCo6Ge6", "UNb6Sn6"]
out["synthesized"] = {c: {"rank_v2": int(u2.loc[c, "rank"]), "rank_v3": int(u3.loc[c, "rank"]), "ehull_v2": float(u2.loc[c, "e_above_hull"]),
                          "ehull_v3": float(u3.loc[c, "e_above_hull"])} for c in syn}
print("synthesized:", out["synthesized"])

print("\n== 2. MACE vs DFT (DFT formation energy on the same GGA hull)")
z = valid[valid.e_form_dft.notna() & (valid.suspect != True)].copy()
z["e_hull_dft"] = z.e_hull_dft_gga
for t in (E_THRES, 0.05):
    for grp, sel in (("lanthanides", z.R != "U"), ("uranium", z.R == "U")):
        q = z[sel]; m, dd = q.e_hull_gga < t, q.e_hull_dft < t
        tp, tn, fp, fn = int((m & dd).sum()), int((~m & ~dd).sum()), int((m & ~dd).sum()), int((~m & dd).sum())
        po = (tp + tn) / len(q); pe = ((tp + fp) * (tp + fn) + (tn + fn) * (tn + fp)) / len(q) ** 2
        res = {"n": int(len(q)), "agree": po, "kappa": (po - pe) / (1 - pe), "both_stable": tp, "both_unstable": tn,
               "mace_only_stable": fp, "dft_only_stable": fn, "ehull_mae_meV": float(1000 * (q.e_hull_gga - q.e_hull_dft).abs().mean())}
        out[f"mace_vs_dft_{grp}_t{t}"] = res
        print(f"  E_thres {t:.2f} {grp:11s} n={len(q):4d}: agree {po:.1%} kappa {res['kappa']:.2f}; both stable {tp}, both unstable {tn}, "
              f"MACE-only {fp}, DFT-only {fn}; E_hull MAE {res['ehull_mae_meV']:.0f} meV/atom")
out["n_dft_outliers_excluded"] = int((valid.suspect == True).sum())
r_mace = pd.Series(rS(z.e_hull_gga.values) * v3["full"].r_dos.reindex(z.index).values, index=z.index)
r_dft = pd.Series(rS(z.e_hull_dft.values) * v3["full"].r_dos.reindex(z.index).values, index=z.index)
compare(r_mace, r_dft, "ranking MACE vs DFT formation energies, all")
uz = z.R == "U"
compare(r_mace[uz], r_dft[uz], "ranking MACE vs DFT formation energies, uranium")
lz = z.R != "U"
compare(r_mace[lz], r_dft[lz], "ranking MACE vs DFT formation energies, lanthanides")
mt = r_mace.sort_values(ascending=False).index[:15]; dr = r_dft.rank(ascending=False)
out["mace_top15_dft_ranks"] = {c: int(dr[c]) for c in mt}
print("MACE top-15 (all) -> rank with DFT:", out["mace_top15_dft_ranks"])
json.dump(out, open(H / "stability_checks.json", "w"), indent=1, default=float)
