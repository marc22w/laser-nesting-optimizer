"""Genereaza piesele de exemplu in folderul piese/."""
from nesting.exemple import genereaza_exemple

folder = genereaza_exemple("piese")
print(f"Generat {len(list(folder.glob('*.dxf')))} fisiere in {folder}/")
