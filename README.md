# Laser Nesting Optimizer

![tests](https://github.com/marc22w/laser-nesting-optimizer/actions/workflows/tests.yml/badge.svg)

A Python tool that turns sheet-metal parts drawn in CAD into cut-ready laser files.
Parts are read from DXF, nested across as many sheets as needed, ordered for cutting
like a CAM system would, and exported as one DXF per sheet with a cutting-time estimate
(tested in Autodesk Fusion).

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
| MaxRects (single strategy) | 2 | 81.8%, 31.8% |
| **Best of 15 strategies** | **2** | **84.2%, 29.2%** |

**Cutting**: optimized cut order on the same job:

| Sheet | Cut length | Pierces | Idle travel (optimized / naive) | Est. time |
|---|---|---|---|---|
| 1 | 20.3 m | 220 | **13.0 m** / 19.1 m (−32%) | ~8 min 37 s |
| 2 | 7.6 m | 16 | **2.3 m** / 3.0 m (−24%) | ~2 min 41 s |

Pierce count matters: on sheet 1, the 208 holes of the perforated plates add almost
2 minutes of piercing alone.

## Features

- **DXF import**: one file per part; quantity from the file name
  (`flange_x3.dxf` = 3 pieces); bounding box from lines, arcs, circles,
  polylines and splines; automatic unit conversion (cm, inch → mm).
- **Nesting**
  - *Shelf packing*: simple row-based baseline.
  - *MaxRects* with 90° rotation and three placement rules
    (Best Short Side Fit, Best Area Fit, Bottom-Left).
  - *Strategy search*: tries 5 sort orders × 3 rules and keeps the result with the
    fewest sheets (ties broken by the largest reusable offcut).
  - *Multi-sheet*: when a sheet is full, remaining parts go to a new one.
- **Cut-ready DXF export** with the **real part geometry** (holes, arcs, L-shapes),
  translated and rotated to the nested position, on separate layers
  (`TAIERE` cut, `FOAIE` sheet, `ETICHETE` labels, `TRASEU` idle travel).
- **Cut ordering** like a CAM post-processor: inner contours (holes) before the
  outer contour of each part, nearest-neighbour sequencing to shorten idle travel.
- **Cutting-time estimate** per sheet from total contour length and pierce count.
- **188 automated tests** (pytest), run on every push with **GitHub Actions**.

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
Laser speed and pierce time are set at the top of `main.py`.

## Project structure

```
nesting/
  models.py         # Part and Placement data classes
  import_dxf.py     # read parts from DXF files
  packer.py         # shelf packing (baseline)
  maxrects.py       # MaxRects with rotation and 3 placement rules
  optimizer.py      # search over 15 sort/rule strategies
  multisheet.py     # nesting across multiple sheets
  cut_order.py      # holes-first, nearest-neighbour cut sequencing
  cutting_time.py   # cut length, pierce count, time estimate
  export_dxf.py     # write nested sheets to DXF with real geometry
  plot.py           # matplotlib visualization
tests/              # pytest suite
.github/workflows/  # CI: tests on every push
main.py             # full pipeline: import, nest, order, export, estimate
```

## Roadmap

- [x] Import parts from DXF files
- [x] Multi-sheet nesting
- [x] Export the real part geometry (holes, arcs)
- [x] Cutting-time estimate per sheet (cut length + pierce count)
- [x] Strategy search over sort orders and placement rules
- [x] Cut ordering (holes first, nearest-neighbour)
- [ ] Irregular (true-shape) nesting with Shapely
- [ ] Command-line options (sheet size, gap, laser parameters)

## Tech stack

Python · ezdxf · matplotlib · pytest · GitHub Actions

## Author

Marc Vintila, Precision Engineering student, Technical University of Cluj-Napoca