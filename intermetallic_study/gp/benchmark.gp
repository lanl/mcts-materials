# Benchmark: fraction of runs that have evaluated the best compound vs number of compounds evaluated.
load "style.gp"; load "data/bench_meta.gp"
eval DOUBLE(6, 3.1)
set output "out/Fig_benchmark_rev7.pdf"
set multiplot layout 1,2 margins 0.1,0.98,0.34,0.91 spacing 0.08
M = "mctsi bo ga greedy walk random"
T = "MCTS|Bayesian optimization|Genetic algorithm|Greedy local search|Random walk|Random search"
COL = "#d7301f #4393c3 #1b9e77 #e6ab02 #7570b3 #8a8a8a"
DT = "1 2 1 1 3 2"
LW = "3.0 1.6 1.6 1.6 1.6 1.6"
lbl(i) = system(sprintf("echo '%s' | cut -d'|' -f%d", T, i))
set yrange [0:1.02]; set ytics 0, 0.25 format "%.2f"
set key off
set ylabel "fraction of runs with the best compound" tc rgb INK offset 1.2, 0
set title "(a) uranium space (108)" center tc rgb INK
set xlabel "compounds evaluated" tc rgb INK offset 0, 0.3
set xrange [0:B_u_only]; set xtics 0, 10
plot for [i=1:6] sprintf("data/bench_u_only_%s.dat", word(M, i)) u 1:2 w steps lc rgb word(COL, i) lw real(word(LW, i)) dt int(word(DT, i))
unset ylabel; set format y ""
set title "(b) lanthanide-uranium space (1,728)" center tc rgb INK
set xrange [0:B_full]; set xtics 0, 200
# shared legend under both panels: 4 columns x 2 rows, drawn as arrows + labels in screen coordinates
do for [i=1:6] {
  cx = 0.07 + 0.31 * ((i - 1) % 3); cy = 0.13 - 0.055 * ((i - 1) / 3)
  set arrow i from screen cx, screen cy to screen cx + 0.04, screen cy nohead lc rgb word(COL, i) lw real(word(LW, i)) dt int(word(DT, i))
  set label 100 + i lbl(i) at screen cx + 0.05, screen cy left tc rgb INK
}
plot for [i=1:6] sprintf("data/bench_full_%s.dat", word(M, i)) u 1:2 w steps lc rgb word(COL, i) lw real(word(LW, i)) dt int(word(DT, i))
unset multiplot
