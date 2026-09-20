"""Figures for the Wikipedia article "Hypervolume indicator": the 2-D and the 3-D case.

Conventions follow the article: minimisation, an approximation set A = {a^1, ..., a^n},
a reference point r with a_i <= r_i, the boxes [a, r] and

    HV(A; r) = lambda_m ( union_{a in A} [a, r] ).

Writes hypervolume-indicator-2d.{svg,png} and hypervolume-indicator-3d.{svg,png}.
Set PAREN = True for the parenthesised labels a^(i) used in the text of the article.
"""
import os

import matplotlib
matplotlib.use("Agg")
import matplotlib.colors as mcolors
import matplotlib.patheffects as pe
import matplotlib.pyplot as plt
import numpy as np
from matplotlib.patches import FancyArrowPatch, Rectangle
from mpl_toolkits.mplot3d.art3d import Line3DCollection, Poly3DCollection
from mpl_toolkits.mplot3d.proj3d import proj_transform

OUT = os.path.dirname(os.path.abspath(__file__))
PALETTE = ["#4C78A8", "#F58518", "#54A24B", "#B279A2", "#E45756"]
INK = "#1b1f23"
GREY = "#7b8794"
PAREN = True

plt.rcParams.update({"mathtext.fontset": "cm", "font.family": "DejaVu Sans",
                     "font.size": 15, "svg.fonttype": "path"})


def name(i):
    return (r"$a^{(%d)}$" if PAREN else r"$a^{%d}$") % i


def shade(c, f):
    rgb = np.array(mcolors.to_rgb(c))
    return tuple(np.clip(rgb * f if f <= 1 else rgb + (1 - rgb) * (f - 1), 0, 1))


def save(fig, stem):
    for ext in ("svg", "png"):
        fig.savefig(os.path.join(OUT, stem + "." + ext), dpi=250, facecolor="white",
                    bbox_inches="tight", pad_inches=0.06)
    plt.close(fig)
    print("wrote", stem + ".svg/.png")


# ----------------------------------------------------------------------- 2-D
def fig_2d():
    A = np.array([[0.12, 0.90], [0.26, 0.62], [0.45, 0.45], [0.63, 0.26], [0.88, 0.13]])
    r = np.array([1.0, 1.0])
    A = A[np.argsort(A[:, 0])]
    xs = np.append(A[:, 0], r[0])

    fig, ax = plt.subplots(figsize=(6.6, 6.4))
    # staircase boundary of the dominated region, and the region itself as one polygon
    px, py = [A[0, 0]], [r[1]]
    for i, a in enumerate(A):
        px += [a[0], xs[i + 1]]
        py += [a[1], a[1]]
    ax.fill(px + [r[0]], py + [r[1]], facecolor=shade(PALETTE[0], 1.62), edgecolor="none",
            zorder=1)
    ax.plot(px, py, color=INK, lw=2.0, solid_joinstyle="miter", zorder=3)
    ax.plot([r[0], r[0], A[0, 0]], [A[-1, 1], r[1], r[1]], color=GREY, lw=1.2,
            ls=(0, (5, 4)), zorder=3)
    # points and reference point
    for i, a in enumerate(A):
        ax.plot(a[0], a[1], "o", ms=8.5, mfc=INK, mec="white", mew=1.0, zorder=4)
        if i == 0:      # straight below, so that the label keeps clear of the f_2 axis
            ax.text(a[0], a[1] - 0.05, name(i + 1), ha="center", va="top", color=INK)
        else:
            ax.text(a[0] - 0.035, a[1] - 0.04, name(i + 1), ha="right", va="top", color=INK)
    ax.plot(r[0], r[1], "s", ms=8.5, mfc="white", mec=INK, mew=1.5, zorder=4)
    ax.text(r[0] + 0.035, r[1] + 0.015, r"$r$", ha="left", va="bottom", color=INK)
    ax.text(0.73, 0.83, r"$\mathrm{HV}(A;r)$", ha="center", va="center", color=INK, zorder=4)

    ax.annotate("", xy=(1.28, 0), xytext=(0, 0),
                arrowprops=dict(arrowstyle="-|>", color=INK, lw=1.5, shrinkA=0, shrinkB=0))
    ax.annotate("", xy=(0, 1.28), xytext=(0, 0),
                arrowprops=dict(arrowstyle="-|>", color=INK, lw=1.5, shrinkA=0, shrinkB=0))
    ax.text(1.30, -0.015, r"$f_1$", ha="left", va="top", color=INK)
    ax.text(-0.015, 1.30, r"$f_2$", ha="right", va="bottom", color=INK)
    ax.set_xlim(-0.10, 1.40)
    ax.set_ylim(-0.10, 1.40)
    ax.set_aspect("equal")
    ax.axis("off")
    save(fig, "hypervolume-indicator-2d")


# ----------------------------------------------------------------------- 3-D
class Arrow3D(FancyArrowPatch):
    def __init__(self, xs, ys, zs, **kw):
        super().__init__((0, 0), (0, 0), **kw)
        self._xyz = (xs, ys, zs)

    def do_3d_projection(self, renderer=None):
        xs, ys, zs = proj_transform(*self._xyz, self.axes.M)
        self.set_positions((xs[0], ys[0]), (xs[1], ys[1]))
        return float(np.min(zs))


def fig_3d():
    A = np.array([[0.15, 0.55, 0.78], [0.45, 0.20, 0.60], [0.66, 0.72, 0.26],
                  [0.30, 0.86, 0.45]])
    r = np.array([1.0, 1.0, 1.0])
    elev, azim = -20.0, -128.0
    xs = np.append(np.sort(A[:, 0]), r[0])
    ys = np.append(np.sort(A[:, 1]), r[1])
    nx, ny = len(xs) - 1, len(ys) - 1
    Z = np.full((nx, ny), np.inf)
    own = np.full((nx, ny), -1)
    for i in range(nx):
        for j in range(ny):
            for q, a in enumerate(A):
                if a[0] <= xs[i] + 1e-12 and a[1] <= ys[j] + 1e-12 and a[2] < Z[i, j]:
                    Z[i, j], own[i, j] = a[2], q

    polys, cols, segs = [], [], []
    for i in range(nx):
        for j in range(ny):
            q = own[i, j]
            if q < 0:
                continue
            c = PALETTE[q]
            x0, x1, y0, y1, z = xs[i], xs[i + 1], ys[j], ys[j + 1], Z[i, j]
            polys.append([(x0, y0, z), (x1, y0, z), (x1, y1, z), (x0, y1, z)])   # floor
            cols.append(shade(c, 1.45))
            zp = r[2] if i == 0 else min(Z[i - 1, j], r[2])                      # wall facing -f1
            if z < zp - 1e-12:
                polys.append([(x0, y0, z), (x0, y1, z), (x0, y1, zp), (x0, y0, zp)])
                cols.append(shade(c, 1.08))
                segs += [[(x0, y0, z), (x0, y1, z)], [(x0, y0, zp), (x0, y1, zp)],
                         [(x0, y0, z), (x0, y0, zp)], [(x0, y1, z), (x0, y1, zp)]]
            zp = r[2] if j == 0 else min(Z[i, j - 1], r[2])                      # wall facing -f2
            if z < zp - 1e-12:
                polys.append([(x0, y0, z), (x1, y0, z), (x1, y0, zp), (x0, y0, zp)])
                cols.append(shade(c, 0.80))
                segs += [[(x0, y0, z), (x1, y0, z)], [(x0, y0, zp), (x1, y0, zp)],
                         [(x0, y0, z), (x0, y0, zp)], [(x1, y0, z), (x1, y0, zp)]]
            if i == nx - 1:
                segs.append([(x1, y0, z), (x1, y1, z)])
            if j == ny - 1:
                segs.append([(x0, y1, z), (x1, y1, z)])

    def key(s):
        return tuple(sorted(tuple(round(v, 9) for v in p) for p in s))

    keys = [key(s) for s in segs]
    once = [s for s, k in zip(segs, keys) if keys.count(k) == 1]   # drop internal grid seams
    # the two edges of the ceiling z = r_3 that meet at r are hidden behind the solid: dashed
    hidden = [[(r[0], ys[0], r[2]), (r[0], r[1], r[2])],
              [(xs[0], r[1], r[2]), (r[0], r[1], r[2])],
              [(r[0], r[1], Z[nx - 1, ny - 1]), (r[0], r[1], r[2])]]

    fig = plt.figure(figsize=(6.8, 6.0))
    ax = fig.add_subplot(111, projection="3d", computed_zorder=False)
    ax.set_proj_type("ortho")
    ax.add_collection3d(Poly3DCollection(polys, facecolors=cols, edgecolors=cols,
                                         linewidths=0.4, zorder=1))
    ax.add_collection3d(Line3DCollection(once, colors=INK, linewidths=1.0, zorder=2))
    ax.add_collection3d(Line3DCollection(hidden, colors=GREY, linewidths=0.9, zorder=3,
                                         linestyles=(0, (4, 4))))
    for q, a in enumerate(A):
        ax.plot([a[0]], [a[1]], [a[2]], "o", ms=8.5, mfc=INK, mec="white", mew=1.0,
                zorder=4)
    # label offsets, chosen so that every label sits on the face its point owns
    offs = [(0.05, 0.26, -0.02, "center"), (0.00, -0.03, -0.09, "top"),
            (0.03, 0.00, -0.09, "top"), (-0.02, 0.00, -0.09, "top")]
    for q, (a, (dx, dy, dz, va)) in enumerate(zip(A, offs)):
        ax.text(a[0] + dx, a[1] + dy, a[2] + dz, name(q + 1), ha="center", va=va,
                color=INK, zorder=5)
    # the reference point is the far corner of the solid (the dashed edges meet there)
    ax.plot([r[0]], [r[1]], [r[2]], "s", ms=8.5, mfc="white", mec=INK, mew=1.5, zorder=4)
    ax.text(r[0] + 0.02, r[1] - 0.06, r[2] + 0.05, r"$r$", ha="left", va="bottom", color=INK,
            zorder=5, path_effects=[pe.withStroke(linewidth=2.5, foreground="white")])
    ax.text2D(0.03, 0.95, r"$\mathrm{HV}(A;r)$", transform=ax.transAxes, color=INK, zorder=5)

    ax.set_xlim(0.10, 1.05)
    ax.set_ylim(0.10, 1.05)
    ax.set_zlim(0.10, 1.05)
    ax.set_box_aspect((1, 1, 1))
    ax.view_init(elev=elev, azim=azim)
    ax.set_axis_off()

    # orientation triad (the origin itself plays no role in the definition of HV)
    gx = fig.add_axes([0.05, 0.035, 0.22, 0.22], projection="3d")
    gx.set_proj_type("ortho")
    for v, lab in [((1, 0, 0), r"$f_1$"), ((0, 1, 0), r"$f_2$"), ((0, 0, 1), r"$f_3$")]:
        gx.add_artist(Arrow3D([0, v[0]], [0, v[1]], [0, v[2]], arrowstyle="-|>",
                              mutation_scale=12, lw=1.4, color=INK))
        gx.text(v[0] * 1.30, v[1] * 1.30, v[2] * 1.28, lab, ha="center", va="center", color=INK)
    gx.set_xlim(-0.15, 1.15)
    gx.set_ylim(-0.15, 1.15)
    gx.set_zlim(-0.15, 1.15)
    gx.set_box_aspect((1, 1, 1))
    gx.view_init(elev=elev, azim=azim)
    gx.set_axis_off()
    gx.patch.set_alpha(0.0)
    save(fig, "hypervolume-indicator-3d")


if __name__ == "__main__":
    fig_2d()
    fig_3d()
