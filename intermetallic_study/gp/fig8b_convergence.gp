load "style.gp"; load "data/fig8b_meta.gp"
eval SINGLE
set output "out/Fig8.pdf"
set lmargin 7.5; set rmargin 1; set tmargin 0.6; set bmargin 3
set xlabel "Compounds evaluated" tc rgb INK offset 0,0.4; set ylabel "Best reward found" tc rgb INK offset 1.2,0
set xrange [0:108]; set yrange [0:1.3]; set xtics 0,20; set ytics 0,0.2
set key bottom right reverse Left samplen 1.4 spacing 1.15
Q = "0-25 25-50 50-75 75-100"; QC = V1." ".V2." ".V3." ".V4
budget = sprintf("< printf '%d 0\\n%d 2\\n'", BUDGET, BUDGET)
plot for [i=1:4] sprintf("data/fig8b_%s.dat", word(Q,i)) u 1:3:4 w filledcurves fc rgb word(QC,i) fs transparent solid 0.25 noborder, \
     for [i=4:1:-1] sprintf("data/fig8b_%s.dat", word(Q,i)) u 1:2 w l lc rgb word(QC,i) lw 3.5 t word(Q,i)."%", \
     BEST95 w l lc rgb "#b0b0b0" lw 1.3 dt 3 t "95% best", \
     budget u 1:2 w l lc rgb "#e05050" lw 1.3 dt 2 t sprintf("Budget (%d)", BUDGET)
