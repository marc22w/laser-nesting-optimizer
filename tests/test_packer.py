import random

import pytest

from nesting.models import Part
from nesting.packer import shelf_pack

SHEET_W, SHEET_H = 2000, 1000


def piese_aleatoare(n, seed):
    rnd = random.Random(seed)
    return [Part(f"P{i}", rnd.randint(50, 900), rnd.randint(50, 600))
            for i in range(n)]


def se_suprapun(a, b, gap):
    """True daca doua piese plasate se suprapun sau sunt mai apropiate decat gap."""
    return not (a.x + a.part.w + gap <= b.x + 1e-9 or
                b.x + b.part.w + gap <= a.x + 1e-9 or
                a.y + a.part.h + gap <= b.y + 1e-9 or
                b.y + b.part.h + gap <= a.y + 1e-9)


@pytest.mark.parametrize("seed", range(20))
def test_nicio_piesa_nu_iese_din_foaie(seed):
    placed, _ = shelf_pack(piese_aleatoare(30, seed), SHEET_W, SHEET_H)
    for pl in placed:
        assert pl.x >= 0 and pl.y >= 0
        assert pl.x + pl.part.w <= SHEET_W
        assert pl.y + pl.part.h <= SHEET_H


@pytest.mark.parametrize("seed", range(20))
def test_piesele_nu_se_suprapun(seed):
    gap = 2.0
    placed, _ = shelf_pack(piese_aleatoare(30, seed), SHEET_W, SHEET_H, gap)
    for i, a in enumerate(placed):
        for b in placed[i + 1:]:
            assert not se_suprapun(a, b, gap), f"{a.part.name} si {b.part.name}"


def test_nicio_piesa_pierduta():
    parts = piese_aleatoare(40, seed=1)
    placed, skipped = shelf_pack(parts, SHEET_W, SHEET_H)
    assert len(placed) + len(skipped) == len(parts)


def test_piesa_prea_mare_e_sarita():
    placed, skipped = shelf_pack([Part("mare", 2500, 100)], SHEET_W, SHEET_H)
    assert placed == []
    assert [p.name for p in skipped] == ["mare"]


def test_foaie_goala():
    placed, skipped = shelf_pack([], SHEET_W, SHEET_H)
    assert placed == [] and skipped == []
