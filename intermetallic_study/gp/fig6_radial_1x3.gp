load "style.gp"; load "data/fig6_bbox_1x3.gp"
eval DOUBLE(6, 3.4)
set output "out/Fig6_1x3.pdf"
set multiplot layout 1,3 margins 0.005,0.995,0.16,0.985 spacing 0.01,0.0
unset border; unset tics; unset grid; set size ratio -1
# pad the ranges to the panel aspect ratio so each tree is centred in its panel (2 x 2 layout: panel 0.4925 x 0.385 of the canvas)
A = (0.33 * 6) / (0.825 * 3.4); CX = 0.5*(XMIN+XMAX); CY = 0.5*(YMIN+YMAX); W = XMAX-XMIN; HH = YMAX-YMIN
W2 = (W/HH < A ? HH*A : W); H2 = (W/HH < A ? HH : W/A)
set xrange [CX-W2/2:CX+W2/2]; set yrange [CY-H2/2:CY+H2/2]
set palette defined (0 "#c9513f", 0.25 "#f0a988", 0.5 "#f7f7f7", 0.75 "#9ec8e2", 1 "#4a90c4")   # softened RdBu
set colorbox horizontal user origin graph 0.18, graph -0.06 size graph 0.64, graph 0.032 border
set cbtics out scale 0.5 offset 0,-0.1
RING_R = ROOTR*0.8   # dashed rim of the starting node (x-axis units)
set object 99 circle at ROOTX,ROOTY size RING_R fc rgb "#00000000" fs empty border lc rgb INK lw 2.5 dt 2 front
SCALE = 2.8                      # point size per layout unit of node radius (6 in figure, 2 x 2 panels)
len(dx,dy) = sqrt(dx*dx + dy*dy)
sh(d, L, rp, rc) = (L > rp + rc + 0.05 ? d * (L - rp - rc) / L : d * 0.1)   # shortened edge vector
st(x, d, L, rp, rc) = (L > rp + rc + 0.05 ? x + d * rp / L : x + d * 0.45)   # edge start on the parent rim
panel(col, letter, cbl, lo, hi, cbt, logcb) = sprintf('set label 1 "(%s)" at graph 0.0, graph 1.0 left font FONTB tc rgb INK front; set cblabel "%s" tc rgb INK offset 0,0.6; set cbrange [%s:%s]; set cbtics %s; %s; \
  plot "data/fig6_edges_1x3.dat" u (st($1,$3,len($3,$4),$5,$6)):(st($2,$4,len($3,$4),$5,$6)):(sh($3,len($3,$4),$5,$6)):(sh($4,len($3,$4),$5,$6)) w vectors head filled size 0.16,22 lc rgb "#808080" lw 1.2, \
  "data/fig6_nodes_1x3.dat" u ($8==1?NaN:$1):2:($15*SCALE+0.15) w p pt 7 ps variable lc rgb INK, "" u 1:2:($15*SCALE):%d w p pt 7 ps variable lc palette, \
  "" u 10:11:(($7>0 && $7<=15) ? sprintf("%%d",$7) : "") w labels font FONTB tc rgb INK, \
  NaN notitle', letter, cbl, lo, hi, cbt, logcb, col)
eval panel(3, "a", "{/:Italic r}", "0.01", "1.3", "(0.01, 0.1, 1)", "set logscale cb; set format cb \"%g\"")
eval panel(4, "b", "{/:Italic r_S}", "0.3", "2.8", "0.5", "unset logscale cb; set format cb \"%g\"")
eval panel(5, "c", "{/:Italic r}_{DOS}", "0.005", "0.5", "(0.01, 0.1)", "set logscale cb; set format cb \"%g\"")
unset multiplot
