"""Arcade flight model for open, high-altitude flight.

Orientation changes are applied in the jet's own frame so pitch/roll/yaw compose
the way a stick would, and forward motion follows the nose. There is no terrain
up here - just a floor above the atmosphere and a ceiling.
"""

from .config import (
    BOOST_SPEED,
    CEILING_Z,
    EARTH_SURFACE_Z,
    FLOOR_Z,
    MAX_SPEED,
    MIN_SPEED,
    PITCH_RATE,
    ROLL_RATE,
    START_ALT,
    THROTTLE_RATE,
    YAW_RATE,
    clamp,
)


class Controls:
    """A snapshot of the pilot's inputs for one frame."""

    def __init__(self, pitch=0.0, roll=0.0, yaw=0.0, throttle=0.0, boost=False):
        self.pitch = pitch
        self.roll = roll
        self.yaw = yaw
        self.throttle = throttle
        self.boost = boost


class FlightModel:
    def __init__(self, jet):
        self.jet = jet
        self.throttle = 0.65
        self.speed = MIN_SPEED + (MAX_SPEED - MIN_SPEED) * self.throttle
        self.boosting = False

    @property
    def altitude_km(self):
        # A cinematic "edge of space" readout derived from world height.
        return 48.0 + (self.jet.getZ() - EARTH_SURFACE_Z - 430.0) / 22.0

    @property
    def heading(self):
        return self.jet.getH() % 360.0

    @property
    def mach(self):
        return self.speed / 300.0

    def reset(self):
        self.jet.setPosHpr(0, -260, START_ALT, 0, 0, 0)
        self.throttle = 0.65
        self.speed = MIN_SPEED + (MAX_SPEED - MIN_SPEED) * self.throttle
        self.boosting = False

    def update(self, dt, controls):
        self.boosting = controls.boost
        self.throttle = clamp(
            self.throttle + controls.throttle * THROTTLE_RATE * dt, 0.0, 1.0
        )

        target = BOOST_SPEED if controls.boost else (
            MIN_SPEED + self.throttle * (MAX_SPEED - MIN_SPEED)
        )
        self.speed += (target - self.speed) * min(1.0, dt * 0.8)

        self.jet.setP(self.jet, controls.pitch * PITCH_RATE * dt)
        self.jet.setR(self.jet, controls.roll * ROLL_RATE * dt)
        self.jet.setH(self.jet, -controls.yaw * YAW_RATE * dt)

        pos = self.jet.getPos()
        pos += self.jet.getQuat().getForward() * self.speed * dt
        pos.setZ(clamp(pos.getZ(), FLOOR_Z, CEILING_Z))
        self.jet.setPos(pos)
