"""Genereaza imaginea comparativa pentru README: docs/comparison.png"""
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
from matplotlib.patches import Rectangle

from nesting.models import Part
from nesting.packer import shelf_pack
from nesting.maxrects import maxrects_pack

W, H = 2000, 1000
dims = [(400, 300), (600, 200), (300, 300), (500, 450),
        (250, 150), (800, 250), (350, 400)] * 2
parts = [Part(f"P{i}", w, h) for i, (w, h) in enumerate(dims)]

fig, axes = plt.subplots(1, 2, figsize=(16, 4.6))
for ax, (nume, alg) in zip(axes, [("Shelf packing", shelf_pack),
                                   ("MaxRects + 90° rotation", maxrects_pack)]):
    placed, skipped = alg(parts, W, H)
    util = sum(p.w * p.h for p in placed) / (W * H) * 100
    ax.add_patch(Rectangle((0, 0), W, H, fill=False, lw=2))
    for pl in placed:
        ax.add_patch(Rectangle((pl.x, pl.y), pl.w, pl.h, alpha=0.6, ec="black",
                               fc="tab:orange" if pl.rotated else "tab:blue"))
        ax.text(pl.x + pl.w / 2, pl.y + pl.h / 2, pl.part.name,
                ha="center", va="center", fontsize=8)
    ax.set_xlim(0, W); ax.set_ylim(0, H); ax.set_aspect("equal")
    ax.set_title(f"{nume}: {util:.1f}% sheet utilization, {len(skipped)} unplaced")
fig.tight_layout()
fig.savefig("docs/comparison.png", dpi=150)
print("Salvat: docs/comparison.png")
