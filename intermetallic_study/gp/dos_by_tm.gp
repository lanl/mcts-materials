load "style.gp"; load "data/tm_medians.gp"
eval DOUBLE(6, 6)
set output "out/FigS_dos_by_tm.pdf"
set multiplot layout 5,6 margins 0.08,0.99,0.07,0.97 spacing 0.03,0.07
TM = "Ti V Cr Mn Fe Co Ni Cu Zn Zr Nb Mo Tc Ru Rh Pd Ag Cd Hf Ta W Re Os Ir Pt Au Hg"
set xrange [-2:2]; set yrange [0:2.6]; set xtics ("-2" -2, "0" 0, "2" 2); set ytics (0, 2)
set arrow 1 from 0, graph 0 to 0, graph 1 nohead ls 15
unset grid
col(i) = (i<=17 ? B2 : i<=32 ? B3 : i<=47 ? B5 : B7)
set key horizontal
set key at screen 0.8, screen 0.12 center maxrows 1 samplen 0.8 width -1
do for [k=1:27] {
  tm = word(TM,k)
  set title tm center offset 0,-0.6 tc rgb INK
  if (k > 21) { set xlabel "E - E_F (eV)" tc rgb INK offset 0,0.6 } else { unset xlabel; set format x "" }
  if (k > 21) { set format x "%g" }
  if (k % 6 == 1) { set format y "%g" } else { set format y "" }
  if (k == 1) {
    plot for [i=3:62] sprintf("data/tm_%s.dat", tm) u 1:i w l lc rgb col(i) lw 0.3, "" u 1:2 w l lc rgb INK lw 1, \
         NaN w l lc rgb B2 lw 1.6 t "Si", NaN w l lc rgb B3 lw 1.6 t "Ge", NaN w l lc rgb B5 lw 1.6 t "Sn", NaN w l lc rgb B7 lw 1.6 t "Pb", NaN w l lc rgb INK lw 1.6 t "median"
    unset key
  } else {
    plot for [i=3:62] sprintf("data/tm_%s.dat", tm) u 1:i w l lc rgb col(i) lw 0.3, "" u 1:2 w l lc rgb INK lw 1
  }
}
set label 10 "DOS (states/eV/atom)" at screen 0.015, screen 0.5 center rotate by 90 tc rgb INK
set origin 0,0; set size 1,1; unset border; unset tics; unset xlabel; unset ylabel; unset title; unset arrow 1
plot NaN notitle
unset multiplot
