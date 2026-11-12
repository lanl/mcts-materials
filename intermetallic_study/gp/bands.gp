# Band structure + total DOS for three compounds side by side: per compound a square
# band panel and a narrow DOS panel (as in the supplied figure); shared energy axis;
# 6 in wide, 10 pt text. Band lines: raster images from the supplied PDFs (resampled,
# smoothed) on calibrated axes (export_bands.py); DOS curves: extracted vector data.
# usage: gnuplot -e "SET='RE'; OUT='out/Fig_bands_RE.pdf'; N1=...; F1=...; ..." bands.gp
load "style.gp"; load sprintf("data/bands_%s.gp", SET)
LM = 0.56; SQ = 1.33; GAP = 0.05; DW = 0.36; SEP = 0.13; RM = 0.04   # inches
TT = 0.26; BB = 0.42                                                 # title space above, labels below
W = LM + 3 * (SQ + GAP + DW) + 2 * SEP + RM; HH = TT + SQ + BB
set term pdfcairo size W*1in, HH*1in font FONT lw 1 rounded
set output OUT
set multiplot
KL = "Γ M K Γ A L H A"
set tics nomirror out scale 0.5 tc rgb INK
set border 15 lc rgb INK lw 0.8
top = 1.0 - TT / HH; bot = BB / HH
set tmargin at screen top; set bmargin at screen bot
do for [c=1:3] {
  x0 = LM + (c - 1) * (SQ + GAP + DW + SEP)
  K = value(sprintf("K%d", c))
  # ---- band panel (square)
  set lmargin at screen x0 / W; set rmargin at screen (x0 + SQ) / W
  set xrange [0:1]; set yrange [-2:1.5]
  if (c == 1) { set ytics -2, 0.5, 1.5 format "%.1f"; set ylabel "E − E_F (eV)" tc rgb INK offset 1.0, 0 } else { set ytics -2, 0.5, 1.5 format ""; unset ylabel }
  set xtics (); do for [i=1:8] { set xtics add (word(KL, i) real(word(K, i))) }
  unset arrow; do for [i=2:7] { tag = i; set arrow tag from first real(word(K, i)), graph 0 to first real(word(K, i)), graph 1 nohead lc rgb "#c8c8c8" lw 0.6 back }
  set arrow 20 from graph 0, first 0 to graph 1, first 0 nohead lc rgb MUTED lw 0.8 dt 2 front
  unset label
  set label 1 sprintf("(%s)", word("a b c", c)) at screen (c == 1 ? 0.01 : (x0 - 0.1) / W), screen 1.0 - 0.45 * TT / HH left font FONTB tc rgb INK
  set label 2 value(sprintf("N%d", c)) at screen (x0 + SQ / 2) / W, screen 1.0 - 0.5 * TT / HH center tc rgb INK
  img = value(sprintf("IMG%d", c)); ix = value(sprintf("IX%d", c)); iw = value(sprintf("IW%d", c)); iy = value(sprintf("IY%d", c)); ih = value(sprintf("IH%d", c))
  pw = value(sprintf("PXW%d", c)); ph = value(sprintf("PXH%d", c))
  plot img binary filetype=png dx=iw/pw dy=ih/ph origin=(ix, iy) with rgbimage notitle
  # ---- DOS panel
  unset label; unset arrow; unset ylabel
  set lmargin at screen (x0 + SQ + GAP) / W; set rmargin at screen (x0 + SQ + GAP + DW) / W
  dmax = value(sprintf("DOSMAX%d", c)); set xrange [0:dmax * 1.12]; st = (dmax > 2 ? 2 : 1); set xtics st, st format "%g"
  set ytics format ""
  set xlabel "DOS" tc rgb INK offset 0, 0.5
  set arrow 20 from graph 0, first 0 to graph 1, first 0 nohead lc rgb MUTED lw 0.8 dt 2 front
  f = sprintf("data/bands_%s_dos.dat", value(sprintf("F%d", c)))
  plot sprintf("< awk '!/^#/{if(!n){print 0, $1}; n=1; print $2, $1; e=$1} END{print 0, e}' %s", f) u 1:2 w filledcurves closed fc rgb "#d9d9d9" fs solid 1.0 noborder notitle, \
       f u 2:1 w l lc rgb INK lw 1.2 notitle
  unset xlabel
}
unset multiplot
