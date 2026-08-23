# /// script
# requires-python = ">=3.13"
# dependencies = [
#     "marimo>=0.23.11",
#     "dummypy",
#     "loman",
# ]
#
# [tool.uv.sources]
# dummypy = { path = "../../..", editable=true }
#
# ///

"""Render a loman computation graph, draggable, without running graphviz.

No, this notebook does not use ``dot`` — and the ``Computation.draw()`` call
below is not a counter-example. ``draw()`` only builds objects: a
``networkx.DiGraph`` in ``GraphView.viz_dag``, and an in-memory
``pydotplus.Dot`` in ``viz_dot``. Graphviz's ``dot`` binary is execed later and
elsewhere, by whatever asks that ``Dot`` for a rendering — ``GraphView.svg()``,
``_repr_svg_()`` or ``.view()``. This notebook calls none of the three, and
never leaves a ``GraphView`` as a cell output either, since marimo would call
``_repr_svg_`` on it and shell out. It reads ``viz_dag`` and draws that itself.

Checked with ``dot`` off PATH rather than assumed: ``draw()`` returns normally
and ``viz_dag`` is populated, while ``svg()`` raises
``InvocationException: GraphViz's executables not found``.

The layout is only a starting position. It is handed to a self-contained SVG
that lets you drag the nodes around, so an edge hidden behind another can be
pulled clear. Nothing here is a new dependency: ``networkx`` is already declared
by ``loman`` itself, and the drag handling is a few lines of plain DOM code with
no library behind it.
"""

import marimo

__generated_with = "0.23.11"
app = marimo.App(width="medium")


@app.cell(hide_code=True)
def _(mo):
    mo.md(r"""
    ## Render a loman graph without running graphviz — and drag it

    **Is `dot` used here? No.** The cell below calls `comp.draw()`, which sounds like
    it would, so the line is worth drawing precisely: `draw()` only *builds* things —
    `GraphView.viz_dag`, a `networkx.DiGraph`, and `GraphView.viz_dot`, a
    `pydotplus.Dot` held in memory. Nothing execs graphviz's `dot` binary until
    something asks that `Dot` to render: `GraphView.svg()`, `_repr_svg_()` or
    `.view()`. This notebook calls none of them, and deliberately never leaves a
    `GraphView` as a cell output, because marimo would then call `_repr_svg_` on it
    and shell out. Off PATH, `draw()` still returns and `svg()` raises
    `InvocationException: GraphViz's executables not found`.

    That matters because `dot` is a system package, not a Python one. It used to be
    installed by a `build-extras.sh` hook, whose caller disappeared in January 2026
    when a sync replaced the hand-written `Makefile` with the `.rhiza/make.d/` layer
    — so the install quietly stopped happening. Both the hook and this notebook's
    dependency on it are now gone.

    `viz_dag` is all a layout needs. Assigning each node its topological generation
    and calling `nx.multipartite_layout` gives the same layering `dot` would have
    chosen, and the cell after that turns it into SVG by hand.

    That layout is the *starting* position, not the last word: **drag any node** to
    move it, and its edges follow. Hovering a node highlights the edges it takes
    part in, and *Reset layout* puts everything back where `networkx` placed it.
    The drawing is hand-written SVG for exactly that reason — an earlier version of
    this notebook rendered the same layout as a matplotlib PNG, which cannot be
    pulled apart. `a -> c` skips a layer, so drawn straight it hides behind the
    `a -> b -> c` segments that share its x position; the edges are curved to
    separate them, and now you can also just drag `b` out of the way.

    A pure-Python Sugiyama layout (`grandalf`) would lay this out more tidily, but
    it is GPLv2-or-EPLv1 and this project is MIT — `make license` rejects copyleft,
    so it is not an option. `networkx` is BSD and already in the lockfile via
    `loman`, so this route adds nothing at all — and the dragging is hand-written
    DOM code rather than a graph-widget dependency for the same reason.
    """)
    return


@app.cell
def _():
    import loman

    return (loman,)


@app.cell
def _(loman):
    comp = loman.Computation()
    comp.add_node("a", value=1)  # Input node
    comp.add_node("b", lambda a: a + 1)  # b depends on a
    comp.add_node("c", lambda a, b: 2 * a + b)  # c depends on a and b
    comp.add_node("d", lambda b, c: b + c)  # d depends on b and c
    comp.add_node("e", lambda c: c + 1)  # e depends on c
    comp.compute_all()
    return (comp,)


@app.cell
def _(comp):
    # draw() runs no binary; it returns a GraphView holding a networkx DiGraph. Take
    # that, plus loman's own node labels and its state colouring (green = up to date,
    # red = error) — the one thing the `dot` rendering carried that a bare layout does
    # not. The GraphView itself is never made a cell output: marimo would call its
    # `_repr_svg_`, and *that* is what execs `dot`.
    dag = comp.draw().viz_dag
    labels = {n: dag.nodes[n].get("label", n) for n in dag.nodes}
    colors = {n: dag.nodes[n].get("fillcolor", "#cfe8ff") for n in dag.nodes}
    return colors, dag, labels


@app.cell
def _(dag):
    import networkx as nx

    # multipartite_layout needs each node tagged with the layer it belongs to;
    # a DAG's topological generations are exactly that.
    for layer, nodes in enumerate(nx.topological_generations(dag)):
        for node in nodes:
            dag.nodes[node]["layer"] = layer

    # align="horizontal" stacks the layers vertically; negating y makes the roots the
    # highest points, which is how a dependency graph is normally read. The cell below
    # turns that into screen coordinates, where y grows downwards.
    pos = {n: (x, -y) for n, (x, y) in nx.multipartite_layout(dag, subset_key="layer", align="horizontal").items()}
    return (pos,)


@app.cell
def _(colors, dag, labels, pos):
    import json

    width, height, pad, radius = 640, 420, 46, 26

    def _fit(values, lo, hi):
        """Map `values` onto [lo, hi], centring them if they are all equal."""
        vmin, vmax = min(values), max(values)
        span = vmax - vmin
        if span == 0:
            return [(lo + hi) / 2 for _ in values]
        return [lo + (v - vmin) / span * (hi - lo) for v in values]

    # networkx lays out in mathematical coordinates, y pointing up; SVG's y points
    # down. So the y range is given high-to-low, which puts the roots back at the
    # top of the picture.
    _order = list(dag.nodes)
    _xs = _fit([pos[n][0] for n in _order], pad, width - pad)
    _ys = _fit([pos[n][1] for n in _order], height - pad, pad)

    graph_data = json.dumps(
        {
            "width": width,
            "height": height,
            "pad": pad,
            "r": radius,
            "nodes": [
                {"id": str(n), "label": str(labels[n]), "fill": str(colors[n]), "x": x, "y": y}
                for n, x, y in zip(_order, _xs, _ys, strict=True)
            ],
            "edges": [{"source": str(u), "target": str(v)} for u, v in dag.edges],
        }
    )
    return (graph_data,)


@app.cell
def _(graph_data, mo):
    # A whole graph widget in one <script>: positions come from networkx above,
    # everything below is plain DOM. `mo.iframe` is what lets the script run at
    # all — `mo.Html` strips script tags — and it sandboxes these styles away
    # from the notebook's own.
    _template = """<!doctype html>
    <meta charset="utf-8">
    <style>
      body { margin: 0; font: 13px/1.4 system-ui, sans-serif; color: #6b7280; }
      svg { touch-action: none; user-select: none; display: block; }
      .node { cursor: grab; }
      .node.dragging { cursor: grabbing; }
      .node circle { stroke: #33404d; stroke-width: 1.5; }
      .node:hover circle, .node.dragging circle { stroke-width: 3; }
      .node text { fill: #13293d; font: 600 12px system-ui, sans-serif; text-anchor: middle; }
      path.edge { fill: none; stroke: #8a8f98; stroke-width: 1.6; }
      path.edge.incident { stroke: #4a90d9; stroke-width: 2.6; }
      button { font: inherit; color: inherit; background: none; border: 1px solid currentColor;
               border-radius: 5px; padding: 3px 10px; cursor: pointer; }
    </style>
    <svg id="graph" width="100%"></svg>
    <p><button id="reset">Reset layout</button> &nbsp; drag a node to move it</p>
    <script>
      const DATA = __DATA__;
      const SVG_NS = "http://www.w3.org/2000/svg";
      /* Edge curvature, as a fraction of the chord: enough to keep a -> c clear of the
         a -> b -> c pair it would otherwise hide behind. Note the block comments —
         `mo.iframe` flattens this document onto one line, and a `//` comment would
         take the rest of the script with it. */
      const RAD = 0.12;

      const svg = document.getElementById("graph");
      svg.setAttribute("viewBox", `0 0 ${DATA.width} ${DATA.height}`);
      const marker = (id, fill) =>
        `<marker id="${id}" viewBox="0 0 10 10" refX="9" refY="5" markerWidth="7" markerHeight="7"` +
        ` orient="auto-start-reverse" markerUnits="userSpaceOnUse">` +
        `<path d="M0,0 L10,5 L0,10 z" fill="${fill}"/></marker>`;
      svg.innerHTML = `<defs>${marker("arrow", "#8a8f98")}${marker("arrow-on", "#4a90d9")}</defs>`;
      const edgeLayer = document.createElementNS(SVG_NS, "g");
      const nodeLayer = document.createElementNS(SVG_NS, "g");
      svg.append(edgeLayer, nodeLayer);

      const home = new Map(DATA.nodes.map((n) => [n.id, { x: n.x, y: n.y }]));
      const at = new Map(DATA.nodes.map((n) => [n.id, { x: n.x, y: n.y }]));
      const shapes = new Map();

      const edges = DATA.edges.map((e) => {
        const el = document.createElementNS(SVG_NS, "path");
        el.setAttribute("class", "edge");
        el.setAttribute("marker-end", "url(#arrow)");
        edgeLayer.append(el);
        return { ...e, el };
      });

      for (const n of DATA.nodes) {
        const g = document.createElementNS(SVG_NS, "g");
        g.setAttribute("class", "node");
        const circle = document.createElementNS(SVG_NS, "circle");
        circle.setAttribute("r", DATA.r);
        circle.setAttribute("fill", n.fill);
        const title = document.createElementNS(SVG_NS, "title");
        title.textContent = n.label;
        const text = document.createElementNS(SVG_NS, "text");
        text.setAttribute("dy", "0.35em");
        text.textContent = n.label;
        g.append(title, circle, text);
        nodeLayer.append(g);
        shapes.set(n.id, { g, circle, text });
        g.addEventListener("pointerdown", (ev) => startDrag(ev, n.id));
        g.addEventListener("pointerenter", () => highlight(n.id, true));
        g.addEventListener("pointerleave", () => highlight(n.id, false));
      }

      /* A quadratic Bezier whose control point sits RAD * |chord| off the midpoint,
         with both ends pulled back onto the node rims so the arrowhead lands there. */
      function towards(p, q, d) {
        const dx = q.x - p.x, dy = q.y - p.y, len = Math.hypot(dx, dy) || 1;
        return { x: p.x + (dx / len) * d, y: p.y + (dy / len) * d };
      }

      function drawEdge(e) {
        const a = at.get(e.source), b = at.get(e.target);
        const c = { x: (a.x + b.x) / 2 - RAD * (b.y - a.y), y: (a.y + b.y) / 2 + RAD * (b.x - a.x) };
        const s = towards(a, c, DATA.r), t = towards(b, c, DATA.r + 4);
        e.el.setAttribute("d", `M${s.x},${s.y} Q${c.x},${c.y} ${t.x},${t.y}`);
      }

      function drawNode(id) {
        const p = at.get(id), s = shapes.get(id);
        s.circle.setAttribute("cx", p.x);
        s.circle.setAttribute("cy", p.y);
        s.text.setAttribute("x", p.x);
        s.text.setAttribute("y", p.y);
        for (const e of edges) if (e.source === id || e.target === id) drawEdge(e);
      }

      function highlight(id, on) {
        for (const e of edges) {
          if (e.source !== id && e.target !== id) continue;
          e.el.classList.toggle("incident", on);
          /* the arrowhead is a marker, so it takes its colour from the marker, not the path */
          e.el.setAttribute("marker-end", on ? "url(#arrow-on)" : "url(#arrow)");
        }
      }

      function startDrag(ev, id) {
        ev.preventDefault();
        const { g } = shapes.get(id);
        g.classList.add("dragging");
        g.setPointerCapture(ev.pointerId);
        const point = svg.createSVGPoint();
        const grab = at.get(id);
        const start = toSvg(ev);
        const offset = { x: grab.x - start.x, y: grab.y - start.y };

        function toSvg(e) {
          point.x = e.clientX;
          point.y = e.clientY;
          return point.matrixTransform(svg.getScreenCTM().inverse());
        }
        const clamp = (v, hi) => Math.min(Math.max(v, DATA.pad / 2), hi - DATA.pad / 2);

        const move = (e) => {
          const p = toSvg(e);
          at.set(id, { x: clamp(p.x + offset.x, DATA.width), y: clamp(p.y + offset.y, DATA.height) });
          drawNode(id);
        };
        const stop = () => {
          g.classList.remove("dragging");
          g.removeEventListener("pointermove", move);
          g.removeEventListener("pointerup", stop);
          g.removeEventListener("pointercancel", stop);
        };
        g.addEventListener("pointermove", move);
        g.addEventListener("pointerup", stop);
        g.addEventListener("pointercancel", stop);
      }

      function redraw() {
        for (const e of edges) drawEdge(e);
        for (const id of at.keys()) drawNode(id);
      }

      document.getElementById("reset").addEventListener("click", () => {
        for (const [id, p] of home) at.set(id, { ...p });
        redraw();
      });

      redraw();
    </script>
    """

    graph = mo.iframe(_template.replace("__DATA__", graph_data), height="520px")
    graph
    return


@app.cell
def _():
    import marimo as mo

    return (mo,)


if __name__ == "__main__":
    app.run()
