# RM6X6 flat-band study

The scripts that produce every result, table and figure of the manuscript
*Machine Learning-Accelerated Monte Carlo Tree Search for Inverse Design of
Quantum Materials* from the search code in `src/mcts_framework`. The study
runs with `mcts-run` and the cached property data described below; it needs
no Materials Project key and no DFT or MACE calculation of its own.

Everything here is read relative to this directory (`STUDY`) and the
repository root (`MCTS_REPO`, default: the parent of this directory).

## Data files (not in the repository)

Place these in `data/`. They are released with the manuscript; until then
they are available from the authors.

| File | Content | Used by |
|---|---|---|
| `mace_cache_v3_gga.csv` | MACE-MP-0 relaxed energies, `e_form` and `e_above_hull` (GGA/GGA+U hull with MP2020 corrections) of all 1,728 compositions | every search (`cache_path` in the configs), `rankings/compute_rankings.py` |
| `rdos_bandpass_RE_U.csv` | the band-pass `r_DOS` of every composition, computed from the DFT DOS with `mcts_framework.intermetallic.dos_bandpass` | every search (`doscar_data_path`), rankings |
| `projected_DOS.h5` | DFT total and element-projected DOS of the lanthanide compounds (`runs/RE_f_core`) and of the uranium compounds (`runs/U_f_core`) | `gp/export_gp_data.py`, `review/reward_sensitivity.py` |
| `u_doscar_list.csv` | DOSCAR paths of the uranium compounds (f in valence) | same |
| `formation_energy_parity_dft_vs_mace.csv` | DFT and MACE formation energies of every composition | `gp/export_gp_data.py`, `review/hull_check.py` |
| `mp_thermo_docs.jsonl` | the Materials Project thermo documents of every R–M–X system (one line per chemical system) | `review/hull_check.py` |
| `mace_cache_mixed_hull.csv` | the MACE cache of the earlier study with the mixed r²SCAN/GGA hull | `review/hull_check.py` (hull comparison, SI) |
| `experimental_compounds.txt` | the RM6X6 compounds reported in the literature (included) | tables, `collect_numbers.py` |
| `three_RE_candidates_bands_DOS.pdf`, `three_U_candidates_bands_DOS.pdf` | band structures supplied as PDFs | `gp/export_bands.py` |
| `mat_Sn6Tb1Cu6_sg191.cif` | the TbCu6Sn6 prototype used to start the lanthanide-uranium search (included) | `generate_study.py` |

The search configurations also use `examples/mat_Pb6U1W6_sg191.cif` from the
repository for the uranium space.

## Steps

All Python steps need the packages of the `[intermetallic]` extra plus
`pandas`, `scipy`, `h5py` and `pyyaml`; `review/hull_check.py` and
`review/stability_checks.py` need `pymatgen`; `review/baselines.py` needs
`scikit-learn`. Set `PY` to a Python with these packages (default `python3`).

1. **Reference rankings** (`rankings/u_only_ranking.csv`, `full_ranking.csv`):
   `$PY rankings/compute_rankings.py`. `E_THRES` at the top of the file is the
   stability threshold of the manuscript (0.054 eV/atom).
2. **Search configurations.** `generate_study.py grid --c 0.3 --rep-budget 0.5`
   writes the 15 uranium starting compounds (`grid_starting_materials.json`)
   and the representative searches; `generate_study.py full --c 0.3` writes
   the 15 lanthanide starting compounds and the lanthanide-uranium searches;
   `generate_variants.py <names>` writes the search-settings sweep of
   Supplementary Table S4 (`x8_d1n1_a05_term` is the setting used in the
   manuscript). Each call writes a run list (`run_list_*.txt`).
3. **Searches.** From this directory, `sbatch run_study.sbatch <run list>`
   runs every configuration of the list with 100 concurrent `mcts-run`
   processes (about 45 s per uranium search, a few minutes per lanthanide
   search, all from cached data). Finished runs are skipped on resubmission.
4. **Other search strategies** (Fig. 6, Table S3): from `review/`,
   `sbatch baselines.sbatch` (about an hour for the lanthanide-uranium space).
5. **Metrics and tables.** `./run_analysis.sh` runs, in order,
   `analyze_runs.py`, `analyze_budget.py`, `gp/export_gp_data.py`,
   `gp/export_run_data.py`, `make_tables.py`, `collect_numbers.py`,
   `review/stability_checks.py` and `review/reward_sensitivity.py`, and
   reports each step's exit status. Then `review/mcts_metrics.py`,
   `review/compare_methods.py` and `review/variants_compare.py` score the
   searches against the other strategies, and `fig8_pw.py` writes the
   convergence curves of Fig. 11 from the settings-sweep runs.
   `collect_numbers.py` writes `tables/numbers_v3.json`, which holds every
   number quoted in the text.
6. **Figures.** `gp/label_layout.py`, then `gnuplot <script>` for each
   script in `gp/` (gnuplot 6, pdfcairo). `FIG6_RUN=u_only FIG6_SUFFIX=_1x3
   FIG6_RING=1.7 FIG6_GAP=0.3 $PY gp/export_run_data.py representative`
   lays out the tree of Fig. 5.

## What produces what

| Manuscript item | Script(s) |
|---|---|
| Tables 1, 2; Figs. 4, 5, 7 | `gp/export_run_data.py representative`, `gp/label_layout.py`, `gp/fig4_scatter_u.gp`, `gp/fig6_radial_1x3.gp`, `gp/fig9_scatter_full.gp` |
| Fig. 3, Figs. 8–10, S1–S3, S5 | `gp/export_gp_data.py`, `gp/fig3_reward.gp`, `gp/dos_candidates.gp`, `gp/dos_trends.gp`, `gp/bandpass_response.gp`, `gp/dos_heatmap.gp`, `gp/dos_by_tm.gp`, `gp/parity.gp` |
| Fig. 9, S4 (bands) | `gp/export_bands.py`, `gp/bands_stacked.gp` |
| Fig. 6, Table S3 | `review/baselines.py`, `review/mcts_metrics.py`, `review/variants_compare.py`, `gp/export_review_data.py`, `gp/benchmark.gp` |
| Fig. 11 | `fig8_pw.py`, `gp/fig8b_convergence.gp` |
| Table S1, Sec. A.6–A.7 | `review/hull_check.py`, `review/stability_checks.py` |
| Table S2 | `review/reward_sensitivity.py` |
| Table S4 | `generate_variants.py`, `review/variants_compare.py` |
| Tables S5, S6 | `make_tables.py` |

Run directories (`representative/`, `full/`, `grid/`, `variants/`), run lists,
logs and generated tables are ignored by git.
