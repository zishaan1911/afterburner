"""Afterburner plume, engine lights and the bloom post-process."""

from direct.filter.CommonFilters import CommonFilters
from panda3d.core import CardMaker, ColorBlendAttrib, PointLight

# Additive blending, weighted by the sprite's alpha, for the glowing plume.
ADDITIVE = ColorBlendAttrib.make(
    ColorBlendAttrib.MAdd, ColorBlendAttrib.OIncomingAlpha, ColorBlendAttrib.OOne
)

# Billboarded flame blobs: (distance behind the nozzle, base radius), sized for
# the ~20 m Su-57.
_PLUME = ((0.45, 0.6), (1.5, 0.46), (2.8, 0.3), (4.2, 0.17))


class Afterburner:
    def __init__(self, render, anchors, flame_tex):
        self.render = render
        self.sprites = []       # (nodepath, base_radius, distance)
        self.lights = []        # (PointLight, light_nodepath)

        cm = CardMaker("flame")
        cm.setFrame(-1, 1, -1, 1)

        for anchor in anchors:
            for dist, radius in _PLUME:
                sprite = anchor.attachNewNode(cm.generate())
                sprite.setTexture(flame_tex, 1)
                sprite.setAttrib(ADDITIVE)
                sprite.setBillboardPointEye()
                sprite.setLightOff()
                sprite.setDepthWrite(False)
                sprite.setFogOff()
                sprite.setPos(0, -dist, 0)
                self.sprites.append((sprite, radius, dist))

            light = PointLight("engine")
            light.setColor((0.6, 0.3, 0.1, 1))
            light.setAttenuation((1.0, 0.0, 0.003))
            light_np = anchor.attachNewNode(light)
            light_np.setPos(0, -1.5, 0)
            render.setLight(light_np)
            self.lights.append((light, light_np))

    def update(self, throttle, boost):
        intensity = throttle * 0.5 + 0.15
        if boost:
            intensity = 1.1
        for sprite, radius, dist in self.sprites:
            sprite.setScale(radius * (0.6 + intensity))
            sprite.setPos(0, -dist * (0.6 + intensity), 0)
        for light, _np in self.lights:
            glow = intensity * 0.6
            light.setColor((glow, glow * 0.42, glow * 0.12, 1))


def setup_bloom(base):
    """Enable a bloom filter so the afterburner and sun glow."""
    filters = CommonFilters(base.win, base.cam)
    filters.setBloom(
        blend=(0.3, 0.4, 0.3, 0.0),
        desat=0.0,
        intensity=1.1,
        size="medium",
        mintrigger=0.80,
        maxtrigger=1.0,
    )
    return filters
