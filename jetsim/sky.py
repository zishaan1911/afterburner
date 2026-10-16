"""Sky dome, atmospheric fog and scene lighting."""

from panda3d.core import (
    AmbientLight,
    CardMaker,
    ColorBlendAttrib,
    DirectionalLight,
    Fog,
)

HORIZON_COLOR = (0.62, 0.74, 0.84)

# Additive blending, weighted by the sprite's alpha, for glows.
ADDITIVE = ColorBlendAttrib.make(
    ColorBlendAttrib.MAdd, ColorBlendAttrib.OIncomingAlpha, ColorBlendAttrib.OOne
)


def setup_sky(base, sky_tex, sun_tex):
    """A screen-filling gradient parented to the camera, plus a glowing sun."""
    cm = CardMaker("sky")
    cm.setFrame(-1.0, 1.0, -1.0, 1.0)
    sky = base.camera.attachNewNode(cm.generate())
    sky.setTexture(sky_tex, 1)
    sky.setPos(0, 150, 0)     # directly ahead of the camera (it looks +Y)
    sky.setScale(340, 1, 210)
    sky.setBin("background", 0)
    sky.setDepthTest(False)
    sky.setDepthWrite(False)
    sky.setLightOff()
    sky.setFogOff()
    sky.setTwoSided(True)

    sun = base.camera.attachNewNode(cm.generate())
    sun.setTexture(sun_tex, 1)
    sun.setAttrib(ADDITIVE)
    sun.setPos(-70, 150, 55)
    sun.setScale(26, 1, 26)
    sun.setColor(1.0, 0.95, 0.8, 1)
    sun.setBin("background", 1)
    sun.setDepthTest(False)
    sun.setDepthWrite(False)
    sun.setLightOff()
    sun.setFogOff()

    fog = Fog("fog")
    fog.setColor(*HORIZON_COLOR)
    fog.setExpDensity(0.00026)
    base.render.setFog(fog)
    base.setBackgroundColor(*HORIZON_COLOR)
    return sky


def setup_lights(render):
    """Warm directional sun plus a cool ambient fill, with per-pixel shading."""
    sun = DirectionalLight("sun")
    sun.setColor((0.95, 0.88, 0.78, 1))
    sun_np = render.attachNewNode(sun)
    sun_np.setHpr(-40, -55, 0)
    render.setLight(sun_np)

    ambient = AmbientLight("ambient")
    ambient.setColor((0.30, 0.34, 0.42, 1))
    ambient_np = render.attachNewNode(ambient)
    render.setLight(ambient_np)

    render.setShaderAuto()
    return sun_np, ambient_np
