from .models import Part, Placement


def shelf_pack(parts, sheet_w, sheet_h, gap=2.0):
    """Aranjeaza piesele pe randuri (rafturi), de la stanga la dreapta."""
    parts = sorted(parts, key=lambda p: p.h, reverse=True)
    placed, skipped = [], []
    x = y = shelf_h = 0.0

    for p in parts:
        if p.w > sheet_w:
            skipped.append(p)
            continue
        if x + p.w > sheet_w:          
            x, y = 0.0, y + shelf_h + gap
            shelf_h = 0.0
        if y + p.h > sheet_h:          
            skipped.append(p)
            continue
        placed.append(Placement(p, x, y))
        x += p.w + gap
        shelf_h = max(shelf_h, p.h)

    return placed, skipped
