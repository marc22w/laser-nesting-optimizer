import ezdxf

from nesting.models import Part
from nesting.maxrects import maxrects_pack
from nesting.export_dxf import export_dxf


def test_export_dxf(tmp_path):
    parts = [Part("A", 400, 300), Part("B", 900, 1900), Part("C", 200, 200)]
    placed, _ = maxrects_pack(parts, 2000, 1000)
    fisier = export_dxf(placed, 2000, 1000, str(tmp_path / "test.dxf"))

    doc = ezdxf.readfile(fisier)
    msp = doc.modelspace()
    taieri = msp.query('LWPOLYLINE[layer=="TAIERE"]')
    assert len(taieri) == len(placed)
    assert len(msp.query('LWPOLYLINE[layer=="FOAIE"]')) == 1

    # fiecare contur are exact dimensiunile piesei asezate
    for poly, pl in zip(taieri, placed):
        xs = [p[0] for p in poly.get_points()]
        ys = [p[1] for p in poly.get_points()]
        assert max(xs) - min(xs) == pl.w
        assert max(ys) - min(ys) == pl.h
