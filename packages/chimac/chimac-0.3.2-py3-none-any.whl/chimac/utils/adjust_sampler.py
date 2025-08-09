import math
from math import erfc
from typing import Optional

import numpy as np


def adjust_and_sample(
    k: float, phi: int, alpha: float = 0.05, rng: Optional[np.random.Generator] = None
) -> bool:
    """Adjust DOF and sample a chi-square variable, then compute p-value using erfc.

    Args:
        k: base degrees of freedom.
        phi: number of elements already sampled (phi in the paper).
        alpha: significance level.
        rng: optional numpy Generator for deterministic behavior.

    Returns:
        True if the sampled p-value < alpha (meaning we select the operation), else False.
    """
    if rng is None:
        rng = np.random.default_rng()

    k_adj = float(k) / math.sqrt(phi + 1.0)
    # Ensure k_adj is positive and not too small to avoid degenerate chisq draw
    k_adj = max(k_adj, 1e-6)

    # Draw from chi-square with adjusted dof
    sample = rng.chisquare(df=k_adj)

    # p-value as in the paper: p = 0.5 * erfc(sqrt(x/2))
    p_value = 0.5 * erfc(math.sqrt(sample / 2.0))

    return p_value < alpha
