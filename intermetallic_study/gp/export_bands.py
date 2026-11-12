#!/usr/bin/env python3
"""Extract the band-structure figures supplied as PDFs (matplotlib output:
band lines rasterized, DOS curves and axes as vector paths) into data that
gnuplot can re-plot at journal size:
  data/bands_<compound>.png          band raster, cropped to the axes
  data/bands_<compound>_dos.dat      E (eV), total DOS (as plotted in the PDF)
  data/bands_<set>.gp                axis calibration: k positions of the
                                      high-symmetry points, image placement
Energy axis: the tick labels 1.5 ... -2.0 eV sit at fixed y positions;
DOS axis: tick labels under each DOS panel. Usage: python3 export_bands.py
"""
import re
from pathlib import Path
import fitz

G = Path(__file__).resolve().parent; D = G / "data"
UP = 4
SETS = {"RE": (str(G.parent / "data/three_RE_candidates_bands_DOS.pdf"), ["DyFe6Sn6", "TmFe6Sn6", "PmMn6Sn6"]),
        "U": (str(G.parent / "data/three_U_candidates_bands_DOS.pdf"), ["UTc6Ge6", "UTc6Sn6", "UTi6Sn6"])}


def num(s):
    s = s.replace("−", "-").strip()
    return float(s) if re.fullmatch(r"-?\d+(\.\d+)?", s) else None


for tag, (pdf, names) in SETS.items():
    pg = fitz.open(pdf)[0]
    dr = pg.get_drawings()
    spans = [s for b in pg.get_text("dict")["blocks"] for l in b.get("lines", []) for s in l["spans"] if s["text"].strip()]
    imgs = sorted(pg.get_image_info(xrefs=True), key=lambda i: i["bbox"][0])
    panels = sorted([d["rect"] for d in dr if d["type"] == "f" and d["fill"] == (1.0, 1.0, 1.0) and d["rect"].width < 500], key=lambda r: r.x0)
    band_ax = [r for r in panels if any(abs(i["bbox"][0] - r.x0) < 2 for i in imgs)]
    dos_ax = [r for r in panels if r not in band_ax]
    assert len(band_ax) == 3 and len(dos_ax) == 3, (len(band_ax), len(dos_ax))
    # energy calibration from the left tick labels of the first band panel (labels lose their minus sign; the order fixes it)
    ylab = sorted([s for s in spans if s["bbox"][2] < band_ax[0].x0 and num(s["text"]) is not None], key=lambda s: s["bbox"][1])
    yc = [(s["bbox"][1] + s["bbox"][3]) / 2 for s in ylab]
    E_top, E_bot = 1.5, -2.0
    assert len(yc) == 8, len(yc)
    y_top, y_bot = yc[0], yc[-1]
    E = lambda y: E_top + (y - y_top) * (E_bot - E_top) / (y_bot - y_top)
    lines = [f"# calibration for {pdf}"]
    for k, (name, ax, dax, im) in enumerate(zip(names, band_ax, dos_ax, imgs), 1):
        # band raster
        pix = fitz.Pixmap(pg.parent, im["xref"])
        if pix.n > 3 or pix.alpha:
            pix = fitz.Pixmap(fitz.csRGB, pix)
        pix.save(str(D / f"bands_{name}_raw.png"))
        # the source raster is ~100 dpi; resample 4x with Lanczos so the viewer does not enlarge single pixels
        from PIL import Image
        im0 = Image.open(D / f"bands_{name}_raw.png").convert("L")
        from PIL import ImageFilter
        import numpy as np
        up = im0.resize((im0.width * UP, im0.height * UP), Image.LANCZOS).filter(ImageFilter.GaussianBlur(UP * 0.4))
        a = np.asarray(up, float) / 255.0                       # blur removes the pixel steps; a contrast curve restores crisp, dark lines
        a = 1.0 / (1.0 + np.exp(-(a - 0.5) / 0.1))
        a = (a - a.min()) / (a.max() - a.min())
        up = Image.fromarray((a * 255).astype(np.uint8)).convert("RGB")
        up.save(D / f"bands_{name}.png")
        PXW_, PXH_ = up.size
        x0, y0, x1, y1 = im["bbox"]
        # k positions: gray vertical guide lines inside this panel plus the panel edges
        guides = sorted({round(d["rect"].x0, 2) for d in dr if d["type"] == "s" and d.get("width") and abs(d["width"] - 0.6) < 0.05
                         and ax.x0 < d["rect"].x0 < ax.x1 and abs(d["rect"].width) < 0.1})
        kpos = [ax.x0] + guides + [ax.x1]
        assert len(kpos) == 8, (name, kpos)
        kn = [(x - ax.x0) / (ax.x1 - ax.x0) for x in kpos]
        lines.append(f"K{k} = '{' '.join(f'{v:.5f}' for v in kn)}'")
        lines.append(f"IMG{k} = 'data/bands_{name}.png'; IX{k} = {(x0 - ax.x0) / (ax.x1 - ax.x0):.5f}; IW{k} = {(x1 - x0) / (ax.x1 - ax.x0):.5f}; "
                     f"IY{k} = {E(y1):.5f}; IH{k} = {E(y0) - E(y1):.5f}; PXW{k} = {PXW_}; PXH{k} = {PXH_}")
        # DOS curve and its axis calibration
        curve = max((d for d in dr if d["type"] == "s" and d.get("width") and abs(d["width"] - 1.0) < 0.05
                     and dax.x0 - 1 <= d["rect"].x0 and d["rect"].x1 <= dax.x1 + 1), key=lambda d: len(d["items"]))
        ticks = sorted({round(d["rect"].x0, 2) for d in dr if d["type"] == "fs" and dax.x0 - 0.5 <= d["rect"].x0 <= dax.x1 + 0.5
                        and abs(d["rect"].width) < 0.1 and d["rect"].height > 2})
        tlab = sorted([s for s in spans if dax.x0 - 6 <= (s["bbox"][0] + s["bbox"][2]) / 2 <= dax.x1 + 6
                       and s["bbox"][1] > dax.y1 - 5 and num(s["text"]) is not None], key=lambda s: s["bbox"][0])
        assert len(ticks) >= 2 and len(tlab) == len(ticks), (name, ticks, [s["text"] for s in tlab])
        (xa, va), (xb, vb) = (ticks[0], num(tlab[0]["text"])), (ticks[-1], num(tlab[-1]["text"]))
        dos = lambda x: va + (x - xa) * (vb - va) / (xb - xa)
        pts = []
        for it in curve["items"]:
            if it[0] == "l":
                for p in (it[1], it[2]):
                    pts.append((E(p.y), dos(p.x)))
        pts = sorted(set((round(e, 5), round(v, 5)) for e, v in pts))
        with open(D / f"bands_{name}_dos.dat", "w") as fh:
            fh.write("# E-E_F (eV)  DOS (as plotted)\n")
            for e, v in pts:
                fh.write(f"{e:.5f} {v:.5f}\n")
        lines.append(f"DOSMAX{k} = {max(v for _, v in pts):.3f}; DOSTICK{k} = {vb - va if len(ticks) == 2 else (vb - va) / (len(ticks) - 1):g}")
        print(tag, name, "image", pix.width, "x", pix.height, "DOS max", round(max(v for _, v in pts), 3),
              "at E =", [e for e, v in pts if v == max(v for _, v in pts)][0], "k ticks", [round(v, 3) for v in kn])
    (D / f"bands_{tag}.gp").write_text("\n".join(lines) + "\n")
