# /// script
# requires-python = ">=3.13"
# dependencies = [
#     "marimo==0.18.4",
#     "dummypy",
# ]
#
# [tool.uv.sources]
# dummypy = { path = "../../..", editable=true }
#
# ///


"""Demo application using marimo and dummypy."""

import marimo

__generated_with = "0.10.9"
app = marimo.App()


@app.cell
def __import_libs():
    import dummypy as dp

    return (dp,)


@app.cell
def __create_grid(dp):
    grid = dp.Grid()
    return (grid,)


@app.cell
def __show_grid(grid):
    grid


@app.cell
def __show_diff(grid):
    grid.diff()


if __name__ == "__main__":
    app.run()
