"""Fuzz the dummypy ``Grid`` constructor and ``diff()`` against arbitrary sizes.

``Grid`` builds a pair of ``(n+1) x (n+1)`` DataFrames from an integer size and
``diff()`` returns their element-wise difference. The constructor must never
crash on adversarial sizes with an unexpected exception — it should either build
a grid or raise a clean, documented error. This harness exercises that contract
with coverage-guided input.

Run locally:
    pip install atheris numpy pandas attrs
    python tests/fuzz/fuzz_grid.py -atheris_runs=20000

Run in ClusterFuzzLite: this file is built by .clusterfuzzlite/build.sh.
"""

from __future__ import annotations

import sys

import atheris

with atheris.instrument_imports():
    from dummypy import Grid


def test_one_input(data: bytes) -> None:
    """Exercise Grid construction and diff() with a fuzzed grid size."""
    fdp = atheris.FuzzedDataProvider(data)
    # Bound the size: the grid allocates an (n+1) x (n+1) matrix, so an
    # unbounded n would trivially exhaust memory without exercising any real
    # logic. Widen this range to hunt for edge cases (e.g. negative sizes).
    n = fdp.ConsumeIntInRange(0, 1000)

    grid = Grid(n=n)
    grid.diff()


def main() -> None:
    """Run the Atheris fuzz loop."""
    atheris.Setup(sys.argv, test_one_input)
    atheris.Fuzz()


if __name__ == "__main__":
    main()
