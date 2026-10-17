"""Fighter jet model loading.

Primary path: load the high-detail Su-57 glTF (matte materials so the stealth
livery lights correctly under standard shading, landing gear retracted for
flight). Falls back to a procedural box jet if the model is missing.
"""

import os

from panda3d.core import Material, NodePath

from .config import JET_SCALE
from .geometry import box

# Parts of the Su-57 glTF to hide so the jet is in a clean flight configuration.
_HIDE_KEYWORDS = (
    "leg", "wheel", "tire", "mudguard", "steer", "brace", "gear",
    "landing light", "door",
)


def build_jet(parent, model_path=None):
    """Return ``(root_nodepath, engine_anchor_nodes)``."""
    if model_path and os.path.exists(model_path):
        try:
            return _build_glb(parent, model_path)
        except Exception as exc:  # pragma: no cover - defensive
            print("GLB jet load failed (%s); using procedural jet." % exc)
    return _build_procedural(parent)


def _build_glb(parent, model_path):
    import gltf

    inner = NodePath(gltf.load_model(model_path))
    inner.setMaterialOff(1)       # drop metallic PBR mats -> textures as diffuse
    inner.setColorScale(0.60, 0.64, 0.72, 1)   # moodier, cooler stealth grey

    for np in inner.findAllMatches("**"):
        name = np.getName().lower()
        if any(k in name for k in _HIDE_KEYWORDS):
            np.hide()

    inner.setH(-90)               # model nose is -X; rotate so the nose is +Y

    root = parent.attachNewNode("jet")
    inner.reparentTo(root)

    mn, mx = inner.getTightBounds()
    center = (mn + mx) * 0.5
    inner.setPos(-center.x, -center.y, -center.z)

    # Find the two exhaust nozzles by name and take the outermost node per side.
    left = None
    right = None
    for np in inner.findAllMatches("**"):
        if "nozzle" in np.getName().lower():
            p = np.getPos(root)
            if p.x < 0 and (left is None or p.x < left.x):
                left = p
            elif p.x > 0 and (right is None or p.x > right.x):
                right = p

    anchors = []
    if left is not None and right is not None:
        for p in (left, right):
            a = root.attachNewNode("engine")
            a.setPos(p.x, p.y - 0.4, p.z)
            anchors.append(a)
    else:                          # fallback: approximate the rear nozzles
        mn, mx = inner.getTightBounds(root)
        zc = (mn.z + mx.z) * 0.5
        for sx in (-1.0, 1.0):
            a = root.attachNewNode("engine")
            a.setPos(sx, mn.y + 0.5, zc)
            anchors.append(a)

    root.setScale(JET_SCALE)
    return root, anchors


# ---------------------------------------------------------------------------
# Procedural fallback jet (used only if the glTF asset is unavailable).
# ---------------------------------------------------------------------------
BODY = (0.24, 0.26, 0.30)
DARK = (0.13, 0.14, 0.17)
GLASS = (0.05, 0.10, 0.20)
ACCENT = (0.15, 0.16, 0.19)
NOZZLE = (0.08, 0.08, 0.10)


def _build_procedural(parent):
    root = parent.attachNewNode("jet")

    box(root, (0.95, 7.0, 0.95), pos=(0, 0.0, 0.0), color=BODY)
    box(root, (0.58, 2.8, 0.60), pos=(0, 4.4, 0.05), color=BODY)
    box(root, (0.24, 1.3, 0.26), pos=(0, 6.0, 0.03), color=DARK)
    box(root, (1.12, 3.2, 0.52), pos=(0, 0.6, -0.58), color=DARK)
    box(root, (0.48, 3.4, 0.42), pos=(0, -1.4, 0.52), color=ACCENT)
    box(root, (0.62, 1.1, 0.42), pos=(0, 2.3, 0.62), color=GLASS)
    box(root, (0.66, 1.4, 0.58), pos=(0, 1.3, 0.66), color=GLASS)
    box(root, (4.8, 2.8, 0.14), pos=(-2.7, -0.5, -0.05), hpr=(20, 0, 7), color=BODY)
    box(root, (4.8, 2.8, 0.14), pos=(2.7, -0.5, -0.05), hpr=(-20, 0, -7), color=BODY)
    box(root, (2.2, 1.4, 0.12), pos=(-1.35, -3.1, 0.0), hpr=(16, 0, 5), color=BODY)
    box(root, (2.2, 1.4, 0.12), pos=(1.35, -3.1, 0.0), hpr=(-16, 0, -5), color=BODY)
    box(root, (0.12, 1.7, 1.5), pos=(-0.55, -2.7, 0.85), hpr=(0, 0, 24), color=ACCENT)
    box(root, (0.12, 1.7, 1.5), pos=(0.55, -2.7, 0.85), hpr=(0, 0, -24), color=ACCENT)

    anchors = []
    for side in (-1, 1):
        box(root, (0.46, 1.1, 0.46), pos=(side * 0.46, -3.7, 0.0), color=NOZZLE)
        anchor = root.attachNewNode("engine_%d" % side)
        anchor.setPos(side * 0.46, -4.3, 0.0)
        anchors.append(anchor)

    metal = Material()
    metal.setSpecular((0.95, 0.95, 1.0, 1))
    metal.setShininess(75)
    root.setMaterial(metal, 1)
    root.setScale(1.6)
    return root, anchors
