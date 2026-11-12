import ezdxf

from nesting.models import Part
from nesting.maxrects import maxrects_pack
from nesting.export_dxf import export_dxf


def dimensiuni(poly):
    xs = [p[0] for p in poly.get_points()]
    ys = [p[1] for p in poly.get_points()]
    return (round(max(xs) - min(xs), 6), round(max(ys) - min(ys), 6))


def test_export_dxf(tmp_path):
    parts = [Part("A", 400, 300), Part("B", 900, 500), Part("C", 200, 200)]
    placed, _ = maxrects_pack(parts, 2000, 1000)
    statistici = {}
    fisier = export_dxf(placed, 2000, 1000, str(tmp_path / "test.dxf"),
                        traseu=True, statistici=statistici)

    msp = ezdxf.readfile(fisier).modelspace()
    taieri = msp.query('LWPOLYLINE[layer=="TAIERE"]')
    assert len(taieri) == len(placed)
    assert len(msp.query('LWPOLYLINE[layer=="FOAIE"]')) == 1

    # fiecare contur are dimensiunile unei piese asezate (ordinea poate diferi)
    assert sorted(dimensiuni(p) for p in taieri) == sorted(
        (round(pl.w, 6), round(pl.h, 6)) for pl in placed)

    # traseul in gol: cate o linie pana la fiecare contur
    assert 1 <= len(msp.query('LINE[layer=="TRASEU"]')) <= len(placed)
    assert statistici["contururi"] == len(placed)
    assert statistici["deplasare_mm"] <= statistici["deplasare_naiva_mm"] + 1e-9


def test_fara_traseu_implicit(tmp_path):
    placed, _ = maxrects_pack([Part("A", 400, 300)], 2000, 1000)
    fisier = export_dxf(placed, 2000, 1000, str(tmp_path / "t.dxf"))
    msp = ezdxf.readfile(fisier).modelspace()
    assert len(msp.query('LINE[layer=="TRASEU"]')) == 0
