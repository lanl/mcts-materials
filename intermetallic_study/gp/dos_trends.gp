load "style.gp"; load "data/dos_labels.gp"
eval DOUBLE(6, 5.6)
set output "out/Fig_dos_trends.pdf"
set multiplot layout 2,2 margins 0.09,0.99,0.08,0.96 spacing 0.1,0.14
set xrange [-2:2]; set xtics -2,1,2; set xlabel "E - E_F (eV)" tc rgb INK offset 0,0.5; set ylabel "DOS (states/eV/atom)" tc rgb INK offset 1.5,0
set arrow 1 from 0, graph 0 to 0, graph 1 nohead ls 15
set key top right reverse Left samplen 0.8 spacing 0.85
set palette defined (0 B1, 1 B7); set cbrange [0:14]; unset colorbox
RE = "La Ce Pr Nd Pm Sm Eu Gd Tb Dy Ho Er Tm Yb Lu"
set label 9 "(a)" at graph 0, graph 1 left offset 0,0.6 font FONTB tc rgb INK front; set title "RFe_6Sn_6, R = La → Lu" center offset 0,-0.5 tc rgb INK; set yrange [0:4.8]; set ytics 2
plot for [i=1:15] sprintf("data/dos_%sFe6Sn6.dat", word(RE,i)) u 1:2:(i-1) w l lc palette lw 1 t (i%2==1 ? sprintf("%s (%.2f)", word(RE,i), value(sprintf("RDOS_%sFe6Sn6", word(RE,i)))) : "")
set label 9 "(b)" at graph 0, graph 1 left offset 0,0.6 font FONTB tc rgb INK front; set title "DyFe_6X_6, X = Si → Pb" center offset 0,-0.5 tc rgb INK; unset ylabel
XS = "Si Ge Sn Pb"; XC = B3." ".B4." ".B5." ".B7
plot for [i=1:4] sprintf("data/dos_DyFe6%s6.dat", word(XS,i)) u 1:2 w l lc rgb word(XC,i) lw 1.3 t sprintf("%s (%.2f; E_{hull} %.2f)", word(XS,i), value(sprintf("RDOS_DyFe6%s6", word(XS,i))), value(sprintf("EHULL_DyFe6%s6", word(XS,i))))
set label 9 "(c)" at graph 0, graph 1 left offset 0,0.6 font FONTB tc rgb INK front; set title "U vs Dy, same framework" center offset 0,-0.5 tc rgb INK; set ylabel "DOS (states/eV/atom)" tc rgb INK offset 1.5,0
plot "data/dos_UFe6Sn6.dat" u 1:2 w l lc rgb C2 lw 1.3 t sprintf("UFe_6Sn_6 (%.2f)", RDOS_UFe6Sn6), \
     "data/dos_DyFe6Sn6.dat" u 1:2 w l lc rgb B5 lw 1.3 t sprintf("DyFe_6Sn_6 (%.2f)", RDOS_DyFe6Sn6), \
     "data/dos_UTc6Ge6.dat" u 1:2 w l lc rgb C2 lw 1.3 dt 2 t sprintf("UTc_6Ge_6 (%.2f)", RDOS_UTc6Ge6), \
     "data/dos_DyTc6Ge6.dat" u 1:2 w l lc rgb B5 lw 1.3 dt 2 t sprintf("DyTc_6Ge_6 (%.2f)", RDOS_DyTc6Ge6)
set label 9 "(d)" at graph 0, graph 1 left offset 0,0.6 font FONTB tc rgb INK front; set title "synthesized UM_6X_6" center offset 0,-0.5 tc rgb INK; unset ylabel; set yrange [0:3.2]; set ytics 1
plot "data/dos_UCr6Ge6.dat" u 1:2 w l lc rgb C2 lw 1.3 t sprintf("UCr_6Ge_6 (#%d)", RANK_UCr6Ge6), \
     "data/dos_UV6Sn6.dat" u 1:2 w l lc rgb B5 lw 1.3 t sprintf("UV_6Sn_6 (#%d)", RANK_UV6Sn6), \
     "data/dos_UCo6Ge6.dat" u 1:2 w l lc rgb C3 lw 1.3 t sprintf("UCo_6Ge_6 (#%d)", RANK_UCo6Ge6), \
     "data/dos_UNb6Sn6.dat" u 1:2 w l lc rgb C4 lw 1.3 t sprintf("UNb_6Sn_6 (#%d)", RANK_UNb6Sn6)
unset multiplot
