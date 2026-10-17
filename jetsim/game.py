"""The Panda3D application: Su-57 jet, edge-of-space world, physics and HUD."""

import os
import sys

import simplepbr
from simplepbr import EnvMap
from direct.showbase.ShowBase import ShowBase
from panda3d.core import ClockObject, Filename, loadPrcFileData

from .config import (
    BASE_FOV,
    BOOST_SPEED,
    CAM_DISTANCE,
    CAM_HEIGHT,
    CAM_LAG,
    EXPOSURE,
    MAX_FOV,
)
from .effects import Afterburner
from .flight import Controls, FlightModel
from .hud import Hud
from .jet import build_jet
from .scene import Scene
from . import textures

loadPrcFileData("", "window-title Afterburner - Su-57 Edge of Space")
loadPrcFileData("", "win-size 1280 720")
loadPrcFileData("", "framebuffer-multisample 1")
loadPrcFileData("", "multisamples 4")
loadPrcFileData("", "sync-video #f")
loadPrcFileData("", "show-frame-rate-meter #t")

_CLOCK = ClockObject.getGlobalClock()
_ASSETS = os.path.join(os.path.dirname(os.path.dirname(__file__)), "assets")


class JetSimApp(ShowBase):
    def __init__(self):
        ShowBase.__init__(self)
        self.disableMouse()
        self.camLens.setNearFar(0.5, 40000)

        # Physically based rendering pipeline: metal/roughness, normal maps,
        # HDR filmic tonemapping, and image-based lighting from a scene-matched
        # environment map (ambient + reflections on the airframe).
        env_path = os.path.join(_ASSETS, "env.png")
        env_map = None
        if os.path.exists(env_path):
            try:
                env_map = EnvMap.from_file_path(
                    Filename.fromOsSpecific(env_path), blocking_prepare=True)
            except Exception as exc:  # pragma: no cover
                print("env map load failed:", exc)
        self.pipeline = simplepbr.init(
            msaa_samples=4,
            use_normal_maps=True,
            use_emission_maps=True,
            use_occlusion_maps=True,
            enable_shadows=False,
            exposure=EXPOSURE,
            env_map=env_map,
        )

        self.scene = Scene(
            self,
            os.path.join(_ASSETS, "earth_surface.jpg"),
            os.path.join(_ASSETS, "milkyway.jpg"),
        )
        self.jet, anchors = build_jet(self.render, os.path.join(_ASSETS, "su57.glb"))
        self.afterburner = Afterburner(self.render, anchors, textures.flame())
        self.flight = FlightModel(self.jet)
        self.flight.reset()
        self.hud = Hud(self)

        self._snap_camera()
        self._bind_keys()
        self.taskMgr.add(self._update, "update")

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
        self.camera.lookAt(self.jet.getPos() + quat.getForward() * 30, quat.getUp())

    def _update_camera(self, dt):
        pos, quat = self._desired_camera()
        cur = self.camera.getPos()
        self.camera.setPos(cur + (pos - cur) * min(1.0, dt * CAM_LAG))
        self.camera.lookAt(
            self.jet.getPos() + quat.getForward() * 30 + quat.getUp() * 3,
            quat.getUp(),
        )
        fov = BASE_FOV + (self.flight.speed / BOOST_SPEED) * 22.0
        self.camLens.setFov(min(fov, MAX_FOV))

    # -- main loop ---------------------------------------------------------
    def _update(self, task):
        dt = min(_CLOCK.getDt(), 0.05)
        self.flight.update(dt, self._read_controls())
        self.afterburner.update(self.flight.throttle, self.flight.boosting)
        self._update_camera(dt)
        self.scene.update(dt, self.camera.getPos())
        self.hud.update(self.flight)
        return task.cont
