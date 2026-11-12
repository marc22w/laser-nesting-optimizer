from pathlib import Path

import matplotlib.pyplot as plt

from nesting.models import Part
from nesting.packer import shelf_pack
from nesting.maxrects import maxrects_pack
from nesting.plot import plot_sheet
from nesting.export_dxf import export_dxf
from nesting.import_dxf import citeste_folder

SHEET_W, SHEET_H = 2000, 1000  # foaie standard 2000x1000 mm
FOLDER_PIESE = Path("piese")

if FOLDER_PIESE.is_dir() and any(FOLDER_PIESE.glob("*.dxf")):
    parts = citeste_folder(FOLDER_PIESE)
    print(f"Citit {len(parts)} piese din {FOLDER_PIESE}/")
else:
    dimensiuni = [(400, 300), (600, 200), (300, 300), (500, 450),
                  (250, 150), (800, 250), (350, 400)] * 2
    parts = [Part(f"P{i}", w, h) for i, (w, h) in enumerate(dimensiuni)]
    print("Folderul piese/ lipseste -> folosesc piesele demo")

for nume, algoritm in [("Shelf (rafturi)", shelf_pack),
                       ("MaxRects", maxrects_pack)]:
    placed, skipped = algoritm(parts, SHEET_W, SHEET_H)
    used = sum(p.w * p.h for p in placed)
    util = used / (SHEET_W * SHEET_H) * 100
    print(f"{nume:<16} plasate: {len(placed):>2}, neincapute: {len(skipped)}, "
          f"utilizare: {util:.1f}%")
    plot_sheet(placed, SHEET_W, SHEET_H, f"{nume} - {util:.1f}%")

    if algoritm is maxrects_pack:
        export_dxf(placed, SHEET_W, SHEET_H, "nesting_maxrects.dxf")
        print("Salvat: nesting_maxrects.dxf")
        if skipped:
            print("Neincapute:", ", ".join(p.name for p in skipped))

plt.show()  # deschide ambele ferestre
