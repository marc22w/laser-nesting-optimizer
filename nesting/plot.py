import matplotlib.pyplot as plt
from matplotlib.patches import Rectangle


def plot_sheet(placements, sheet_w, sheet_h):
    fig, ax = plt.subplots(figsize=(12, 6))
    ax.add_patch(Rectangle((0, 0), sheet_w, sheet_h, fill=False, lw=2))

    for pl in placements:
        ax.add_patch(Rectangle((pl.x, pl.y), pl.part.w, pl.part.h,
                               alpha=0.5, ec="black"))
        ax.text(pl.x + pl.part.w / 2, pl.y + pl.part.h / 2, pl.part.name,
                ha="center", va="center", fontsize=8)

    ax.set_xlim(0, sheet_w)
    ax.set_ylim(0, sheet_h)
    ax.set_aspect("equal")
    ax.set_title("Nesting - foaie de tabla")
    plt.show()
