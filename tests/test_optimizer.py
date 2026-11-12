import random

import pytest

from nesting.models import Part
from nesting.maxrects import SORTARI, REGULI, maxrects_pack
from nesting.multisheet import nest_multi
from nesting.optimizer import nest_optim

SHEET_W, SHEET_H = 2000, 1000


def piese_aleatoare(n, seed):
    rnd = random.Random(seed)
    return [Part(f"P{i}", rnd.randint(50, 900), rnd.randint(50, 600))
            for i in range(n)]


def se_suprapun(a, b, gap):
    eps = 1e-9
    return not (a.x + a.w + gap <= b.x + eps or b.x + b.w + gap <= a.x + eps or
                a.y + a.h + gap <= b.y + eps or b.y + b.h + gap <= a.y + eps)


@pytest.mark.parametrize("sortare", list(SORTARI))
@pytest.mark.parametrize("regula", REGULI)
def test_fiecare_strategie_e_valida(sortare, regula):
    gap = 2.0
    placed, skipped = maxrects_pack(piese_aleatoare(40, 7), SHEET_W, SHEET_H,
                                    gap, sortare=sortare, regula=regula)
    assert len(placed) + len(skipped) == 40
    for pl in placed:
        assert 0 <= pl.x and pl.x + pl.w <= SHEET_W
        assert 0 <= pl.y and pl.y + pl.h <= SHEET_H
    for i, a in enumerate(placed):
        for b in placed[i + 1:]:
            assert not se_suprapun(a, b, gap)


@pytest.mark.parametrize("seed", range(10))
def test_optim_nu_e_mai_slab_decat_varianta_implicita(seed):
    parts = piese_aleatoare(60, seed)
    foi_impl, _ = nest_multi(parts, SHEET_W, SHEET_H, maxrects_pack)
    foi_opt, imposibile, _ = nest_optim(parts, SHEET_W, SHEET_H)
    assert imposibile == []
    assert len(foi_opt) <= len(foi_impl)


@pytest.mark.parametrize("seed", range(5))
def test_optim_plaseaza_toate_piesele_o_data(seed):
    parts = piese_aleatoare(60, seed)
    foi, _, strategie = nest_optim(parts, SHEET_W, SHEET_H)
    nume = sorted(pl.part.name for foaie in foi for pl in foaie)
    assert nume == sorted(p.name for p in parts)
    assert strategie[0] in SORTARI and strategie[1] in REGULI


def test_regula_necunoscuta():
    with pytest.raises(ValueError):
        maxrects_pack([Part("A", 10, 10)], SHEET_W, SHEET_H, regula="xyz")
