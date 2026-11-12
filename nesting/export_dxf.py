"""Export DXF: foaia si piesele asezate, gata de deschis in Fusion / trimis la laser."""
import ezdxf
from ezdxf import units
from ezdxf.enums import TextEntityAlignment


def export_dxf(placements, sheet_w, sheet_h, path, foaie=True):
    doc = ezdxf.new("R2010")
    doc.units = units.MM                 # Fusion citeste dimensiunile in mm
    doc.layers.add("FOAIE", color=8)     # gri: conturul foii, doar referinta
    doc.layers.add("TAIERE", color=1)    # rosu: conturul pieselor de taiat
    doc.layers.add("ETICHETE", color=3)  # verde: numele pieselor
    msp = doc.modelspace()

    def dreptunghi(x, y, w, h, layer):
        msp.add_lwpolyline([(x, y), (x + w, y), (x + w, y + h), (x, y + h)],
                           close=True, dxfattribs={"layer": layer})

    if foaie:
        dreptunghi(0, 0, sheet_w, sheet_h, "FOAIE")

    for pl in placements:
        dreptunghi(pl.x, pl.y, pl.w, pl.h, "TAIERE")
        text = msp.add_text(pl.part.name, height=min(pl.w, pl.h) * 0.15,
                            dxfattribs={"layer": "ETICHETE"})
        text.set_placement((pl.x + pl.w / 2, pl.y + pl.h / 2),
                           align=TextEntityAlignment.MIDDLE_CENTER)

    doc.saveas(path)
    return path
