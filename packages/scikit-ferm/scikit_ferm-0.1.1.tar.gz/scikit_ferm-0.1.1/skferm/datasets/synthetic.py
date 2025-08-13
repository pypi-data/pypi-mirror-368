import numpy as np
import numpy.typing as npt

from skferm.growth_models.gompertz import gompertz, modified_gompertz
from skferm.growth_models.logistic import logistic_growth


def generate_synthetic_growth(time: npt.ArrayLike, model: str = "logistic", noise_std: float = 0.0, **kwargs) -> dict:
    """
    Generate synthetic growth data using specified growth model.

    Parameters
    ----------
    - time (array-like): Time points.
    - model (str): Growth model to use ("logistic", "monod", etc.).
    - noise_std (float): Standard deviation of Gaussian noise to add.
    **kwargs: Parameters for the growth model.

    Returns
    -------
    - dict: A dictionary with time and population arrays.
    """
    if model == "logistic":
        growth_function = logistic_growth
    elif model == "gompertz":
        growth_function = gompertz
    elif model == "modified_gompertz":
        growth_function = modified_gompertz
    else:
        raise ValueError(f"Unsupported model: {model}")

    time = np.asarray(time)
    population = growth_function(time, **kwargs)
    noise = np.random.normal(loc=0.0, scale=noise_std, size=len(population))
    return {"time": time, "population": population + noise}
