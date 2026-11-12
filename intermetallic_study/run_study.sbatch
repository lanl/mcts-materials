#!/bin/bash
#SBATCH -J v4_eval
#SBATCH -p pdebug
#SBATCH -A pls2
#SBATCH -N 1
#SBATCH --ntasks-per-node=112
#SBATCH -t 01:00:00
#SBATCH -o logs/%x_%j.out        # relative to the submit directory: run `sbatch` from the study directory
# Run every config in the given run list (cached MCTS runs, ~46 s each) with
# 100 concurrent workers.  sbatch run_study.sbatch run_list_csweep.txt

set -u
STUDY="${STUDY:-$SLURM_SUBMIT_DIR}"
LIST="$STUDY/${1:?run list required}"
REPO="${MCTS_REPO:-$(dirname "$STUDY")}"
# No Materials Project key is needed: every configuration reads E_hull from the MACE cache (data/mace_cache_v3_gga.csv).
export OMP_NUM_THREADS=1 MKL_NUM_THREADS=1
mkdir -p "$STUDY/logs/runs"
cd "$REPO"

run_one() {
    cfg="$1"
    out=$(python3 -c "import yaml,sys; print(yaml.safe_load(open(sys.argv[1]))['mcts']['output_dir'])" "$cfg")
    if [ -f "$out/summary.json" ]; then echo "skip $cfg"; return 0; fi
    log="$STUDY/logs/runs/$(echo "$cfg" | sed "s#$STUDY/##; s#/#__#g; s#.yaml#.log#")"
    "$REPO/.venv/bin/mcts-run" run --config "$cfg" > "$log" 2>&1 || echo "FAILED $cfg"
}
export -f run_one
export STUDY REPO

start=$(date +%s)
xargs -P 100 -I{} bash -c 'run_one "$@"' _ {} < "$LIST"
n_done=0; while read -r cfg; do out=$(grep output_dir "$cfg" | awk '{print $2}'); [ -f "$out/summary.json" ] && n_done=$((n_done+1)); done < "$LIST"
echo "done in $(( $(date +%s) - start )) s: $n_done / $(wc -l < "$LIST") summaries"
