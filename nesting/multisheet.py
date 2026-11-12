"""Nesting pe mai multe foi: cand o foaie se umple, piesele ramase trec pe una noua."""
from .maxrects import maxrects_pack


def nest_multi(parts, sheet_w, sheet_h, algoritm=maxrects_pack, gap=2.0):
    """Intoarce (foi, imposibile).

    foi        - lista de foi; fiecare foaie e o lista de Placement
    imposibile - piesele care nu incap nici pe o foaie goala
    """
    foi, imposibile = [], []
    ramase = list(parts)

    while ramase:
        placed, skipped = algoritm(ramase, sheet_w, sheet_h, gap)
        if not placed:
            # nicio piesa nu mai incape nici pe o foaie goala -> ne oprim
            imposibile.extend(skipped)
            break
        foi.append(placed)
        ramase = skipped

    return foi, imposibile


def utilizare(placed, sheet_w, sheet_h):
    """Procentul din foaie acoperit de piese."""
    return sum(p.w * p.h for p in placed) / (sheet_w * sheet_h) * 100
