"""Heads-up display: flight data, a throttle bar and a boresight reticle."""

from direct.gui.OnscreenText import OnscreenText
from panda3d.core import CardMaker, TextNode

GREEN = (0.55, 1.0, 0.65, 1.0)
AMBER = (1.0, 0.75, 0.2, 1.0)


def _bar(parent, x, y, w, h, color):
    cm = CardMaker("bar")
    cm.setFrame(0, w, 0, h)
    np = parent.attachNewNode(cm.generate())
    np.setPos(x, 0, y)
    np.setColor(*color)
    np.setTransparency(True)
    return np


class Hud:
    def __init__(self, base):
        a2d = base.aspect2d

        self.readout = OnscreenText(
            text="", parent=a2d, pos=(-1.28, 0.86), scale=0.058,
            align=TextNode.ALeft, fg=GREEN, mayChange=True,
            shadow=(0, 0, 0, 0.6),
        )

        OnscreenText(
            text="W/S pitch   A/D roll   Q/E yaw   SHIFT/CTRL throttle   "
                 "SPACE boost   R reset",
            parent=a2d, pos=(0, -0.94), scale=0.045,
            align=TextNode.ACenter, fg=(0.8, 0.85, 0.9, 0.85),
            shadow=(0, 0, 0, 0.6),
        )

        # Throttle bar (background frame + a fill that scales each frame).
        _bar(a2d, -1.28, -0.74, 0.5, 0.045, (0.1, 0.15, 0.12, 0.5))
        self.throttle_fill = _bar(a2d, -1.28, -0.74, 0.5, 0.045, (0.3, 1.0, 0.4, 0.85))
        self.throttle_label = OnscreenText(
            text="THR", parent=a2d, pos=(-1.28, -0.68), scale=0.04,
            align=TextNode.ALeft, fg=GREEN, mayChange=True,
        )

        # Centre reticle.
        _bar(a2d, -0.05, 0.0, 0.1, 0.004, GREEN)
        _bar(a2d, 0.0, -0.05, 0.004, 0.1, GREEN)

    def update(self, flight):
        boost = "  AB" if flight.boosting else ""
        self.readout.setText(
            "SPD  %4.0f\n"
            "MACH %4.2f\n"
            "ALT  %5.0f\n"
            "HDG  %03.0f%s"
            % (flight.speed, flight.mach, flight.altitude, flight.heading, boost)
        )
        self.throttle_fill.setScale(max(0.001, flight.throttle), 1, 1)
        color = AMBER if flight.boosting else GREEN
        self.throttle_fill.setColor(color[0], color[1], color[2], 0.85)
