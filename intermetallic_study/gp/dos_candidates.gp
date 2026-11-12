load "style.gp"; load "data/dos_labels.gp"
eval DOUBLE(6, 4.4)
set output "out/Fig_dos_candidates.pdf"
set multiplot layout 2,3 margins 0.09,0.99,0.17,0.95 spacing 0.06,0.16
set xrange [-2:2]; set xtics -2,1,2; set xlabel "E - E_F (eV)" tc rgb INK offset 0,0.5
set arrow 1 from 0, graph 0 to 0, graph 1 nohead ls 15
set object 1 rect from -0.3, graph 0 to 0.3, graph 1 fc rgb C7 fs transparent solid 0.06 noborder behind
panel(c, let, ttl, ymax, yt) = sprintf('set label 9 "(%s)" at graph 0, graph 1 left offset 0,0.6 font FONTB tc rgb INK front; set title "%s" center offset 0,-0.5 tc rgb INK; set yrange [0:%g]; set ytics %g; set label 1 sprintf("r_{DOS} %%.2f", RDOS_%s) at graph 0.96,0.9 right tc rgb INK front; plot "data/dos_%s.dat" u 1:2 w l ls 10, "" u 1:6 w l ls 12, "" u 1:7 w l ls 13, "" u 1:5 w l ls 11', let, ttl, ymax, yt, c, c)
unset key
# manual single-row legend in the bottom margin
LX = "0.22 0.40 0.58 0.76"; LT = "total M_(6) X_(6) R/U"
set arrow 52 from screen 0.22, screen 0.035 to screen 0.245, screen 0.035 nohead ls 10 front
set arrow 53 from screen 0.40, screen 0.035 to screen 0.425, screen 0.035 nohead ls 12 front
set arrow 54 from screen 0.58, screen 0.035 to screen 0.605, screen 0.035 nohead ls 13 front
set arrow 55 from screen 0.76, screen 0.035 to screen 0.785, screen 0.035 nohead ls 11 front
do for [i=1:4] { tag = 50+i; txt = (word(LT,i) eq "M_(6)" ? "M (6)" : word(LT,i) eq "X_(6)" ? "X (6)" : word(LT,i) eq "R/U" ? "R / U" : word(LT,i)); px = real(word(LX,i))+0.032; set label tag txt at screen px, screen 0.035 left tc rgb INK front }
set ylabel "DOS (states/eV/atom)" tc rgb INK offset 1.5,0
eval panel("UTc6Ge6", "a", "UTc_6Ge_6", 2.2, 1)
unset ylabel
eval panel("UTc6Sn6", "b", "UTc_6Sn_6", 2.2, 1)
eval panel("UTi6Sn6", "c", "UTi_6Sn_6", 2.2, 1)
set ylabel "DOS (states/eV/atom)" tc rgb INK offset 1.5,0
eval panel("DyFe6Sn6", "d", "DyFe_6Sn_6", 4.8, 2)
unset ylabel
eval panel("TmFe6Sn6", "e", "TmFe_6Sn_6", 4.8, 2)
eval panel("PmMn6Sn6", "f", "PmMn_6Sn_6", 4.8, 2)
unset multiplot
