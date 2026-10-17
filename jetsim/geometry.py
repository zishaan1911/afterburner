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


def make_uv_sphere(radius=1.0, lat=48, lon=96, invert=False):
    """A UV sphere (pole on +Z) with normals and equirectangular texcoords.

    ``invert`` flips the winding and normals so the sphere is seen from inside
    (used for the star dome).
    """
    import math

    fmt = GeomVertexFormat.getV3n3t2()
    vdata = GeomVertexData("sphere", fmt, Geom.UHStatic)
    vdata.setNumRows((lat + 1) * (lon + 1))
    vertex = GeomVertexWriter(vdata, "vertex")
    normal = GeomVertexWriter(vdata, "normal")
    texcoord = GeomVertexWriter(vdata, "texcoord")

    for i in range(lat + 1):
        theta = math.pi * i / lat          # 0 at north pole (+Z)
        st, ct = math.sin(theta), math.cos(theta)
        for j in range(lon + 1):
            phi = 2.0 * math.pi * j / lon
            x = st * math.cos(phi)
            y = st * math.sin(phi)
            z = ct
            vertex.addData3(x * radius, y * radius, z * radius)
            n = -1.0 if invert else 1.0
            normal.addData3(x * n, y * n, z * n)
            texcoord.addData2(j / lon, 1.0 - i / lat)

    tris = GeomTriangles(Geom.UHStatic)
    row = lon + 1
    for i in range(lat):
        for j in range(lon):
            a = i * row + j
            b = a + 1
            c = a + row
            d = c + 1
            if invert:
                tris.addVertices(a, c, b)
                tris.addVertices(b, c, d)
            else:
                tris.addVertices(a, b, c)
                tris.addVertices(b, d, c)

    geom = Geom(vdata)
    geom.addPrimitive(tris)
    node = GeomNode("sphere")
    node.addGeom(geom)
    return node
