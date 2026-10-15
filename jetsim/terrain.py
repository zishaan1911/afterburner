"""Procedural terrain built on Panda3D's GeoMipTerrain.

The heightfield is generated analytically so the same function can be reused for
cheap elevation queries (jet-vs-ground clearance) without sampling the mesh.
"""

import math

from panda3d.core import GeoMipTerrain, PNMImage, Texture

from .config import HSCALE, TERRAIN_SIZE, ZSCALE, clamp, lerp3

WATER = (0.12, 0.26, 0.44)
GRASS = (0.16, 0.38, 0.13)
ROCK = (0.33, 0.28, 0.23)
SNOW = (0.90, 0.93, 0.97)


class Terrain:
    def __init__(self, render):
        self.size = TERRAIN_SIZE
        self.sx = HSCALE
        self.sy = HSCALE
        self.sz = ZSCALE
        self.ox = -(self.size - 1) * HSCALE / 2.0
        self.oy = -(self.size - 1) * HSCALE / 2.0

        heightmap = self._build_heightmap()
        colormap = self._build_colormap(heightmap)

        self.terrain = GeoMipTerrain("terrain")
        self.terrain.setHeightfield(heightmap)
        self.terrain.setBlockSize(32)
        self.terrain.setNear(90)
        self.terrain.setFar(500)
        self.terrain.setMinLevel(1)

        self.root = self.terrain.getRoot()
        self.root.setScale(self.sx, self.sy, self.sz)
        self.root.setPos(self.ox, self.oy, 0)

        color_tex = Texture()
        color_tex.load(colormap)
        self.root.setTexture(color_tex, 1)
        self.root.reparentTo(render)
        self.terrain.generate()

    # -- generation --------------------------------------------------------
    def _height01(self, i, j):
        u = i / (self.size - 1)
        v = j / (self.size - 1)
        x = u * 2.0 - 1.0
        y = v * 2.0 - 1.0

        value = 0.40 + 0.34 * (
            0.50 * math.sin(u * 6.283 * 1.5) * math.cos(v * 6.283 * 1.3)
            + 0.30 * math.sin(u * 6.283 * 3.1 + 1.7) * math.sin(v * 6.283 * 2.6 + 0.4)
            + 0.20 * math.sin((u + v) * 6.283 * 4.2)
        )
        # Tall mountain ranges, and a calm valley at the spawn point.
        value += 0.42 * math.exp(-((x + 0.45) ** 2 + (y - 0.4) ** 2) * 2.2)
        value += 0.34 * math.exp(-((x - 0.6) ** 2 + (y + 0.55) ** 2) * 2.6)
        value -= 0.32 * math.exp(-(x * x + y * y) * 4.5)
        return clamp(value, 0.0, 1.0)

    def _build_heightmap(self):
        img = PNMImage(self.size, self.size)
        for j in range(self.size):
            for i in range(self.size):
                h = self._height01(i, j)
                img.setXel(i, j, h, h, h)
        return img

    def _color_for(self, h):
        if h < 0.17:
            return lerp3(WATER, GRASS, h / 0.17)
        if h < 0.48:
            return lerp3(GRASS, ROCK, (h - 0.17) / 0.31)
        if h < 0.74:
            return lerp3(ROCK, SNOW, (h - 0.48) / 0.26)
        return SNOW

    def _build_colormap(self, heightmap):
        img = PNMImage(self.size, self.size)
        for j in range(self.size):
            for i in range(self.size):
                img.setXel(i, j, *self._color_for(heightmap.getGray(i, j)))
        return img

    # -- queries -----------------------------------------------------------
    def elevation(self, x, y):
        """World-space ground height beneath ``(x, y)``."""
        hx = clamp((x - self.ox) / self.sx, 0, self.size - 1)
        hy = clamp((y - self.oy) / self.sy, 0, self.size - 1)
        return self.terrain.getElevation(hx, hy) * self.sz + self.root.getZ()

    @property
    def half_extent(self):
        return (self.size - 1) * self.sx / 2.0

    def update(self, focus):
        self.terrain.setFocalPoint(focus)
        self.terrain.update()
