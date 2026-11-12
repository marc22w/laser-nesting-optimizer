from dataclasses import dataclass


@dataclass
class Part:
    name: str
    w: float  # latime, mm
    h: float  # inaltime, mm


@dataclass
class Placement:
    part: Part
    x: float
    y: float
