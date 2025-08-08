import numpy as np

# This file contains the implementation of various probability distributions
# Custom distributions can inherit from the Distribution class


class Distribution:
    """
    Callable base class for all probability distributions.
    This class provides a common interface for all distributions.
    It should be inherited by all custom distributions.

    Attributes:
        name (str): The name of the distribution.
        func (callable): The function that defines the distribution.
        vars (tuple): The variable names for the parameters of the distribution from func.
    """

    def __init__(self, name: str, func: callable):
        self.name: str = name
        self.func: callable = func
        # Get parameter names from the function signature
        self.vars = func.__code__.co_varnames[: func.__code__.co_argcount]
        self._validate()

    def _validate(self):
        if not callable(self.func):
            raise TypeError(f"{self.name} must be a callable function.")

    def __call__(self, *args, **kwargs):
        """
        Call the distribution function with the provided arguments.
        This method allows both positional and keyword arguments to be passed
        to the underlying numpy-compatible function.
        """
        return self.func(*args, **kwargs)

    def __str__(self):
        return f"Distribution(name='{self.name}', vars={self.vars})"

    def __repr__(self):
        return f"Distribution(name='{self.name}', func={self.func.__name__})"


class NormalDistribution1D(Distribution):
    """
    Normal distribution in 1D.
    """

    def __init__(self, mean: float = 0.0, stddev: float = 1.0):
        def normal_func(x):
            return (1 / (stddev * np.sqrt(2 * np.pi))) * np.exp(
                -0.5 * ((x - mean) / stddev) ** 2
            )

        super().__init__("NormalDistribution1D", normal_func)
        self.mean = mean
        self.stddev = stddev


class NormalDistribution2D(Distribution):
    """
    Normal distribution in 2D.
    """

    def __init__(
        self,
        mean_x: float = 0.0,
        mean_y: float = 0.0,
        stddev_x: float = 1.0,
        stddev_y: float = 1.0,
    ):
        def normal_func(x, y):
            return (1 / (2 * np.pi * stddev_x * stddev_y)) * np.exp(
                -0.5 * (((x - mean_x) / stddev_x) ** 2 + ((y - mean_y) / stddev_y) ** 2)
            )

        super().__init__("NormalDistribution2D", normal_func)
        self.mean_x = mean_x
        self.mean_y = mean_y
        self.stddev_x = stddev_x
        self.stddev_y = stddev_y


class UniformDistribution(Distribution):
    """
    Uniform distribution in Nd.
    """

    def __init__(self, value: float = 1.0):
        def uniform_func(*args) -> float:
            if args and isinstance(args[0], np.ndarray):
                # Return a new array of the same shape as the input, filled with `value`.
                return np.full_like(args[0], fill_value=value, dtype=float)
            else:
                # Otherwise, we are in a scalar context, so just return the value.
                return value

        super().__init__("UniformDistribution", uniform_func)
        self.value = value


class LinearDistribution1D(Distribution):
    """
    Linear distribution in 1D.
    """

    def __init__(
        self, slope: float = 1.0, intercept: float = 0.0, domain: tuple = (0.0, 1.0)
    ):
        def linear_func(x) -> float:
            return slope * x + intercept

        super().__init__("LinearDistribution1D", linear_func)
        self.slope = slope
        self.intercept = intercept
        self.domain = domain


class LinearDistribution2D(Distribution):
    """
    Linear distribution in 2D.
    """

    def __init__(
        self,
        slope_x: float = 1.0,
        slope_y: float = 1.0,
        intercept_x: float = 0.0,
        intercept_y: float = 0.0,
        domain: tuple = ((0.0, 1.0), (0.0, 1.0)),
    ):
        def linear_func(x, y) -> float:
            return slope_x * x + slope_y * y + intercept_x + intercept_y

        super().__init__("LinearDistribution2D", linear_func)
        self.slope_x = slope_x
        self.slope_y = slope_y
        self.intercept_x = intercept_x
        self.intercept_y = intercept_y
        self.domain = domain


class ExponentialDistribution1D(Distribution):
    """
    Exponential distribution in 1D.
    """

    def __init__(self, rate: float = 1.0, domain: tuple = (0.0, 1.0)):
        def exponential_func(x) -> float:
            return rate * np.exp(-rate * x)

        super().__init__("ExponentialDistribution1D", exponential_func)
        self.rate = rate
        self.domain = domain


class ExponentialDistribution2D(Distribution):
    """
    Exponential distribution in 2D.
    """

    def __init__(
        self,
        rate_x: float = 1.0,
        rate_y: float = 1.0,
        domain: tuple = ((0.0, 1.0), (0.0, 1.0)),
    ):
        def exponential_func(x, y) -> float:
            return rate_x * np.exp(-rate_x * x) * rate_y * np.exp(-rate_y * y)

        super().__init__("ExponentialDistribution2D", exponential_func)
        self.rate_x = rate_x
        self.rate_y = rate_y
        self.domain = domain
