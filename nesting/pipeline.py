"""Tot fluxul intr-o functie: folder cu piese DXF -> foi nestate, DXF-uri, statistici."""
import io
import tempfile
import zipfile
from dataclasses import dataclass
from pathlib import Path

from .cutting_time import ParametriLaser, estimare_foaie
from .export_dxf import export_dxf
from .import_dxf import citeste_folder
from .multisheet import utilizare
from .optimizer import nest_optim


@dataclass
class RezultatFoaie:
    placements: list
    utilizare: float
    lungime_mm: float
    strapungeri: int
    timp_s: float
    deplasare_mm: float
    deplasare_naiva_mm: float
    dxf: bytes


@dataclass
class Rezultat:
    foi: list
    imposibile: list
    strategie: tuple
    numar_piese: int

    @property
    def timp_total_s(self):
        return sum(f.timp_s for f in self.foi)

    def zip_dxf(self):
        buf = io.BytesIO()
        with zipfile.ZipFile(buf, "w", zipfile.ZIP_DEFLATED) as z:
            for i, foaie in enumerate(self.foi, start=1):
                z.writestr(f"foaia_{i}.dxf", foaie.dxf)
        return buf.getvalue()


def proceseaza(folder_piese, sheet_w, sheet_h, gap=2.0, laser=ParametriLaser()):
    parts = citeste_folder(folder_piese)
    foi, imposibile, strategie = nest_optim(parts, sheet_w, sheet_h, gap)
    cache, rezultate = {}, []
    with tempfile.TemporaryDirectory() as tmp:
        for i, foaie in enumerate(foi, start=1):
            lungime, strapungeri, timp = estimare_foaie(foaie, laser, cache)
            stat = {}
            fisier = Path(tmp) / f"foaia_{i}.dxf"
            # fara traseu: un CAM ar putea taia si liniile de deplasare
            export_dxf(foaie, sheet_w, sheet_h, str(fisier), statistici=stat)
            rezultate.append(RezultatFoaie(
                placements=foaie,
                utilizare=utilizare(foaie, sheet_w, sheet_h),
                lungime_mm=lungime, strapungeri=strapungeri, timp_s=timp,
                deplasare_mm=stat["deplasare_mm"],
                deplasare_naiva_mm=stat["deplasare_naiva_mm"],
                dxf=fisier.read_bytes()))
    return Rezultat(rezultate, imposibile, strategie, len(parts))
