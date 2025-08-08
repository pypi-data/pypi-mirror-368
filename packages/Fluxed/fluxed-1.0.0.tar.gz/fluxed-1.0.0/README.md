# Fluxed

[![PyPI Version](https://img.shields.io/pypi/v/Fluxed.svg?style=flat-square)](https://pypi.org/project/Fluxed/)
[![Build Status](https://img.shields.io/travis/com/CrazeXD/Fluxed.svg?style=flat-square)](https://travis-ci.com/CrazeXD/Fluxed)
[![License: GPL v3](https://img.shields.io/badge/License-GPLv3-blue.svg?style=flat-square)](https://www.gnu.org/licenses/gpl-3.0)

**Fluxed** is a Python package for defining N-dimensional shapes and computing the flux of arbitrary intensity distributions through them. It features a powerful tool to numerically find distribution parameters that match a desired flux value, enabling comparisons across different geometries and distributions.

Built on `numpy` and `scipy`, Fluxed provides an intuitive, array-based interface for complex spatial analysis.

## Key Features

-   **N-Dimensional Shapes**: Define complex shapes and borders in any number of dimensions using simple NumPy arrays.
-   **Automated Boundary Detection**: Automatically determines if a shape's border is closed and encloses a valid region for flux calculation.
-   **Flux Computation**: Calculates the integrated flux (sum of intensity) within a closed shape for any given intensity distribution.
-   **Rich Distribution Library**: Comes with common distributions like `Normal`, `Uniform`, `Linear`, and `Exponential` in 1D and 2D.
-   **Custom Distributions**: Easily extend the framework with your own custom, callable distribution functions.
-   **Flux Matching**: The core feature—numerically optimize the parameters of a target distribution to match the flux of a source shape. This is perfect for modeling, simulation, and comparative analysis.

## Installation

Fluxed is available on PyPI. You can install it using pip:

```bash
pip install Fluxed
```

The package requires `numpy` and `scipy`, which will be installed automatically as dependencies.

## Core Concepts

### 1. `NdShape`
An `NdShape` object represents a shape in N-dimensional space. You create it from a NumPy array where `1`s define the border and `0`s represent empty space. The class can automatically determine if the border is `is_closed` and can calculate the flux within this enclosed region.

### 2. `Distribution`
A `Distribution` is a callable object that returns an intensity value for a given coordinate. The library provides several ready-to-use distributions (e.g., `NormalDistribution2D`), and you can easily create your own by inheriting from the `Distribution` base class.

### 3. Flux
In the context of this package, "flux" is the sum of all intensity values from a `Distribution` over the discrete points *inside* the enclosed region of an `NdShape`. It's a discrete integral of the intensity over the shape's area or volume.

## Quickstart

Let's walk through a complete example, from calculating a simple flux to using the advanced flux-matching feature.

### Step 1: Define a Shape

First, let's create a simple 2D shape: a 3x3 hollow square within a 5x5 grid.

```python
import numpy as np
from Fluxed.shapes import NdShape

# 1s are the border, 0s are the interior/exterior
border_array = np.array([
    [1, 1, 1, 1, 1],
    [1, 0, 0, 0, 1],
    [1, 0, 0, 0, 1],
    [1, 0, 0, 0, 1],
    [1, 1, 1, 1, 1],
], dtype=int)

my_shape = NdShape(border_array)

print(f"Shape is {my_shape.dimensions}D")
print(f"Is the shape closed? {my_shape.is_closed}")

# > Shape is 2D
# > Is the shape closed? True
```

### Step 2: Calculate a Simple Flux

Now, let's calculate the flux using a `UniformDistribution`. With a value of `1.0`, the flux will be equal to the enclosed area.

```python
from Fluxed.distributions import UniformDistribution

# Create a distribution where the intensity is 1.0 everywhere
uniform_dist = UniformDistribution(value=1.0)

# Calculate the flux
total_flux = my_shape.get_flux(uniform_dist)

# The enclosed area is 3x3 = 9. The flux should be 9.0.
print(f"Total flux for uniform distribution: {total_flux}")

# > Total flux for uniform distribution: 9.0
```

### Step 3: Match Flux with a Different Distribution

This is where Fluxed shines. Let's say we have a source of energy that produces a total flux of **90.0**. We want to model this energy source on our shape using a `NormalDistribution2D` (a Gaussian). What should the parameters of the Gaussian be (`mean`, `stddev`) to produce the same total flux?

The `match_flux_parameters` function solves this for us.

```python
from Fluxed.distributions import NormalDistribution2D
from Fluxed.match import match_flux_parameters

# --- Source ---
# Our source is a uniform distribution with value 10.0
# The enclosed area is 9, so the target flux is 9 * 10.0 = 90.0
source_dist = UniformDistribution(value=10.0)

# --- Target ---
# We want to find the parameters for a NormalDistribution2D
# that will also produce a flux of 90.0 on the same shape.
TargetDistClass = NormalDistribution2D

# We want the optimizer to find the standard deviations.
# We'll fix the mean to be the center of the grid (2, 2).
# To do this, we create a simple wrapper.
class CenteredNormal(NormalDistribution2D):
    def __init__(self, stddev_x: float = 1.0, stddev_y: float = 1.0):
        # Fix the mean to the center of our 5x5 grid
        super().__init__(mean_x=2.0, mean_y=2.0, stddev_x=stddev_x, stddev_y=stddev_y)

# Parameters for the optimizer to find
params_to_find = ['stddev_x', 'stddev_y']
initial_guess = [1.0, 1.0]  # An initial guess for the standard deviations
bounds = [(0.1, None), (0.1, None)] # Stddev must be positive

# --- Run the optimizer ---
result = match_flux_parameters(
    source_shape=my_shape,
    source_dist=source_dist,
    target_shape=my_shape,
    TargetDistClass=CenteredNormal,
    param_names=params_to_find,
    initial_guess=initial_guess,
    bounds=bounds
)

# --- Analyze the result ---
if result['success']:
    print("Optimization successful!")
    print(f"Target Flux: {result['target_flux']:.4f}")
    print(f"Achieved Flux: {result['final_flux']:.4f}")
    print("Found optimal parameters:")
    for param, value in result['parameters'].items():
        print(f"  {param}: {value:.4f}")
else:
    print(f"Optimization failed: {result['message']}")
```

**Example Output:**
```
Calculating target flux from source shape and UniformDistribution...
Target Flux = 90.0000

Optimizing parameters ['stddev_x', 'stddev_y'] for CenteredNormal...
Optimization successful!
Target Flux: 90.0000
Achieved Flux: 90.0000
Found optimal parameters:
  stddev_x: 1.2585
  stddev_y: 1.2585
```
The result tells us that a 2D Normal distribution centered at (2, 2) with a standard deviation of approximately 1.26 along both axes will produce the same total flux as a uniform distribution of value 10.

## Creating a Custom Distribution

It's easy to define your own distributions. Just inherit from `Distribution` and provide a callable function.

Let's create a 1D distribution that varies with the sine of the x-coordinate.

```python
import numpy as np
from Fluxed.distributions import Distribution

class SineDistribution1D(Distribution):
    """A custom distribution where intensity varies sinusoidally."""
    def __init__(self, frequency: float = 1.0, amplitude: float = 1.0):
        # The function must accept arguments corresponding to the dimensions
        # of the space it will be used in.
        def sine_func(x):
            # We add `amplitude` to ensure intensity is always non-negative
            return amplitude * np.sin(frequency * x) + amplitude

        # Call the parent constructor
        super().__init__("SineDistribution1D", sine_func)
        self.frequency = frequency
        self.amplitude = amplitude

# --- Usage ---
shape_1d = NdShape(np.array([1, 0, 0, 0, 1])) # A simple 1D enclosed space
my_sine_dist = SineDistribution1D(frequency=np.pi/2, amplitude=10)

# The function will be evaluated at x=1, 2, 3
# sin(pi/2*1) = 1  -> intensity = 10*1 + 10 = 20
# sin(pi/2*2) = 0  -> intensity = 10*0 + 10 = 10
# sin(pi/2*3) = -1 -> intensity = 10*(-1) + 10 = 0
# Expected flux = 20 + 10 + 0 = 30
flux = shape_1d.get_flux(my_sine_dist)
print(f"Flux for custom sine distribution: {flux}")
# > Flux for custom sine distribution: 30.0
```

## Running Tests

To run the test suite from a local clone of the repository, install the development dependencies and run `pytest`.

```bash
git clone https://github.com/CrazeXD/Fluxed.git
cd Fluxed
pip install -r requirements.txt  # Or similar for dev dependencies
pip install pytest
pytest
```

## Contributing

Contributions are welcome! If you have ideas for new features, distributions, or improvements, please open an issue to discuss it first. Pull requests are also appreciated.

## License

This project is licensed under the GNU General Public License v3.0 - see the [LICENSE](LICENSE) file for details.