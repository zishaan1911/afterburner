"""Tunable constants and small math helpers for the simulator."""

# --- Terrain ---------------------------------------------------------------
TERRAIN_SIZE = 257          # heightfield resolution (must be 2^n + 1)
HSCALE = 16.0               # world units per heightfield pixel
ZSCALE = 130.0              # vertical scale of the terrain

# --- Flight model ----------------------------------------------------------
MIN_SPEED = 45.0            # units/second with the throttle closed
MAX_SPEED = 340.0           # units/second at full military throttle
BOOST_SPEED = 470.0         # units/second with the afterburner lit
PITCH_RATE = 55.0           # degrees/second
ROLL_RATE = 135.0           # degrees/second
YAW_RATE = 28.0             # degrees/second
THROTTLE_RATE = 0.6         # throttle units/second
GRAVITY = 42.0              # downward drift when slow
LIFT_SPEED = 150.0          # speed at which lift fully counters gravity
START_ALT = 240.0           # spawn altitude
MAX_ALT = 980.0             # altitude ceiling
GROUND_CLEARANCE = 9.0      # minimum height above the terrain

# --- Camera ----------------------------------------------------------------
CAM_DISTANCE = 17.0
CAM_HEIGHT = 4.5
CAM_LAG = 4.5
BASE_FOV = 62.0
MAX_FOV = 84.0


def clamp(value, low, high):
    return max(low, min(high, value))


def lerp(a, b, t):
    return a + (b - a) * t


def lerp3(a, b, t):
    return (lerp(a[0], b[0], t), lerp(a[1], b[1], t), lerp(a[2], b[2], t))
