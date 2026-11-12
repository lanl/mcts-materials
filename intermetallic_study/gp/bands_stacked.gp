# Band structure + total DOS for three compounds, stacked one per row, with a square
# band panel and a narrow DOS panel (as in the supplied figure); 10 pt text.
# Band lines: raster images from the supplied PDFs (resampled 4x) placed on calibrated
# axes (export_bands.py); DOS curves: the extracted vector data.
# usage: gnuplot -e "SET='RE'; OUT='out/Fig_bands_RE.pdf'; N1=...; F1=...; ..." bands.gp
load "style.gp"; load sprintf("data/bands_%s.gp", SET)
LM = 0.62; SQ = 1.47; GAP = 0.12; DW = 0.62; RM = 0.1          # inches
TT = 0.22; BL = 0.24                                             # title space above, tick labels below each row
XB = 0.2                                                         # extra room under the bottom row for the DOS label
W = LM + SQ + GAP + DW + RM; HH = 3 * (TT + SQ + BL) + XB
set term pdfcairo size W*1in, HH*1in font FONT lw 1 rounded
set output OUT
set multiplot
KL = "Γ M K Γ A L H A"
set tics nomirror out scale 0.5 tc rgb INK
set border 15 lc rgb INK lw 0.8
do for [r=1:3] {
  top = 1.0 - ((r - 1) * (TT + SQ + BL) + TT) / HH; bot = top - SQ / HH
  K = value(sprintf("K%d", r))
  # ---- band panel (square)
  set lmargin at screen LM / W; set rmargin at screen (LM + SQ) / W; set tmargin at screen top; set bmargin at screen bot
  set xrange [0:1]; set yrange [-2:1.5]; set ytics -2, 0.5, 1.5 format "%.1f"
  set ylabel "E − E_F (eV)" tc rgb INK offset 1.0, 0
  set xtics (); do for [i=1:8] { set xtics add (word(KL, i) real(word(K, i))) }
  unset arrow; do for [i=2:7] { tag = i; set arrow tag from first real(word(K, i)), graph 0 to first real(word(K, i)), graph 1 nohead lc rgb "#c8c8c8" lw 0.6 back }
  set arrow 20 from graph 0, first 0 to graph 1, first 0 nohead lc rgb MUTED lw 0.8 dt 2 front
  unset label
  set label 1 sprintf("(%s)", word("a b c", r)) at screen 0.01, screen top + 0.55 * TT / HH left font FONTB tc rgb INK
  set label 2 value(sprintf("N%d", r)) at screen (LM + SQ / 2) / W, screen top + 0.45 * TT / HH center tc rgb INK
  img = value(sprintf("IMG%d", r)); ix = value(sprintf("IX%d", r)); iw = value(sprintf("IW%d", r)); iy = value(sprintf("IY%d", r)); ih = value(sprintf("IH%d", r))
  pw = value(sprintf("PXW%d", r)); ph = value(sprintf("PXH%d", r))
  plot img binary filetype=png dx=iw/pw dy=ih/ph origin=(ix, iy) with rgbimage notitle
  # ---- DOS panel
  unset label; unset arrow; unset ylabel
  set lmargin at screen (LM + SQ + GAP) / W; set rmargin at screen (LM + SQ + GAP + DW) / W
  dmax = value(sprintf("DOSMAX%d", r)); set xrange [0:dmax * 1.12]; set xtics 0, (dmax > 2 ? 2 : 1) format "%g"
  set ytics format ""
  if (r == 3) { set xlabel "DOS" tc rgb INK offset 0, 0.5 } else { unset xlabel }
  set arrow 20 from graph 0, first 0 to graph 1, first 0 nohead lc rgb MUTED lw 0.8 dt 2 front
  f = sprintf("data/bands_%s_dos.dat", value(sprintf("F%d", r)))
  plot sprintf("< awk '!/^#/{if(!n){print 0, $1}; n=1; print $2, $1; e=$1} END{print 0, e}' %s", f) u 1:2 w filledcurves closed fc rgb "#d9d9d9" fs solid 1.0 noborder notitle, \
       f u 2:1 w l lc rgb INK lw 1.2 notitle
  unset xlabel
}
unset multiplot
