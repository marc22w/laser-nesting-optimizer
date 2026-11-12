import math

import ezdxf
import pytest
from ezdxf import units

from nesting.models import Part, Placement
from nesting.import_dxf import citeste_folder
from nesting.cutting_time import (ParametriLaser, estimare_foaie,
                                  format_timp, numar_contururi)


def test_piesa_fara_dxf_e_dreptunghi():
    pl = Placement(Part("A", 300, 200), 0, 0)
    lungime, strapungeri, _ = estimare_foaie([pl])
    assert lungime == pytest.approx(1000)
    assert strapungeri == 1


def test_timp_calculat_corect():
    # 3000 mm la 3000 mm/min = 60 s, plus 1 strapungere x 0.5 s
    pl = Placement(Part("A", 1000, 500), 0, 0)
    _, _, timp = estimare_foaie([pl], ParametriLaser(3000, 0.5))
    assert timp == pytest.approx(60.5)


def test_placa_cu_gaura(tmp_path):
    doc = ezdxf.new("R2010")
    doc.units = units.MM
    msp = doc.modelspace()
    msp.add_lwpolyline([(0, 0), (300, 0), (300, 200), (0, 200)], close=True)
    msp.add_circle((150, 100), radius=10)
    doc.saveas(str(tmp_path / "placa.dxf"))

    part = citeste_folder(tmp_path)[0]
    lungime, strapungeri, _ = estimare_foaie([Placement(part, 0, 0)])
    assert lungime == pytest.approx(1000 + 2 * math.pi * 10, rel=1e-3)
    assert strapungeri == 2


def test_contur_din_linii_si_arce_e_un_singur_contur(tmp_path):
    # capac 800 x 350 cu colturi R20, desenat din 4 linii + 4 arce
    doc = ezdxf.new("R2010")
    doc.units = units.MM
    msp = doc.modelspace()
    r, w, h = 20, 800, 350
    msp.add_line((r, 0), (w - r, 0))
    msp.add_line((w, r), (w, h - r))
    msp.add_line((w - r, h), (r, h))
    msp.add_line((0, h - r), (0, r))
    msp.add_arc((w - r, r), r, 270, 360)
    msp.add_arc((w - r, h - r), r, 0, 90)
    msp.add_arc((r, h - r), r, 90, 180)
    msp.add_arc((r, r), r, 180, 270)
    doc.saveas(str(tmp_path / "capac.dxf"))

    part = citeste_folder(tmp_path)[0]
    lungime, strapungeri, _ = estimare_foaie([Placement(part, 0, 0)])
    asteptat = 2 * (w - 2 * r) + 2 * (h - 2 * r) + 2 * math.pi * r
    assert lungime == pytest.approx(asteptat, rel=1e-3)
    assert strapungeri == 1


def test_conversie_cm(tmp_path):
    doc = ezdxf.new("R2010")
    doc.units = units.CM
    doc.modelspace().add_lwpolyline([(0, 0), (30, 0), (30, 20), (0, 20)], close=True)
    doc.saveas(str(tmp_path / "cm.dxf"))

    part = citeste_folder(tmp_path)[0]
    lungime, _, _ = estimare_foaie([Placement(part, 0, 0)])
    assert lungime == pytest.approx(1000)  # 100 cm perimetru = 1000 mm


def test_numar_contururi_fara_ezdxf():
    # doua segmente separate care nu se ating + un cerc inchis
    capete = [((0, 0), (1, 0)), ((5, 5), (6, 5)), ((9, 9), (9, 9))]
    assert numar_contururi(capete) == 3


def test_format_timp():
    assert format_timp(272) == "4 min 32 s"
    assert format_timp(59.6) == "1 min 00 s"
