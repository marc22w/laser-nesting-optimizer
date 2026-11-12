"""Import DXF: fiecare fisier .dxf dintr-un folder devine o piesa.

Numele fisierului da numele piesei; sufixul _xN da cantitatea
(ex: flansa_x3.dxf -> 3 bucati). Dimensiunile sunt cele ale dreptunghiului
care cuprinde toata geometria piesei (bounding box), convertite in mm.
Piesa tine minte fisierul sursa, ca exportul sa poata copia geometria reala.
"""
import re
from pathlib import Path

import ezdxf
from ezdxf import bbox, units

from .models import Part

GEOMETRIE = "LINE ARC CIRCLE LWPOLYLINE POLYLINE SPLINE ELLIPSE"
_CANTITATE = re.compile(r"^(?P<nume>.+?)_x(?P<n>\d+)$")


def _factor_mm(doc):
    """Factorul de conversie din unitatile desenului in mm."""
    u = doc.units
    if u in (0, units.MM):  # 0 = fara unitati -> presupunem mm
        return 1.0
    return units.conversion_factor(u, units.MM)


def _analizeaza(path):
    """Intoarce (latime_mm, inaltime_mm, origine, factor) pentru un fisier."""
    doc = ezdxf.readfile(str(path))
    ext = bbox.extents(doc.modelspace().query(GEOMETRIE))
    if not ext.has_data:
        raise ValueError(f"{path}: nu am gasit nicio geometrie")
    f = _factor_mm(doc)
    w = round(ext.size.x * f, 3)
    h = round(ext.size.y * f, 3)
    return w, h, (ext.extmin.x, ext.extmin.y), f


def citeste_piesa(path):
    """Intoarce (latime, inaltime) in mm pentru geometria din fisier."""
    w, h, _, _ = _analizeaza(path)
    return w, h


def citeste_folder(folder):
    """Citeste toate fisierele .dxf din folder si intoarce lista de piese."""
    parts = []
    fisiere = sorted(p for p in Path(folder).iterdir()
                     if p.suffix.lower() == ".dxf")
    for path in fisiere:
        m = _CANTITATE.match(path.stem)
        nume, n = (m["nume"], int(m["n"])) if m else (path.stem, 1)
        w, h, origine, f = _analizeaza(path)
        for i in range(n):
            parts.append(Part(f"{nume}-{i + 1}" if n > 1 else nume, w, h,
                              source=str(path), origin=origine, scale=f))
    return parts
