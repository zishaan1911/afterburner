"""Procedurally modelled twin-tail fighter jet.

The nose points along +Y (the jet's forward axis). Everything is assembled from
scaled cubes and given a gunmetal material so the lighting reads as metal.
"""

from panda3d.core import Material

from .geometry import box

BODY = (0.24, 0.26, 0.30)
DARK = (0.13, 0.14, 0.17)
GLASS = (0.05, 0.10, 0.20)
ACCENT = (0.15, 0.16, 0.19)
NOZZLE = (0.08, 0.08, 0.10)


def build_jet(parent):
    """Build the jet under ``parent`` and return ``(root, engine_anchors)``."""
    root = parent.attachNewNode("jet")

    # Main fuselage and tapered nose.
    box(root, (0.95, 7.0, 0.95), pos=(0, 0.0, 0.0), color=BODY)
    box(root, (0.58, 2.8, 0.60), pos=(0, 4.4, 0.05), color=BODY)
    box(root, (0.24, 1.3, 0.26), pos=(0, 6.0, 0.03), color=DARK)
    # Belly intake and dorsal spine.
    box(root, (1.12, 3.2, 0.52), pos=(0, 0.6, -0.58), color=DARK)
    box(root, (0.48, 3.4, 0.42), pos=(0, -1.4, 0.52), color=ACCENT)

    # Bubble canopy (two blocks so it reads as a slanted windscreen).
    box(root, (0.62, 1.1, 0.42), pos=(0, 2.3, 0.62), hpr=(0, 0, 0), color=GLASS)
    box(root, (0.66, 1.4, 0.58), pos=(0, 1.3, 0.66), color=GLASS)

    # Swept delta wings (H = sweep, R = dihedral).
    box(root, (4.8, 2.8, 0.14), pos=(-2.7, -0.5, -0.05), hpr=(20, 0, 7), color=BODY)
    box(root, (4.8, 2.8, 0.14), pos=(2.7, -0.5, -0.05), hpr=(-20, 0, -7), color=BODY)

    # Horizontal tailplanes.
    box(root, (2.2, 1.4, 0.12), pos=(-1.35, -3.1, 0.0), hpr=(16, 0, 5), color=BODY)
    box(root, (2.2, 1.4, 0.12), pos=(1.35, -3.1, 0.0), hpr=(-16, 0, -5), color=BODY)

    # Twin canted vertical stabilisers.
    box(root, (0.12, 1.7, 1.5), pos=(-0.55, -2.7, 0.85), hpr=(0, 0, 24), color=ACCENT)
    box(root, (0.12, 1.7, 1.5), pos=(0.55, -2.7, 0.85), hpr=(0, 0, -24), color=ACCENT)

    # Engine nozzles and the anchor nodes where the afterburner plume attaches.
    engine_anchors = []
    for side in (-1, 1):
        box(root, (0.46, 1.1, 0.46), pos=(side * 0.46, -3.7, 0.0), color=NOZZLE)
        anchor = root.attachNewNode("engine_%d" % side)
        anchor.setPos(side * 0.46, -4.3, 0.0)
        engine_anchors.append(anchor)

    # Specular-only material: leaving diffuse/ambient unset lets each part's own
    # colour drive the shading, while the material adds crisp metal highlights.
    metal = Material()
    metal.setSpecular((0.95, 0.95, 1.0, 1))
    metal.setShininess(75)
    root.setMaterial(metal, 1)

    root.setScale(1.6)
    return root, engine_anchors
