"""Figures for the Wikipedia article "Hypervolume indicator": the 2-D and the 3-D case.

Conventions follow the article: minimisation, an approximation set A = {a^1, ..., a^n},
a reference point r with a_i <= r_i, the boxes [a, r] and

    HV(A; r) = lambda_m ( union_{a in A} [a, r] ).

Writes hypervolume-indicator-2d.{svg,png} and hypervolume-indicator-3d.{svg,png}.
Set PAREN = False for the plain labels a^i instead of a^(i).

Note on the 3-D view.  For a minimisation problem the dominated region hangs from the
reference point, so its staircase-shaped boundary faces the origin and can only be seen
from a viewpoint below the region (elev < 0).  The faces are therefore shaded the way a
light at the camera illuminates them (Lambert, headlight): the undersides, which are the
faces most oblique to the viewer, are darkest, and the walls facing -f2 are brightest.
The axis triad is drawn *inside* the same 3-D axes, so its arrows are projected with
exactly the same matrix as the boxes and are parallel to their edges by construction.
"""
import os
import re

import matplotlib
matplotlib.use("Agg")
import matplotlib.colors as mcolors
import matplotlib.patheffects as pe
import matplotlib.pyplot as plt
import numpy as np
from matplotlib.lines import Line2D
from matplotlib.patches import FancyArrowPatch
from mpl_toolkits.mplot3d.art3d import Line3DCollection, Poly3DCollection
from mpl_toolkits.mplot3d.proj3d import proj_transform

OUT = os.path.dirname(os.path.abspath(__file__))
PALETTE = ["#4C78A8", "#F58518", "#54A24B", "#B279A2", "#E45756"]
INK = "#1b1f23"
GREY = "#7b8794"
RED = "#D62728"          # the reference point
DROP = "#9aa5b1"         # projection lines
PAREN = True

plt.rcParams.update({"mathtext.fontset": "cm", "font.family": "DejaVu Sans",
                     "font.size": 15, "svg.fonttype": "path"})


def name(i):
    return (r"$a^{(%d)}$" if PAREN else r"$a^{%d}$") % i


def shade(c, f):
    rgb = np.array(mcolors.to_rgb(c))
    return tuple(np.clip(rgb * f if f <= 1 else rgb + (1 - rgb) * (f - 1), 0, 1))


def save(fig, stem, margin=0.015):
    """Write SVG and PNG and trim both to the drawn content.

    A 3-D axes reserves the projection of the whole data cube, whose corners stay empty
    here, and bbox_inches="tight" keeps that box.  The PNG is therefore trimmed to its
    non-white pixels and the same relative crop is applied to the viewBox of the SVG."""
    png, svg = (os.path.join(OUT, stem + e) for e in (".png", ".svg"))
    fig.savefig(png, dpi=250, facecolor="white", bbox_inches="tight", pad_inches=0.06)
    fig.savefig(svg, facecolor="white", bbox_inches="tight", pad_inches=0.06)
    plt.close(fig)

    from PIL import Image
    im = Image.open(png).convert("RGB")
    W, H = im.size
    ink = np.asarray(im).min(axis=2) < 250
    rows, colsx = np.where(ink)
    if len(rows) == 0:
        return
    pad = int(margin * max(W, H))
    x0, x1 = max(0, colsx.min() - pad), min(W, colsx.max() + 1 + pad)
    y0, y1 = max(0, rows.min() - pad), min(H, rows.max() + 1 + pad)
    im.crop((x0, y0, x1, y1)).save(png)

    text = open(svg, encoding="utf-8").read()
    m = re.search(r'viewBox="0 0 ([0-9.]+) ([0-9.]+)"', text)
    vw, vh = float(m.group(1)), float(m.group(2))
    box = (vw * x0 / W, vh * y0 / H, vw * (x1 - x0) / W, vh * (y1 - y0) / H)
    text = text.replace(m.group(0), 'viewBox="%.3f %.3f %.3f %.3f"' % box)
    text = re.sub(r'width="[0-9.]+pt"', 'width="%.3fpt"' % box[2], text, count=1)
    text = re.sub(r'height="[0-9.]+pt"', 'height="%.3fpt"' % box[3], text, count=1)
    open(svg, "w", encoding="utf-8").write(text)
    print("wrote", stem + ".svg/.png", "%dx%d px" % (x1 - x0, y1 - y0))


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
    ax.plot(r[0], r[1], "s", ms=8.5, mfc=RED, mec=INK, mew=1.0, zorder=4)
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


def staircase(P2, r2):
    """Boundary polygon of the union of the rectangles [p, r2], p in P2 (2-D)."""
    keep, best = [], np.inf
    for p in P2[np.argsort(P2[:, 0])]:
        if p[1] < best - 1e-12:                     # only non-dominated points matter
            keep.append(p)
            best = p[1]
    Q = np.array(keep)
    xs = np.append(Q[:, 0], r2[0])
    px, py = [Q[0, 0]], [r2[1]]
    for i, p in enumerate(Q):
        px += [p[0], xs[i + 1]]
        py += [p[1], p[1]]
    return np.array(px + [r2[0]]), np.array(py + [r2[1]])


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
    A = np.array([[0.15, 0.55, 0.78], [0.52, 0.20, 0.55], [0.66, 0.72, 0.26],
                  [0.30, 0.86, 0.45]])
    r = np.array([1.0, 1.0, 1.0])
    elev, azim = -20.0, -128.0
    EPS = 1e-12
    # the union of the boxes is a height field over the grid of the point coordinates:
    # over cell (i, j) it reaches from the floor Z[i,j] up to r_3
    xs = np.append(np.sort(A[:, 0]), r[0])
    ys = np.append(np.sort(A[:, 1]), r[1])
    nx, ny = len(xs) - 1, len(ys) - 1
    Z = np.full((nx, ny), np.inf)
    own = np.full((nx, ny), -1)
    for i in range(nx):
        for j in range(ny):
            for q, a in enumerate(A):
                if a[0] <= xs[i] + EPS and a[1] <= ys[j] + EPS and a[2] < Z[i, j]:
                    Z[i, j], own[i, j] = a[2], q

    def wall_x(i, j):
        """z-interval of the wall of cell (i,j) in the plane x = xs[i] (it faces -f1)."""
        if not (0 <= i < nx and 0 <= j < ny) or own[i, j] < 0:
            return None
        top = r[2] if i == 0 else min(Z[i - 1, j], r[2])
        return (Z[i, j], top) if Z[i, j] < top - EPS else None

    def wall_y(i, j):
        """z-interval of the wall of cell (i,j) in the plane y = ys[j] (it faces -f2)."""
        if not (0 <= i < nx and 0 <= j < ny) or own[i, j] < 0:
            return None
        top = r[2] if j == 0 else min(Z[i, j - 1], r[2])
        return (Z[i, j], top) if Z[i, j] < top - EPS else None

    # Lambert shading for a light at the camera: brightness ~ |n . view|, so the
    # undersides (n = -e3) are darkest and the walls facing -f2 are brightest
    SH_FLOOR, SH_WALL_X, SH_WALL_Y = 0.92, 1.16, 1.40

    polys, cols, segs = [], [], []
    for i in range(nx):
        for j in range(ny):
            q = own[i, j]
            if q < 0:
                continue
            c = PALETTE[q]
            x0, x1, y0, y1, z = xs[i], xs[i + 1], ys[j], ys[j + 1], Z[i, j]
            polys.append([(x0, y0, z), (x1, y0, z), (x1, y1, z), (x0, y1, z)])
            cols.append(shade(c, SH_FLOOR))
            iv = wall_x(i, j)
            if iv:
                polys.append([(x0, y0, iv[0]), (x0, y1, iv[0]), (x0, y1, iv[1]), (x0, y0, iv[1])])
                cols.append(shade(c, SH_WALL_X))
                segs += [[(x0, y0, iv[0]), (x0, y1, iv[0])], [(x0, y0, iv[1]), (x0, y1, iv[1])]]
            iv = wall_y(i, j)
            if iv:
                polys.append([(x0, y0, iv[0]), (x1, y0, iv[0]), (x1, y0, iv[1]), (x0, y0, iv[1])])
                cols.append(shade(c, SH_WALL_Y))
                segs += [[(x0, y0, iv[0]), (x1, y0, iv[0])], [(x0, y0, iv[1]), (x1, y0, iv[1])]]
            if i == nx - 1:                       # silhouette of the floor at f_1 = r_1
                segs.append([(x1, y0, z), (x1, y1, z)])
            if j == ny - 1:                       # silhouette of the floor at f_2 = r_2
                segs.append([(x0, y1, z), (x1, y1, z)])

    def crease(a, b):
        """Where two coplanar neighbouring walls do not cover the same z-interval, and
        only there, the shared vertical line is a real edge of the solid."""
        if a is None or b is None:
            return [x for x in (a, b) if x is not None]
        out = [(min(a[0], b[0]), max(a[0], b[0])), (min(a[1], b[1]), max(a[1], b[1]))]
        return [(lo, hi) for lo, hi in out if hi - lo > EPS]

    for i in range(nx):                            # vertical edges of the walls x = xs[i]
        for b in range(ny + 1):
            for lo, hi in crease(wall_x(i, b - 1), wall_x(i, b)):
                segs.append([(xs[i], ys[b], lo), (xs[i], ys[b], hi)])
    for j in range(ny):                            # vertical edges of the walls y = ys[j]
        for b in range(nx + 1):
            for lo, hi in crease(wall_y(b - 1, j), wall_y(b, j)):
                segs.append([(xs[b], ys[j], lo), (xs[b], ys[j], hi)])

    # the three edges of the solid that meet at r run behind it: dashed, as hidden edges
    hidden = [[(r[0], ys[0], r[2]), (r[0], r[1], r[2])],
              [(xs[0], r[1], r[2]), (r[0], r[1], r[2])],
              [(r[0], r[1], Z[nx - 1, ny - 1]), (r[0], r[1], r[2])]]

    fig = plt.figure(figsize=(7.6, 5.9))
    ax = fig.add_subplot(111, projection="3d", computed_zorder=False)
    ax.set_proj_type("ortho")

    # projections of the points and of the dominated region onto the coordinate planes
    # f1-f2 (at f3 = 0) and f2-f3 (at f1 = 0): the same construction one dimension lower,
    # which makes the dominance relations easy to check
    dark = [shade(c, 0.55) for c in PALETTE]
    fill, edge = "#edf0f3", "#b7c0c9"      # neutral, so that no box colour is echoed
    for cols2, r2, lift in ((( 0, 1), (r[0], r[1]), lambda u, v: (u, v, 0.0)),
                            (( 1, 2), (r[1], r[2]), lambda u, v: (0.0, u, v))):
        px, py = staircase(A[:, cols2], r2)
        poly = [lift(u, v) for u, v in zip(px, py)]
        ax.add_collection3d(Poly3DCollection([poly], facecolors=[fill], edgecolors="none",
                                             zorder=0))
        ring = [[poly[k], poly[(k + 1) % len(poly)]] for k in range(len(poly))]
        ax.add_collection3d(Line3DCollection(ring, colors=edge, linewidths=1.0,
                                             linestyles=(0, (4, 3)), zorder=0.4))
        for q, a in enumerate(A):
            f = lift(a[cols2[0]], a[cols2[1]])
            ax.plot([f[0]], [f[1]], [f[2]], "o", ms=5.5, mfc=dark[q], mec="none",
                    zorder=0.6)
            ax.plot([a[0], f[0]], [a[1], f[1]], [a[2], f[2]], ls=(0, (4, 3)), lw=0.9,
                    color=DROP, zorder=3.6)   # in front: the planes are nearer than the solid

    ax.add_collection3d(Poly3DCollection(polys, facecolors=cols, edgecolors=cols,
                                         linewidths=0.4, zorder=1))
    ax.add_collection3d(Line3DCollection(segs, colors=INK, linewidths=1.0, zorder=2))
    ax.add_collection3d(Line3DCollection(hidden, colors=shade(RED, 1.55), linewidths=1.0,
                                         zorder=3, linestyles=(0, (4, 4))))
    for q, a in enumerate(A):
        ax.plot([a[0]], [a[1]], [a[2]], "o", ms=9, mfc=dark[q], mec="white", mew=1.0,
                zorder=4)
    ax.plot([r[0]], [r[1]], [r[2]], "s", ms=9, mfc=RED, mec="white", mew=1.0, zorder=4)
    ax.text(0.35, 0.35, 1.20, r"$\mathrm{HV}(A;r)$", ha="center", va="center", color=INK,
            zorder=5)
    handles = [Line2D([], [], ls="none", marker="o", ms=8, mfc=dark[q], mec="white",
                      mew=0.8, label=name(q + 1)) for q in range(len(A))]
    handles.append(Line2D([], [], ls="none", marker="s", ms=8, mfc=RED, mec="white",
                          mew=0.8, label=r"$r$"))
    ax.legend(handles=handles, loc="upper left", frameon=False, labelspacing=0.55,
              handletextpad=0.3, borderpad=0.2, fontsize=15)

    # axis triad, drawn in the same 3-D axes: same projection matrix as the boxes
    o, arm = np.array([0.02, 1.52, 0.10]), 0.36
    for k, lab in enumerate([r"$f_1$", r"$f_2$", r"$f_3$"]):
        e = np.zeros(3)
        e[k] = 1.0
        t = o + arm * e
        ax.add_artist(Arrow3D([o[0], t[0]], [o[1], t[1]], [o[2], t[2]], arrowstyle="-|>",
                              mutation_scale=13, lw=1.5, color=INK, zorder=6))
        p = o + 1.30 * arm * e
        ax.text(p[0], p[1], p[2], lab, ha="center", va="center", color=INK, zorder=6)

    ax.set_xlim(0.00, 1.10)
    ax.set_ylim(0.00, 1.95)
    ax.set_zlim(0.00, 1.32)
    ax.set_box_aspect((1.10, 1.95, 1.32))          # isotropic: box aspect = data ranges
    ax.view_init(elev=elev, azim=azim)
    ax.set_axis_off()
    save(fig, "hypervolume-indicator-3d")


if __name__ == "__main__":
    fig_2d()
    fig_3d()
