load "style.gp"
eval SINGLE
set output "out/Fig4.pdf"
set border 3
set lmargin 7.5; set rmargin 2.2; set tmargin 0.6; set bmargin 3
set xlabel "r_{DOS} (states/eV/atom)" tc rgb INK offset 0,0.4; set ylabel "E_{hull} (eV/atom)" tc rgb INK offset 1.2,0
set xrange [-0.01:0.5]; set yrange [-0.2:1]; set xtics 0,0.1,0.5; set ytics -0.2,0.2,1
set arrow 1 from graph 0, first 0 to graph 1, first 0 nohead lc rgb INK lw 1 dt 2
set key top right reverse Left samplen 1 spacing 1.15
set label 38 "8" at 0.115, 0.400 left font FONT tc rgb INK front
set arrow 38 from 0.111, 0.400 to 0.0425, 0.0210 nohead lc rgb MUTED lw 0.7 back
set label 35 "5" at 0.115, 0.315 left font FONT tc rgb INK front
set arrow 35 from 0.111, 0.315 to 0.0617, -0.0109 nohead lc rgb MUTED lw 0.7 back
set label 43 "13" at 0.156, 0.353 right font FONT tc rgb INK front
set arrow 43 from 0.160, 0.343 to 0.1858, 0.2931 nohead lc rgb MUTED lw 0.7 back
set label 42 "12" at 0.227, 0.348 left font FONT tc rgb INK front
set arrow 42 from 0.223, 0.338 to 0.1967, 0.2879 nohead lc rgb MUTED lw 0.7 back
plot "data/fig4_space.dat" u 1:2 w p pt 7 ps 0.4 lc rgb GRAY t "All compounds", \
     "data/fig4_mcts_top15.dat" u 1:2 w p pt 9 ps 1.2 lc rgb SKY t "Top 15 (MCTS)", \
     "data/fig4_mcts_top15.dat" u 1:2:($1 > 0.1 && $3 != 13 && $3 != 12 ? sprintf("%d", $3) : "") w labels offset char 0.9,0.55 font FONT tc rgb INK, \
     "data/fig4_synth_no.dat" u 1:2 w p pt 4 ps 1.1 lw 1.5 lc rgb ORANGE t "Unsuccessful synthesis", \
     "data/fig4_synth_yes.dat" u 1:2 w p pt 5 ps 1.1 lc rgb ORANGE t "Successful synthesis"
