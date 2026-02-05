# /// script
# requires-python = ">=3.12"
# dependencies = [
#     "marimo==0.18.4",
#     "dummypy",
#     "loman",
# ]
#
# [tool.uv.sources]
# dummypy = { path = "../../..", editable=true }
#
# ///

"""Demo build-extras.sh with loman and graphviz."""

import marimo

__generated_with = "0.18.4"
app = marimo.App(width="medium")


@app.cell(hide_code=True)
def _(mo):
    mo.md(r"""
    ## Verify loman renders graphviz plots

    graphiz is installed in `.rhiza/scripts/customisations/build-extras.sh`
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
    comp.add_node("c", lambda a, b: 2 * a)  # c depends on a and b
    comp.add_node("d", lambda b, c: b + c)  # d depends on b and c
    comp.add_node("e", lambda c: c + 1)  # e depends on c
    comp.compute_all()
    return (comp,)


@app.cell
def _(comp):
    comp.draw()
    return


@app.cell
def _():
    import marimo as mo

    return (mo,)


if __name__ == "__main__":
    app.run()
