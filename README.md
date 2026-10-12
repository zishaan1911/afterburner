# Afterburner

An insane-looking 3D fighter jet simulator built with [Panda3D](https://www.panda3d.org/).

Procedural everything — the jet, the terrain, the sky, and a glowing afterburner
with real-time bloom. No external assets required; it runs straight from Python.

![afterburner](docs/screenshot.png)

## Features

- Procedurally modelled twin-tail fighter jet
- Rolling procedural terrain with height-based colouring (water → grass → rock → snow)
- Gradient sky, atmospheric fog and a bloom post-process pipeline
- Dual-engine afterburner with dynamic point lights that flare with throttle
- Arcade flight model: pitch / roll / yaw, throttle, and an afterburner boost
- Smooth chase camera with speed-reactive field of view
- Heads-up display: airspeed, Mach, altitude, heading and throttle

## Install

```bash
python -m pip install -r requirements.txt
```

## Fly

```bash
python main.py
```

## Controls

| Key | Action |
| --- | --- |
| `W` / `S` | Pitch nose down / up |
| `A` / `D` | Roll left / right |
| `Q` / `E` | Yaw left / right |
| `Shift` / `Ctrl` | Throttle up / down |
| `Space` | Afterburner boost |
| `R` | Reset |
| `Esc` | Quit |

## Requirements

- Python 3.9+
- Panda3D 1.10+
