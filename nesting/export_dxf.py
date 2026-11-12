"""Export DXF: foaia si piesele asezate, gata de deschis in Fusion / trimis la laser.

Piesele citite din DXF sunt exportate cu geometria lor reala (contur, gauri,
arce), mutata si rotita conform nesting-ului. Piesele fara fisier sursa
sunt desenate ca dreptunghiuri.
"""
import math

import ezdxf
from ezdxf import units
from ezdxf.enums import TextEntityAlignment
from ezdxf.math import Matrix44

from .import_dxf import GEOMETRIE


def _matrice(pl):
    """Transformarea din coordonatele fisierului sursa in coordonatele foii."""
    p = pl.part
    ox, oy = p.origin
    pasi = [Matrix44.translate(-ox, -oy, 0),  # coltul piesei in (0, 0)
            Matrix44.scale(p.scale)]          # unitatile fisierului -> mm
    if pl.rotated:
        # rotire 90 grade in sens trigonometric, apoi inapoi in cadranul pozitiv
        pasi += [Matrix44.z_rotate(math.radians(90)),
                 Matrix44.translate(p.h, 0, 0)]
    pasi.append(Matrix44.translate(pl.x, pl.y, 0))  # pozitia pe foaie
    return Matrix44.chain(*pasi)


def _geometrie_sursa(path, cache):
    """Citeste o singura data entitatile din fiecare fisier sursa."""
    if path not in cache:
        doc = ezdxf.readfile(path)
        cache[path] = (doc, list(doc.modelspace().query(GEOMETRIE)))
    return cache[path][1]


def export_dxf(placements, sheet_w, sheet_h, path, foaie=True):
    doc = ezdxf.new("R2010")
    doc.units = units.MM                 # Fusion citeste dimensiunile in mm
    doc.layers.add("FOAIE", color=8)     # gri: conturul foii, doar referinta
    doc.layers.add("TAIERE", color=1)    # rosu: conturul pieselor de taiat
    doc.layers.add("ETICHETE", color=3)  # verde: numele pieselor
    msp = doc.modelspace()
    cache = {}

    def dreptunghi(x, y, w, h, layer):
        msp.add_lwpolyline([(x, y), (x + w, y), (x + w, y + h), (x, y + h)],
                           close=True, dxfattribs={"layer": layer})

    if foaie:
        dreptunghi(0, 0, sheet_w, sheet_h, "FOAIE")

    for pl in placements:
        if pl.part.source:
            m = _matrice(pl)
            for entitate in _geometrie_sursa(pl.part.source, cache):
                copie = entitate.copy()
                copie.transform(m)
                copie.dxf.layer = "TAIERE"
                copie.dxf.color = 256  # culoarea vine de la layer
                msp.add_foreign_entity(copie, copy=False)
        else:
            dreptunghi(pl.x, pl.y, pl.w, pl.h, "TAIERE")

        text = msp.add_text(pl.part.name, height=min(pl.w, pl.h) * 0.15,
                            dxfattribs={"layer": "ETICHETE"})
        text.set_placement((pl.x + pl.w / 2, pl.y + pl.h / 2),
                           align=TextEntityAlignment.MIDDLE_CENTER)

    doc.saveas(path)
    return path
