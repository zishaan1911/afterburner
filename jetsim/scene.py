"""Edge-of-space scene: the curved Earth below, a real Milky Way sky, an
atmosphere limb glow, a golden-hour sun and warm/earthshine lighting."""

from panda3d.core import (
    AmbientLight,
    CardMaker,
    ColorBlendAttrib,
    DirectionalLight,
    Filename,
    Material,
    Shader,
    Texture,
    TransparencyAttrib,
)

from . import textures
from .config import (
    ATMO_THICKNESS,
    EARTH_RADIUS,
    EARTH_SURFACE_Z,
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
    float rim = pow(1.0 - max(dot(N, V), 0.0), 3.0);
    float s = max(dot(N, sundir), 0.0);
    vec3 col = mix(vec3(0.22, 0.45, 1.0), vec3(1.0, 0.5, 0.16), pow(s, 1.3));
    o_color = vec4(col * rim * 2.1, rim);
}
"""


def _load_texture(base, path):
    tex = base.loader.loadTexture(Filename.fromOsSpecific(path))
    tex.setMinfilter(Texture.FTLinearMipmapLinear)
    tex.setMagfilter(Texture.FTLinear)
    return tex


def setup_lights(render):
    """Warm low sun, deep ambient, and a cool earthshine fill from below."""
    # Intensities are HDR (tonemapped by simplepbr), hence the > 1 values.
    sun = DirectionalLight("sun")
    sun.setColor((3.4, 2.2, 1.3, 1))          # warm golden-hour key light
    sun_np = render.attachNewNode(sun)
    sun_np.setHpr(*SUN_HPR)
    render.setLight(sun_np)

    ambient = AmbientLight("ambient")
    ambient.setColor((0.10, 0.12, 0.18, 1))   # cool sky/earthshine fill
    render.setLight(render.attachNewNode(ambient))

    fill = DirectionalLight("earthshine")
    fill.setColor((0.14, 0.20, 0.32, 1))
    fill_np = render.attachNewNode(fill)
    fill_np.setHpr(0, 82, 0)
    render.setLight(fill_np)
    return sun_np


class Scene:
    def __init__(self, base, earth_tex_path, milkyway_path):
        self.base = base
        render = base.render
        base.setBackgroundColor(0.0, 0.0, 0.0)

        self.sun_np = setup_lights(render)
        self.sun_dir = -self.sun_np.getQuat(render).getForward()

        self.dome = self._build_space_dome(milkyway_path)
        self.earth = self._build_earth(earth_tex_path)
        self.atmo = self._build_atmosphere()
        self.sun_sprite = self._build_sun()

    # -- construction ------------------------------------------------------
    def _build_space_dome(self, milkyway_path):
        dome = self.base.render.attachNewNode(
            make_uv_sphere(STAR_RADIUS * 1.6, 48, 96, invert=True))
        dome.setTexture(_load_texture(self.base, milkyway_path), 1)
        dome.setColorScale(0.62, 0.66, 0.80, 1)   # dim a touch, keep it cool
        dome.setLightOff()
        dome.setShaderOff()
        dome.setDepthWrite(False)
        dome.setBin("background", 0)
        dome.setTwoSided(True)
        return dome

    def _build_earth(self, tex_path):
        earth = self.base.render.attachNewNode(make_uv_sphere(EARTH_RADIUS, 96, 192))
        tex = _load_texture(self.base, tex_path)
        tex.setWrapU(Texture.WMRepeat)
        earth.setTexture(tex, 1)
        mat = Material("earth")
        mat.setBaseColor((1, 1, 1, 1))
        mat.setMetallic(0.0)
        mat.setRoughness(0.58)        # a little ocean sheen
        earth.setMaterial(mat, 1)
        # Light the Earth with its own neutral, bright daylight - decoupled from
        # the warm golden-hour sun that lights the jet - so the oceans read as
        # deep blue instead of being washed warm.
        earth.setLightOff()
        day_sun = DirectionalLight("earth_sun")
        day_sun.setColor((2.2, 2.35, 2.6, 1))
        sun_np = earth.attachNewNode(day_sun)
        sun_np.setHpr(*SUN_HPR)
        earth.setLight(sun_np)
        amb = AmbientLight("earth_amb")
        amb.setColor((0.14, 0.18, 0.26, 1))
        earth.setLight(earth.attachNewNode(amb))
        earth.setPos(0, 0, EARTH_SURFACE_Z - EARTH_RADIUS)
        earth.setP(62)            # tilt so continents, not the pole, face up
        earth.setH(120)
        return earth

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
