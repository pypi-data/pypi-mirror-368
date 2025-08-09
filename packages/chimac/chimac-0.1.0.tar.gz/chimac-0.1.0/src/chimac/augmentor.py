import math
import os
from pathlib import Path
from typing import Dict, Optional

from PIL import Image

from .chimac import ChiMAC


class DatasetAugmenter:
    def __init__(self, chi_mac: ChiMAC, image_exts=(".jpg", ".jpeg", ".png", ".bmp")):
        self.chi_mac = chi_mac
        self.image_exts = set(e.lower() for e in image_exts)

    def _is_image(self, p: Path) -> bool:
        return p.suffix.lower() in self.image_exts

    def balance_directory(
        self,
        src_root: str | os.PathLike,
        out_root: str | os.PathLike,
        target_per_class: Optional[int] = None,
        seed: Optional[int] = None,
    ) -> Dict[str, int]:
        """Balance classes in src_root and write augmented images into out_root.

        Args:
            src_root: input dataset root with class subfolders
            out_root: output root where original + augmented images will be written
            target_per_class: if None, target is the max class count in source; otherwise that value
            seed: optional seed to use for file naming determinism

        Returns:
            dict mapping class -> final count
        """
        src_root = Path(src_root)
        out_root = Path(out_root)
        out_root.mkdir(parents=True, exist_ok=True)

        classes = [d for d in src_root.iterdir() if d.is_dir()]
        counts = {
            c.name: len([p for p in c.iterdir() if self._is_image(p)]) for c in classes
        }

        if target_per_class is None:
            target = max(counts.values()) if counts else 0
        else:
            target = int(target_per_class)

        final_counts = {}

        for c in classes:
            dst_class_dir = out_root / c.name
            dst_class_dir.mkdir(parents=True, exist_ok=True)

            imgs = [p for p in c.iterdir() if self._is_image(p)]
            # copy originals
            for p in imgs:
                dst = dst_class_dir / p.name
                if not dst.exists():
                    Image.open(p).save(dst)

            cur_count = len(imgs)
            needed = max(0, target - cur_count)

            if needed > 0 and imgs:
                per_image = math.ceil(needed / len(imgs))
                counter = 0
                for p in imgs:
                    img = Image.open(p).convert("RGB")
                    to_make = min(per_image, needed - counter)
                    aug_imgs = self.chi_mac.augment_n(img, to_make)
                    for idx, a in enumerate(aug_imgs):
                        out_name = f"AUGMENTED_{p.stem}_{idx}.png"
                        a.save(dst_class_dir / out_name)
                        counter += 1
                        if counter >= needed:
                            break
                    if counter >= needed:
                        break

            final_counts[c.name] = len(list(dst_class_dir.iterdir()))

        return final_counts
