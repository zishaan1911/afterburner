"""Edge-of-space scene: the curved Earth below, atmosphere limb glow, a star
field, a golden-hour sun and warm/earthshine lighting."""

import math
import random

from panda3d.core import (
    AmbientLight,
    CardMaker,
    ColorBlendAttrib,
    DirectionalLight,
    Geom,
    GeomNode,
    GeomPoints,
    GeomVertexData,
    GeomVertexFormat,
    GeomVertexWriter,
    Filename,
    NodePath,
    Shader,
    Texture,
    TransparencyAttrib,
)

from . import textures
from .config import (
    ATMO_THICKNESS,
    EARTH_RADIUS,
    EARTH_SURFACE_Z,
    STAR_COUNT,
    STAR_RADIUS,
    SUN_HPR,
)
from .geometry import make_uv_sphere

ADDITIVE = ColorBlendAttrib.make(
    ColorBlendAttrib.MAdd, ColorBlendAttrib.OIncomingAlpha, ColorBlendAttrib.OOne
)

_ATMO_VERT = """#version 150
uniform mat4 p3d_ModelViewProjectionMatrix;
uniform mat4 p3d_ModelMatrix;
in vec4 p3d_Vertex;
in vec3 p3d_Normal;
out vec3 wN;
out vec3 wP;
void main() {
    gl_Position = p3d_ModelViewProjectionMatrix * p3d_Vertex;
    wN = normalize(mat3(p3d_ModelMatrix) * p3d_Normal);
    wP = (p3d_ModelMatrix * p3d_Vertex).xyz;
}
"""

_ATMO_FRAG = """#version 150
in vec3 wN;
in vec3 wP;
uniform vec3 campos;
uniform vec3 sundir;
out vec4 o_color;
void main() {
    vec3 V = normalize(campos - wP);
    vec3 N = normalize(wN);
    float rim = pow(1.0 - max(dot(N, V), 0.0), 2.6);
    float s = max(dot(N, sundir), 0.0);
    vec3 col = mix(vec3(0.20, 0.42, 1.0), vec3(1.0, 0.52, 0.18), pow(s, 1.3));
    o_color = vec4(col * rim, rim);
}
"""


def setup_lights(render):
    """Warm low sun, deep ambient, and a cool earthshine fill from below."""
    sun = DirectionalLight("sun")
    sun.setColor((1.18, 0.80, 0.46, 1))
    sun_np = render.attachNewNode(sun)
    sun_np.setHpr(*SUN_HPR)
    render.setLight(sun_np)

    ambient = AmbientLight("ambient")
    ambient.setColor((0.15, 0.17, 0.24, 1))
    render.setLight(render.attachNewNode(ambient))

    fill = DirectionalLight("earthshine")
    fill.setColor((0.10, 0.15, 0.26, 1))
    fill_np = render.attachNewNode(fill)
    fill_np.setHpr(0, 82, 0)
    render.setLight(fill_np)

    render.setShaderAuto()
    return sun_np


class Scene:
    def __init__(self, base, earth_tex_path):
        self.base = base
        render = base.render
        base.setBackgroundColor(0.012, 0.02, 0.05)

        self.sun_np = setup_lights(render)
        self.sun_dir = -self.sun_np.getQuat(render).getForward()

        self.dome = self._build_space_dome()
        self.earth = self._build_earth(earth_tex_path)
        self.stars = self._build_stars()
        self.atmo = self._build_atmosphere()
        self.sun_sprite = self._build_sun()

    # -- construction ------------------------------------------------------
    def _build_space_dome(self):
        dome = self.base.render.attachNewNode(
            make_uv_sphere(STAR_RADIUS * 1.6, 24, 48, invert=True))
        dome.setColor(0.015, 0.025, 0.06, 1)
        dome.setLightOff()
        dome.setShaderOff()
        dome.setDepthWrite(False)
        dome.setBin("background", 0)
        dome.setTwoSided(True)
        return dome

    def _build_earth(self, tex_path):
        earth = self.base.render.attachNewNode(make_uv_sphere(EARTH_RADIUS, 96, 192))
        tex = self.base.loader.loadTexture(Filename.fromOsSpecific(tex_path))
        tex.setMinfilter(Texture.FTLinearMipmapLinear)
        tex.setMagfilter(Texture.FTLinear)
        earth.setTexture(tex, 1)
        earth.setPos(0, 0, EARTH_SURFACE_Z - EARTH_RADIUS)
        earth.setP(62)            # tilt so continents, not the pole, face up
        earth.setH(120)
        # A dedicated fill just for the Earth so it stays bright and blue while
        # the jet and sky keep a low, moody ambient.
        earth_fill = AmbientLight("earth_fill")
        earth_fill.setColor((0.85, 0.90, 0.98, 1))
        earth.setLight(earth.attachNewNode(earth_fill))
        return earth

    def _build_stars(self):
        fmt = GeomVertexFormat.getV3c4()
        vdata = GeomVertexData("stars", fmt, Geom.UHStatic)
        vdata.setNumRows(STAR_COUNT)
        vtx = GeomVertexWriter(vdata, "vertex")
        col = GeomVertexWriter(vdata, "color")
        pts = GeomPoints(Geom.UHStatic)
        rng = random.Random(42)
        for i in range(STAR_COUNT):
            z = rng.uniform(-1, 1)
            t = rng.uniform(0, 2 * math.pi)
            r = math.sqrt(max(0.0, 1 - z * z))
            vtx.addData3(r * math.cos(t) * STAR_RADIUS,
                         r * math.sin(t) * STAR_RADIUS,
                         z * STAR_RADIUS)
            b = rng.uniform(0.35, 1.0) ** 1.5
            col.addData4(b, b, b * rng.uniform(0.9, 1.15), 1)
            pts.addVertex(i)
        geom = Geom(vdata)
        geom.addPrimitive(pts)
        node = GeomNode("stars")
        node.addGeom(geom)
        np = self.base.render.attachNewNode(node)
        np.setLightOff()
        np.setBin("background", 2)
        np.setDepthWrite(False)
        np.setRenderModeThickness(1.6)
        np.setShaderOff()
        return np

    def _build_atmosphere(self):
        try:
            shader = Shader.make(Shader.SL_GLSL, vertex=_ATMO_VERT,
                                 fragment=_ATMO_FRAG)
        except Exception as exc:  # pragma: no cover
            print("atmosphere shader failed:", exc)
            return None
        atmo = self.base.render.attachNewNode(
            make_uv_sphere(EARTH_RADIUS + ATMO_THICKNESS, 64, 128))
        atmo.setPos(0, 0, EARTH_SURFACE_Z - EARTH_RADIUS)
        atmo.setShader(shader)
        atmo.setShaderInput("sundir", self.sun_dir)
        atmo.setShaderInput("campos", (0, 0, 0))
        atmo.setAttrib(ADDITIVE)
        atmo.setTransparency(TransparencyAttrib.MAlpha)
        atmo.setDepthWrite(False)
        atmo.setLightOff()
        atmo.setBin("fixed", 10)
        atmo.setTwoSided(True)
        return atmo

    def _build_sun(self):
        cm = CardMaker("sun")
        cm.setFrame(-1, 1, -1, 1)
        sun = self.base.render.attachNewNode(cm.generate())
        sun.setTexture(textures.puff(), 1)
        sun.setAttrib(ADDITIVE)
        sun.setBillboardPointEye()
        sun.setLightOff()
        sun.setDepthWrite(False)
        sun.setBin("background", 3)
        sun.setColor(1.0, 0.72, 0.38, 1)
        sun.setScale(520)
        sun.setPos(self.sun_dir * (STAR_RADIUS * 0.85))
        return sun

    # -- per-frame ---------------------------------------------------------
    def update(self, dt, cam_pos):
        if self.atmo is not None:
            self.atmo.setShaderInput("campos", cam_pos)
        self.earth.setH(self.earth.getH() + dt * 0.35)
