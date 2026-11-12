"""Estimarea timpului de taiere: lungimea contururilor si numarul de strapungeri."""
from dataclasses import dataclass

import ezdxf
from ezdxf import path as ezpath

from .import_dxf import GEOMETRIE


@dataclass
class ParametriLaser:
    viteza_mm_min: float = 3000.0  # viteza de taiere
    strapungere_s: float = 0.5     # timpul unei strapungeri (inceputul fiecarui contur)


def _cheie(punct):
    """Punct rotunjit, ca doua capete care se ating sa aiba aceeasi cheie."""
    return (round(punct.x, 2), round(punct.y, 2))


def _lungime(p):
    """Lungimea unui path, aproximata prin puncte foarte dese (eroare < 0.01)."""
    puncte = list(p.flattening(0.01))
    return sum(a.distance(b) for a, b in zip(puncte, puncte[1:]))


def numar_contururi(capete):
    """Numara contururile din perechile (start, end) ale entitatilor.

    O entitate inchisa (cerc, polilinie inchisa) e un contur de sine statator.
    Liniile si arcele care se ating cap la cap formeaza impreuna un singur contur.
    """
    parinte = {}

    def radacina(k):
        parinte.setdefault(k, k)
        while parinte[k] != k:
            parinte[k] = parinte[parinte[k]]
            k = parinte[k]
        return k

    inchise = 0
    for a, b in capete:
        if a == b:
            inchise += 1
        else:
            parinte[radacina(a)] = radacina(b)
    deschise = len({radacina(k) for k in list(parinte)})
    return inchise + deschise


def analiza_piesa(part, cache):
    """Intoarce (lungime_taiere_mm, numar_contururi) pentru o piesa."""
    if not part.source:
        return 2 * (part.w + part.h), 1  # piesa fara DXF: doar dreptunghiul
    if part.source not in cache:
        doc = ezdxf.readfile(part.source)
        lungime, capete = 0.0, []
        for entitate in doc.modelspace().query(GEOMETRIE):
            p = ezpath.make_path(entitate)
            lungime += _lungime(p)
            capete.append((_cheie(p.start), _cheie(p.end)))
        cache[part.source] = (lungime, numar_contururi(capete))
    lungime, contururi = cache[part.source]
    return lungime * part.scale, contururi


def estimare_foaie(placements, parametri=ParametriLaser(), cache=None):
    """Intoarce (lungime_mm, strapungeri, timp_secunde) pentru o foaie."""
    cache = {} if cache is None else cache
    lungime = strapungeri = 0
    for pl in placements:
        l, n = analiza_piesa(pl.part, cache)
        lungime += l
        strapungeri += n
    timp = lungime / (parametri.viteza_mm_min / 60) + strapungeri * parametri.strapungere_s
    return lungime, strapungeri, timp


def format_timp(secunde):
    minute, sec = divmod(round(secunde), 60)
    return f"{minute} min {sec:02d} s"
