load "style.gp"
eval DOUBLE(6, 6.2)
set output "out/Fig2.pdf"
set multiplot layout 2,2 margins 0.01,0.99,0.01,0.96 spacing 0.02,0.06
unset border; unset tics; unset grid; unset key; set size ratio -1
set xrange [-0.3:10.1]; set yrange [-0.1:10.3]
set title "(a) Selection" left offset -2,-0.7 tc rgb INK
set object 2 circle at 5.0,9.5 size 0.36 fc rgb "#3987e5" fs solid 1.0 border lc rgb "#262626" lw 1.6 front
set arrow 3 from 5.0,9.5 to 2.9,8.2 nohead lc rgb "#8a8a8a" lw 1.2 front
set arrow 4 from 5.0,9.5 to 5.0,8.2 nohead lc rgb "#8a8a8a" lw 1.2 front
set arrow 5 from 5.0,9.5 to 7.1,8.2 nohead lc rgb "#8a8a8a" lw 1.2 front
set object 6 rect center 2.9,8.2 size 0.66,0.6 fc rgb "#cde2fb" fs solid 1.0 border lc rgb "white" lw 0.8 front
set object 7 rect center 5.0,8.2 size 0.66,0.6 fc rgb "#3987e5" fs solid 1.0 border lc rgb "#262626" lw 1.6 front
set object 8 rect center 7.1,8.2 size 0.66,0.6 fc rgb "#cde2fb" fs solid 1.0 border lc rgb "white" lw 0.8 front
set arrow 9 from 4.98,9.1 to 4.98,8.549999999999999 head filled size 0.22,20 lc rgb "#eb6834" lw 2.2 front
set object 10 rect center 0.35,4.55 size 0.6799999999999999,0.74 fc rgb "#3987e5" fs solid 1.0 border lc rgb "white" lw 0.6 front
set label 10 "Ti" at 0.35,4.55 center tc rgb "white" font "Helvetica,10" front
set object 11 rect center 1.0699999999999998,4.55 size 0.6799999999999999,0.74 fc rgb "#3987e5" fs solid 1.0 border lc rgb "white" lw 0.6 front
set label 11 "V" at 1.0699999999999998,4.55 center tc rgb "white" font "Helvetica,10" front
set object 12 rect center 1.79,4.55 size 0.6799999999999999,0.74 fc rgb "#3987e5" fs solid 1.0 border lc rgb "#eb6834" lw 2.2 front
set label 12 "Cr" at 1.79,4.55 center tc rgb "white" font "Helvetica,10" front
set object 13 rect center 2.5100000000000002,4.55 size 0.6799999999999999,0.74 fc rgb "#3987e5" fs solid 1.0 border lc rgb "#eb6834" lw 2.2 front
set label 13 "Mn" at 2.5100000000000002,4.55 center tc rgb "white" font "Helvetica,10" front
set object 14 rect center 3.23,4.55 size 0.6799999999999999,0.74 fc rgb "#3987e5" fs solid 1.0 border lc rgb "white" lw 0.6 front
set label 14 "Fe" at 3.23,4.55 center tc rgb "white" font "Helvetica,10" front
set object 15 rect center 3.9499999999999997,4.55 size 0.6799999999999999,0.74 fc rgb "#3987e5" fs solid 1.0 border lc rgb "white" lw 0.6 front
set label 15 "Co" at 3.9499999999999997,4.55 center tc rgb "white" font "Helvetica,10" front
set object 16 rect center 4.67,4.55 size 0.6799999999999999,0.74 fc rgb "#3987e5" fs solid 1.0 border lc rgb "white" lw 0.6 front
set label 16 "Ni" at 4.67,4.55 center tc rgb "white" font "Helvetica,10" front
set object 17 rect center 5.39,4.55 size 0.6799999999999999,0.74 fc rgb "#3987e5" fs solid 1.0 border lc rgb "white" lw 0.6 front
set label 17 "Cu" at 5.39,4.55 center tc rgb "white" font "Helvetica,10" front
set object 18 rect center 6.109999999999999,4.55 size 0.6799999999999999,0.74 fc rgb "#3987e5" fs solid 1.0 border lc rgb "white" lw 0.6 front
set label 18 "Zn" at 6.109999999999999,4.55 center tc rgb "white" font "Helvetica,10" front
set object 19 rect center 0.35,3.7699999999999996 size 0.6799999999999999,0.74 fc rgb "#3987e5" fs solid 1.0 border lc rgb "white" lw 0.6 front
set label 19 "Zr" at 0.35,3.7699999999999996 center tc rgb "white" font "Helvetica,10" front
set object 20 rect center 1.0699999999999998,3.7699999999999996 size 0.6799999999999999,0.74 fc rgb "#3987e5" fs solid 1.0 border lc rgb "white" lw 0.6 front
set label 20 "Nb" at 1.0699999999999998,3.7699999999999996 center tc rgb "white" font "Helvetica,10" front
set object 21 rect center 1.79,3.7699999999999996 size 0.6799999999999999,0.74 fc rgb "#3987e5" fs solid 1.0 border lc rgb "white" lw 0.6 front
set label 21 "Mo" at 1.79,3.7699999999999996 center tc rgb "white" font "Helvetica,10" front
set object 22 rect center 2.5100000000000002,3.7699999999999996 size 0.6799999999999999,0.74 fc rgb "#3987e5" fs solid 1.0 border lc rgb "white" lw 0.6 front
set label 22 "Tc" at 2.5100000000000002,3.7699999999999996 center tc rgb "white" font "Helvetica,10" front
set object 23 rect center 3.23,3.7699999999999996 size 0.6799999999999999,0.74 fc rgb "#3987e5" fs solid 1.0 border lc rgb "white" lw 0.6 front
set label 23 "Ru" at 3.23,3.7699999999999996 center tc rgb "white" font "Helvetica,10" front
set object 24 rect center 3.9499999999999997,3.7699999999999996 size 0.6799999999999999,0.74 fc rgb "#3987e5" fs solid 1.0 border lc rgb "white" lw 0.6 front
set label 24 "Rh" at 3.9499999999999997,3.7699999999999996 center tc rgb "white" font "Helvetica,10" front
set object 25 rect center 4.67,3.7699999999999996 size 0.6799999999999999,0.74 fc rgb "#3987e5" fs solid 1.0 border lc rgb "white" lw 0.6 front
set label 25 "Pd" at 4.67,3.7699999999999996 center tc rgb "white" font "Helvetica,10" front
set object 26 rect center 5.39,3.7699999999999996 size 0.6799999999999999,0.74 fc rgb "#3987e5" fs solid 1.0 border lc rgb "white" lw 0.6 front
set label 26 "Ag" at 5.39,3.7699999999999996 center tc rgb "white" font "Helvetica,10" front
set object 27 rect center 6.109999999999999,3.7699999999999996 size 0.6799999999999999,0.74 fc rgb "#3987e5" fs solid 1.0 border lc rgb "white" lw 0.6 front
set label 27 "Cd" at 6.109999999999999,3.7699999999999996 center tc rgb "white" font "Helvetica,10" front
set object 28 rect center 0.35,2.9899999999999998 size 0.6799999999999999,0.74 fc rgb "#3987e5" fs solid 1.0 border lc rgb "white" lw 0.6 front
set label 28 "Hf" at 0.35,2.9899999999999998 center tc rgb "white" font "Helvetica,10" front
set object 29 rect center 1.0699999999999998,2.9899999999999998 size 0.6799999999999999,0.74 fc rgb "#3987e5" fs solid 1.0 border lc rgb "white" lw 0.6 front
set label 29 "Ta" at 1.0699999999999998,2.9899999999999998 center tc rgb "white" font "Helvetica,10" front
set object 30 rect center 1.79,2.9899999999999998 size 0.6799999999999999,0.74 fc rgb "#3987e5" fs solid 1.0 border lc rgb "white" lw 0.6 front
set label 30 "W" at 1.79,2.9899999999999998 center tc rgb "white" font "Helvetica,10" front
set object 31 rect center 2.5100000000000002,2.9899999999999998 size 0.6799999999999999,0.74 fc rgb "#3987e5" fs solid 1.0 border lc rgb "white" lw 0.6 front
set label 31 "Re" at 2.5100000000000002,2.9899999999999998 center tc rgb "white" font "Helvetica,10" front
set object 32 rect center 3.23,2.9899999999999998 size 0.6799999999999999,0.74 fc rgb "#3987e5" fs solid 1.0 border lc rgb "white" lw 0.6 front
set label 32 "Os" at 3.23,2.9899999999999998 center tc rgb "white" font "Helvetica,10" front
set object 33 rect center 3.9499999999999997,2.9899999999999998 size 0.6799999999999999,0.74 fc rgb "#3987e5" fs solid 1.0 border lc rgb "white" lw 0.6 front
set label 33 "Ir" at 3.9499999999999997,2.9899999999999998 center tc rgb "white" font "Helvetica,10" front
set object 34 rect center 4.67,2.9899999999999998 size 0.6799999999999999,0.74 fc rgb "#3987e5" fs solid 1.0 border lc rgb "white" lw 0.6 front
set label 34 "Pt" at 4.67,2.9899999999999998 center tc rgb "white" font "Helvetica,10" front
set object 35 rect center 5.39,2.9899999999999998 size 0.6799999999999999,0.74 fc rgb "#3987e5" fs solid 1.0 border lc rgb "white" lw 0.6 front
set label 35 "Au" at 5.39,2.9899999999999998 center tc rgb "white" font "Helvetica,10" front
set object 36 rect center 6.109999999999999,2.9899999999999998 size 0.6799999999999999,0.74 fc rgb "#3987e5" fs solid 1.0 border lc rgb "white" lw 0.6 front
set label 36 "Hg" at 6.109999999999999,2.9899999999999998 center tc rgb "white" font "Helvetica,10" front
set object 37 rect center 8.9,5.35 size 0.6799999999999999,0.74 fc rgb "#eb6834" fs solid 1.0 border lc rgb "white" lw 0.6 front
set label 37 "Si" at 8.9,5.35 center tc rgb "white" font "Helvetica,10" front
set object 38 rect center 8.9,4.569999999999999 size 0.6799999999999999,0.74 fc rgb "#eb6834" fs solid 1.0 border lc rgb "white" lw 0.6 front
set label 38 "Ge" at 8.9,4.569999999999999 center tc rgb "white" font "Helvetica,10" front
set object 39 rect center 8.9,3.7899999999999996 size 0.6799999999999999,0.74 fc rgb "#eb6834" fs solid 1.0 border lc rgb "#eb6834" lw 2.2 front
set label 39 "Sn" at 8.9,3.7899999999999996 center tc rgb "white" font "Helvetica,10" front
set object 40 rect center 8.9,3.01 size 0.6799999999999999,0.74 fc rgb "#eb6834" fs solid 1.0 border lc rgb "white" lw 0.6 front
set label 40 "Pb" at 8.9,3.01 center tc rgb "white" font "Helvetica,10" front
set object 41 rect center 0.35,1.55 size 0.58,0.74 fc rgb "#1baf7a" fs solid 1.0 border lc rgb "white" lw 0.6 front
set label 41 "La" at 0.35,1.55 center tc rgb "white" font "Helvetica,10" front
set object 42 rect center 0.97,1.55 size 0.58,0.74 fc rgb "#1baf7a" fs solid 1.0 border lc rgb "white" lw 0.6 front
set label 42 "Ce" at 0.97,1.55 center tc rgb "white" font "Helvetica,10" front
set object 43 rect center 1.5899999999999999,1.55 size 0.58,0.74 fc rgb "#1baf7a" fs solid 1.0 border lc rgb "white" lw 0.6 front
set label 43 "Pr" at 1.5899999999999999,1.55 center tc rgb "white" font "Helvetica,10" front
set object 44 rect center 2.21,1.55 size 0.58,0.74 fc rgb "#1baf7a" fs solid 1.0 border lc rgb "white" lw 0.6 front
set label 44 "Nd" at 2.21,1.55 center tc rgb "white" font "Helvetica,10" front
set object 45 rect center 2.83,1.55 size 0.58,0.74 fc rgb "#1baf7a" fs solid 1.0 border lc rgb "white" lw 0.6 front
set label 45 "Pm" at 2.83,1.55 center tc rgb "white" font "Helvetica,10" front
set object 46 rect center 3.45,1.55 size 0.58,0.74 fc rgb "#1baf7a" fs solid 1.0 border lc rgb "white" lw 0.6 front
set label 46 "Sm" at 3.45,1.55 center tc rgb "white" font "Helvetica,10" front
set object 47 rect center 4.069999999999999,1.55 size 0.58,0.74 fc rgb "#1baf7a" fs solid 1.0 border lc rgb "white" lw 0.6 front
set label 47 "Eu" at 4.069999999999999,1.55 center tc rgb "white" font "Helvetica,10" front
set object 48 rect center 4.6899999999999995,1.55 size 0.58,0.74 fc rgb "#1baf7a" fs solid 1.0 border lc rgb "white" lw 0.6 front
set label 48 "Gd" at 4.6899999999999995,1.55 center tc rgb "white" font "Helvetica,10" front
set object 49 rect center 5.31,1.55 size 0.58,0.74 fc rgb "#1baf7a" fs solid 1.0 border lc rgb "white" lw 0.6 front
set label 49 "Tb" at 5.31,1.55 center tc rgb "white" font "Helvetica,10" front
set object 50 rect center 5.93,1.55 size 0.58,0.74 fc rgb "#1baf7a" fs solid 1.0 border lc rgb "white" lw 0.6 front
set label 50 "Dy" at 5.93,1.55 center tc rgb "white" font "Helvetica,10" front
set object 51 rect center 6.55,1.55 size 0.58,0.74 fc rgb "#1baf7a" fs solid 1.0 border lc rgb "white" lw 0.6 front
set label 51 "Ho" at 6.55,1.55 center tc rgb "white" font "Helvetica,10" front
set object 52 rect center 7.17,1.55 size 0.58,0.74 fc rgb "#1baf7a" fs solid 1.0 border lc rgb "white" lw 0.6 front
set label 52 "Er" at 7.17,1.55 center tc rgb "white" font "Helvetica,10" front
set object 53 rect center 7.789999999999999,1.55 size 0.58,0.74 fc rgb "#1baf7a" fs solid 1.0 border lc rgb "white" lw 0.6 front
set label 53 "Tm" at 7.789999999999999,1.55 center tc rgb "white" font "Helvetica,10" front
set object 54 rect center 8.41,1.55 size 0.58,0.74 fc rgb "#1baf7a" fs solid 1.0 border lc rgb "white" lw 0.6 front
set label 54 "Yb" at 8.41,1.55 center tc rgb "white" font "Helvetica,10" front
set object 55 rect center 9.03,1.55 size 0.58,0.74 fc rgb "#1baf7a" fs solid 1.0 border lc rgb "white" lw 0.6 front
set label 55 "Lu" at 9.03,1.55 center tc rgb "white" font "Helvetica,10" front
set object 56 rect center 2.21,0.55 size 0.58,0.74 fc rgb "#262626" fs solid 1.0 border lc rgb "#eb6834" lw 2.2 front
set label 56 "U" at 2.21,0.55 center tc rgb "white" font "Helvetica,10" front
set arrow 57 from 1.79,5.159999999999999 to 2.5100000000000002,5.159999999999999 head filled size 0.22,20 lc rgb "#eb6834" lw 2.2 front
plot NaN notitle
unset for [i=2:57] object i; unset for [i=2:57] label i; unset for [i=2:57] arrow i; unset label 900
set title "(b) Expansion" left offset -2,-0.7 tc rgb INK
set object 58 circle at 5.0,9.5 size 0.36 fc rgb "#cde2fb" fs solid 1.0 border lc rgb "white" lw 0.8 front
set arrow 59 from 5.0,9.5 to 2.9,8.2 nohead lc rgb "#8a8a8a" lw 1.2 front
set arrow 60 from 5.0,9.5 to 5.0,8.2 nohead lc rgb "#8a8a8a" lw 1.2 front
set arrow 61 from 5.0,9.5 to 7.1,8.2 nohead lc rgb "#8a8a8a" lw 1.2 front
set object 62 rect center 2.9,8.2 size 0.66,0.6 fc rgb "#cde2fb" fs solid 1.0 border lc rgb "white" lw 0.8 front
set object 63 rect center 5.0,8.2 size 0.66,0.6 fc rgb "#3987e5" fs solid 1.0 border lc rgb "white" lw 0.8 front
set object 64 rect center 7.1,8.2 size 0.66,0.6 fc rgb "#cde2fb" fs solid 1.0 border lc rgb "white" lw 0.8 front
set arrow 65 from 5.0,8.2 to 4.1,6.9 nohead lc rgb "#8a8a8a" lw 1.2 front
set arrow 66 from 5.0,8.2 to 5.9,6.9 nohead lc rgb "#eb6834" lw 2 front
set object 67 circle at 4.1,6.9 size 0.36 fc rgb "#cde2fb" fs solid 1.0 border lc rgb "white" lw 0.8 front
set object 68 circle at 5.9,6.9 size 0.36 fc rgb "#eb6834" fs solid 1.0 border lc rgb "#262626" lw 1.6 front
set object 69 rect center 0.35,4.55 size 0.6799999999999999,0.74 fc rgb "#3987e5" fs solid 1.0 border lc rgb "white" lw 0.6 front
set label 69 "Ti" at 0.35,4.55 center tc rgb "white" font "Helvetica,10" front
set object 70 rect center 1.0699999999999998,4.55 size 0.6799999999999999,0.74 fc rgb "#3987e5" fs solid 1.0 border lc rgb "white" lw 0.6 front
set label 70 "V" at 1.0699999999999998,4.55 center tc rgb "white" font "Helvetica,10" front
set object 71 rect center 1.79,4.55 size 0.6799999999999999,0.74 fc rgb "#3987e5" fs solid 1.0 border lc rgb "white" lw 0.6 front
set label 71 "Cr" at 1.79,4.55 center tc rgb "white" font "Helvetica,10" front
set object 72 rect center 2.5100000000000002,4.55 size 0.6799999999999999,0.74 fc rgb "#3987e5" fs solid 1.0 border lc rgb "#eb6834" lw 2.2 front
set label 72 "Mn" at 2.5100000000000002,4.55 center tc rgb "white" font "Helvetica,10" front
set object 73 rect center 3.23,4.55 size 0.6799999999999999,0.74 fc rgb "#3987e5" fs solid 1.0 border lc rgb "#eb6834" lw 2.2 front
set label 73 "Fe" at 3.23,4.55 center tc rgb "white" font "Helvetica,10" front
set object 74 rect center 3.9499999999999997,4.55 size 0.6799999999999999,0.74 fc rgb "#3987e5" fs solid 1.0 border lc rgb "white" lw 0.6 front
set label 74 "Co" at 3.9499999999999997,4.55 center tc rgb "white" font "Helvetica,10" front
set object 75 rect center 4.67,4.55 size 0.6799999999999999,0.74 fc rgb "#3987e5" fs solid 1.0 border lc rgb "white" lw 0.6 front
set label 75 "Ni" at 4.67,4.55 center tc rgb "white" font "Helvetica,10" front
set object 76 rect center 5.39,4.55 size 0.6799999999999999,0.74 fc rgb "#3987e5" fs solid 1.0 border lc rgb "white" lw 0.6 front
set label 76 "Cu" at 5.39,4.55 center tc rgb "white" font "Helvetica,10" front
set object 77 rect center 6.109999999999999,4.55 size 0.6799999999999999,0.74 fc rgb "#3987e5" fs solid 1.0 border lc rgb "white" lw 0.6 front
set label 77 "Zn" at 6.109999999999999,4.55 center tc rgb "white" font "Helvetica,10" front
set object 78 rect center 0.35,3.7699999999999996 size 0.6799999999999999,0.74 fc rgb "#3987e5" fs solid 1.0 border lc rgb "white" lw 0.6 front
set label 78 "Zr" at 0.35,3.7699999999999996 center tc rgb "white" font "Helvetica,10" front
set object 79 rect center 1.0699999999999998,3.7699999999999996 size 0.6799999999999999,0.74 fc rgb "#3987e5" fs solid 1.0 border lc rgb "white" lw 0.6 front
set label 79 "Nb" at 1.0699999999999998,3.7699999999999996 center tc rgb "white" font "Helvetica,10" front
set object 80 rect center 1.79,3.7699999999999996 size 0.6799999999999999,0.74 fc rgb "#3987e5" fs solid 1.0 border lc rgb "white" lw 0.6 front
set label 80 "Mo" at 1.79,3.7699999999999996 center tc rgb "white" font "Helvetica,10" front
set object 81 rect center 2.5100000000000002,3.7699999999999996 size 0.6799999999999999,0.74 fc rgb "#3987e5" fs solid 1.0 border lc rgb "white" lw 0.6 front
set label 81 "Tc" at 2.5100000000000002,3.7699999999999996 center tc rgb "white" font "Helvetica,10" front
set object 82 rect center 3.23,3.7699999999999996 size 0.6799999999999999,0.74 fc rgb "#3987e5" fs solid 1.0 border lc rgb "white" lw 0.6 front
set label 82 "Ru" at 3.23,3.7699999999999996 center tc rgb "white" font "Helvetica,10" front
set object 83 rect center 3.9499999999999997,3.7699999999999996 size 0.6799999999999999,0.74 fc rgb "#3987e5" fs solid 1.0 border lc rgb "white" lw 0.6 front
set label 83 "Rh" at 3.9499999999999997,3.7699999999999996 center tc rgb "white" font "Helvetica,10" front
set object 84 rect center 4.67,3.7699999999999996 size 0.6799999999999999,0.74 fc rgb "#3987e5" fs solid 1.0 border lc rgb "white" lw 0.6 front
set label 84 "Pd" at 4.67,3.7699999999999996 center tc rgb "white" font "Helvetica,10" front
set object 85 rect center 5.39,3.7699999999999996 size 0.6799999999999999,0.74 fc rgb "#3987e5" fs solid 1.0 border lc rgb "white" lw 0.6 front
set label 85 "Ag" at 5.39,3.7699999999999996 center tc rgb "white" font "Helvetica,10" front
set object 86 rect center 6.109999999999999,3.7699999999999996 size 0.6799999999999999,0.74 fc rgb "#3987e5" fs solid 1.0 border lc rgb "white" lw 0.6 front
set label 86 "Cd" at 6.109999999999999,3.7699999999999996 center tc rgb "white" font "Helvetica,10" front
set object 87 rect center 0.35,2.9899999999999998 size 0.6799999999999999,0.74 fc rgb "#3987e5" fs solid 1.0 border lc rgb "white" lw 0.6 front
set label 87 "Hf" at 0.35,2.9899999999999998 center tc rgb "white" font "Helvetica,10" front
set object 88 rect center 1.0699999999999998,2.9899999999999998 size 0.6799999999999999,0.74 fc rgb "#3987e5" fs solid 1.0 border lc rgb "white" lw 0.6 front
set label 88 "Ta" at 1.0699999999999998,2.9899999999999998 center tc rgb "white" font "Helvetica,10" front
set object 89 rect center 1.79,2.9899999999999998 size 0.6799999999999999,0.74 fc rgb "#3987e5" fs solid 1.0 border lc rgb "white" lw 0.6 front
set label 89 "W" at 1.79,2.9899999999999998 center tc rgb "white" font "Helvetica,10" front
set object 90 rect center 2.5100000000000002,2.9899999999999998 size 0.6799999999999999,0.74 fc rgb "#3987e5" fs solid 1.0 border lc rgb "white" lw 0.6 front
set label 90 "Re" at 2.5100000000000002,2.9899999999999998 center tc rgb "white" font "Helvetica,10" front
set object 91 rect center 3.23,2.9899999999999998 size 0.6799999999999999,0.74 fc rgb "#3987e5" fs solid 1.0 border lc rgb "white" lw 0.6 front
set label 91 "Os" at 3.23,2.9899999999999998 center tc rgb "white" font "Helvetica,10" front
set object 92 rect center 3.9499999999999997,2.9899999999999998 size 0.6799999999999999,0.74 fc rgb "#3987e5" fs solid 1.0 border lc rgb "white" lw 0.6 front
set label 92 "Ir" at 3.9499999999999997,2.9899999999999998 center tc rgb "white" font "Helvetica,10" front
set object 93 rect center 4.67,2.9899999999999998 size 0.6799999999999999,0.74 fc rgb "#3987e5" fs solid 1.0 border lc rgb "white" lw 0.6 front
set label 93 "Pt" at 4.67,2.9899999999999998 center tc rgb "white" font "Helvetica,10" front
set object 94 rect center 5.39,2.9899999999999998 size 0.6799999999999999,0.74 fc rgb "#3987e5" fs solid 1.0 border lc rgb "white" lw 0.6 front
set label 94 "Au" at 5.39,2.9899999999999998 center tc rgb "white" font "Helvetica,10" front
set object 95 rect center 6.109999999999999,2.9899999999999998 size 0.6799999999999999,0.74 fc rgb "#3987e5" fs solid 1.0 border lc rgb "white" lw 0.6 front
set label 95 "Hg" at 6.109999999999999,2.9899999999999998 center tc rgb "white" font "Helvetica,10" front
set object 96 rect center 8.9,5.35 size 0.6799999999999999,0.74 fc rgb "#eb6834" fs solid 1.0 border lc rgb "white" lw 0.6 front
set label 96 "Si" at 8.9,5.35 center tc rgb "white" font "Helvetica,10" front
set object 97 rect center 8.9,4.569999999999999 size 0.6799999999999999,0.74 fc rgb "#eb6834" fs solid 1.0 border lc rgb "white" lw 0.6 front
set label 97 "Ge" at 8.9,4.569999999999999 center tc rgb "white" font "Helvetica,10" front
set object 98 rect center 8.9,3.7899999999999996 size 0.6799999999999999,0.74 fc rgb "#eb6834" fs solid 1.0 border lc rgb "#eb6834" lw 2.2 front
set label 98 "Sn" at 8.9,3.7899999999999996 center tc rgb "white" font "Helvetica,10" front
set object 99 rect center 8.9,3.01 size 0.6799999999999999,0.74 fc rgb "#eb6834" fs solid 1.0 border lc rgb "white" lw 0.6 front
set label 99 "Pb" at 8.9,3.01 center tc rgb "white" font "Helvetica,10" front
set object 100 rect center 0.35,1.55 size 0.58,0.74 fc rgb "#1baf7a" fs solid 1.0 border lc rgb "white" lw 0.6 front
set label 100 "La" at 0.35,1.55 center tc rgb "white" font "Helvetica,10" front
set object 101 rect center 0.97,1.55 size 0.58,0.74 fc rgb "#1baf7a" fs solid 1.0 border lc rgb "white" lw 0.6 front
set label 101 "Ce" at 0.97,1.55 center tc rgb "white" font "Helvetica,10" front
set object 102 rect center 1.5899999999999999,1.55 size 0.58,0.74 fc rgb "#1baf7a" fs solid 1.0 border lc rgb "white" lw 0.6 front
set label 102 "Pr" at 1.5899999999999999,1.55 center tc rgb "white" font "Helvetica,10" front
set object 103 rect center 2.21,1.55 size 0.58,0.74 fc rgb "#1baf7a" fs solid 1.0 border lc rgb "white" lw 0.6 front
set label 103 "Nd" at 2.21,1.55 center tc rgb "white" font "Helvetica,10" front
set object 104 rect center 2.83,1.55 size 0.58,0.74 fc rgb "#1baf7a" fs solid 1.0 border lc rgb "white" lw 0.6 front
set label 104 "Pm" at 2.83,1.55 center tc rgb "white" font "Helvetica,10" front
set object 105 rect center 3.45,1.55 size 0.58,0.74 fc rgb "#1baf7a" fs solid 1.0 border lc rgb "white" lw 0.6 front
set label 105 "Sm" at 3.45,1.55 center tc rgb "white" font "Helvetica,10" front
set object 106 rect center 4.069999999999999,1.55 size 0.58,0.74 fc rgb "#1baf7a" fs solid 1.0 border lc rgb "white" lw 0.6 front
set label 106 "Eu" at 4.069999999999999,1.55 center tc rgb "white" font "Helvetica,10" front
set object 107 rect center 4.6899999999999995,1.55 size 0.58,0.74 fc rgb "#1baf7a" fs solid 1.0 border lc rgb "white" lw 0.6 front
set label 107 "Gd" at 4.6899999999999995,1.55 center tc rgb "white" font "Helvetica,10" front
set object 108 rect center 5.31,1.55 size 0.58,0.74 fc rgb "#1baf7a" fs solid 1.0 border lc rgb "white" lw 0.6 front
set label 108 "Tb" at 5.31,1.55 center tc rgb "white" font "Helvetica,10" front
set object 109 rect center 5.93,1.55 size 0.58,0.74 fc rgb "#1baf7a" fs solid 1.0 border lc rgb "white" lw 0.6 front
set label 109 "Dy" at 5.93,1.55 center tc rgb "white" font "Helvetica,10" front
set object 110 rect center 6.55,1.55 size 0.58,0.74 fc rgb "#1baf7a" fs solid 1.0 border lc rgb "white" lw 0.6 front
set label 110 "Ho" at 6.55,1.55 center tc rgb "white" font "Helvetica,10" front
set object 111 rect center 7.17,1.55 size 0.58,0.74 fc rgb "#1baf7a" fs solid 1.0 border lc rgb "white" lw 0.6 front
set label 111 "Er" at 7.17,1.55 center tc rgb "white" font "Helvetica,10" front
set object 112 rect center 7.789999999999999,1.55 size 0.58,0.74 fc rgb "#1baf7a" fs solid 1.0 border lc rgb "white" lw 0.6 front
set label 112 "Tm" at 7.789999999999999,1.55 center tc rgb "white" font "Helvetica,10" front
set object 113 rect center 8.41,1.55 size 0.58,0.74 fc rgb "#1baf7a" fs solid 1.0 border lc rgb "white" lw 0.6 front
set label 113 "Yb" at 8.41,1.55 center tc rgb "white" font "Helvetica,10" front
set object 114 rect center 9.03,1.55 size 0.58,0.74 fc rgb "#1baf7a" fs solid 1.0 border lc rgb "white" lw 0.6 front
set label 114 "Lu" at 9.03,1.55 center tc rgb "white" font "Helvetica,10" front
set object 115 rect center 2.21,0.55 size 0.58,0.74 fc rgb "#262626" fs solid 1.0 border lc rgb "#eb6834" lw 2.2 front
set label 115 "U" at 2.21,0.55 center tc rgb "white" font "Helvetica,10" front
set arrow 116 from 2.5100000000000002,5.159999999999999 to 3.23,5.159999999999999 head filled size 0.22,20 lc rgb "#eb6834" lw 2.2 front
plot NaN notitle
unset for [i=2:116] object i; unset for [i=2:116] label i; unset for [i=2:116] arrow i; unset label 900
set title "(c) Simulation" left offset -2,-0.7 tc rgb INK
set object 117 circle at 5.0,9.5 size 0.36 fc rgb "#cde2fb" fs solid 1.0 border lc rgb "white" lw 0.8 front
set arrow 118 from 5.0,9.5 to 2.9,8.2 nohead lc rgb "#8a8a8a" lw 1.2 front
set arrow 119 from 5.0,9.5 to 5.0,8.2 nohead lc rgb "#8a8a8a" lw 1.2 front
set arrow 120 from 5.0,9.5 to 7.1,8.2 nohead lc rgb "#8a8a8a" lw 1.2 front
set object 121 rect center 2.9,8.2 size 0.66,0.6 fc rgb "#cde2fb" fs solid 1.0 border lc rgb "white" lw 0.8 front
set object 122 rect center 5.0,8.2 size 0.66,0.6 fc rgb "#3987e5" fs solid 1.0 border lc rgb "white" lw 0.8 front
set object 123 rect center 7.1,8.2 size 0.66,0.6 fc rgb "#cde2fb" fs solid 1.0 border lc rgb "white" lw 0.8 front
set arrow 124 from 5.0,8.2 to 4.1,6.9 nohead lc rgb "#8a8a8a" lw 1.2 front
set arrow 125 from 5.0,8.2 to 5.9,6.9 nohead lc rgb "#8a8a8a" lw 1.2 front
set object 126 circle at 4.1,6.9 size 0.36 fc rgb "#cde2fb" fs solid 1.0 border lc rgb "white" lw 0.8 front
set object 127 circle at 5.9,6.9 size 0.36 fc rgb "#eb6834" fs solid 1.0 border lc rgb "#262626" lw 1.6 front
set arrow 128 from 6.28,6.9 to 6.72,6.9 head filled size 0.22,20 lc rgb "#eb6834" lw 1.8 dt 2 front
set object 129 circle at 7.1,6.9 size 0.36 fc rgb "white" fs solid 1.0 border lc rgb "#262626" lw 1.6 front
set arrow 130 from 7.4799999999999995,6.9 to 7.920000000000001,6.9 head filled size 0.22,20 lc rgb "#eb6834" lw 1.8 dt 2 front
set object 131 circle at 8.3,6.9 size 0.36 fc rgb "white" fs solid 1.0 border lc rgb "#262626" lw 1.6 front
set arrow 132 from 8.680000000000001,6.9 to 9.12,6.9 head filled size 0.22,20 lc rgb "#eb6834" lw 1.8 dt 2 front
set object 133 circle at 9.5,6.9 size 0.36 fc rgb "white" fs solid 1.0 border lc rgb "#262626" lw 1.6 front
set label 900 "rollout" at 8.3,7.55 center tc rgb "#eb6834" font "Helvetica,10" front
set object 134 rect center 0.35,4.55 size 0.6799999999999999,0.74 fc rgb "#3987e5" fs solid 1.0 border lc rgb "white" lw 0.6 front
set label 134 "Ti" at 0.35,4.55 center tc rgb "white" font "Helvetica,10" front
set object 135 rect center 1.0699999999999998,4.55 size 0.6799999999999999,0.74 fc rgb "#3987e5" fs solid 1.0 border lc rgb "white" lw 0.6 front
set label 135 "V" at 1.0699999999999998,4.55 center tc rgb "white" font "Helvetica,10" front
set object 136 rect center 1.79,4.55 size 0.6799999999999999,0.74 fc rgb "#3987e5" fs solid 1.0 border lc rgb "white" lw 0.6 front
set label 136 "Cr" at 1.79,4.55 center tc rgb "white" font "Helvetica,10" front
set object 137 rect center 2.5100000000000002,4.55 size 0.6799999999999999,0.74 fc rgb "#3987e5" fs solid 1.0 border lc rgb "white" lw 0.6 front
set label 137 "Mn" at 2.5100000000000002,4.55 center tc rgb "white" font "Helvetica,10" front
set object 138 rect center 3.23,4.55 size 0.6799999999999999,0.74 fc rgb "#3987e5" fs solid 1.0 border lc rgb "#eb6834" lw 2.2 front
set label 138 "Fe" at 3.23,4.55 center tc rgb "white" font "Helvetica,10" front
set object 139 rect center 3.9499999999999997,4.55 size 0.6799999999999999,0.74 fc rgb "#3987e5" fs solid 1.0 border lc rgb "#eb6834" lw 2.2 front
set label 139 "Co" at 3.9499999999999997,4.55 center tc rgb "white" font "Helvetica,10" front
set object 140 rect center 4.67,4.55 size 0.6799999999999999,0.74 fc rgb "#3987e5" fs solid 1.0 border lc rgb "white" lw 0.6 front
set label 140 "Ni" at 4.67,4.55 center tc rgb "white" font "Helvetica,10" front
set object 141 rect center 5.39,4.55 size 0.6799999999999999,0.74 fc rgb "#3987e5" fs solid 1.0 border lc rgb "white" lw 0.6 front
set label 141 "Cu" at 5.39,4.55 center tc rgb "white" font "Helvetica,10" front
set object 142 rect center 6.109999999999999,4.55 size 0.6799999999999999,0.74 fc rgb "#3987e5" fs solid 1.0 border lc rgb "white" lw 0.6 front
set label 142 "Zn" at 6.109999999999999,4.55 center tc rgb "white" font "Helvetica,10" front
set object 143 rect center 0.35,3.7699999999999996 size 0.6799999999999999,0.74 fc rgb "#3987e5" fs solid 1.0 border lc rgb "white" lw 0.6 front
set label 143 "Zr" at 0.35,3.7699999999999996 center tc rgb "white" font "Helvetica,10" front
set object 144 rect center 1.0699999999999998,3.7699999999999996 size 0.6799999999999999,0.74 fc rgb "#3987e5" fs solid 1.0 border lc rgb "white" lw 0.6 front
set label 144 "Nb" at 1.0699999999999998,3.7699999999999996 center tc rgb "white" font "Helvetica,10" front
set object 145 rect center 1.79,3.7699999999999996 size 0.6799999999999999,0.74 fc rgb "#3987e5" fs solid 1.0 border lc rgb "white" lw 0.6 front
set label 145 "Mo" at 1.79,3.7699999999999996 center tc rgb "white" font "Helvetica,10" front
set object 146 rect center 2.5100000000000002,3.7699999999999996 size 0.6799999999999999,0.74 fc rgb "#3987e5" fs solid 1.0 border lc rgb "white" lw 0.6 front
set label 146 "Tc" at 2.5100000000000002,3.7699999999999996 center tc rgb "white" font "Helvetica,10" front
set object 147 rect center 3.23,3.7699999999999996 size 0.6799999999999999,0.74 fc rgb "#3987e5" fs solid 1.0 border lc rgb "white" lw 0.6 front
set label 147 "Ru" at 3.23,3.7699999999999996 center tc rgb "white" font "Helvetica,10" front
set object 148 rect center 3.9499999999999997,3.7699999999999996 size 0.6799999999999999,0.74 fc rgb "#3987e5" fs solid 1.0 border lc rgb "white" lw 0.6 front
set label 148 "Rh" at 3.9499999999999997,3.7699999999999996 center tc rgb "white" font "Helvetica,10" front
set object 149 rect center 4.67,3.7699999999999996 size 0.6799999999999999,0.74 fc rgb "#3987e5" fs solid 1.0 border lc rgb "white" lw 0.6 front
set label 149 "Pd" at 4.67,3.7699999999999996 center tc rgb "white" font "Helvetica,10" front
set object 150 rect center 5.39,3.7699999999999996 size 0.6799999999999999,0.74 fc rgb "#3987e5" fs solid 1.0 border lc rgb "white" lw 0.6 front
set label 150 "Ag" at 5.39,3.7699999999999996 center tc rgb "white" font "Helvetica,10" front
set object 151 rect center 6.109999999999999,3.7699999999999996 size 0.6799999999999999,0.74 fc rgb "#3987e5" fs solid 1.0 border lc rgb "white" lw 0.6 front
set label 151 "Cd" at 6.109999999999999,3.7699999999999996 center tc rgb "white" font "Helvetica,10" front
set object 152 rect center 0.35,2.9899999999999998 size 0.6799999999999999,0.74 fc rgb "#3987e5" fs solid 1.0 border lc rgb "white" lw 0.6 front
set label 152 "Hf" at 0.35,2.9899999999999998 center tc rgb "white" font "Helvetica,10" front
set object 153 rect center 1.0699999999999998,2.9899999999999998 size 0.6799999999999999,0.74 fc rgb "#3987e5" fs solid 1.0 border lc rgb "white" lw 0.6 front
set label 153 "Ta" at 1.0699999999999998,2.9899999999999998 center tc rgb "white" font "Helvetica,10" front
set object 154 rect center 1.79,2.9899999999999998 size 0.6799999999999999,0.74 fc rgb "#3987e5" fs solid 1.0 border lc rgb "white" lw 0.6 front
set label 154 "W" at 1.79,2.9899999999999998 center tc rgb "white" font "Helvetica,10" front
set object 155 rect center 2.5100000000000002,2.9899999999999998 size 0.6799999999999999,0.74 fc rgb "#3987e5" fs solid 1.0 border lc rgb "white" lw 0.6 front
set label 155 "Re" at 2.5100000000000002,2.9899999999999998 center tc rgb "white" font "Helvetica,10" front
set object 156 rect center 3.23,2.9899999999999998 size 0.6799999999999999,0.74 fc rgb "#3987e5" fs solid 1.0 border lc rgb "white" lw 0.6 front
set label 156 "Os" at 3.23,2.9899999999999998 center tc rgb "white" font "Helvetica,10" front
set object 157 rect center 3.9499999999999997,2.9899999999999998 size 0.6799999999999999,0.74 fc rgb "#3987e5" fs solid 1.0 border lc rgb "white" lw 0.6 front
set label 157 "Ir" at 3.9499999999999997,2.9899999999999998 center tc rgb "white" font "Helvetica,10" front
set object 158 rect center 4.67,2.9899999999999998 size 0.6799999999999999,0.74 fc rgb "#3987e5" fs solid 1.0 border lc rgb "white" lw 0.6 front
set label 158 "Pt" at 4.67,2.9899999999999998 center tc rgb "white" font "Helvetica,10" front
set object 159 rect center 5.39,2.9899999999999998 size 0.6799999999999999,0.74 fc rgb "#3987e5" fs solid 1.0 border lc rgb "white" lw 0.6 front
set label 159 "Au" at 5.39,2.9899999999999998 center tc rgb "white" font "Helvetica,10" front
set object 160 rect center 6.109999999999999,2.9899999999999998 size 0.6799999999999999,0.74 fc rgb "#3987e5" fs solid 1.0 border lc rgb "white" lw 0.6 front
set label 160 "Hg" at 6.109999999999999,2.9899999999999998 center tc rgb "white" font "Helvetica,10" front
set object 161 rect center 8.9,5.35 size 0.6799999999999999,0.74 fc rgb "#eb6834" fs solid 1.0 border lc rgb "white" lw 0.6 front
set label 161 "Si" at 8.9,5.35 center tc rgb "white" font "Helvetica,10" front
set object 162 rect center 8.9,4.569999999999999 size 0.6799999999999999,0.74 fc rgb "#eb6834" fs solid 1.0 border lc rgb "#eb6834" lw 2.2 front
set label 162 "Ge" at 8.9,4.569999999999999 center tc rgb "white" font "Helvetica,10" front
set object 163 rect center 8.9,3.7899999999999996 size 0.6799999999999999,0.74 fc rgb "#eb6834" fs solid 1.0 border lc rgb "#eb6834" lw 2.2 front
set label 163 "Sn" at 8.9,3.7899999999999996 center tc rgb "white" font "Helvetica,10" front
set object 164 rect center 8.9,3.01 size 0.6799999999999999,0.74 fc rgb "#eb6834" fs solid 1.0 border lc rgb "white" lw 0.6 front
set label 164 "Pb" at 8.9,3.01 center tc rgb "white" font "Helvetica,10" front
set object 165 rect center 0.35,1.55 size 0.58,0.74 fc rgb "#1baf7a" fs solid 1.0 border lc rgb "white" lw 0.6 front
set label 165 "La" at 0.35,1.55 center tc rgb "white" font "Helvetica,10" front
set object 166 rect center 0.97,1.55 size 0.58,0.74 fc rgb "#1baf7a" fs solid 1.0 border lc rgb "white" lw 0.6 front
set label 166 "Ce" at 0.97,1.55 center tc rgb "white" font "Helvetica,10" front
set object 167 rect center 1.5899999999999999,1.55 size 0.58,0.74 fc rgb "#1baf7a" fs solid 1.0 border lc rgb "white" lw 0.6 front
set label 167 "Pr" at 1.5899999999999999,1.55 center tc rgb "white" font "Helvetica,10" front
set object 168 rect center 2.21,1.55 size 0.58,0.74 fc rgb "#1baf7a" fs solid 1.0 border lc rgb "#eb6834" lw 2.2 front
set label 168 "Nd" at 2.21,1.55 center tc rgb "white" font "Helvetica,10" front
set object 169 rect center 2.83,1.55 size 0.58,0.74 fc rgb "#1baf7a" fs solid 1.0 border lc rgb "white" lw 0.6 front
set label 169 "Pm" at 2.83,1.55 center tc rgb "white" font "Helvetica,10" front
set object 170 rect center 3.45,1.55 size 0.58,0.74 fc rgb "#1baf7a" fs solid 1.0 border lc rgb "white" lw 0.6 front
set label 170 "Sm" at 3.45,1.55 center tc rgb "white" font "Helvetica,10" front
set object 171 rect center 4.069999999999999,1.55 size 0.58,0.74 fc rgb "#1baf7a" fs solid 1.0 border lc rgb "white" lw 0.6 front
set label 171 "Eu" at 4.069999999999999,1.55 center tc rgb "white" font "Helvetica,10" front
set object 172 rect center 4.6899999999999995,1.55 size 0.58,0.74 fc rgb "#1baf7a" fs solid 1.0 border lc rgb "white" lw 0.6 front
set label 172 "Gd" at 4.6899999999999995,1.55 center tc rgb "white" font "Helvetica,10" front
set object 173 rect center 5.31,1.55 size 0.58,0.74 fc rgb "#1baf7a" fs solid 1.0 border lc rgb "white" lw 0.6 front
set label 173 "Tb" at 5.31,1.55 center tc rgb "white" font "Helvetica,10" front
set object 174 rect center 5.93,1.55 size 0.58,0.74 fc rgb "#1baf7a" fs solid 1.0 border lc rgb "white" lw 0.6 front
set label 174 "Dy" at 5.93,1.55 center tc rgb "white" font "Helvetica,10" front
set object 175 rect center 6.55,1.55 size 0.58,0.74 fc rgb "#1baf7a" fs solid 1.0 border lc rgb "white" lw 0.6 front
set label 175 "Ho" at 6.55,1.55 center tc rgb "white" font "Helvetica,10" front
set object 176 rect center 7.17,1.55 size 0.58,0.74 fc rgb "#1baf7a" fs solid 1.0 border lc rgb "white" lw 0.6 front
set label 176 "Er" at 7.17,1.55 center tc rgb "white" font "Helvetica,10" front
set object 177 rect center 7.789999999999999,1.55 size 0.58,0.74 fc rgb "#1baf7a" fs solid 1.0 border lc rgb "white" lw 0.6 front
set label 177 "Tm" at 7.789999999999999,1.55 center tc rgb "white" font "Helvetica,10" front
set object 178 rect center 8.41,1.55 size 0.58,0.74 fc rgb "#1baf7a" fs solid 1.0 border lc rgb "white" lw 0.6 front
set label 178 "Yb" at 8.41,1.55 center tc rgb "white" font "Helvetica,10" front
set object 179 rect center 9.03,1.55 size 0.58,0.74 fc rgb "#1baf7a" fs solid 1.0 border lc rgb "white" lw 0.6 front
set label 179 "Lu" at 9.03,1.55 center tc rgb "white" font "Helvetica,10" front
set object 180 rect center 2.21,0.55 size 0.58,0.74 fc rgb "#262626" fs solid 1.0 border lc rgb "#eb6834" lw 2.2 front
set label 180 "U" at 2.21,0.55 center tc rgb "white" font "Helvetica,10" front
set arrow 181 from 3.23,5.159999999999999 to 3.9499999999999997,5.159999999999999 head filled size 0.22,20 lc rgb "#eb6834" lw 2.2 front
set arrow 182 from 9.48,3.7899999999999996 to 9.48,4.569999999999999 head filled size 0.22,20 lc rgb "#eb6834" lw 2.2 front
set arrow 183 from 2.74,0.55 to 2.74,1.55 head filled size 0.22,20 lc rgb "#eb6834" lw 2.2 front
plot NaN notitle
unset for [i=2:183] object i; unset for [i=2:183] label i; unset for [i=2:183] arrow i; unset label 900
set title "(d) Backpropagation" left offset -2,-0.7 tc rgb INK
set object 184 circle at 5.0,9.5 size 0.36 fc rgb "#3987e5" fs solid 1.0 border lc rgb "#262626" lw 1.6 front
set arrow 185 from 5.0,9.5 to 2.9,8.2 nohead lc rgb "#8a8a8a" lw 1.2 front
set arrow 186 from 5.0,9.5 to 5.0,8.2 nohead lc rgb "#8a8a8a" lw 1.2 front
set arrow 187 from 5.0,9.5 to 7.1,8.2 nohead lc rgb "#8a8a8a" lw 1.2 front
set object 188 rect center 2.9,8.2 size 0.66,0.6 fc rgb "#cde2fb" fs solid 1.0 border lc rgb "white" lw 0.8 front
set object 189 rect center 5.0,8.2 size 0.66,0.6 fc rgb "#3987e5" fs solid 1.0 border lc rgb "#262626" lw 1.6 front
set object 190 rect center 7.1,8.2 size 0.66,0.6 fc rgb "#cde2fb" fs solid 1.0 border lc rgb "white" lw 0.8 front
set arrow 191 from 5.0,8.2 to 4.1,6.9 nohead lc rgb "#8a8a8a" lw 1.2 front
set arrow 192 from 5.0,8.2 to 5.9,6.9 nohead lc rgb "#8a8a8a" lw 1.2 front
set object 193 circle at 4.1,6.9 size 0.36 fc rgb "#cde2fb" fs solid 1.0 border lc rgb "white" lw 0.8 front
set object 194 circle at 5.9,6.9 size 0.36 fc rgb "#eb6834" fs solid 1.0 border lc rgb "#262626" lw 1.6 front
set arrow 195 from 5.65,7.2 to 5.25,7.85 head filled size 0.22,20 lc rgb "#eb6834" lw 2.2 front
set arrow 196 from 5.1,8.549999999999999 to 5.1,9.1 head filled size 0.22,20 lc rgb "#eb6834" lw 2.2 front
set object 197 rect center 0.35,4.55 size 0.6799999999999999,0.74 fc rgb "#3987e5" fs solid 1.0 border lc rgb "white" lw 0.6 front
set label 197 "Ti" at 0.35,4.55 center tc rgb "white" font "Helvetica,10" front
set object 198 rect center 1.0699999999999998,4.55 size 0.6799999999999999,0.74 fc rgb "#3987e5" fs solid 1.0 border lc rgb "white" lw 0.6 front
set label 198 "V" at 1.0699999999999998,4.55 center tc rgb "white" font "Helvetica,10" front
set object 199 rect center 1.79,4.55 size 0.6799999999999999,0.74 fc rgb "#3987e5" fs solid 1.0 border lc rgb "white" lw 0.6 front
set label 199 "Cr" at 1.79,4.55 center tc rgb "white" font "Helvetica,10" front
set object 200 rect center 2.5100000000000002,4.55 size 0.6799999999999999,0.74 fc rgb "#3987e5" fs solid 1.0 border lc rgb "white" lw 0.6 front
set label 200 "Mn" at 2.5100000000000002,4.55 center tc rgb "white" font "Helvetica,10" front
set object 201 rect center 3.23,4.55 size 0.6799999999999999,0.74 fc rgb "#3987e5" fs solid 1.0 border lc rgb "#eb6834" lw 2.2 front
set label 201 "Fe" at 3.23,4.55 center tc rgb "white" font "Helvetica,10" front
set object 202 rect center 3.9499999999999997,4.55 size 0.6799999999999999,0.74 fc rgb "#3987e5" fs solid 1.0 border lc rgb "white" lw 0.6 front
set label 202 "Co" at 3.9499999999999997,4.55 center tc rgb "white" font "Helvetica,10" front
set object 203 rect center 4.67,4.55 size 0.6799999999999999,0.74 fc rgb "#3987e5" fs solid 1.0 border lc rgb "white" lw 0.6 front
set label 203 "Ni" at 4.67,4.55 center tc rgb "white" font "Helvetica,10" front
set object 204 rect center 5.39,4.55 size 0.6799999999999999,0.74 fc rgb "#3987e5" fs solid 1.0 border lc rgb "white" lw 0.6 front
set label 204 "Cu" at 5.39,4.55 center tc rgb "white" font "Helvetica,10" front
set object 205 rect center 6.109999999999999,4.55 size 0.6799999999999999,0.74 fc rgb "#3987e5" fs solid 1.0 border lc rgb "white" lw 0.6 front
set label 205 "Zn" at 6.109999999999999,4.55 center tc rgb "white" font "Helvetica,10" front
set object 206 rect center 0.35,3.7699999999999996 size 0.6799999999999999,0.74 fc rgb "#3987e5" fs solid 1.0 border lc rgb "white" lw 0.6 front
set label 206 "Zr" at 0.35,3.7699999999999996 center tc rgb "white" font "Helvetica,10" front
set object 207 rect center 1.0699999999999998,3.7699999999999996 size 0.6799999999999999,0.74 fc rgb "#3987e5" fs solid 1.0 border lc rgb "white" lw 0.6 front
set label 207 "Nb" at 1.0699999999999998,3.7699999999999996 center tc rgb "white" font "Helvetica,10" front
set object 208 rect center 1.79,3.7699999999999996 size 0.6799999999999999,0.74 fc rgb "#3987e5" fs solid 1.0 border lc rgb "white" lw 0.6 front
set label 208 "Mo" at 1.79,3.7699999999999996 center tc rgb "white" font "Helvetica,10" front
set object 209 rect center 2.5100000000000002,3.7699999999999996 size 0.6799999999999999,0.74 fc rgb "#3987e5" fs solid 1.0 border lc rgb "white" lw 0.6 front
set label 209 "Tc" at 2.5100000000000002,3.7699999999999996 center tc rgb "white" font "Helvetica,10" front
set object 210 rect center 3.23,3.7699999999999996 size 0.6799999999999999,0.74 fc rgb "#3987e5" fs solid 1.0 border lc rgb "white" lw 0.6 front
set label 210 "Ru" at 3.23,3.7699999999999996 center tc rgb "white" font "Helvetica,10" front
set object 211 rect center 3.9499999999999997,3.7699999999999996 size 0.6799999999999999,0.74 fc rgb "#3987e5" fs solid 1.0 border lc rgb "white" lw 0.6 front
set label 211 "Rh" at 3.9499999999999997,3.7699999999999996 center tc rgb "white" font "Helvetica,10" front
set object 212 rect center 4.67,3.7699999999999996 size 0.6799999999999999,0.74 fc rgb "#3987e5" fs solid 1.0 border lc rgb "white" lw 0.6 front
set label 212 "Pd" at 4.67,3.7699999999999996 center tc rgb "white" font "Helvetica,10" front
set object 213 rect center 5.39,3.7699999999999996 size 0.6799999999999999,0.74 fc rgb "#3987e5" fs solid 1.0 border lc rgb "white" lw 0.6 front
set label 213 "Ag" at 5.39,3.7699999999999996 center tc rgb "white" font "Helvetica,10" front
set object 214 rect center 6.109999999999999,3.7699999999999996 size 0.6799999999999999,0.74 fc rgb "#3987e5" fs solid 1.0 border lc rgb "white" lw 0.6 front
set label 214 "Cd" at 6.109999999999999,3.7699999999999996 center tc rgb "white" font "Helvetica,10" front
set object 215 rect center 0.35,2.9899999999999998 size 0.6799999999999999,0.74 fc rgb "#3987e5" fs solid 1.0 border lc rgb "white" lw 0.6 front
set label 215 "Hf" at 0.35,2.9899999999999998 center tc rgb "white" font "Helvetica,10" front
set object 216 rect center 1.0699999999999998,2.9899999999999998 size 0.6799999999999999,0.74 fc rgb "#3987e5" fs solid 1.0 border lc rgb "white" lw 0.6 front
set label 216 "Ta" at 1.0699999999999998,2.9899999999999998 center tc rgb "white" font "Helvetica,10" front
set object 217 rect center 1.79,2.9899999999999998 size 0.6799999999999999,0.74 fc rgb "#3987e5" fs solid 1.0 border lc rgb "white" lw 0.6 front
set label 217 "W" at 1.79,2.9899999999999998 center tc rgb "white" font "Helvetica,10" front
set object 218 rect center 2.5100000000000002,2.9899999999999998 size 0.6799999999999999,0.74 fc rgb "#3987e5" fs solid 1.0 border lc rgb "white" lw 0.6 front
set label 218 "Re" at 2.5100000000000002,2.9899999999999998 center tc rgb "white" font "Helvetica,10" front
set object 219 rect center 3.23,2.9899999999999998 size 0.6799999999999999,0.74 fc rgb "#3987e5" fs solid 1.0 border lc rgb "white" lw 0.6 front
set label 219 "Os" at 3.23,2.9899999999999998 center tc rgb "white" font "Helvetica,10" front
set object 220 rect center 3.9499999999999997,2.9899999999999998 size 0.6799999999999999,0.74 fc rgb "#3987e5" fs solid 1.0 border lc rgb "white" lw 0.6 front
set label 220 "Ir" at 3.9499999999999997,2.9899999999999998 center tc rgb "white" font "Helvetica,10" front
set object 221 rect center 4.67,2.9899999999999998 size 0.6799999999999999,0.74 fc rgb "#3987e5" fs solid 1.0 border lc rgb "white" lw 0.6 front
set label 221 "Pt" at 4.67,2.9899999999999998 center tc rgb "white" font "Helvetica,10" front
set object 222 rect center 5.39,2.9899999999999998 size 0.6799999999999999,0.74 fc rgb "#3987e5" fs solid 1.0 border lc rgb "white" lw 0.6 front
set label 222 "Au" at 5.39,2.9899999999999998 center tc rgb "white" font "Helvetica,10" front
set object 223 rect center 6.109999999999999,2.9899999999999998 size 0.6799999999999999,0.74 fc rgb "#3987e5" fs solid 1.0 border lc rgb "white" lw 0.6 front
set label 223 "Hg" at 6.109999999999999,2.9899999999999998 center tc rgb "white" font "Helvetica,10" front
set object 224 rect center 8.9,5.35 size 0.6799999999999999,0.74 fc rgb "#eb6834" fs solid 1.0 border lc rgb "white" lw 0.6 front
set label 224 "Si" at 8.9,5.35 center tc rgb "white" font "Helvetica,10" front
set object 225 rect center 8.9,4.569999999999999 size 0.6799999999999999,0.74 fc rgb "#eb6834" fs solid 1.0 border lc rgb "white" lw 0.6 front
set label 225 "Ge" at 8.9,4.569999999999999 center tc rgb "white" font "Helvetica,10" front
set object 226 rect center 8.9,3.7899999999999996 size 0.6799999999999999,0.74 fc rgb "#eb6834" fs solid 1.0 border lc rgb "#eb6834" lw 2.2 front
set label 226 "Sn" at 8.9,3.7899999999999996 center tc rgb "white" font "Helvetica,10" front
set object 227 rect center 8.9,3.01 size 0.6799999999999999,0.74 fc rgb "#eb6834" fs solid 1.0 border lc rgb "white" lw 0.6 front
set label 227 "Pb" at 8.9,3.01 center tc rgb "white" font "Helvetica,10" front
set object 228 rect center 0.35,1.55 size 0.58,0.74 fc rgb "#1baf7a" fs solid 1.0 border lc rgb "white" lw 0.6 front
set label 228 "La" at 0.35,1.55 center tc rgb "white" font "Helvetica,10" front
set object 229 rect center 0.97,1.55 size 0.58,0.74 fc rgb "#1baf7a" fs solid 1.0 border lc rgb "white" lw 0.6 front
set label 229 "Ce" at 0.97,1.55 center tc rgb "white" font "Helvetica,10" front
set object 230 rect center 1.5899999999999999,1.55 size 0.58,0.74 fc rgb "#1baf7a" fs solid 1.0 border lc rgb "white" lw 0.6 front
set label 230 "Pr" at 1.5899999999999999,1.55 center tc rgb "white" font "Helvetica,10" front
set object 231 rect center 2.21,1.55 size 0.58,0.74 fc rgb "#1baf7a" fs solid 1.0 border lc rgb "white" lw 0.6 front
set label 231 "Nd" at 2.21,1.55 center tc rgb "white" font "Helvetica,10" front
set object 232 rect center 2.83,1.55 size 0.58,0.74 fc rgb "#1baf7a" fs solid 1.0 border lc rgb "white" lw 0.6 front
set label 232 "Pm" at 2.83,1.55 center tc rgb "white" font "Helvetica,10" front
set object 233 rect center 3.45,1.55 size 0.58,0.74 fc rgb "#1baf7a" fs solid 1.0 border lc rgb "white" lw 0.6 front
set label 233 "Sm" at 3.45,1.55 center tc rgb "white" font "Helvetica,10" front
set object 234 rect center 4.069999999999999,1.55 size 0.58,0.74 fc rgb "#1baf7a" fs solid 1.0 border lc rgb "white" lw 0.6 front
set label 234 "Eu" at 4.069999999999999,1.55 center tc rgb "white" font "Helvetica,10" front
set object 235 rect center 4.6899999999999995,1.55 size 0.58,0.74 fc rgb "#1baf7a" fs solid 1.0 border lc rgb "white" lw 0.6 front
set label 235 "Gd" at 4.6899999999999995,1.55 center tc rgb "white" font "Helvetica,10" front
set object 236 rect center 5.31,1.55 size 0.58,0.74 fc rgb "#1baf7a" fs solid 1.0 border lc rgb "white" lw 0.6 front
set label 236 "Tb" at 5.31,1.55 center tc rgb "white" font "Helvetica,10" front
set object 237 rect center 5.93,1.55 size 0.58,0.74 fc rgb "#1baf7a" fs solid 1.0 border lc rgb "white" lw 0.6 front
set label 237 "Dy" at 5.93,1.55 center tc rgb "white" font "Helvetica,10" front
set object 238 rect center 6.55,1.55 size 0.58,0.74 fc rgb "#1baf7a" fs solid 1.0 border lc rgb "white" lw 0.6 front
set label 238 "Ho" at 6.55,1.55 center tc rgb "white" font "Helvetica,10" front
set object 239 rect center 7.17,1.55 size 0.58,0.74 fc rgb "#1baf7a" fs solid 1.0 border lc rgb "white" lw 0.6 front
set label 239 "Er" at 7.17,1.55 center tc rgb "white" font "Helvetica,10" front
set object 240 rect center 7.789999999999999,1.55 size 0.58,0.74 fc rgb "#1baf7a" fs solid 1.0 border lc rgb "white" lw 0.6 front
set label 240 "Tm" at 7.789999999999999,1.55 center tc rgb "white" font "Helvetica,10" front
set object 241 rect center 8.41,1.55 size 0.58,0.74 fc rgb "#1baf7a" fs solid 1.0 border lc rgb "white" lw 0.6 front
set label 241 "Yb" at 8.41,1.55 center tc rgb "white" font "Helvetica,10" front
set object 242 rect center 9.03,1.55 size 0.58,0.74 fc rgb "#1baf7a" fs solid 1.0 border lc rgb "white" lw 0.6 front
set label 242 "Lu" at 9.03,1.55 center tc rgb "white" font "Helvetica,10" front
set object 243 rect center 2.21,0.55 size 0.58,0.74 fc rgb "#262626" fs solid 1.0 border lc rgb "#eb6834" lw 2.2 front
set label 243 "U" at 2.21,0.55 center tc rgb "white" font "Helvetica,10" front
plot NaN notitle
unset for [i=2:243] object i; unset for [i=2:243] label i; unset for [i=2:243] arrow i; unset label 900
unset multiplot
