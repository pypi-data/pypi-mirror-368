from typing import Callable, List, Optional

import numpy as np
from PIL import Image

from ..utils.adjust_sampler import adjust_and_sample
from . import __name__


class ChiMAC:
    def __init__(
        self,
        f_aug: List[Callable[[Image.Image], Image.Image]],
        k: float = 4.0,
        alpha: float = 0.05,
        seed: Optional[int] = None,
    ):
        """Initialize the Chi-MAC augmenter.

        Args:
            f_aug: ordered list of augmentation callables (each callable takes and returns a PIL image)
            k: base degrees of freedom for chi-square
            alpha: significance level used in AdjustAndSample
            seed: optional int seed for deterministic behavior
        """
        self.f_aug = list(f_aug)
        self.k = float(k)
        self.alpha = float(alpha)
        self.rng = np.random.default_rng(seed)

    def augment(self, img: Image.Image) -> Image.Image:
        """Augment single PIL image using Chi-MAC algorithm."""
        phi = 0
        selected_ops = []

        # iterate through operations and decide whether to include each
        for op in self.f_aug:
            pick = adjust_and_sample(self.k, phi, self.alpha, rng=self.rng)
            if pick:
                selected_ops.append(op)
                phi += 1

        # Apply selected operations sequentially
        aug = img
        for op in selected_ops:
            aug = op(aug)

        return aug

    def augment_n(self, img: Image.Image, n: int) -> list:
        """Produce n augmented variants of img. Useful to oversample a class."""
        out = []
        for _ in range(n):
            out.append(self.augment(img))
        return out
