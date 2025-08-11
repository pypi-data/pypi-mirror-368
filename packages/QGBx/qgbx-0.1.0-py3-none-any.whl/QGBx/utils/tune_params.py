import numpy as np
from scipy.optimize import least_squares


def flatten_indices(N):
    """
    Precompute start indices in a flattened vector representing
    the triangular structure of a Galton board with N rows.

    Each row i has (i+1) pegs; this function returns an array
    of offsets where each row's block begins in the flat vector.
    
    Args:
        N (int): Number of rows.

    Returns:
        np.ndarray: Array of start indices for each row.
    """
    offsets = np.cumsum([0] + [i + 1 for i in range(N)])[:-1]
    return offsets


def galton_bin_probs_flat(x, N):
    """
    Given a flat vector x of length M = N*(N+1)//2 representing per-peg
    right-turn probabilities in a triangular Galton board, compute the
    final bin probabilities after N rows.

    Args:
        x (array-like): Flat array of peg probabilities.
        N (int): Number of rows.

    Returns:
        np.ndarray: Probability distribution over bins (length N+1).
    """
    offsets = flatten_indices(N)
    dp = np.zeros((N + 1, N + 1))
    dp[0, 0] = 1.0

    for i in range(N):
        p_row = x[offsets[i]: offsets[i] + (i + 1)]
        for k in range(i + 1):
            prob_here = dp[i, k]
            if prob_here == 0:
                continue
            pi = p_row[k]
            dp[i + 1, k] += prob_here * (1 - pi)
            dp[i + 1, k + 1] += prob_here * pi

    return dp[N]


def solve_per_peg(N, target, x0=None, bounds=(0, 1), **lsq_kwargs):
    """
    Solve for each peg's right-turn probability in a Galton board
    to approximate a desired target bin distribution.

    Args:
        N (int): Number of rows.
        target (array-like): Desired bin distribution (length N+1, sums to 1).
        x0 (array-like, optional): Initial guess for peg probabilities.
            Defaults to 0.5 for all pegs.
        bounds (tuple, optional): Bounds for each peg probability. Defaults to (0, 1).
        **lsq_kwargs: Additional keyword arguments for scipy.optimize.least_squares.

    Returns:
        OptimizeResult: Result of least squares optimization. The `.x` attribute
        contains the optimized peg probabilities in flat form.
    """
    target = np.asarray(target, float)
    if target.shape[0] != N + 1:
        raise ValueError(f"target must have length N+1 = {N+1}")
    if not np.isclose(target.sum(), 1.0):
        raise ValueError("target must sum to 1")

    M = N * (N + 1) // 2
    if x0 is None:
        x0 = 0.5 * np.ones(M)
    else:
        x0 = np.asarray(x0, float)
        if x0.shape[0] != M:
            raise ValueError(f"x0 must have length {M}")

    def resid(x):
        return galton_bin_probs_flat(x, N) - target

    res = least_squares(resid, x0, bounds=bounds, **lsq_kwargs)
    return res


def rx_angles_from_probabilities(probs):
    """
    Convert measurement probabilities p = P(|1⟩) to RX rotation angles θ,
    where sin²(θ/2) = p, so θ = 2 * arcsin(√p).

    Args:
        probs (array-like): Probabilities in [0,1].

    Returns:
        np.ndarray: Corresponding RX rotation angles in radians.
    """
    probs = np.clip(probs, 0, 1)
    return 2 * np.arcsin(np.sqrt(probs))


def cos_angles_from_probabilities(probs):
    """
    Convert measurement probabilities p = P(|1⟩) to RX rotation angles θ,
    using cos formulation: θ = 2 * arccos(√p).

    Args:
        probs (array-like): Probabilities in [0,1].

    Returns:
        np.ndarray: Corresponding RX rotation angles in radians.
    """
    probs = np.clip(probs, 0, 1)
    return 2 * np.arccos(np.sqrt(probs))


def probabilities_from_rx_angles(thetas):
    """
    Convert RX rotation angles θ to measurement probabilities p = sin²(θ/2).

    Args:
        thetas (array-like): RX angles in radians.

    Returns:
        np.ndarray: Corresponding measurement probabilities.
    """
    thetas = np.array(thetas)
    return np.sin(thetas / 2) ** 2


def galton_bin_probs_layer(p):
    """
    Compute the probability distribution over bins for a Galton board
    with per-row right-turn probabilities p.

    Args:
        p (array-like): Length n, probabilities for each row.

    Returns:
        np.ndarray: Probability distribution over n+1 bins.
    """
    probs = np.array([1.0])
    for pi in p:
        probs = np.convolve(probs, [1 - pi, pi])
    return probs


def solve_galton_layer(target, p_init=None, bounds=(0, 1), **lsq_kwargs):
    """
    Solve for per-row probabilities p such that the Galton board output
    distribution matches the target.

    Args:
        target (array-like): Desired distribution (length n+1, sums to 1).
        p_init (array-like, optional): Initial guess for p. Defaults to 0.5.
        bounds (tuple, optional): Bounds for p values. Defaults to (0, 1).
        **lsq_kwargs: Extra args passed to scipy.optimize.least_squares.

    Returns:
        OptimizeResult: Result of least squares optimization.
    """
    target = np.asarray(target, dtype=float)
    n = len(target) - 1

    if p_init is None:
        p_init = 0.5 * np.ones(n)
    elif len(p_init) != n:
        raise ValueError(f"p_init must have length {n}.")
    if not np.isclose(target.sum(), 1.0):
        raise ValueError("Target distribution must sum to 1.")

    def residuals(p):
        probs = galton_bin_probs_layer(p)
        return probs - target

    return least_squares(residuals, p_init, bounds=bounds, **lsq_kwargs)


def reconstruct_original_rows(flat_probs, N):
    """
    Reconstruct the original non-reversed rows from a flattened
    reversed-row vector representation.

    Args:
        flat_probs (list or array): Flattened list with reversed rows.
        N (int): Number of rows.

    Returns:
        list: Flattened list with original row ordering restored.
    """
    offsets = flatten_indices(N)
    original = []
    idx = 0
    for i in range(N):
        row_len = i + 1
        row = flat_probs[idx: idx + row_len][::-1]  # reverse row back
        original.extend(row)
        idx += row_len
    return original
