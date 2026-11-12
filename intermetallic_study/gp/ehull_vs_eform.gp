load "style.gp"
eval DOUBLE(6, 3.1)
set output "out/FigS_ehull_vs_eform.pdf"
set multiplot layout 1,2 margins 0.1,0.98,0.17,0.9 spacing 0.1
set size ratio 1
set xrange [-1.0:1.2]; set yrange [-0.2:1.6]; set xtics 0.5; set ytics 0.5
set xlabel "E_{form} (eV/atom)" tc rgb INK offset 0,0.4; set ylabel "E_{hull} (eV/atom)" tc rgb INK
set arrow 1 from graph 0, first 0 to graph 1, first 0 nohead lc rgb MUTED lw 1 dt 2
set arrow 2 from 0, graph 0 to 0, graph 1 nohead lc rgb MUTED lw 1 dt 2
set title "(a) Uranium compounds" center tc rgb INK
plot "data/eform_ehull_u.dat" u 1:2 w p pt 7 ps 0.55 lc rgb "#304682b4"
set title "(b) Lanthanide compounds" center tc rgb INK; unset ylabel
plot "data/eform_ehull_re.dat" u 1:2 w p pt 7 ps 0.3 lc rgb "#304682b4"
unset multiplot
