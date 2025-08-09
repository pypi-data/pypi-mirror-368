import random

import torchvision.transforms.functional as F


def op_rotate(theta_range=(-30, 30)):
    def _fn(img):
        angle = random.uniform(*theta_range)
        return F.rotate(img, angle)

    return _fn


def op_scale(factor=1.5):
    # We'll scale the image by factor and then center-crop / pad back to original size
    def _fn(img):
        if hasattr(img, "size"):
            w, h = img.size
        else:
            # For tensor images
            _, h, w = img.shape

        new_w = int(round(w * factor))
        new_h = int(round(h * factor))

        img_resized = F.resize(img, [new_h, new_w])

        # Center-crop or pad back to original
        if new_w >= w and new_h >= h:
            return F.center_crop(img_resized, [h, w])
        else:
            # pad
            pad_w = max(0, w - new_w)
            pad_h = max(0, h - new_h)
            # padding left, top, right, bottom
            left = pad_w // 2
            top = pad_h // 2
            right = pad_w - left
            bottom = pad_h - top
            return F.pad(img_resized, [left, top, right, bottom])

    return _fn


def op_translate(dx_range=(-20, 20), dy_range=(-20, 20)):
    def _fn(img):
        dx = int(round(random.uniform(*dx_range)))
        dy = int(round(random.uniform(*dy_range)))
        return F.affine(img, angle=0.0, translate=[dx, dy], scale=1.0, shear=[0.0])

    return _fn


def op_flip():
    def _fn(img):
        # randomly choose horizontal or vertical
        if random.random() < 0.5:
            return F.hflip(img)
        else:
            return F.vflip(img)

    return _fn


def op_brightness(brightness_factor=0.8):
    def _fn(img):
        return F.adjust_brightness(img, brightness_factor)

    return _fn


def op_contrast(contrast_factor=1.2):
    def _fn(img):
        return F.adjust_contrast(img, contrast_factor)

    return _fn


def op_saturation(saturation_factor=0.5):
    def _fn(img):
        return F.adjust_saturation(img, saturation_factor)

    return _fn


def op_hue(hue_factor=0.2):
    def _fn(img):
        return F.adjust_hue(img, hue_factor)

    return _fn
