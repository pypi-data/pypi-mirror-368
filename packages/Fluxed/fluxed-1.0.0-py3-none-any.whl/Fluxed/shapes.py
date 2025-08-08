import numpy as np
import scipy.ndimage

from Fluxed.distributions import Distribution

import functools
import warnings
from typing import Optional, Tuple, Any

# --- NdShape Class ---
class NdShape:
    """
    A class to represent an N-dimensional shape defined by a border,
    and compute flux through its enclosed region based on an intensity distribution.

    1s in the initial `shape_array` represent border points, 0s represent empty space.
    The 'flux' is the sum of intensity values within the enclosed region, where
    intensity is determined by a provided Distribution object.

    Attributes:
        _shape_array (np.ndarray): The N-dimensional array defining the shape's border.
        _intensity_array (np.ndarray): Stores the computed intensity values across the
                                       entire shape domain, populated by `fill_intensity_array`.
        _current_distribution_id (str): A simple identifier for the last used distribution
                                        for internal caching purposes.

    Properties:
        shape_array (np.ndarray): Returns the underlying NumPy array defining the border.
        dimensions (int): Returns the number of dimensions of the shape.
        is_closed (bool): Checks and caches whether the shape's border encloses a region.
    """

    def __init__(self, shape_array: np.ndarray) -> None:
        """
        Initializes the NdShape with a given NumPy array defining the border.

        Args:
            shape_array (np.ndarray): The N-dimensional array representing the shape's border.
                                      1s represent border points, 0s represent empty space.

        Raises:
            TypeError: If the input 'shape_array' is not a NumPy array.
            ValueError: If the array contains values other than 0 or 1.
        """
        if not isinstance(shape_array, np.ndarray):
            raise TypeError("Input 'shape_array' must be a NumPy array.")

        unique_values = np.unique(shape_array)
        if not np.all(np.isin(unique_values, [0, 1])):
            raise ValueError(
                f"Shape array must contain only 0s and 1s. Found: {unique_values}"
            )

        self._shape_array: np.ndarray = shape_array
        self._intensity_array: Optional[np.ndarray] = None  # No intensity array initially
        # Tracks the distribution used to fill intensity
        self._current_distribution_id: Optional[Tuple[Any, ...]] = None

    @property
    def shape_array(self) -> np.ndarray:
        """
        Returns the underlying NumPy array representing the shape's border definition.
        """
        return self._shape_array

    @property
    def dimensions(self) -> int:
        """
        Returns the number of dimensions of the shape.
        """
        return self._shape_array.ndim

    @functools.cached_property
    def is_closed(self) -> bool:
        """
        Checks if the shape's border (1s) completely encloses any region of 0s.
        A shape is considered closed if there is at least one region of 0s
        that is not connected to the array's boundary.

        Returns:
            bool: True if the shape contains at least one enclosed region, False otherwise.
        """

        # Label all connected components of '0's (empty space)
        # `structure=scipy.ndimage.generate_binary_structure(self.dimensions, 1)`
        # defines connectivity. `rank=1` means direct (face-connected) neighbors.
        structure = scipy.ndimage.generate_binary_structure(self.dimensions, 1)
        labeled_regions, num_features = scipy.ndimage.label(
            self._shape_array == 0, structure=structure)

        if num_features == 0:
            # No empty space at all, so no enclosed regions.
            return False

        # Identify labels that touch the array boundaries
        boundary_labels = set()
        shape_dims = self._shape_array.shape

        # Use np.nditer for efficient iteration over N-dimensional array indices
        it = np.nditer(self._shape_array, flags=['multi_index'])
        while not it.finished:
            idx = it.multi_index
            is_on_boundary = False
            for d in range(self.dimensions):
                # Check if current index is on any dimension's boundary
                if idx[d] == 0 or idx[d] == shape_dims[d] - 1:
                    is_on_boundary = True
                    break

            # If it's a boundary 0
            if is_on_boundary and self._shape_array[idx] == 0:
                boundary_labels.add(labeled_regions[idx])
            it.iternext()

        # If there's any labeled region of 0s that *doesn't* touch the boundary,
        # then it's an enclosed region, and the shape is closed.
        return num_features > len(boundary_labels)

    @functools.lru_cache(maxsize=None)
    def _get_flux_internal(self, distribution_id_tuple: Tuple[Any, ...]) -> float:
        """
        Internal cached method to compute flux. Assumes _intensity_array is populated
        correctly for the given distribution_id_tuple.

        Args:
            distribution_id_tuple (tuple): A unique, hashable identifier for the
                                           distribution and coordinate system used.

        Returns:
            float: The computed flux.
        """
        # This check should ideally not be hit if `get_flux` is called correctly,
        # as `get_flux` ensures `_intensity_array` and `_current_distribution_id`
        # are in sync before calling this cached method.
        if self._intensity_array is None or self._current_distribution_id != distribution_id_tuple:
            raise RuntimeError(
                "Intensity array not correctly populated or synced with cache key. "
                "This indicates an internal caching or state management issue."
            )

        # Identify the interior points: cells that were originally 0 but are filled by holes.
        filled_array = scipy.ndimage.binary_fill_holes(self._shape_array)
        interior_mask = (filled_array == 1) & (self._shape_array == 0)

        # Sum intensities only within the identified interior region
        return float(np.sum(self._intensity_array[interior_mask]))

    def fill_intensity_array(self, distribution: Distribution, *coords_arrays: np.ndarray) -> None:
        """
        Fills the shape's domain with intensity values from the given distribution.
        This method computes the `_intensity_array` which will be used for flux calculations.

        Args:
            distribution (Distribution): An instance of the Distribution class.
            *coords_arrays (np.ndarray): Variable number of 1D NumPy arrays, each defining
                the coordinate values along a dimension (x, y, z, ...). The number of arrays
                must match the shape's dimensions. If no coordinate arrays are provided,
                integer indices (0 to dim_size-1) are used for each dimension.

        Raises:
            TypeError: If `distribution` is not a `Distribution` instance.
            ValueError: If the number or shape of `coords_arrays` is incorrect.
        """
        if not isinstance(distribution, Distribution):
            raise TypeError(
                "`distribution` must be an instance of the `Distribution` class.")

        dims = self.shape_array.shape
        num_dims = self.dimensions

        # Prepare coordinate grids based on provided or default indices
        coord_grids = []
        if coords_arrays:  # If coordinate arrays are provided
            if len(coords_arrays) != num_dims:
                raise ValueError(
                    f"Number of coordinate arrays ({len(coords_arrays)}) must "
                    f"match the shape's dimensions ({num_dims})."
                )
            for i, c_arr in enumerate(coords_arrays):
                if not isinstance(c_arr, np.ndarray) or c_arr.ndim != 1 or c_arr.size != dims[i]:
                    raise ValueError(
                        f"Coordinate array for dimension {i} is invalid: must be "
                        f"a 1D NumPy array with size {dims[i]}."
                    )
                coord_grids.append(c_arr)
        else:  # Use integer indices (0, 1, 2...) if no coordinate arrays provided
            for d in range(num_dims):
                coord_grids.append(np.arange(dims[d]))

        # Generate the N-D coordinate meshgrid for all points in the array
        mesh_coords = np.meshgrid(*coord_grids, indexing='ij')

        # Create a unique ID for the distribution + coordinates setup for caching
        # This makes the cache key more robust than just distribution.name
        # It hashes the coordinate arrays for uniqueness.
        coord_hashes = tuple(hash(tuple(c.tolist())) for c in coord_grids)
        self._current_distribution_id = (
            distribution.name, coord_hashes)

        # Initialize raw intensity array
        intensity_values = np.zeros(dims, dtype=float)

        # Attempt vectorized application of the distribution function
        try:
            # Test if function supports vectorized input by passing small arrays
            test_inputs = [np.array([1.0, 2.0], dtype=float)
                           for _ in range(num_dims)]
            test_output = distribution(*test_inputs)

            if isinstance(test_output, np.ndarray) and test_output.shape == (2,):
                # If it supports, flatten meshgrid coordinates and apply once
                flattened_coords = [m.ravel() for m in mesh_coords]
                intensity_values = distribution(
                    *flattened_coords).reshape(dims)
            else:
                # Fallback to element-wise application if not vectorized
                raise TypeError(
                    "Distribution function does not appear to support vectorized input.")

        except (TypeError, ValueError, IndexError, AttributeError):
            # Fallback for non-vectorized functions or if the heuristic fails
            warnings.warn(
                f"Distribution '{distribution.name}' function does not support direct "
                f"vectorized input or an error occurred during vectorized test. "
                f"Falling back to slower element-wise computation. Consider optimizing "
                f"your distribution function for NumPy array inputs if performance is critical."
            )
            it = np.nditer(intensity_values, flags=[
                           'multi_index'], op_flags=['writeonly'])
            while not it.finished:
                current_coords = it.multi_index
                intensity_values[current_coords] = distribution(
                    *current_coords)
                it.iternext()

        # Apply normalization if specified by the distribution
        self._intensity_array = intensity_values

        # Invalidate the internal flux cache for all distribution IDs,
        # as the underlying intensity array has now changed.
        self._get_flux_internal.cache_clear()

    def get_flux(self, distribution: Distribution, *coords_arrays: np.ndarray) -> float:
        """
        Computes the total flux (sum of intensity values) within the enclosed region
        of the shape, given a distribution of intensity.

        The flux is only well-defined and computed if the shape is closed.

        Args:
            distribution (Distribution): An instance of the Distribution class.
            *coords_arrays (np.ndarray): Variable number of 1D NumPy arrays, each defining
                the coordinate values along a dimension (x, y, z, ...). The number of arrays
                must match the shape's dimensions. If no coordinate arrays are provided,
                integer indices (0 to dim_size-1) are used for each dimension.

        Returns:
            float: The total sum of intensity values within the enclosed region.
                   Returns 0.0 if the shape is not closed, or if SciPy is not available.
                   Returns 0.0 if there is no enclosed region.
        """

        if not self.is_closed:
            warnings.warn(
                "Shape is not closed. Flux is ill-defined for border shapes. "
                "Returning 0.0."
            )
            return 0.0

        # Populate or re-populate the intensity array based on the distribution and coordinates
        self.fill_intensity_array(distribution, *coords_arrays)

        # Retrieve flux from cache using the unique ID generated by fill_intensity_array
        return self._get_flux_internal(self._current_distribution_id)

    def get_enclosed_intensity_array(self) -> np.ndarray:
        """
        Returns an array showing the intensity values only within the enclosed region,
        with 0s elsewhere. Requires `fill_intensity_array` to have been called.

        Returns:
            np.ndarray: An array of the same shape as the original, with intensity values
                        in the enclosed region and 0s elsewhere.
                        Returns an array of zeros if the shape is not closed.

        Raises:
            RuntimeError: If `fill_intensity_array` has not been called prior to this method.
        """
        if self._intensity_array is None:
            raise RuntimeError(
                "Intensity array not filled. Call `fill_intensity_array` first.")

        if not self.is_closed:
            warnings.warn(
                "Shape is not closed. No defined enclosed region to visualize.")
            return np.zeros_like(self._shape_array, dtype=float)

        filled_array = scipy.ndimage.binary_fill_holes(self._shape_array)
        # Identify interior points: where filled_array is 1 AND original shape_array was 0
        interior_mask = (filled_array == 1) & (self._shape_array == 0)

        enclosed_intensity = np.zeros_like(self._intensity_array, dtype=float)
        enclosed_intensity[interior_mask] = self._intensity_array[interior_mask]
        return enclosed_intensity

    def get_full_intensity_array(self) -> np.ndarray:
        """
        Returns the full intensity array computed by the last call to `fill_intensity_array`.
        This array contains intensity values for all points in the domain, not just the enclosed region.

        Returns:
            np.ndarray: The full intensity array.

        Raises:
            RuntimeError: If `fill_intensity_array` has not been called prior to this method.
        """
        if self._intensity_array is None:
            raise RuntimeError(
                "Intensity array not filled. Call `fill_intensity_array` first.")
        # Return a copy to prevent external modification
        return self._intensity_array.copy()

    def __str__(self) -> str:
        """
        Provides a user-friendly string representation of the NdShape object.
        """
        closed_status = self.is_closed

        flux_info = "N/A (call .get_flux() to compute)"
        if self._intensity_array is not None:
            # _current_distribution_id is a tuple (name, normalize, coord_hashes)
            flux_info = f"Intensity filled with '{self._current_distribution_id[0]}'" + \
                (" (normalized)" if self._current_distribution_id[1] else "")
            if self.is_closed:
                # Cannot compute flux in __str__ without passing distribution and coords again.
                # Just indicate it's ready.
                flux_info += ", flux ready (call .get_flux())."
            else:
                flux_info += ", flux N/A (not closed)."

        return (f"NdShape("
                f"dimensions={self.dimensions}, "
                f"shape={self.shape_array.shape}, "
                f"is_closed={closed_status}, "
                f"status='{flux_info}'"
                f")")

    def __repr__(self) -> str:
        """
        Provides a more detailed, unambiguous string representation of the NdShape object,
        suitable for recreation.
        """
        # For repr, we only represent the initial shape_array
        return (f"NdShape("
                f"shape_array=np.array({self.shape_array.tolist()}, "
                f"dtype={self.shape_array.dtype}))")
