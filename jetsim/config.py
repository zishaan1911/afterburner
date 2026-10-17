"""Tunable constants and small math helpers for the simulator."""

# --- Jet -------------------------------------------------------------------
JET_SCALE = 1.0             # the Su-57 glTF is modelled in metres (~20 m long)

# --- Edge-of-space scene ---------------------------------------------------
EARTH_RADIUS = 3200.0       # world units
EARTH_SURFACE_Z = -430.0    # top of the globe sits this far below the origin
ATMO_THICKNESS = 170.0      # atmosphere shell thickness
STAR_RADIUS = 9000.0        # star dome radius
STAR_COUNT = 1400
# Sun direction (heading, pitch) in degrees - low on the horizon for golden hour
SUN_HPR = (52.0, -8.0, 0.0)

# --- Flight model ----------------------------------------------------------
MIN_SPEED = 60.0            # units/second with the throttle closed
MAX_SPEED = 420.0           # units/second at full military throttle
BOOST_SPEED = 620.0         # units/second with the afterburner lit
PITCH_RATE = 42.0           # degrees/second
ROLL_RATE = 115.0           # degrees/second
YAW_RATE = 22.0             # degrees/second
THROTTLE_RATE = 0.6         # throttle units/second
START_ALT = 60.0            # spawn altitude above the origin plane
FLOOR_Z = -360.0            # don't descend into the atmosphere/Earth
CEILING_Z = 1600.0          # altitude ceiling

# --- Rendering -------------------------------------------------------------
EXPOSURE = 0.0              # simplepbr filmic-tonemap exposure stops

# --- Camera ----------------------------------------------------------------
CAM_DISTANCE = 27.0
CAM_HEIGHT = 7.0
CAM_LAG = 4.0
BASE_FOV = 60.0
MAX_FOV = 80.0


def clamp(value, low, high):
    return max(low, min(high, value))


def lerp(a, b, t):
    return a + (b - a) * t


def lerp3(a, b, t):
    return (lerp(a[0], b[0], t), lerp(a[1], b[1], t), lerp(a[2], b[2], t))
