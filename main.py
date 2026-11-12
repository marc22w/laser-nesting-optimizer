from nesting.models import Part
from nesting.packer import shelf_pack
from nesting.plot import plot_sheet

SHEET_W, SHEET_H = 2000, 1000  # foaie standard 2000x1000 mm

dimensiuni = [(400, 300), (600, 200), (300, 300), (500, 450),
              (250, 150), (800, 250), (350, 400)] * 2

parts = [Part(f"P{i}", w, h) for i, (w, h) in enumerate(dimensiuni)]

placed, skipped = shelf_pack(parts, SHEET_W, SHEET_H)

used = sum(p.part.w * p.part.h for p in placed)
print(f"Plasate: {len(placed)}, neincapute: {len(skipped)}")
print(f"Utilizare foaie: {used / (SHEET_W * SHEET_H) * 100:.1f}%")

plot_sheet(placed, SHEET_W, SHEET_H)
