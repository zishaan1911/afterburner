"""Procedural geometry helpers.

Panda3D installed from pip ships without the sample models, so every piece of
the jet is built here from a single unit cube generated in code.
"""

from panda3d.core import (
    Geom,
    GeomNode,
    GeomTriangles,
    GeomVertexData,
    GeomVertexFormat,
    GeomVertexWriter,
)

# Six faces of a unit cube centred on the origin, each with an outward normal
# and four counter-clockwise vertices (so the default back-face cull keeps the
# outside visible).
_FACES = (
    ((0, 0, 1), ((-.5, -.5, .5), (.5, -.5, .5), (.5, .5, .5), (-.5, .5, .5))),
    ((0, 0, -1), ((-.5, .5, -.5), (.5, .5, -.5), (.5, -.5, -.5), (-.5, -.5, -.5))),
    ((0, 1, 0), ((-.5, .5, -.5), (-.5, .5, .5), (.5, .5, .5), (.5, .5, -.5))),
    ((0, -1, 0), ((.5, -.5, -.5), (.5, -.5, .5), (-.5, -.5, .5), (-.5, -.5, -.5))),
    ((1, 0, 0), ((.5, -.5, -.5), (.5, .5, -.5), (.5, .5, .5), (.5, -.5, .5))),
    ((-1, 0, 0), ((-.5, .5, -.5), (-.5, -.5, -.5), (-.5, -.5, .5), (-.5, .5, .5))),
)


def make_box():
    """Return a GeomNode containing a unit cube centred on the origin."""
    fmt = GeomVertexFormat.getV3n3()
    vdata = GeomVertexData("box", fmt, Geom.UHStatic)
    vdata.setNumRows(24)
    vertex = GeomVertexWriter(vdata, "vertex")
    normal = GeomVertexWriter(vdata, "normal")
    tris = GeomTriangles(Geom.UHStatic)

    index = 0
    for face_normal, verts in _FACES:
        for v in verts:
            vertex.addData3(*v)
            normal.addData3(*face_normal)
        tris.addVertices(index, index + 1, index + 2)
        tris.addVertices(index, index + 2, index + 3)
        index += 4

    geom = Geom(vdata)
    geom.addPrimitive(tris)
    node = GeomNode("box")
    node.addGeom(geom)
    return node


def box(parent, size, pos=(0, 0, 0), hpr=(0, 0, 0), color=(1, 1, 1, 1),
        two_sided=False):
    """Attach a scaled, positioned cube to ``parent`` and return the NodePath."""
    np = parent.attachNewNode(make_box())
    np.setScale(*size)
    np.setPos(*pos)
    np.setHpr(*hpr)
    if len(color) == 3:
        color = (color[0], color[1], color[2], 1.0)
    np.setColor(*color)
    if two_sided:
        np.setTwoSided(True)
    return np
