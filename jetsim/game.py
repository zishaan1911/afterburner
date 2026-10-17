"""The Panda3D application that ties the jet, world, physics and HUD together."""

import random
import sys

from direct.showbase.ShowBase import ShowBase
from panda3d.core import (
    AntialiasAttrib,
    CardMaker,
    ClockObject,
    TransparencyAttrib,
    loadPrcFileData,
)

from .config import BASE_FOV, CAM_DISTANCE, CAM_HEIGHT, CAM_LAG, MAX_FOV, BOOST_SPEED
from .effects import Afterburner, setup_bloom
from .flight import Controls, FlightModel
from .hud import Hud
from .jet import build_jet
from .sky import setup_lights, setup_sky
from .terrain import Terrain
from . import textures

loadPrcFileData("", "window-title Afterburner - Fighter Jet Simulator")
loadPrcFileData("", "win-size 1280 720")
loadPrcFileData("", "framebuffer-multisample 1")
loadPrcFileData("", "multisamples 4")
loadPrcFileData("", "sync-video #f")
loadPrcFileData("", "show-frame-rate-meter #t")

_CLOCK = ClockObject.getGlobalClock()


class JetSimApp(ShowBase):
    def __init__(self):
        ShowBase.__init__(self)
        self.disableMouse()
        self.render.setAntialias(AntialiasAttrib.MAuto)
        self.camLens.setNearFar(0.5, 7000)

        flame_tex = textures.flame()
        sun_tex = textures.puff()
        cloud_tex = textures.puff()
        sky_tex = textures.gradient_sky()

        setup_lights(self.render)
        self.sky = setup_sky(self, sky_tex, sun_tex)
        self.terrain = Terrain(self.render)
        self.jet, anchors = build_jet(self.render)
        self.afterburner = Afterburner(self.render, anchors, flame_tex)
        self.flight = FlightModel(self.jet, self.terrain)
        self.flight.reset()
        self._make_clouds(cloud_tex)
        self.hud = Hud(self)
        self.filters = setup_bloom(self)

        self._snap_camera()
        self._bind_keys()
        self.taskMgr.add(self._update, "update")

    # -- world dressing ----------------------------------------------------
    def _make_clouds(self, cloud_tex, count=22):
        rng = random.Random(7)
        extent = self.terrain.half_extent - 200
        cm = CardMaker("cloud")
        cm.setFrame(-1, 1, -1, 1)
        for _ in range(count):
            cloud = self.render.attachNewNode(cm.generate())
            cloud.setTexture(cloud_tex, 1)
            cloud.setBillboardPointEye()
            cloud.setTransparency(TransparencyAttrib.MAlpha)
            cloud.setLightOff()
            cloud.setDepthWrite(False)
            cloud.setPos(
                rng.uniform(-extent, extent),
                rng.uniform(-extent, extent),
                rng.uniform(420, 780),
            )
            cloud.setScale(rng.uniform(90, 200))
            cloud.setColor(1, 1, 1, rng.uniform(0.35, 0.6))

    # -- input -------------------------------------------------------------
    def _bind_keys(self):
        self.keys = {k: False for k in (
            "w", "s", "a", "d", "q", "e", "throttle_up", "throttle_down", "boost"
        )}
        binds = {
            "w": "w", "s": "s", "a": "a", "d": "d", "q": "q", "e": "e",
            "arrow_up": "w", "arrow_down": "s",
            "arrow_left": "a", "arrow_right": "d",
            "shift": "throttle_up", "control": "throttle_down",
            "space": "boost",
        }
        for key, name in binds.items():
            self.accept(key, self._set_key, [name, True])
            self.accept(key + "-up", self._set_key, [name, False])
        self.accept("r", self.flight.reset)
        self.accept("escape", sys.exit)

    def _set_key(self, name, value):
        self.keys[name] = value

    def _read_controls(self):
        k = self.keys
        return Controls(
            pitch=(1.0 if k["s"] else 0.0) - (1.0 if k["w"] else 0.0),
            roll=(1.0 if k["d"] else 0.0) - (1.0 if k["a"] else 0.0),
            yaw=(1.0 if k["e"] else 0.0) - (1.0 if k["q"] else 0.0),
            throttle=(1.0 if k["throttle_up"] else 0.0)
            - (1.0 if k["throttle_down"] else 0.0),
            boost=k["boost"],
        )

    # -- camera ------------------------------------------------------------
    def _desired_camera(self):
        quat = self.jet.getQuat()
        return (
            self.jet.getPos()
            - quat.getForward() * CAM_DISTANCE
            + quat.getUp() * CAM_HEIGHT
        ), quat

    def _snap_camera(self):
        pos, quat = self._desired_camera()
        self.camera.setPos(pos)
        self.camera.lookAt(self.jet.getPos() + quat.getForward() * 25, quat.getUp())

    def _update_camera(self, dt):
        pos, quat = self._desired_camera()
        cur = self.camera.getPos()
        self.camera.setPos(cur + (pos - cur) * min(1.0, dt * CAM_LAG))
        self.camera.lookAt(
            self.jet.getPos() + quat.getForward() * 25 + quat.getUp() * 2,
            quat.getUp(),
        )
        fov = BASE_FOV + (self.flight.speed / BOOST_SPEED) * 26.0
        self.camLens.setFov(min(fov, MAX_FOV))

    # -- main loop ---------------------------------------------------------
    def _update(self, task):
        dt = min(_CLOCK.getDt(), 0.05)
        self.flight.update(dt, self._read_controls())
        self.afterburner.update(self.flight.throttle, self.flight.boosting)
        self._update_camera(dt)
        self.terrain.update(self.camera)
        self.hud.update(self.flight)
        return task.cont
