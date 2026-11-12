import math
import random

from nesting.cut_order import (Contur, distanta_naiva, grupeaza, ordine_taiere)


def cerc(nume, cx, cy, r):
    """Segment inchis: start == end."""
    return (nume, (cx + r, cy), (cx + r, cy), (cx - r, cy - r, cx + r, cy + r))


def linie(nume, a, b):
    return (nume, a, b, (min(a[0], b[0]), min(a[1], b[1]),
                         max(a[0], b[0]), max(a[1], b[1])))


def placa(x, y, w=300, h=200, gauri=((50, 50),)):
    """O piesa: contur exterior din 4 linii + gauri rotunde R5."""
    p = [(x, y), (x + w, y), (x + w, y + h), (x, y + h)]
    segmente = [linie(f"L{i}", p[i], p[(i + 1) % 4]) for i in range(4)]
    segmente += [cerc(f"G{i}", x + gx, y + gy, 5) for i, (gx, gy) in enumerate(gauri)]
    return grupeaza(segmente)


def test_liniile_care_se_ating_formeaza_un_contur():
    contururi = placa(0, 0, gauri=())
    assert len(contururi) == 1
    assert sorted(contururi[0].elemente) == ["L0", "L1", "L2", "L3"]
    assert contururi[0].bbox == (0, 0, 300, 200)


def test_cercurile_sunt_contururi_separate():
    contururi = placa(0, 0, gauri=((50, 50), (100, 50), (150, 50)))
    assert len(contururi) == 4


def test_gaurile_se_taie_inaintea_exteriorului():
    piese = [placa(0, 0, gauri=((50, 50), (250, 150))),
             placa(400, 0, gauri=((100, 100),))]
    ordine, _ = ordine_taiere(piese)
    # pentru fiecare piesa, exteriorul (contur cu 4 linii) vine dupa gaurile ei
    pozitii_exterior = [i for i, c in enumerate(ordine) if len(c.elemente) == 4]
    assert len(pozitii_exterior) == 2
    assert pozitii_exterior[0] == 2      # 2 gauri, apoi exteriorul piesei 1
    assert pozitii_exterior[1] == 4      # 1 gaura, apoi exteriorul piesei 2


def test_fiecare_contur_e_taiat_o_singura_data():
    piese = [placa(x, y, gauri=((50, 50), (150, 100)))
             for x in (0, 400, 800) for y in (0, 300)]
    ordine, _ = ordine_taiere(piese)
    total = sum(len(p) for p in piese)
    assert len(ordine) == total
    assert len({id(c) for c in ordine}) == total


def test_optimizarea_scurteaza_deplasarea():
    # piese asezate intr-o ordine haotica: optimizarea trebuie sa ajute
    rnd = random.Random(3)
    pozitii = [(x, y) for x in range(0, 1800, 350) for y in range(0, 800, 250)]
    rnd.shuffle(pozitii)
    piese = [placa(x, y, w=300, h=200, gauri=((60, 60), (240, 140)))
             for x, y in pozitii]
    _, optim = ordine_taiere(piese)
    assert optim < 0.8 * distanta_naiva(piese)


def test_distanta_simpla():
    piese = [[Contur(["a"], (3, 4), (3, 4, 3, 4))]]
    _, d = ordine_taiere(piese)
    assert math.isclose(d, 5)          # de la (0,0) la (3,4)
    assert math.isclose(distanta_naiva(piese), 5)
