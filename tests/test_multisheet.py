import random

import pytest

from nesting.models import Part
from nesting.packer import shelf_pack
from nesting.maxrects import maxrects_pack
from nesting.multisheet import nest_multi, utilizare

SHEET_W, SHEET_H = 2000, 1000


def piese_aleatoare(n, seed):
    rnd = random.Random(seed)
    return [Part(f"P{i}", rnd.randint(50, 900), rnd.randint(50, 600))
            for i in range(n)]


@pytest.mark.parametrize("algoritm", [shelf_pack, maxrects_pack])
@pytest.mark.parametrize("seed", range(10))
def test_toate_piesele_sunt_plasate_o_singura_data(algoritm, seed):
    parts = piese_aleatoare(80, seed)
    foi, imposibile = nest_multi(parts, SHEET_W, SHEET_H, algoritm)
    plasate = [pl.part.name for foaie in foi for pl in foaie]
    assert imposibile == []
    assert sorted(plasate) == sorted(p.name for p in parts)


def test_piesa_prea_mare_e_raportata():
    parts = [Part("ok", 500, 500), Part("urias", 3000, 3000)]
    foi, imposibile = nest_multi(parts, SHEET_W, SHEET_H)
    assert len(foi) == 1
    assert [p.name for p in imposibile] == ["urias"]


def test_fara_piese():
    assert nest_multi([], SHEET_W, SHEET_H) == ([], [])


def test_numar_minim_de_foi():
    # 6 piese de 999x999: incap cate 2 pe foaie -> 3 foi
    parts = [Part(f"P{i}", 999, 999) for i in range(6)]
    foi, _ = nest_multi(parts, SHEET_W, SHEET_H)
    assert len(foi) == 3


@pytest.mark.parametrize("seed", range(10))
def test_maxrects_nu_foloseste_mai_multe_foi_decat_shelf(seed):
    parts = piese_aleatoare(80, seed)
    foi_shelf, _ = nest_multi(parts, SHEET_W, SHEET_H, shelf_pack)
    foi_maxr, _ = nest_multi(parts, SHEET_W, SHEET_H, maxrects_pack)
    assert len(foi_maxr) <= len(foi_shelf)


def test_utilizare():
    foi, _ = nest_multi([Part("A", 1000, 1000)], SHEET_W, SHEET_H)
    assert utilizare(foi[0], SHEET_W, SHEET_H) == pytest.approx(50)
