load "style.gp"; load "data/parity_RE_f_core.gp"; load "data/parity_U_f_valence.gp"
eval DOUBLE(6, 3.1)
set output "out/FigS_mace_parity.pdf"
set multiplot layout 1,2 margins 0.1,0.98,0.17,0.9 spacing 0.1
set size ratio 1
eval VIRIDIS; unset colorbox
set xrange [-1.2:1.2]; set yrange [-1.2:1.2]; set xtics 0.5; set ytics 0.5
set xlabel "DFT E_{form} (eV/atom)" tc rgb INK offset 0,0.4; set ylabel "MACE E_{form} (eV/atom)" tc rgb INK
set title "(a) Uranium" center tc rgb INK
set label 1 sprintf("MAE = %.2f eV/atom\nR^2 = %.2f", MAE_U_f_valence/1000., R2_U_f_valence) at graph 0.05,0.92 left tc rgb INK front
plot "data/parity_U_f_valence_dens.dat" u 1:2:3 w p pt 7 ps 0.5 lc palette, x w l lc rgb "red" lw 1.2
set title "(b) Lanthanides" center tc rgb INK; unset ylabel
set label 1 sprintf("MAE = %.2f eV/atom\nR^2 = %.2f", MAE_RE_f_core/1000., R2_RE_f_core) at graph 0.05,0.92 left tc rgb INK front
plot "data/parity_RE_f_core_dens.dat" u 1:2:3 w p pt 7 ps 0.3 lc palette, x w l lc rgb "red" lw 1.2
unset multiplot
