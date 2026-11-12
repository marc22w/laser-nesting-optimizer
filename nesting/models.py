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
    rotated: bool = False

    @property
    def w(self):
        """Latimea piesei asa cum e asezata pe foaie."""
        return self.part.h if self.rotated else self.part.w

    @property
    def h(self):
        """Inaltimea piesei asa cum e asezata pe foaie."""
        return self.part.w if self.rotated else self.part.h
