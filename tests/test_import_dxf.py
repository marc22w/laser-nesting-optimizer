import ezdxf
import pytest
from ezdxf import units

from nesting.import_dxf import citeste_folder, citeste_piesa


def salveaza(path, w, h, unitate=units.MM, cu_gaura=False):
    doc = ezdxf.new("R2010")
    doc.units = unitate
    msp = doc.modelspace()
    msp.add_lwpolyline([(0, 0), (w, 0), (w, h), (0, h)], close=True)
    if cu_gaura:
        msp.add_circle((w / 2, h / 2), radius=min(w, h) / 4)
    doc.saveas(str(path))


def test_dimensiuni_dreptunghi(tmp_path):
    salveaza(tmp_path / "a.dxf", 300, 200, cu_gaura=True)
    assert citeste_piesa(tmp_path / "a.dxf") == (300, 200)


def test_conversie_din_cm(tmp_path):
    salveaza(tmp_path / "cm.dxf", 30, 20, unitate=units.CM)
    assert citeste_piesa(tmp_path / "cm.dxf") == pytest.approx((300, 200))


def test_cerc_bounding_box(tmp_path):
    doc = ezdxf.new("R2010")
    doc.units = units.MM
    doc.modelspace().add_circle((500, 500), radius=100)
    doc.saveas(str(tmp_path / "cerc.dxf"))
    assert citeste_piesa(tmp_path / "cerc.dxf") == pytest.approx((200, 200))


def test_cantitate_din_nume(tmp_path):
    salveaza(tmp_path / "placa_x3.dxf", 400, 100)
    salveaza(tmp_path / "capac.dxf", 50, 50)
    parts = citeste_folder(tmp_path)
    nume = sorted(p.name for p in parts)
    assert nume == ["capac", "placa-1", "placa-2", "placa-3"]


def test_fisier_fara_geometrie(tmp_path):
    ezdxf.new("R2010").saveas(str(tmp_path / "gol.dxf"))
    with pytest.raises(ValueError):
        citeste_piesa(tmp_path / "gol.dxf")
