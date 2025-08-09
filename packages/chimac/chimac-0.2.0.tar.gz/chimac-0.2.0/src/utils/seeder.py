import os
import random
from typing import Optional

import numpy as np
import torch
from logger import Logger


def seed_all(
    seed: int = 42, logger: Optional[Logger] = None, deterministic: bool = True
) -> None:
    """
    Seed all relevant random number generators for reproducibility.

    Args:
        seed (int): The seed value to use for all RNGs.
        logger (Optional[Logger]): Logger instance to use for logging. Defaults to None.
        deterministic (bool): If True, enables deterministic PyTorch operations.
    """
    # --- Python & NumPy ---
    random.seed(seed)
    np.random.seed(seed)

    # --- PyTorch (CPU & GPU) ---
    torch.manual_seed(seed)
    torch.cuda.manual_seed(seed)
    torch.cuda.manual_seed_all(seed)  # for multi-GPU setups

    # --- CuDNN Settings ---
    if deterministic:
        torch.backends.cudnn.deterministic = True
        torch.backends.cudnn.benchmark = False
        # Use deterministic algorithms if supported
        if hasattr(torch, "use_deterministic_algorithms"):
            torch.use_deterministic_algorithms(True)
    else:
        torch.backends.cudnn.benchmark = True

    # --- Environment ---
    os.environ["PYTHONHASHSEED"] = str(seed)

    # --- Logging ---
    msg = f"Random seed set to {seed} | Deterministic mode: {deterministic}"
    if logger:
        logger.info(msg)
    else:
        print(msg)

    if deterministic:
        note = "Warning: Deterministic mode may reduce training speed."
        if logger:
            logger.warning(note)
        else:
            print(note)
