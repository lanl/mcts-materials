# Shared gnuplot style for the rdos-v2 manuscript figures (gnuplot 6, cairo terminals).
# Matches the original (matplotlib) Overleaf figures: DejaVu Sans 10 pt, black box axes,
# outward tics, no grid, matplotlib marker colours, viridis / RdBu / bwr palettes.
# Journal sizing: single-column figures 3in x 3in, double-column at most 6in x 6in.
FONT  = "DejaVu Sans,10"
FONTB = "DejaVu Sans Bold,10"
SINGLE = "set term pdfcairo size 3in,3in font FONT lw 1 rounded"
DOUBLE(w,h) = sprintf("set term pdfcairo size %gin,%gin font FONT lw 1 rounded", w, h)
INK = "black"; MUTED = "#808080"; GRID = "#e6e6e6"
# marker colours of the original figures
GRAY = "#c8c8c8"; SKY = "#5abce8"; ORANGE = "#e69f00"; RED = "#c8282c"; STEEL = "#4682b4"
# viridis quartile colours (0-25, 25-50, 50-75, 75-100 %)
V1 = "#440154"; V2 = "#31688e"; V3 = "#35b779"; V4 = "#fde725"
VIRIDIS = 'set palette defined (0 "#440154", 0.125 "#482475", 0.25 "#414487", 0.375 "#355f8d", 0.5 "#2a788e", 0.625 "#21918c", 0.75 "#22a884", 0.875 "#44bf70", 0.94 "#7ad151", 1 "#fde725")'
RDBU = 'set palette defined (0 "#67001f", 0.1 "#b2182b", 0.2 "#d6604d", 0.3 "#f4a582", 0.4 "#fddbc7", 0.5 "#f7f7f7", 0.6 "#d1e5f0", 0.7 "#92c5de", 0.8 "#4393c3", 0.9 "#2166ac", 1 "#053061")'
RWB = 'set palette defined (0 "#ff0000", 0.5 "#ffffff", 1 "#0000ff")'   # bwr reversed: low = red, high = blue
# legacy palette of the first gnuplot drafts (still used by the DOS / schematic figures)
C1 = "#2a78d6"; C2 = "#eb6834"; C3 = "#1baf7a"; C4 = "#eda100"; C5 = "#e87ba4"; C6 = "#a8326e"; C7 = "#2b8cbe"
B1 = "#cde2fb"; B2 = "#9ec5f4"; B3 = "#6da7ec"; B4 = "#3987e5"; B5 = "#256abf"; B6 = "#184f95"; B7 = "#0d366b"
set encoding utf8
set border 31 lc rgb INK lw 1
set tics nomirror out scale 0.6 tc rgb INK
unset grid
set key noautotitle samplen 1.5 spacing 1.1 tc rgb INK font FONT
set style line 1 lc rgb C1 lw 2
set style line 2 lc rgb C2 lw 2
set style line 3 lc rgb C3 lw 2
set style line 4 lc rgb C4 lw 2
set style line 5 lc rgb C5 lw 2
set style line 10 lc rgb INK lw 1.6          # total DOS
set style line 11 lc rgb C1 lw 1.2           # f-element projection
set style line 12 lc rgb C3 lw 1.2           # transition metal
set style line 13 lc rgb C2 lw 1.2           # group IV
set style line 14 lc rgb MUTED lw 1 dt 2     # 0.5 eV background
set style line 15 lc rgb MUTED lw 1 dt 3     # E_F / reference lines
set style fill transparent solid 0.35 noborder
