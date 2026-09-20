# Hypervolume-2d3d-Drawing

Reproducible drawings of the **hypervolume indicator** in two and three objectives, made for the
Wikipedia article [Hypervolume indicator](https://en.wikipedia.org/wiki/Hypervolume_indicator).
One small Python script produces both figures as SVG (for upload) and PNG (for convenience).

| 2 objectives | 3 objectives |
|---|---|
| ![Hypervolume indicator in 2-D](hypervolume-indicator-2d.png) | ![Hypervolume indicator in 3-D](hypervolume-indicator-3d.png) |

## What the figures show

For a minimisation problem with $m$ objectives, a finite approximation set
$A = \{a^{1}, \dots, a^{n}\} \subset \mathbb{R}^m$ and a reference point $r$ with $a_i \le r_i$,
each point spans the axis-aligned box $[a, r] = [a_1, r_1] \times \dots \times [a_m, r_m]$, and

$$\mathrm{HV}(A;r) \;=\; \lambda_m\Big(\bigcup_{a \in A} [a, r]\Big),$$

with $\lambda_m$ the $m$-dimensional Lebesgue measure: an area for $m = 2$, a volume for $m = 3$.
The shaded region in each figure is that union, and only non-dominated points contribute to it.

The colours are not decoration. They show the standard sweep decomposition of the union:

* **2-D** — the region is cut into the vertical slab that each point contributes when the points are
  swept in order of $f_1$. Summing the slab areas is the $O(n \log n)$ algorithm for the 2-D case.
* **3-D** — the visible staircase surface is cut into cells, each coloured by the point that
  determines its floor, i.e. the smallest $f_3$ among the points dominating that cell.

Further conventions: the points $a^{i}$ are dark discs, the reference point $r$ is an open square,
and dashed lines are *hidden* edges that run behind the solid and meet at $r$. The 3-D figure is
seen from the origin side, so the staircase faces the reader and the region hangs from $r$. Its axis
triad sits in the corner rather than through the data, because the origin plays no role in the
definition of the indicator — only the directions of the objectives matter.

## Reproducing the figures

```bash
pip install -r requirements.txt
python plot_hypervolume_figures.py
```

This overwrites `hypervolume-indicator-2d.{svg,png}` and `hypervolume-indicator-3d.{svg,png}`.
Only `matplotlib` and `numpy` are needed; the figures are plotted from hard-coded coordinates, so
the output is deterministic.

## Adapting them

Everything worth changing sits at the top of `plot_hypervolume_figures.py` or in the two figure
functions:

* `PAREN = True` switches the labels from $a^{i}$ to the parenthesised form $a^{(i)}$ used in the
  body of the Wikipedia article.
* The arrays `A` in `fig_2d()` and `fig_3d()` hold the objective vectors, `r` the reference point.
  Any mutually non-dominated points work; the 3-D routine recomputes the staircase from scratch.
* `PALETTE`, `INK` and `GREY` set the colours, `elev, azim` in `fig_3d()` the camera.

The SVGs are written with `svg.fonttype = "path"`, i.e. all glyphs are converted to outlines. This is
what Wikimedia Commons needs, because its renderer has only a small set of fonts available and would
otherwise substitute them. The drawback is that the labels are no longer editable as text; remove
that setting if you want translatable labels and accept the font risk.

## Licence

Copyright © 2026 Michael Emmerich.

* The **figures** (`hypervolume-indicator-*.svg`, `hypervolume-indicator-*.png`) are licensed under
  [CC BY 4.0](https://creativecommons.org/licenses/by/4.0/), see `LICENSE-CC-BY-4.0`, which is
  compatible with Wikimedia Commons.
* The **code** (`plot_hypervolume_figures.py`) is licensed under the MIT License, see `LICENSE`.
  Creative Commons licences are not intended for software.
