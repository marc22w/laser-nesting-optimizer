import random

import pytest

from nesting.models import Part
from nesting.packer import shelf_pack
from nesting.maxrects import maxrects_pack

SHEET_W, SHEET_H = 2000, 1000
ALGORITMI = [shelf_pack, maxrects_pack]


def piese_aleatoare(n, seed):
    rnd = random.Random(seed)
    return [Part(f"P{i}", rnd.randint(50, 900), rnd.randint(50, 600))
            for i in range(n)]


def se_suprapun(a, b, gap):
    """True daca doua piese plasate se suprapun sau sunt mai apropiate decat gap."""
    eps = 1e-9
    return not (a.x + a.w + gap <= b.x + eps or
                b.x + b.w + gap <= a.x + eps or
                a.y + a.h + gap <= b.y + eps or
                b.y + b.h + gap <= a.y + eps)


@pytest.mark.parametrize("algoritm", ALGORITMI)
@pytest.mark.parametrize("seed", range(20))
def test_nicio_piesa_nu_iese_din_foaie(algoritm, seed):
    placed, _ = algoritm(piese_aleatoare(30, seed), SHEET_W, SHEET_H)
    for pl in placed:
        assert pl.x >= 0 and pl.y >= 0
        assert pl.x + pl.w <= SHEET_W
        assert pl.y + pl.h <= SHEET_H


@pytest.mark.parametrize("algoritm", ALGORITMI)
@pytest.mark.parametrize("seed", range(20))
def test_piesele_nu_se_suprapun(algoritm, seed):
    gap = 2.0
    placed, _ = algoritm(piese_aleatoare(30, seed), SHEET_W, SHEET_H, gap)
    for i, a in enumerate(placed):
        for b in placed[i + 1:]:
            assert not se_suprapun(a, b, gap), f"{a.part.name} si {b.part.name}"


@pytest.mark.parametrize("algoritm", ALGORITMI)
def test_nicio_piesa_pierduta(algoritm):
    parts = piese_aleatoare(40, seed=1)
    placed, skipped = algoritm(parts, SHEET_W, SHEET_H)
    assert len(placed) + len(skipped) == len(parts)


@pytest.mark.parametrize("algoritm", ALGORITMI)
def test_piesa_prea_mare_e_sarita(algoritm):
    placed, skipped = algoritm([Part("mare", 2500, 1500)], SHEET_W, SHEET_H)
    assert placed == []
    assert [p.name for p in skipped] == ["mare"]


@pytest.mark.parametrize("algoritm", ALGORITMI)
def test_foaie_goala(algoritm):
    placed, skipped = algoritm([], SHEET_W, SHEET_H)
    assert placed == [] and skipped == []


def test_maxrects_roteste_cand_trebuie():
    # piesa de 900x1900 nu incape in picioare pe o foaie 2000x1000, dar culcata da
    placed, skipped = maxrects_pack([Part("lunga", 900, 1900)], SHEET_W, SHEET_H)
    assert skipped == [] and placed[0].rotated


@pytest.mark.parametrize("seed", range(10))
def test_maxrects_nu_e_mai_slab_decat_shelf(seed):
    parts = piese_aleatoare(30, seed)
    arie = lambda placed: sum(p.w * p.h for p in placed)
    shelf, _ = shelf_pack(parts, SHEET_W, SHEET_H)
    maxr, _ = maxrects_pack(parts, SHEET_W, SHEET_H)
    assert arie(maxr) >= arie(shelf)
