"""Genereaza cateva piese de exemplu in folderul piese/ (in mm)."""
from pathlib import Path

import ezdxf
from ezdxf import units

FOLDER = Path("piese")
FOLDER.mkdir(exist_ok=True)


def doc_nou():
    doc = ezdxf.new("R2010")
    doc.units = units.MM
    return doc, doc.modelspace()


def dreptunghi(msp, w, h):
    msp.add_lwpolyline([(0, 0), (w, 0), (w, h), (0, h)], close=True)


# 1. Placa perforata 600 x 400 cu grila de gauri D10, pas 40
doc, msp = doc_nou()
dreptunghi(msp, 600, 400)
for x in range(60, 560, 40):
    for y in range(60, 360, 40):
        msp.add_circle((x, y), radius=5)
doc.saveas(FOLDER / "placa_perforata_x2.dxf")

# 2. Suport in L 300 x 250
doc, msp = doc_nou()
msp.add_lwpolyline([(0, 0), (300, 0), (300, 60), (60, 60),
                    (60, 250), (0, 250)], close=True)
doc.saveas(FOLDER / "suport_L_x4.dxf")

# 3. Flansa rotunda D200 cu 4 gauri
doc, msp = doc_nou()
msp.add_circle((100, 100), radius=100)
msp.add_circle((100, 100), radius=40)
for x, y in [(100, 30), (100, 170), (30, 100), (170, 100)]:
    msp.add_circle((x, y), radius=6)
doc.saveas(FOLDER / "flansa_x3.dxf")

# 4. Capac 800 x 350 cu colturi rotunjite (arce R20)
doc, msp = doc_nou()
r, w, h = 20, 800, 350
msp.add_line((r, 0), (w - r, 0))
msp.add_line((w, r), (w, h - r))
msp.add_line((w - r, h), (r, h))
msp.add_line((0, h - r), (0, r))
msp.add_arc((w - r, r), r, 270, 360)
msp.add_arc((w - r, h - r), r, 0, 90)
msp.add_arc((r, h - r), r, 90, 180)
msp.add_arc((r, r), r, 180, 270)
doc.saveas(FOLDER / "capac_x2.dxf")

# 5. Panou lateral 900 x 450
doc, msp = doc_nou()
dreptunghi(msp, 900, 450)
doc.saveas(FOLDER / "panou_lateral_x2.dxf")

print(f"Generat {len(list(FOLDER.glob('*.dxf')))} fisiere in {FOLDER}/")
