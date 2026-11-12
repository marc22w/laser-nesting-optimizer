"""Ordinea de taiere, ca la un CAM pentru laser.

Reguli:
  1. In fiecare piesa se taie intai contururile interioare (gaurile), apoi conturul
     exterior. Daca s-ar taia intai exteriorul, piesa s-ar putea misca sau cadea,
     iar gaurile ar iesi deplasate.
  2. Piesele si gaurile sunt luate in ordinea "cel mai apropiat urmator"
     (nearest neighbour), ca deplasarile in gol ale capului laser sa fie scurte.
"""
import math
from dataclasses import dataclass


@dataclass
class Contur:
    elemente: list   # ce formeaza conturul (entitati DXF sau orice alt obiect)
    start: tuple     # punctul de intrare (x, y)
    bbox: tuple      # (xmin, ymin, xmax, ymax)

    @property
    def arie_bbox(self):
        xmin, ymin, xmax, ymax = self.bbox
        return (xmax - xmin) * (ymax - ymin)


def _dist(a, b):
    return math.hypot(a[0] - b[0], a[1] - b[1])


def _cheie(punct):
    return (round(punct[0], 2), round(punct[1], 2))


def _uneste_bbox(a, b):
    return (min(a[0], b[0]), min(a[1], b[1]), max(a[2], b[2]), max(a[3], b[3]))


def grupeaza(segmente):
    """Grupeaza segmentele in contururi.

    segmente: lista de (element, start, end, bbox).
    Un segment inchis (start == end, ex. cerc) e un contur de sine statator.
    Segmentele care se ating cap la cap (linii + arce) formeaza un singur contur.
    """
    n = len(segmente)
    parinte = list(range(n))

    def radacina(i):
        while parinte[i] != i:
            parinte[i] = parinte[parinte[i]]
            i = parinte[i]
        return i

    primul_la_punct = {}
    for i, (_, start, end, _) in enumerate(segmente):
        if _cheie(start) == _cheie(end):
            continue  # contur inchis singur
        for punct in (start, end):
            k = _cheie(punct)
            if k in primul_la_punct:
                parinte[radacina(i)] = radacina(primul_la_punct[k])
            else:
                primul_la_punct[k] = i

    grupuri = {}
    for i in range(n):
        grupuri.setdefault(radacina(i), []).append(i)

    contururi = []
    for indici in sorted(grupuri.values()):
        element, start, _, bbox = segmente[indici[0]]
        elemente = [element]
        for i in indici[1:]:
            elemente.append(segmente[i][0])
            bbox = _uneste_bbox(bbox, segmente[i][3])
        contururi.append(Contur(elemente, tuple(start[:2]), bbox))
    return contururi


def _cel_mai_apropiat(pozitie, contururi):
    return min(contururi, key=lambda c: _dist(pozitie, c.start))


def ordine_taiere(piese, start=(0.0, 0.0)):
    """piese: lista; fiecare piesa e lista ei de Contur.

    Intoarce (contururi_in_ordinea_de_taiere, distanta_deplasare_in_gol_mm).
    """
    pozitie, distanta, ordine = start, 0.0, []
    ramase = list(range(len(piese)))
    while ramase:
        # urmatoarea piesa: cea care are un contur cel mai aproape de cap
        idx = min(ramase, key=lambda k: min(_dist(pozitie, c.start) for c in piese[k]))
        ramase.remove(idx)

        contururi = piese[idx]
        exterior = max(contururi, key=lambda c: c.arie_bbox)
        interioare = [c for c in contururi if c is not exterior]

        while interioare:                       # intai gaurile, cea mai apropiata
            c = _cel_mai_apropiat(pozitie, interioare)
            interioare.remove(c)
            distanta += _dist(pozitie, c.start)
            pozitie = c.start
            ordine.append(c)

        distanta += _dist(pozitie, exterior.start)   # la final conturul exterior
        pozitie = exterior.start
        ordine.append(exterior)

    return ordine, distanta


def distanta_naiva(piese, start=(0.0, 0.0)):
    """Deplasarea in gol daca taiem in ordinea din fisier (fara optimizare)."""
    pozitie, distanta = start, 0.0
    for contururi in piese:
        for c in contururi:
            distanta += _dist(pozitie, c.start)
            pozitie = c.start
    return distanta
