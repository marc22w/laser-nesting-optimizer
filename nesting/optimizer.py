"""Incearca toate combinatiile sortare x regula si pastreaza cel mai bun rezultat."""
from functools import partial

from .maxrects import SORTARI, REGULI, maxrects_pack
from .multisheet import nest_multi


def _scor(foi, imposibile):
    """Mai mic = mai bun: cat mai multe piese plasate, cat mai putine foi,
    iar la egalitate cat mai putin material pe ultima foaie (resturi mai mari)."""
    arie_ultima = sum(p.w * p.h for p in foi[-1]) if foi else 0
    return (len(imposibile), len(foi), arie_ultima)


def nest_optim(parts, sheet_w, sheet_h, gap=2.0):
    """Intoarce (foi, imposibile, strategie), unde strategie = (sortare, regula)."""
    cel_mai_bun = None
    for sortare in SORTARI:
        for regula in REGULI:
            algoritm = partial(maxrects_pack, sortare=sortare, regula=regula)
            foi, imposibile = nest_multi(parts, sheet_w, sheet_h, algoritm, gap)
            scor = _scor(foi, imposibile)
            if cel_mai_bun is None or scor < cel_mai_bun[0]:
                cel_mai_bun = (scor, foi, imposibile, (sortare, regula))
    _, foi, imposibile, strategie = cel_mai_bun
    return foi, imposibile, strategie
