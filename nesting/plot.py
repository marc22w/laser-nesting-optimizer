import matplotlib.pyplot as plt
from matplotlib.patches import Rectangle


def plot_sheet(placements, sheet_w, sheet_h, title="Nesting"):
    fig, ax = plt.subplots(figsize=(12, 6))
    ax.add_patch(Rectangle((0, 0), sheet_w, sheet_h, fill=False, lw=2))

    for pl in placements:
        culoare = "tab:orange" if pl.rotated else "tab:blue"
        ax.add_patch(Rectangle((pl.x, pl.y), pl.w, pl.h,
                               alpha=0.5, ec="black", fc=culoare))
        eticheta = pl.part.name + (" (R)" if pl.rotated else "")
        ax.text(pl.x + pl.w / 2, pl.y + pl.h / 2, eticheta,
                ha="center", va="center", fontsize=8)

    ax.set_xlim(0, sheet_w)
    ax.set_ylim(0, sheet_h)
    ax.set_aspect("equal")
    ax.set_title(title)
    return fig
