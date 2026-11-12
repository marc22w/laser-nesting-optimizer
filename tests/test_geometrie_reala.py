
import ezdxf
import pytest
from ezdxf import bbox, units

from nesting.models import Placement
from nesting.import_dxf import citeste_folder
from nesting.export_dxf import export_dxf


def piesa_cu_gaura(folder, nume, w, h, gaura, raza=10, deplasare=(0, 0),
                   unitate=units.MM):

    dx, dy = deplasare
    doc = ezdxf.new("R2010")
    doc.units = unitate
    msp = doc.modelspace()
    msp.add_lwpolyline([(dx, dy), (dx + w, dy), (dx + w, dy + h), (dx, dy + h)],
                       close=True)
    msp.add_circle((dx + gaura[0], dy + gaura[1]), radius=raza)
    doc.saveas(str(folder / f"{nume}.dxf"))


def exporta_si_citeste(placements, tmp_path):
    fisier = str(tmp_path / "foaie.dxf")
    export_dxf(placements, 2000, 1000, fisier)
    return ezdxf.readfile(fisier).modelspace()


def test_gaura_piesa_nerotita(tmp_path):
    piese = tmp_path / "piese"
    piese.mkdir()
    # piesa desenata departe de origine, ca sa verificam si normalizarea
    piesa_cu_gaura(piese, "placa", 300, 200, gaura=(50, 40), deplasare=(1000, 500))
    part = citeste_folder(piese)[0]

    msp = exporta_si_citeste([Placement(part, 100, 100)], tmp_path)
    cerc = msp.query('CIRCLE[layer=="TAIERE"]')[0]
    assert (cerc.dxf.center.x, cerc.dxf.center.y) == pytest.approx((150, 140))


def test_gaura_piesa_rotita(tmp_path):
    piese = tmp_path / "piese"
    piese.mkdir()
    piesa_cu_gaura(piese, "placa", 300, 200, gaura=(50, 40))
    part = citeste_folder(piese)[0]

    # rotita 90 grade: ocupa 200 x 300; punctul (x, y) ajunge in (h - y, x)
    msp = exporta_si_citeste([Placement(part, 100, 100, rotated=True)], tmp_path)
    cerc = msp.query('CIRCLE[layer=="TAIERE"]')[0]
    assert (cerc.dxf.center.x, cerc.dxf.center.y) == pytest.approx((100 + 200 - 40, 100 + 50))


@pytest.mark.parametrize("rotita", [False, True])
def test_geometria_ramane_in_locul_alocat(tmp_path, rotita):
    piese = tmp_path / "piese"
    piese.mkdir()
    piesa_cu_gaura(piese, "placa", 300, 200, gaura=(150, 100), deplasare=(-70, 30))
    part = citeste_folder(piese)[0]
    pl = Placement(part, 400, 250, rotated=rotita)

    msp = exporta_si_citeste([pl], tmp_path)
    ext = bbox.extents(msp.query('*[layer=="TAIERE"]'))
    assert ext.extmin.x == pytest.approx(pl.x)
    assert ext.extmin.y == pytest.approx(pl.y)
    assert ext.size.x == pytest.approx(pl.w)
    assert ext.size.y == pytest.approx(pl.h)


def test_conversie_cm_la_export(tmp_path):
    piese = tmp_path / "piese"
    piese.mkdir()
    # desenata in cm: 30 x 20 cm cu o gaura R1 cm la (5, 4) cm
    piesa_cu_gaura(piese, "placa", 30, 20, gaura=(5, 4), raza=1, unitate=units.CM)
    part = citeste_folder(piese)[0]

    msp = exporta_si_citeste([Placement(part, 0, 0)], tmp_path)
    cerc = msp.query('CIRCLE[layer=="TAIERE"]')[0]
    assert (cerc.dxf.center.x, cerc.dxf.center.y) == pytest.approx((50, 40))
    assert cerc.dxf.radius == pytest.approx(10)  # R1 cm -> R10 mm


def test_toate_entitatile_sunt_copiate(tmp_path):
    piese = tmp_path / "piese"
    piese.mkdir()
    piesa_cu_gaura(piese, "a_x3", 300, 200, gaura=(50, 50))
    parts = citeste_folder(piese)
    placements = [Placement(p, i * 400, 0) for i, p in enumerate(parts)]

    msp = exporta_si_citeste(placements, tmp_path)
    assert len(msp.query('CIRCLE[layer=="TAIERE"]')) == 3
    assert len(msp.query('LWPOLYLINE[layer=="TAIERE"]')) == 3