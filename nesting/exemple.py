"""Piese de exemplu (in mm): placa perforata, suport L, flansa, capac, panou."""
from pathlib import Path

import ezdxf
from ezdxf import units


def _doc_nou():
    doc = ezdxf.new("R2010")
    doc.units = units.MM
    return doc, doc.modelspace()


def _dreptunghi(msp, w, h):
    msp.add_lwpolyline([(0, 0), (w, 0), (w, h), (0, h)], close=True)


def genereaza_exemple(folder="piese"):
    folder = Path(folder)
    folder.mkdir(parents=True, exist_ok=True)

    # placa perforata 600 x 400 cu grila de gauri D10, pas 40
    doc, msp = _doc_nou()
    _dreptunghi(msp, 600, 400)
    for x in range(60, 560, 40):
        for y in range(60, 360, 40):
            msp.add_circle((x, y), radius=5)
    doc.saveas(folder / "placa_perforata_x2.dxf")

    # suport in L 300 x 250
    doc, msp = _doc_nou()
    msp.add_lwpolyline([(0, 0), (300, 0), (300, 60), (60, 60),
                        (60, 250), (0, 250)], close=True)
    doc.saveas(folder / "suport_L_x4.dxf")

    # flansa rotunda D200 cu gaura centrala si 4 gauri
    doc, msp = _doc_nou()
    msp.add_circle((100, 100), radius=100)
    msp.add_circle((100, 100), radius=40)
    for x, y in [(100, 30), (100, 170), (30, 100), (170, 100)]:
        msp.add_circle((x, y), radius=6)
    doc.saveas(folder / "flansa_x3.dxf")

    # capac 800 x 350 cu colturi rotunjite R20
    doc, msp = _doc_nou()
    r, w, h = 20, 800, 350
    msp.add_line((r, 0), (w - r, 0))
    msp.add_line((w, r), (w, h - r))
    msp.add_line((w - r, h), (r, h))
    msp.add_line((0, h - r), (0, r))
    msp.add_arc((w - r, r), r, 270, 360)
    msp.add_arc((w - r, h - r), r, 0, 90)
    msp.add_arc((r, h - r), r, 90, 180)
    msp.add_arc((r, r), r, 180, 270)
    doc.saveas(folder / "capac_x2.dxf")

    # panou lateral 900 x 450
    doc, msp = _doc_nou()
    _dreptunghi(msp, 900, 450)
    doc.saveas(folder / "panou_lateral_x2.dxf")

    return folder
