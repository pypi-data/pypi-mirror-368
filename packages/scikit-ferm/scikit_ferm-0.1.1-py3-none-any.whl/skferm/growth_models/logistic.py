import numpy as np


def logistic_growth(t: np.typing.ArrayLike, N0: float, Nmax: float, r: float) -> np.ndarray:
    """
    Simulate microbial growth using the logistic growth model.

    Parameters:
    - t (array-like): Time points.
    - N0 (float): Initial population size.
    - Nmax (float): Maximum population size (carrying capacity).
    - r (float): Growth rate.

    Returns:
    - array-like: Population at each time point.
    """
    t = np.asarray(t)
    return Nmax / (1 + ((Nmax - N0) / N0) * np.exp(-r * t))
