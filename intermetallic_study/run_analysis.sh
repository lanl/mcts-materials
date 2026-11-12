#!/bin/bash
# Standard analysis chain of the study (after the grid/csweep/representative/full stages have run).
export PYTHONPATH="${MCTS_REPO:-$(cd "$(dirname "$0")/.." && pwd)}/src"
PY="${PY:-python3}"   # needs numpy, pandas, scipy, h5py, pymatgen, yaml
cd "$(dirname "$0")"
step() { echo "=== $1"; shift; "$@" 2>&1 | grep -v "Warn\|matplotlib\|mplstyle\|rcfile\|distribution" | tail -${TAILN:-6}; echo "--- exit ${PIPESTATUS[0]}"; }
step "analyze_runs csweep"      $PY analyze_runs.py csweep -o run_metrics_csweep.csv
step "analyze_runs grid+rep"    $PY analyze_runs.py grid representative -o run_metrics_grid.csv
step "analyze_budget"           $PY analyze_budget.py --budget 54
step "export_gp_data"           $PY gp/export_gp_data.py
step "export_run_data"          $PY gp/export_run_data.py representative grid
step "make_tables"              $PY make_tables.py
TAILN=40 step "collect_numbers" $PY collect_numbers.py
step "stability_checks"         $PY review/stability_checks.py
TAILN=40 step "reward_sensitivity" $PY review/reward_sensitivity.py
