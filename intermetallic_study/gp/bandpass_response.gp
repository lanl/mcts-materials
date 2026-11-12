load "style.gp"; load "data/dos_labels.gp"
eval DOUBLE(6, 5.2)
set output "out/FigS_bandpass_response.pdf"
set multiplot layout 2,2 margins 0.1,0.98,0.09,0.95 spacing 0.14,0.16
set label 9 "(a)" at graph 0, graph 1 left offset 0,0.6 font FONTB tc rgb INK front; set title "band-pass response" center offset 0,-0.5 tc rgb INK
set xlabel "feature width (eV)" tc rgb INK offset 0,0.5; set ylabel "response (unit-height feature)" tc rgb INK offset 1,0
set xrange [0:1.5]; set yrange [0:0.8]; set xtics 0.5; set ytics 0.2
resp(w) = w/sqrt(w**2+0.05**2) - w/sqrt(w**2+0.5**2)
set label 1 sprintf("%.2f", resp(0.1)) at 0.15, resp(0.1)+0.02 tc rgb INK
set label 2 sprintf("%.2f", resp(0.5)) at 0.55, resp(0.5)+0.03 tc rgb INK
set label 3 sprintf("%.2f", resp(1.0)) at 1.05, resp(1.0)+0.03 tc rgb INK
plot "data/bandpass_response.dat" u 1:2 w l lc rgb B5 lw 2, "<echo '0.1 0\n0.5 0\n1.0 0'" u 1:(resp($1)) w p pt 7 ps 0.6 lc rgb C2
unset label 1; unset label 2; unset label 3
set xlabel "E - E_F (eV)" tc rgb INK offset 0,0.5; set ylabel "DOS (states/eV/atom)" tc rgb INK offset 1,0
set xrange [-2:2]; set yrange [0:4.8]; set xtics 1; set ytics 2
set arrow 1 from 0, graph 0 to 0, graph 1 nohead ls 15
set object 1 rect from -0.3, graph 0 to 0.3, graph 1 fc rgb C7 fs transparent solid 0.06 noborder behind
gal(c, let, ttl) = sprintf('set label 9 "(%s)" at graph 0, graph 1 left offset 0,0.6 font FONTB tc rgb INK front; set title "%s" center offset 0,-0.5 tc rgb INK; set label 4 sprintf("r_{DOS} %%.2f", RDOS_%s) at graph 0.05,0.9 left tc rgb INK front; plot "data/dos_%s.dat" u 1:3 w l ls 14, "" u 1:2 w l ls 10', let, ttl, c, c)
eval gal("DyFe6Sn6", "b", "DyFe_6Sn_6: sharp peak at E_F")
eval gal("TmHg6Ge6", "c", "TmHg_6Ge_6: featureless")
eval gal("EuCu6Sn6", "d", "EuCu_6Sn_6: flat (old rank 1)")
unset multiplot
