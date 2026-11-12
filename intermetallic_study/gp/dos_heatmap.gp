load "style.gp"
eval DOUBLE(6, 6)
set output "out/FigS_dos_heatmap.pdf"
NX = 801; NY = 1620; E0 = -2.0; DE = 0.005; VMAX = real(system("awk '{print $5}' data/dos_heatmap_meta.txt"))
set lmargin at screen 0.13; set rmargin at screen 0.84; set tmargin at screen 0.97; set bmargin at screen 0.08
set xlabel "E - E_F (eV)" tc rgb INK offset 0,0.4; set xrange [-2:2]; set xtics 1; set yrange [NY:0]
set ylabel "transition metal M (60 compounds each)" tc rgb INK offset -1.5,0
set palette defined (0 "#ffffff", 1 B1, 2 B2, 3 B3, 4 B4, 5 B5, 6 B6, 7 B7)
set cbrange [0:VMAX]; set cblabel "DOS (states/eV/atom)" tc rgb INK offset 0.5,0; set cbtics 0.5
set colorbox user origin screen 0.87, screen 0.08 size screen 0.03, screen 0.89
TM = "Ti V Cr Mn Fe Co Ni Cu Zn Zr Nb Mo Tc Ru Rh Pd Ag Cd Hf Ta W Re Os Ir Pt Au Hg"
set ytics ( "" 0 ) scale 0
do for [i=1:27] { set ytics add (word(TM,i) 60*(i-1)+30) }
unset grid
set arrow 1 from 0, NY to 0, 0 nohead lc rgb INK lw 0.8 dt 3 front
do for [i=1:26] { set arrow 10+i from -2, 60*i to 2, 60*i nohead lc rgb "white" lw 0.6 front }
plot "data/dos_heatmap.bin" binary array=(NX,NY) format="%float" dx=DE dy=1 origin=(E0,0.5) w image
