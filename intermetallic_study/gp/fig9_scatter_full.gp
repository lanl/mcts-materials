load "style.gp"
eval SINGLE
set output "out/Fig9.pdf"
set border 3
set lmargin 7.5; set rmargin 1; set tmargin 0.6; set bmargin 3
set xlabel "r_{DOS} (states/eV/atom)" tc rgb INK offset 0,0.4; set ylabel "E_{hull} (eV/atom)" tc rgb INK offset 1.2,0
set xrange [-0.03:2.3]; set yrange [-0.1:1.5]; set xtics 0,0.5; set ytics 0,0.2
set arrow 1 from graph 0, first 0 to graph 1, first 0 nohead lc rgb INK lw 1 dt 2
set key at graph 0.98, graph 0.98 right top reverse Left samplen 1 spacing 1.15
set multiplot
set object 2 rect from 1.37, 0.0 to 1.95, 0.085 fc rgb "#00000000" fs empty border lc rgb MUTED lw 0.8 front
plot "data/fig9_space.dat" u 1:2 w p pt 7 ps 0.3 lc rgb GRAY t "All compounds", \
     "data/fig9_mcts_top15.dat" u 1:2 w p pt 9 ps 1.2 lc rgb SKY t "Top 15 (MCTS)", \
     "data/fig9_literature.dat" u 1:2 w p pt 13 ps 0.6 lc rgb RED t "Experimental literature"
# inset: the top-15 region, triangles numbered by MCTS rank (labels in two rows, leader lines)
unset key; unset arrow 1; unset xlabel; unset ylabel; unset title
set border 15 lc rgb INK lw 1
unset object 2
set origin 0.40, 0.30; set size 0.58, 0.47
set object 3 rect from screen 0.40, screen 0.30 to screen 0.985, screen 0.77 fc rgb "white" fs solid 1.0 noborder behind
set lmargin 5; set rmargin 0.5; set tmargin 0.5; set bmargin 1.6
set xrange [1.37:1.95]; set yrange [0.0:0.085]; set xtics 1.4,0.2,1.8 offset 0,0.4; set ytics 0,0.02 offset 0.4,0; set format y "%.2f"
set arrow 1 from graph 0, first 0 to graph 1, first 0 nohead lc rgb INK lw 1 dt 2
set label 58 "8" at 1.400, 0.0780 center font FONT tc rgb INK front
set arrow 58 from 1.400, 0.0740 to 1.6829, 0.0411 nohead lc rgb MUTED lw 0.7 back
set label 56 "6" at 1.573, 0.0780 center font FONT tc rgb INK front
set arrow 56 from 1.573, 0.0740 to 1.6924, 0.0380 nohead lc rgb MUTED lw 0.7 back
set label 54 "4" at 1.747, 0.0780 center font FONT tc rgb INK front
set arrow 54 from 1.747, 0.0740 to 1.6971, 0.0358 nohead lc rgb MUTED lw 0.7 back
set label 51 "1" at 1.920, 0.0780 center font FONT tc rgb INK front
set arrow 51 from 1.920, 0.0740 to 1.9042, 0.0327 nohead lc rgb MUTED lw 0.7 back
set label 65 "15" at 1.400, 0.0050 center font FONT tc rgb INK front
set arrow 65 from 1.400, 0.0090 to 1.3805, 0.0256 nohead lc rgb MUTED lw 0.7 back
set label 64 "14" at 1.452, 0.0050 center font FONT tc rgb INK front
set arrow 64 from 1.452, 0.0090 to 1.3985, 0.0270 nohead lc rgb MUTED lw 0.7 back
set label 63 "13" at 1.504, 0.0050 center font FONT tc rgb INK front
set arrow 63 from 1.504, 0.0090 to 1.4516, 0.0204 nohead lc rgb MUTED lw 0.7 back
set label 62 "12" at 1.556, 0.0050 center font FONT tc rgb INK front
set arrow 62 from 1.556, 0.0090 to 1.4525, 0.0171 nohead lc rgb MUTED lw 0.7 back
set label 61 "11" at 1.608, 0.0050 center font FONT tc rgb INK front
set arrow 61 from 1.608, 0.0090 to 1.4542, 0.0169 nohead lc rgb MUTED lw 0.7 back
set label 60 "10" at 1.660, 0.0050 center font FONT tc rgb INK front
set arrow 60 from 1.660, 0.0090 to 1.4581, 0.0191 nohead lc rgb MUTED lw 0.7 back
set label 59 "9" at 1.712, 0.0050 center font FONT tc rgb INK front
set arrow 59 from 1.712, 0.0090 to 1.4782, 0.0181 nohead lc rgb MUTED lw 0.7 back
set label 57 "7" at 1.764, 0.0050 center font FONT tc rgb INK front
set arrow 57 from 1.764, 0.0090 to 1.5716, 0.0164 nohead lc rgb MUTED lw 0.7 back
set label 55 "5" at 1.816, 0.0050 center font FONT tc rgb INK front
set arrow 55 from 1.816, 0.0090 to 1.6411, 0.0150 nohead lc rgb MUTED lw 0.7 back
set label 53 "3" at 1.868, 0.0050 center font FONT tc rgb INK front
set arrow 53 from 1.868, 0.0090 to 1.6913, 0.0162 nohead lc rgb MUTED lw 0.7 back
set label 52 "2" at 1.920, 0.0050 center font FONT tc rgb INK front
set arrow 52 from 1.920, 0.0090 to 1.8616, 0.0218 nohead lc rgb MUTED lw 0.7 back
plot "data/fig9_space.dat" u 1:2 w p pt 7 ps 0.3 lc rgb GRAY, \
     "data/fig9_mcts_top15.dat" u 1:2 w p pt 9 ps 1.2 lc rgb SKY, \
     "data/fig9_literature.dat" u 1:2 w p pt 13 ps 0.6 lc rgb RED
unset multiplot
