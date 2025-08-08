# tests/test_fluxed_behavior.py

import pytest
import numpy as np

# Adjust the import path based on your project structure
from Fluxed.shapes import NdShape
from Fluxed.distributions import (
    Distribution,
    UniformDistribution,
    NormalDistribution2D,
    LinearDistribution1D
)
from Fluxed.match import match_flux_parameters

# --- Fixtures ---


@pytest.fixture
def closed_2d_shape() -> NdShape:
    """A simple, closed 3x3 square inside a 5x5 grid."""
    border = np.array([
        [1, 1, 1, 1, 1],
        [1, 0, 0, 0, 1],
        [1, 0, 0, 0, 1],
        [1, 0, 0, 0, 1],
        [1, 1, 1, 1, 1],
    ], dtype=int)
    return NdShape(border)


@pytest.fixture
def open_2d_shape() -> NdShape:
    """A 2D shape with a leak in the border."""
    border = np.array([[1, 1, 1], [1, 0, 0], [1, 1, 1]], dtype=int)
    return NdShape(border)


@pytest.fixture
def solid_shape() -> NdShape:
    """A shape with no interior space to fill."""
    return NdShape(np.ones((3, 3), dtype=int))


@pytest.fixture
def hollow_3d_cube() -> NdShape:
    """A 3x3x3 hollow cube inside a 5x5x5 grid."""
    border = np.ones((5, 5, 5), dtype=int)
    border[1:4, 1:4, 1:4] = 0
    return NdShape(border)

# --- Test Suites ---


class TestNdShape:
    """Tests for the core NdShape class functionality."""

    def test_is_closed(self, closed_2d_shape, open_2d_shape, solid_shape):
        assert closed_2d_shape.is_closed is True
        assert open_2d_shape.is_closed is False
        assert solid_shape.is_closed is False  # No empty space to enclose

    def test_get_flux_simple_area(self, closed_2d_shape):
        """Test that flux with a uniform distribution of 1.0 equals the area."""
        assert closed_2d_shape.get_flux(UniformDistribution(1.0)) == 9.0

    def test_flux_for_open_or_solid_shapes(self, open_2d_shape, solid_shape):
        """Flux should be 0 for shapes with no valid enclosed region."""
        dist = UniformDistribution(1.0)
        with pytest.warns(UserWarning):
            assert open_2d_shape.get_flux(dist) == 0.0
        # A solid shape isn't "open" but has no enclosed flux
        assert solid_shape.get_flux(dist) == 0.0

    def test_get_enclosed_intensity_array(self, closed_2d_shape):
        """Verify the array of enclosed intensity values is correct."""
        dist = LinearDistribution1D(slope=10, intercept=0)

        # Wrapper to use a 1D dist in a 2D space on the x-axis
        class Wrapper(dist.__class__):
            def __call__(self, x, y): return self.func(y)

        # This will fill the intensity array
        closed_2d_shape.get_flux(Wrapper(slope=10, intercept=0))

        intensity_array = closed_2d_shape.get_enclosed_intensity_array()

        # Expected values for x = 1, 2, 3 are 10, 20, 30. Summed over 3 y-coords.
        expected = np.array([
            [0, 0, 0, 0, 0],
            [0, 10, 20, 30, 0],
            [0, 10, 20, 30, 0],
            [0, 10, 20, 30, 0],
            [0, 0, 0, 0, 0],
        ])

        assert np.array_equal(intensity_array, expected)

    def test_1d_shape_flux(self):
        """Test a simple 1D case."""
        shape_1d = NdShape(np.array([1, 0, 0, 0, 1]))
        dist_1d = LinearDistribution1D(slope=2, intercept=1)
        # Flux at indices 1, 2, 3 should be:
        # (2*1+1) + (2*2+1) + (2*3+1) = 3 + 5 + 7 = 15
        assert shape_1d.is_closed
        assert shape_1d.get_flux(dist_1d) == 15.0


class TestDistributions:
    """Tests for the Distribution classes, especially vectorization."""

    @pytest.mark.parametrize("coords, expected_shape", [
        ((5,), (1,)),  # Scalar input (becomes tuple of len 1)
        ((np.array([1, 2, 3]),), (3,)),  # Vector input
    ])
    def test_linear1d_vectorization(self, coords, expected_shape):
        """Ensure LinearDistribution1D handles both scalar and vector inputs."""
        dist = LinearDistribution1D(slope=10, intercept=5)
        # We need to simulate how NdShape calls it
        result = dist.func(*coords)
        if expected_shape == (1,):
            assert isinstance(result, (int, float))
        else:
            assert isinstance(result, np.ndarray)
            assert result.shape == expected_shape


class TestFluxMatcher:
    """Integration tests for the match_flux_parameters function."""

    def test_match_flux_2d_simple(self, closed_2d_shape):
        """Test a simple 2D case: match a uniform flux with a constant linear one."""
        source_dist = UniformDistribution(value=10.0)
        target_flux = 90.0

        TargetDistClass = LinearDistribution1D

        class Wrapper(TargetDistClass):
            def __call__(self, x, y): return self.func(x)

        # We want to find an intercept that gives a flux of 90 over 9 points.
        # This means the constant value should be 10.
        # So, we expect slope=0, intercept=10.
        params_to_find = ['slope', 'intercept']
        initial_guess = [1.0, 1.0]  # Start from a bad guess
        bounds = [(0, 0), (None, None)]  # Force slope to be exactly 0

        result = match_flux_parameters(
            source_shape=closed_2d_shape,
            source_dist=source_dist,
            target_shape=closed_2d_shape,
            TargetDistClass=Wrapper,
            param_names=params_to_find,
            initial_guess=initial_guess,
            bounds=bounds
        )

        assert result['success']
        assert np.isclose(result['target_flux'], target_flux)
        assert np.isclose(result['final_flux'], target_flux, rtol=1e-2)
        assert np.isclose(result['parameters']['slope'], 0.0)
        assert np.isclose(result['parameters']['intercept'], 10.0)

    def test_match_flux_cross_dimensional(self, closed_2d_shape, hollow_3d_cube):
        """Test matching flux from a 2D source to a 3D target."""
        source_dist = UniformDistribution(value=1.0)  # Total flux = 9.0

        TargetDistClass = LinearDistribution1D

        class Wrapper(TargetDistClass):
            def __call__(self, x, y, z): return self.func(
                z)  # Depends only on Z

        params_to_find = ['slope', 'intercept']
        initial_guess = [0.0, 0.0]

        result = match_flux_parameters(
            source_shape=closed_2d_shape,
            source_dist=source_dist,
            target_shape=hollow_3d_cube,
            TargetDistClass=Wrapper,
            param_names=params_to_find,
            initial_guess=initial_guess
        )

        assert result['success']
        assert np.isclose(result['target_flux'], 9.0)
        assert np.isclose(result['final_flux'], 9.0, rtol=1e-2)

    def test_optimizer_failure_on_impossible_bounds(self, closed_2d_shape):
        """Test that the optimizer reports failure if no solution is possible."""
        # Target flux is positive
        source_dist = UniformDistribution(value=1.0)  # Flux = 9.0

        TargetDistClass = LinearDistribution1D

        class Wrapper(TargetDistClass):
            def __call__(self, x, y): return self.func(x)

        params_to_find = ['slope', 'intercept']
        initial_guess = [-0.1, -1]
        # IMPOSSIBLE BOUNDS: Force slope and intercept to be negative.
        # With positive integer coordinates, the flux must be negative,
        # so it can never match the positive target flux.
        bounds = [(None, -0.01), (None, -0.01)]

        result = match_flux_parameters(
            source_shape=closed_2d_shape,
            source_dist=source_dist,
            target_shape=closed_2d_shape,
            TargetDistClass=Wrapper,
            param_names=params_to_find,
            initial_guess=initial_guess,
            bounds=bounds
        )

        # The optimizer may report "success" if it finds a local minimum,
        # but the final flux will NOT match the target. This is the key check.
        assert not np.isclose(result['final_flux'], result['target_flux'])
