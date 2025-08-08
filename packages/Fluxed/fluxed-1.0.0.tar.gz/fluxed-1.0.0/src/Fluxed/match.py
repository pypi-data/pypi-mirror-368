import numpy as np
from scipy.optimize import minimize
import warnings

from Fluxed.shapes import NdShape
from Fluxed.distributions import Distribution


def match_flux_parameters(
    source_shape: NdShape,
    source_dist: Distribution,
    target_shape: NdShape,
    TargetDistClass: type,
    param_names: list[str],
    initial_guess: list[float],
    source_coords_arrays: tuple = (),
    target_coords_arrays: tuple = (),
    bounds: list[tuple] = None,
    optimizer_options: dict = None,
) -> dict:
    """
    Computes the parameters for a new distribution on a target shape such that
    its flux matches the flux of a source shape and distribution.

    This is achieved by using a numerical optimizer to minimize the squared
    difference between the two fluxes.

    Args:
        source_shape (NdShape): The shape object for the source flux.
        source_dist (Distribution): The fully configured distribution for the source flux.
        target_shape (NdShape): The shape object for which parameters are being found.
        TargetDistClass (type): The class of the new distribution (e.g., NormalDistribution2D).
        param_names (list[str]): A list of the parameter names (as strings) to be optimized.
                                 These must match the __init__ arguments of TargetDistClass.
                                 Example: ['mean_x', 'mean_y', 'stddev_x']
        initial_guess (list[float]): An initial guess for each parameter in param_names.
                                     The optimizer starts its search from here.
        source_coords_arrays (tuple, optional): Coordinate arrays for the source shape.
        target_coords_arrays (tuple, optional): Coordinate arrays for the target shape.
        bounds (list[tuple], optional): Bounds for each parameter to constrain the search space.
                                        Example: [(0, 10), (0, 10), (0.1, None)] for mean_x, mean_y, stddev_x.
                                        `None` signifies no bound.
        optimizer_options (dict, optional): A dictionary of options to pass to the
                                            scipy.optimize.minimize function.

    Returns:
        dict: A dictionary containing the optimization result:
              - 'success' (bool): Whether the optimizer converged successfully.
              - 'message' (str): A message from the optimizer.
              - 'parameters' (dict): The optimal parameters found.
              - 'final_flux' (float): The flux achieved with the optimal parameters.
              - 'target_flux' (float): The original target flux.
    """
    # Calculate the target flux. This is a constant.
    print(f"Calculating target flux from source shape and {source_dist.name}...")
    target_flux = source_shape.get_flux(source_dist, *source_coords_arrays)
    print(f"Target Flux = {target_flux:.4f}")

    if not target_shape.is_closed:
        warnings.warn(
            "Target shape is not closed. Flux matching is not possible. Returning failure."
        )
        return {
            "success": False,
            "message": "Target shape is not closed.",
            "parameters": None,
            "final_flux": 0.0,
            "target_flux": target_flux,
        }

    # Define the objective function for the optimizer
    # This function takes a vector of parameters 'p' and returns the squared error.
    # It uses a closure to "remember" the other necessary variables.
    def objective_function(p: np.ndarray) -> float:
        # Create a dictionary mapping parameter names to their current guessed values
        params_dict = dict(zip(param_names, p))

        # Create an instance of the target distribution with the current parameters
        try:
            current_dist = TargetDistClass(**params_dict)
        except Exception as e:
            # If the parameters are invalid (e.g., stddev=0), return a large error
            warnings.warn(
                f"Could not instantiate {TargetDistClass.__name__} with params {params_dict}: {e}"
            )
            return 1e12  # Return a large penalty

        # Calculate the flux for this new distribution
        current_flux = target_shape.get_flux(current_dist, *target_coords_arrays)

        # Calculate and return the squared difference
        error = (current_flux - target_flux) ** 2
        return error

    # Run the optimizer
    print(f"\nOptimizing parameters {param_names} for {TargetDistClass.__name__}...")

    method = "L-BFGS-B" if bounds else "Nelder-Mead"

    result = minimize(
        fun=objective_function,
        x0=np.array(initial_guess),
        method=method,
        bounds=bounds,
        options=optimizer_options,
    )

    # Format and return the result
    if result.success:
        print("Optimization successful!")
    else:
        warnings.warn(f"Optimization may have failed: {result.message}")

    final_params = dict(zip(param_names, result.x))
    final_dist = TargetDistClass(**final_params)
    final_flux = target_shape.get_flux(final_dist, *target_coords_arrays)

    return {
        "success": result.success,
        "message": result.message,
        "parameters": final_params,
        "final_flux": final_flux,
        "target_flux": target_flux,
    }
