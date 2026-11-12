import io
import zipfile

import ezdxf

from nesting.exemple import genereaza_exemple
from nesting.pipeline import proceseaza


def test_proceseaza_piesele_demo(tmp_path):
    rez = proceseaza(genereaza_exemple(tmp_path / "piese"), 2000, 1000)
    assert rez.numar_piese == 13
    assert rez.imposibile == []
    assert sum(len(f.placements) for f in rez.foi) == 13
    assert all(0 < f.utilizare <= 100 for f in rez.foi)
    assert rez.timp_total_s > 0


def test_zip_contine_toate_foile(tmp_path):
    rez = proceseaza(genereaza_exemple(tmp_path / "piese"), 2000, 1000)
    with zipfile.ZipFile(io.BytesIO(rez.zip_dxf())) as z:
        assert sorted(z.namelist()) == [f"foaia_{i}.dxf" for i in range(1, len(rez.foi) + 1)]


def test_dxf_descarcat_e_valid_si_fara_traseu(tmp_path):
    rez = proceseaza(genereaza_exemple(tmp_path / "piese"), 2000, 1000)
    fisier = tmp_path / "foaia_1.dxf"
    fisier.write_bytes(rez.foi[0].dxf)
    msp = ezdxf.readfile(str(fisier)).modelspace()
    assert len(msp.query('*[layer=="TAIERE"]')) > 0
    assert len(msp.query('*[layer=="TRASEU"]')) == 0
