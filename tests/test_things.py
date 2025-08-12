"""Unit tests for Grid class.

Test Structure:
---------------
This test suite uses pytest fixtures for efficient test data management and is organized
into three main test classes for logical separation:

1. TestGrid - Core functionality tests (initialization, basic methods, properties)
2. TestGridIntegration - Integration tests with external libraries (numpy, persistence)
3. TestGridMethods - Advanced method behavior tests with custom fixtures

Fixture Organization:
--------------------
The test suite uses several fixtures to provide reusable test data:

- default_grid: Grid() with default parameters (n=10)
- small_grid: Grid(n=2) for detailed testing with minimal data
- tiny_grid: Grid(n=3) for structure verification
- medium_grid: Grid(n=5) for performance and integration testing
- edge_case_grid: Grid(n=0) for boundary condition testing
- parametrized_grid: Parametrized fixture testing multiple sizes [1, 5, 10, 20]

Fixture Benefits:
-----------------
- Eliminates repetitive Grid() instantiation across tests
- Provides consistent test data for related test cases
- Enables parametrized testing for multiple scenarios
- Improves test performance through reusable objects
- Makes test dependencies and requirements explicit

Test Coverage:
--------------
The test suite covers:
- Grid initialization and attributes
- DataFrame creation and structure (x and y properties)
- Difference calculation method (diff)
- Data types and numerical accuracy
- Edge cases and boundary conditions
- Integration with numpy and pandas
- Parametrized testing across different grid sizes
"""

import pytest
import numpy as np
import pandas as pd
from dummypy import Grid


# Fixtures
@pytest.fixture
def default_grid():
    """Fixture for Grid with default parameters."""
    return Grid()


@pytest.fixture
def small_grid():
    """Fixture for small Grid (n=2) for detailed testing."""
    return Grid(n=2)


@pytest.fixture
def tiny_grid():
    """Fixture for tiny Grid (n=3) for structure testing."""
    return Grid(n=3)


@pytest.fixture
def medium_grid():
    """Fixture for medium Grid (n=5) for performance testing."""
    return Grid(n=5)


@pytest.fixture
def edge_case_grid():
    """Fixture for edge case Grid (n=0)."""
    return Grid(n=0)


@pytest.fixture(params=[1, 5, 10, 20])
def parametrized_grid(request):
    """Parametrized fixture for testing different grid sizes."""
    return Grid(n=request.param)


class TestGrid:
    """Test cases for the Grid class."""

    def test_goal_grid_initialization_default(self, default_grid):
        """Test Grid initialization with default parameters."""
        grid = default_grid

        # Check default n value
        assert grid.n == 10

        # Check that x and y grids exist
        assert hasattr(grid, "x")
        assert hasattr(grid, "y")

        # Check dimensions
        assert grid.x.shape == (11, 11)  # n+1 for 0 to n inclusive
        assert grid.y.shape == (11, 11)

    def test_goal_grid_initialization_custom(self):
        """Test Grid initialization with custom n value."""
        n = 5
        grid = Grid(n=n)

        # Check custom n value
        assert grid.n == n

        # Check dimensions
        assert grid.x.shape == (n + 1, n + 1)
        assert grid.y.shape == (n + 1, n + 1)

    def test_grid_x_y_structure(self, tiny_grid):
        """Test that x and y grids have correct structure."""
        grid = tiny_grid  # n=3

        # Expected structure for n=3:
        # y grid should have columns and rows representing coordinates
        # x grid should be transpose of y grid
        expected_y = pd.DataFrame(
            [[0, 1, 2, 3], [0, 1, 2, 3], [0, 1, 2, 3], [0, 1, 2, 3]],
            index=["0", "1", "2", "3"],
            columns=["0", "1", "2", "3"],
        )

        expected_x = expected_y.T

        pd.testing.assert_frame_equal(grid.y, expected_y)
        pd.testing.assert_frame_equal(grid.x, expected_x)

    def test_diff_method(self, small_grid):
        """Test the diff method returns correct differences."""
        grid = small_grid  # n=2

        result = grid.diff()

        # Check dimensions
        assert result.shape == (3, 3)

        # Check specific values
        # When x=0, y=0: diff should be 0
        assert result.loc["0", "0"] == 0
        # When x=2, y=1: diff should be 1
        assert result.loc["2", "1"] == 1
        # When x=1, y=2: diff should be -1
        assert result.loc["1", "2"] == -1

        # Check that result is x - y
        expected = grid.x - grid.y
        pd.testing.assert_frame_equal(result, expected)

    def test_goal_grid_symmetry_properties(self, medium_grid):
        """Test mathematical properties of the grids."""
        grid = medium_grid  # n=5

        # Test that x is transpose of y
        pd.testing.assert_frame_equal(grid.x, grid.y.T)

        # Test that diff is antisymmetric
        diff = grid.diff()
        pd.testing.assert_frame_equal(diff, -diff.T)

    def test_goal_grid_edge_cases(self, edge_case_grid):
        """Test edge cases for Grid."""
        grid = edge_case_grid  # n=0
        assert grid.n == 0
        assert grid.x.shape == (1, 1)
        assert grid.y.shape == (1, 1)
        assert grid.x.loc["0", "0"] == 0
        assert grid.y.loc["0", "0"] == 0

    def test_goal_grid_data_types(self, default_grid):
        """Test that the grids contain correct data types."""
        grid = default_grid

        # Check that home and away are pandas DataFrames
        assert isinstance(grid.x, pd.DataFrame)
        assert isinstance(grid.y, pd.DataFrame)

        # Check that values are numeric
        assert pd.api.types.is_numeric_dtype(grid.x.dtypes.iloc[0])
        assert pd.api.types.is_numeric_dtype(grid.y.dtypes.iloc[0])

    def test_goal_grid_index_and_columns(self, tiny_grid):
        """Test that indexes and columns are properly set."""
        grid = tiny_grid  # n=3

        expected_labels = ["0", "1", "2", "3"]

        # Check home grid
        assert list(grid.x.index) == expected_labels
        assert list(grid.x.columns) == expected_labels

        # Check away grid
        assert list(grid.y.index) == expected_labels
        assert list(grid.y.columns) == expected_labels

    def test_goal_grid_repr(self, medium_grid):
        """Test the string representation of Grid."""
        grid = medium_grid  # n=5
        repr_str = repr(grid)

        assert "Grid" in repr_str
        assert "n=5" in repr_str

    def test_goal_grid_different_sizes(self, parametrized_grid):
        """Test Grid with different n values using parametrized fixture."""
        grid = parametrized_grid
        n = grid.n

        assert grid.x.shape == (n + 1, n + 1)
        assert grid.y.shape == (n + 1, n + 1)

        # Test that methods work correctly
        diff = grid.diff()

        assert diff.shape == (n + 1, n + 1)

        # Test corner values for diff method
        assert diff.iloc[0, 0] == 0  # 0 - 0
        assert diff.iloc[n, 0] == n  # n - 0
        assert diff.iloc[0, n] == -n  # 0 - n


# Integration tests
class TestGridIntegration:
    """Integration tests for Grid with other components."""

    def test_goal_grid_with_numpy_operations(self, tiny_grid):
        """Test that Grid works well with numpy operations."""
        grid = tiny_grid  # n=3

        # Test numpy operations on the dataframes
        x_array = grid.x.values
        y_array = grid.y.values

        assert isinstance(x_array, np.ndarray)
        assert isinstance(y_array, np.ndarray)

        # Test mathematical operations
        diff_array = x_array - y_array

        np.testing.assert_array_equal(diff_array, grid.diff().values)

    def test_goal_grid_persistence(self, medium_grid):
        """Test that Grid maintains state correctly."""
        grid1 = medium_grid  # n=5
        grid2 = Grid(n=5)

        # Should be equal but not the same object
        pd.testing.assert_frame_equal(grid1.x, grid2.x)
        pd.testing.assert_frame_equal(grid1.y, grid2.y)
        assert grid1 is not grid2


# Additional fixture-based tests
class TestGridMethods:
    """Test class focusing on method behavior with fixtures."""

    @pytest.fixture
    def grid_with_results(self, small_grid):
        """Fixture that provides a grid with pre-computed results."""
        grid = small_grid
        return {
            "grid": grid,
            "diff": grid.diff(),
        }

    def test_method_consistency(self, grid_with_results):
        """Test that methods return consistent results."""
        data = grid_with_results
        grid = data["grid"]

        # Methods should return the same result when called multiple times
        pd.testing.assert_frame_equal(data["diff"], grid.diff())

    def test_method_independence(self, grid_with_results):
        """Test that method results are independent of each other."""
        data = grid_with_results
        diff = data["diff"]

        # Modifying one result shouldn't affect the grid
        diff_copy = diff.copy()
        diff_copy.iloc[0, 0] = 999

        # Original diff should be unchanged
        assert diff.iloc[0, 0] == 0
