load "style.gp"
eval DOUBLE(6, 2.6)
set output "out/Fig3.pdf"
set multiplot layout 1,2 margins 0.09,0.98,0.19,0.9 spacing 0.12
set label 9 "(a)" at graph 0, graph 1 left offset 0,0.6 font FONTB tc rgb INK front; unset title
set xlabel "E_{hull} (eV/atom)" tc rgb INK offset 0,0.4; set ylabel "r_S" tc rgb INK
set xrange [-0.05:0.2]; set yrange [0:3]; set xtics 0,0.1; set ytics 0,1
set arrow 1 from 0.054, graph 0 to 0.054, graph 1 nohead ls 15
set label 1 "E_{thres}" at 0.062, 2.7 tc rgb MUTED
plot "data/rS.dat" u 1:2 w l lc rgb C6 lw 2.2, 1 w l lc rgb MUTED lw 0.6
unset arrow 1; unset label 1
set label 9 "(b)" at graph 0, graph 1 left offset 0,0.6 font FONTB tc rgb INK front; unset title
set xlabel "E - E_F (eV)" tc rgb INK offset 0,0.4; set ylabel "DOS (states/eV/atom)" tc rgb INK
set xrange [-2:2]; set yrange [0:4.8]; set xtics 1; set ytics 0,2
set key top left reverse Left samplen 0.8 spacing 0.9
set object 1 rect from -0.3, graph 0 to 0.3, graph 1 fc rgb C7 fs transparent solid 0.06 noborder behind
set arrow 2 from 0, graph 0 to 0, graph 1 nohead ls 15
plot "data/dos_DyFe6Sn6.dat" u 1:8 w l lc rgb "#b0b0b0" lw 0.8 t "DOS", \
     "" u 1:2 w l lc rgb C6 lw 1.6 t "DOS (0.05 eV)", \
     "" u 1:3 w l lc rgb C7 lw 1.6 dt 2 t "background (0.5 eV)"
unset multiplot
