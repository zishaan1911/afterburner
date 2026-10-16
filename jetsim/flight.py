"""Arcade flight model.

Orientation changes are applied in the jet's own frame so pitch/roll/yaw compose
the way a stick would. Forward motion follows the nose; a little gravity bleeds
altitude when the jet gets slow, so speed has to be respected.
"""

from .config import (
    BOOST_SPEED,
    GRAVITY,
    GROUND_CLEARANCE,
    LIFT_SPEED,
    MAX_ALT,
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
    def __init__(self, jet, terrain):
        self.jet = jet
        self.terrain = terrain
        self.throttle = 0.6
        self.speed = MIN_SPEED + (MAX_SPEED - MIN_SPEED) * self.throttle
        self.boosting = False

    @property
    def altitude(self):
        return self.jet.getZ()

    @property
    def heading(self):
        return self.jet.getH() % 360.0

    @property
    def mach(self):
        return self.speed / 340.0

    def reset(self):
        self.jet.setPosHpr(0, -220, START_ALT, 0, 0, 0)
        self.throttle = 0.6
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

        # Rotate in the jet's local frame.
        self.jet.setP(self.jet, controls.pitch * PITCH_RATE * dt)
        self.jet.setR(self.jet, controls.roll * ROLL_RATE * dt)
        self.jet.setH(self.jet, -controls.yaw * YAW_RATE * dt)

        quat = self.jet.getQuat()
        pos = self.jet.getPos()
        pos += quat.getForward() * self.speed * dt

        # Gravity, countered by airspeed.
        lift = clamp(self.speed / LIFT_SPEED, 0.0, 1.0)
        pos.setZ(pos.getZ() - GRAVITY * (1.0 - lift) * dt)

        self._wrap(pos)

        ground = self.terrain.elevation(pos.getX(), pos.getY())
        if pos.getZ() < ground + GROUND_CLEARANCE:
            pos.setZ(ground + GROUND_CLEARANCE)
        if pos.getZ() > MAX_ALT:
            pos.setZ(MAX_ALT)

        self.jet.setPos(pos)

    def _wrap(self, pos):
        limit = self.terrain.half_extent - 60.0
        if pos.getX() > limit:
            pos.setX(-limit)
        elif pos.getX() < -limit:
            pos.setX(limit)
        if pos.getY() > limit:
            pos.setY(-limit)
        elif pos.getY() < -limit:
            pos.setY(limit)
