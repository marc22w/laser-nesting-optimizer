# Laser Nesting Optimizer

A Python tool that arranges sheet-metal parts on laser-cutting sheets to minimize
material waste. Parts are read from DXF files, nested across as many sheets as
needed, and exported as one DXF per sheet, ready for CAD/CAM (tested in Autodesk Fusion).

![Shelf vs MaxRects comparison](docs/comparison.png)

## Results

**Single sheet**: 14 parts on a standard 2000 × 1000 mm sheet, 2 mm gap:

| Algorithm | Parts placed | Sheet utilization |
|---|---|---|
| Shelf packing (baseline) | 12 / 14 | 73.2% |
| **MaxRects + 90° rotation** | **12 / 14** | **84.2%** |

**Multi-sheet**: 13 parts read from DXF (perforated plates, L-brackets, flanges,
covers, side panels):

| Algorithm | Sheets used | Utilization per sheet |
|---|---|---|
| Shelf packing | 2 | 64.5%, 49.0% |
| **MaxRects + 90° rotation** | **2** | **81.8%, 31.8%** |

MaxRects packs the first sheet much denser, leaving a larger reusable offcut on the second.

## Features

- **DXF import**: one file per part; quantity from the file name
  (`flange_x3.dxf` = 3 pieces); bounding box computed from lines, arcs, circles,
  polylines and splines; automatic unit conversion (cm, inch → mm).
- **Two nesting algorithms**
  - *Shelf packing*: simple row-based baseline.
  - *MaxRects (Best Short Side Fit)*: tracks every free rectangle on the sheet and
    tries each part in both orientations, placing it where it fits tightest.
- **Multi-sheet nesting**: when a sheet is full, remaining parts go to a new one;
  parts that cannot fit even on an empty sheet are reported.
- **Kerf / minimum gap** between parts, configurable.
- **DXF export per sheet** on separate layers (`FOAIE` sheet outline, `TAIERE` cut
  contours, `ETICHETE` labels), in millimetres.
- **Visualization** with matplotlib (rotated parts in orange).
- **151 automated tests** (pytest): no part leaves the sheet, no overlaps, gap is
  respected, every part is placed exactly once, unit conversion, DXF round-trip.

## DXF opened in Fusion

![DXF in Fusion](docs/fusion.png)

## Quick start

```bash
git clone https://github.com/marc22w/laser-nesting-optimizer.git
cd laser-nesting-optimizer
python3 -m venv .venv && source .venv/bin/activate
pip install -r requirements.txt

python make_examples.py   # creates sample parts in piese/
python main.py            # nests them, saves output/foaia_1.dxf, foaia_2.dxf, ...
python -m pytest -q       # runs the test suite
```

To nest your own parts, export each one from Fusion as DXF
(right-click sketch → *Save As DXF*) into the `piese/` folder, e.g. `bracket_x4.dxf`.

## Project structure

```
nesting/
  models.py       # Part and Placement data classes
  packer.py       # shelf packing (baseline)
  maxrects.py     # MaxRects algorithm with rotation
  multisheet.py   # nesting across multiple sheets
  import_dxf.py   # read parts from DXF files
  export_dxf.py   # write nested sheets to DXF
  plot.py         # matplotlib visualization
tests/            # pytest suite
main.py           # reads parts, compares algorithms, exports one DXF per sheet
make_examples.py  # generates sample parts in piese/
make_figures.py   # generates docs/comparison.png
```

## Roadmap

- [x] Import parts from DXF files
- [x] Multi-sheet nesting
- [ ] Irregular (non-rectangular) part shapes with Shapely
- [ ] Genetic algorithm to optimize part order and orientation
- [x] Export the real part geometry (holes, arcs) instead of bounding boxes
- [x] Cutting-time estimate per sheet (cut length + pierce count)

## Tech stack

Python · Shapely · ezdxf · matplotlib · pytest

## Author

Marc Vintila, Precision Engineering student, Technical University of Cluj-Napoca
