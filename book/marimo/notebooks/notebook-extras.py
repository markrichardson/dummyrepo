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

"""Render a loman computation graph without the graphviz binary.

``loman``'s own ``Computation.draw()`` returns a ``GraphView`` whose
``_repr_svg_`` shells out to graphviz's ``dot`` — a system package, not a Python
one. This notebook uses the ``GraphView.viz_dag`` seam instead: a plain
``networkx.DiGraph``, layered with ``networkx``'s own ``multipartite_layout``
and drawn with ``matplotlib``. Nothing here needs a binary on PATH, and nothing
here is a new dependency: ``networkx`` and ``matplotlib`` are already declared
by ``loman`` itself.
"""

import marimo

__generated_with = "0.23.11"
app = marimo.App(width="medium")


@app.cell(hide_code=True)
def _(mo):
    mo.md(r"""
    ## Render a loman graph with no graphviz binary

    `loman.Computation.draw()` produces a `GraphView`, and rendering it as SVG
    execs graphviz's `dot`. That is a system package, not a Python one. It used to
    be installed by a `build-extras.sh` hook, whose caller disappeared in January
    2026 when a sync replaced the hand-written `Makefile` with the `.rhiza/make.d/`
    layer — so the install quietly stopped happening. Both the hook and this
    notebook's dependency on it are now gone.

    `GraphView.viz_dag` is a `networkx.DiGraph`, which is all a layout needs.
    Assigning each node its topological generation and calling
    `nx.multipartite_layout` gives the layered arrangement `dot` would produce.

    A pure-Python Sugiyama layout (`grandalf`) would lay this out more tidily, but
    it is GPLv2-or-EPLv1 and this project is MIT — `make license` rejects copyleft,
    so it is not an option. `networkx` and `matplotlib` are BSD/PSF and already in
    the lockfile via `loman`, so this route adds nothing at all.
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
    # The graphviz-free seam: a networkx DiGraph, plus loman's own node labels.
    dag = comp.draw().viz_dag
    labels = {n: dag.nodes[n].get("label", n) for n in dag.nodes}
    return dag, labels


@app.cell
def _(dag):
    import networkx as nx

    # multipartite_layout needs each node tagged with the layer it belongs to;
    # a DAG's topological generations are exactly that.
    for layer, nodes in enumerate(nx.topological_generations(dag)):
        for node in nodes:
            dag.nodes[node]["layer"] = layer

    # align="horizontal" stacks the layers vertically; negating y puts the roots
    # at the top, the direction `dot` draws a dependency graph.
    pos = {n: (x, -y) for n, (x, y) in nx.multipartite_layout(dag, subset_key="layer", align="horizontal").items()}
    return nx, pos


@app.cell
def _(dag, labels, nx, pos):
    import matplotlib.pyplot as plt

    fig, ax = plt.subplots(figsize=(6, 4.5))
    nx.draw_networkx(
        dag,
        pos,
        ax=ax,
        labels=labels,
        node_color="#cfe8ff",
        node_size=1300,
        font_size=9,
        arrows=True,
        # Curve the edges slightly. a -> c skips a layer, so drawn straight it
        # hides behind the a -> b -> c segments that share its x position.
        connectionstyle="arc3,rad=0.12",
    )
    ax.set_axis_off()
    fig
    return


@app.cell
def _():
    import marimo as mo

    return (mo,)


if __name__ == "__main__":
    app.run()
