"""Procedurally generated textures (sky gradient, flame and cloud sprites)."""

import math

from panda3d.core import PNMImage, Texture

from .config import lerp3


def _texture(img):
    tex = Texture()
    tex.load(img)
    tex.setMinfilter(Texture.FTLinearMipmapLinear)
    tex.setMagfilter(Texture.FTLinear)
    return tex


def gradient_sky():
    """A vertical sky gradient: deep blue zenith fading to a pale horizon."""
    height = 256
    zenith = (0.11, 0.33, 0.66)
    middle = (0.44, 0.62, 0.84)
    horizon = (0.78, 0.85, 0.90)
    img = PNMImage(1, height)
    for y in range(height):
        t = y / (height - 1)
        if t < 0.55:
            color = lerp3(zenith, middle, t / 0.55)
        else:
            color = lerp3(middle, horizon, (t - 0.55) / 0.45)
        img.setXel(0, y, *color)
    return _texture(img)


def flame():
    """A soft radial flame sprite, hot white core to orange rim."""
    size = 64
    img = PNMImage(size, size)
    img.addAlpha()
    c = (size - 1) / 2.0
    for y in range(size):
        for x in range(size):
            d = min(1.0, math.hypot(x - c, y - c) / c)
            falloff = (1.0 - d) ** 2
            r = 1.0
            g = min(1.0, 0.52 + 0.42 * (1.0 - d))
            b = min(1.0, 0.10 + 0.30 * (1.0 - d) ** 2)
            img.setXel(x, y, r, g, b)
            img.setAlpha(x, y, falloff * 0.9)
    return _texture(img)


def puff():
    """A soft white cloud puff with a feathered alpha edge."""
    size = 128
    img = PNMImage(size, size)
    img.addAlpha()
    c = (size - 1) / 2.0
    for y in range(size):
        for x in range(size):
            d = min(1.0, math.hypot(x - c, y - c) / c)
            img.setXel(x, y, 1.0, 1.0, 1.0)
            img.setAlpha(x, y, (1.0 - d) ** 3 * 0.9)
    return _texture(img)
