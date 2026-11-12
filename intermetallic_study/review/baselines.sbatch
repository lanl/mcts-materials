#!/bin/bash
#SBATCH -J v4_baselines
#SBATCH -p pdebug
#SBATCH -A pls2
#SBATCH -N 1
#SBATCH --ntasks-per-node=112
#SBATCH -t 01:00:00
#SBATCH -o ../logs/%x_%j.out     # run `sbatch` from the review directory
export OMP_NUM_THREADS=1 MKL_NUM_THREADS=1 OPENBLAS_NUM_THREADS=1
cd "$SLURM_SUBMIT_DIR"
PY="${PY:-python3}"   # needs numpy, pandas, scikit-learn, scipy, pymatgen
start=$(date +%s)
$PY baselines.py --all u_only random,walk,greedy,ga,bo,al,rule_mnfe 105
echo "u_only done in $(( $(date +%s) - start )) s"
$PY baselines.py --all full random,walk,greedy,ga,bo,al,rule_mnfe 105
echo "full done in $(( $(date +%s) - start )) s"
