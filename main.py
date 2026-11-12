import matplotlib.pyplot as plt

from nesting.models import Part
from nesting.packer import shelf_pack
from nesting.maxrects import maxrects_pack
from nesting.plot import plot_sheet

SHEET_W, SHEET_H = 2000, 1000  # foaie standard 2000x1000 mm

dimensiuni = [(400, 300), (600, 200), (300, 300), (500, 450),
              (250, 150), (800, 250), (350, 400)] * 2

parts = [Part(f"P{i}", w, h) for i, (w, h) in enumerate(dimensiuni)]

for nume, algoritm in [("Shelf (rafturi)", shelf_pack),
                       ("MaxRects", maxrects_pack)]:
    placed, skipped = algoritm(parts, SHEET_W, SHEET_H)
    used = sum(p.w * p.h for p in placed)
    util = used / (SHEET_W * SHEET_H) * 100
    print(f"{nume:<16} plasate: {len(placed):>2}, neincapute: {len(skipped)}, "
          f"utilizare: {util:.1f}%")
    plot_sheet(placed, SHEET_W, SHEET_H, f"{nume} - {util:.1f}%")

plt.show()  # deschide ambele ferestre
