import numpy as np


def gompertz(t: np.typing.ArrayLike, a: float, b: float, c: float):
    """
    Predict the value at time t using the modified Gompertz function.

    Parameters:
    t (float or array-like): The time at which to predict the value.
    a (float): The upper asymptote.
    b (float): The displacement along the time axis.
    c (float): The growth rate.

    Returns:
    float or array-like: The function value at time t.
    """
    return a * np.exp(-b * np.exp(-np.array(c) * t))


def modified_gompertz(t: np.typing.ArrayLike, A: float, L: float, mu: float):
    """modified gompertz as proposed by Zwietering et al. 1990

    This gompertz has more interpretable parameters than the original gompertz.

    Args:
        t (float or array-like): The time at which to predict the value.
        A (float): The upper asymptote.
        L (float): The lag phase
        mu (float): The maximum specific growth rate

    Returns:
    float or array-like: The function value at time t.
    """

    return A * np.exp(-np.exp(mu * np.exp(1) / A * (np.array(L) - t) + 1))


# Example usage:
if __name__ == "__main__":
    a, b, c = 1.0, 1.0, 1.0
    t_values = np.linspace(0, 10, 100)
    y = gompertz(t_values, a, b, c)
