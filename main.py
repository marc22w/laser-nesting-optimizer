from pathlib import Path

import matplotlib.pyplot as plt

from nesting.models import Part
from nesting.packer import shelf_pack
from nesting.maxrects import maxrects_pack
from nesting.multisheet import nest_multi, utilizare
from nesting.plot import plot_sheet
from nesting.export_dxf import export_dxf
from nesting.import_dxf import citeste_folder
from nesting.cutting_time import ParametriLaser, estimare_foaie, format_timp

SHEET_W, SHEET_H = 2000, 1000  # foaie standard 2000x1000 mm
LASER = ParametriLaser(viteza_mm_min=3000, strapungere_s=0.5)  # otel 2-3 mm, laser fibra
FOLDER_PIESE = Path("piese")
FOLDER_IESIRE = Path("output")

if FOLDER_PIESE.is_dir() and any(FOLDER_PIESE.glob("*.dxf")):
    parts = citeste_folder(FOLDER_PIESE)
    print(f"Citit {len(parts)} piese din {FOLDER_PIESE}/\n")
else:
    dimensiuni = [(400, 300), (600, 200), (300, 300), (500, 450),
                  (250, 150), (800, 250), (350, 400)] * 2
    parts = [Part(f"P{i}", w, h) for i, (w, h) in enumerate(dimensiuni)]
    print("Folderul piese/ lipseste -> folosesc piesele demo\n")

# 1. Comparatie: cate foi foloseste fiecare algoritm
for nume, algoritm in [("Shelf (rafturi)", shelf_pack),
                       ("MaxRects", maxrects_pack)]:
    foi, _ = nest_multi(parts, SHEET_W, SHEET_H, algoritm)
    procente = ", ".join(f"{utilizare(f, SHEET_W, SHEET_H):.1f}%" for f in foi)
    print(f"{nume:<16} {len(foi)} foi  ({procente})")

# 2. Rezultatul final cu MaxRects: desen, DXF si timp de taiere pe fiecare foaie
foi, imposibile = nest_multi(parts, SHEET_W, SHEET_H, maxrects_pack)
FOLDER_IESIRE.mkdir(exist_ok=True)
cache, timp_total = {}, 0.0
print()
for i, foaie in enumerate(foi, start=1):
    util = utilizare(foaie, SHEET_W, SHEET_H)
    lungime, strapungeri, timp = estimare_foaie(foaie, LASER, cache)
    timp_total += timp
    fisier = FOLDER_IESIRE / f"foaia_{i}.dxf"
    export_dxf(foaie, SHEET_W, SHEET_H, str(fisier))
    print(f"Foaia {i}: {len(foaie):>2} piese, {util:.1f}%, "
          f"taiere {lungime / 1000:.1f} m, {strapungeri} strapungeri, "
          f"~{format_timp(timp)} -> {fisier}")
    plot_sheet(foaie, SHEET_W, SHEET_H,
               f"MaxRects - foaia {i} din {len(foi)}: {util:.1f}%, ~{format_timp(timp)}")

print(f"\nTimp total estimat de taiere: ~{format_timp(timp_total)}")
if imposibile:
    print("ATENTIE, nu incap nici pe o foaie goala:",
          ", ".join(p.name for p in imposibile))

plt.show()
