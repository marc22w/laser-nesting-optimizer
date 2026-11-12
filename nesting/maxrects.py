"""MaxRects: tine evidenta tuturor dreptunghiurilor libere de pe foaie.

Pentru fiecare piesa (si varianta ei rotita cu 90 de grade) se cauta spatiul
liber in care se potriveste cel mai strans (Best Short Side Fit).
"""
from .models import Placement


def _imparte(liber, ocupat):
    """Taie dreptunghiul `ocupat` din `liber`; intoarce bucatile ramase."""
    fx, fy, fw, fh = liber
    ox, oy, ow, oh = ocupat
    if ox >= fx + fw or ox + ow <= fx or oy >= fy + fh or oy + oh <= fy:
        return [liber]  # nu se ating
    bucati = []
    if ox > fx:
        bucati.append((fx, fy, ox - fx, fh))                      # stanga
    if ox + ow < fx + fw:
        bucati.append((ox + ow, fy, fx + fw - ox - ow, fh))       # dreapta
    if oy > fy:
        bucati.append((fx, fy, fw, oy - fy))                      # jos
    if oy + oh < fy + fh:
        bucati.append((fx, oy + oh, fw, fy + fh - oy - oh))       # sus
    return bucati


def _contine(a, b):
    """True daca dreptunghiul a e complet in interiorul lui b."""
    return (a[0] >= b[0] and a[1] >= b[1] and
            a[0] + a[2] <= b[0] + b[2] and a[1] + a[3] <= b[1] + b[3])


def _curata(libere):
    """Scoate dreptunghiurile libere continute in altele (sunt redundante)."""
    rezultat = []
    for i, a in enumerate(libere):
        redundant = any(
            j != i and _contine(a, b) and (a != b or j < i)
            for j, b in enumerate(libere)
        )
        if not redundant:
            rezultat.append(a)
    return rezultat


def maxrects_pack(parts, sheet_w, sheet_h, gap=2.0, allow_rotation=True):
    # Truc pentru gap: fiecare piesa "ocupa" w+gap x h+gap, iar foaia e marita
    # cu gap. Asa intre doua piese ramane mereu cel putin gap.
    libere = [(0.0, 0.0, sheet_w + gap, sheet_h + gap)]
    placed, skipped = [], []

    # piesele mari intai: e mai usor sa strecori piesele mici la final
    for p in sorted(parts, key=lambda p: p.w * p.h, reverse=True):
        variante = [(p.w, p.h, False)]
        if allow_rotation and p.w != p.h:
            variante.append((p.h, p.w, True))

        cea_mai_buna = None  # (scor, x, y, rotita)
        for w, h, rot in variante:
            W, H = w + gap, h + gap
            for fx, fy, fw, fh in libere:
                if W <= fw and H <= fh:
                    scor = (min(fw - W, fh - H), max(fw - W, fh - H))
                    if cea_mai_buna is None or scor < cea_mai_buna[0]:
                        cea_mai_buna = (scor, fx, fy, rot)

        if cea_mai_buna is None:
            skipped.append(p)
            continue

        _, x, y, rot = cea_mai_buna
        pl = Placement(p, x, y, rot)
        placed.append(pl)

        ocupat = (x, y, pl.w + gap, pl.h + gap)
        noi = []
        for liber in libere:
            noi.extend(_imparte(liber, ocupat))
        libere = _curata(noi)

    return placed, skipped
