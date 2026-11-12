import re 
import tempfile
from pathlib import Path

import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
import streamlit as st

from nesting.cutting_time import ParametriLaser, format_timp
from nesting.exemple import genereaza_exemple
from nesting.pipeline import proceseaza
from nesting.plot import plot_sheet

_CANTITATE = re.compile(r"^(?P<nume>.+?)_x(?P<n>\d+)$")

st.set_page_config(page_title="Laser Nesting Optimizer", page_icon="✂️", layout="wide")
st.title("✂️ Laser Nesting Optimizer")
st.caption("Incarca piese DXF, aranjeaza-le pe foi de tabla si descarca fisierele gata de taiat.")

# --- parametri ---
with st.sidebar:
    st.header("Foaia de tabla")
    sheet_w = st.number_input("Latime (mm)", 100, 6000, 2000, step=100)
    sheet_h = st.number_input("Inaltime (mm)", 100, 3000, 1000, step=100)
    gap = st.number_input("Distanta intre piese (mm)", 0.0, 50.0, 2.0, step=0.5)
    st.header("Laser")
    viteza = st.number_input("Viteza de taiere (mm/min)", 100, 50000, 3000, step=100)
    strapungere = st.number_input("Timp de strapungere (s)", 0.0, 10.0, 0.5, step=0.1)
    st.caption("Valorile implicite: otel 2-3 mm, laser cu fibra.")

# --- piese ---
fisiere = st.file_uploader("Piese DXF (cate un fisier pe piesa)", type=["dxf"],
                           accept_multiple_files=True)
cantitati = {}
if fisiere:
    st.subheader("Cantitati")
    coloane = st.columns(min(len(fisiere), 4))
    for i, f in enumerate(fisiere):
        stem = Path(f.name).stem
        m = _CANTITATE.match(stem)
        nume, n = (m["nume"], int(m["n"])) if m else (stem, 1)
        bucati = coloane[i % len(coloane)].number_input(nume, 1, 500, n, key=f"q_{f.name}")
        cantitati[f.name] = (nume, bucati)

col1, col2 = st.columns(2)
ruleaza = col1.button("Aranjeaza piesele", type="primary", disabled=not fisiere,
                      use_container_width=True)
ruleaza_demo = col2.button("Incearca cu piesele demo", use_container_width=True)

if ruleaza or ruleaza_demo:
    laser = ParametriLaser(viteza_mm_min=viteza, strapungere_s=strapungere)
    with st.spinner("Caut cea mai buna aranjare..."), tempfile.TemporaryDirectory() as tmp:
        folder = Path(tmp)
        if ruleaza_demo:
            genereaza_exemple(folder)
        else:
            for f in fisiere:
                nume, bucati = cantitati[f.name]
                (folder / f"{nume}_x{bucati}.dxf").write_bytes(f.getvalue())
        try:
            st.session_state.rezultat = proceseaza(folder, sheet_w, sheet_h, gap, laser)
            st.session_state.foaie = (sheet_w, sheet_h)
        except Exception as e:  # fisier DXF stricat, fara geometrie etc.
            st.session_state.rezultat = None
            st.error(f"Nu am putut procesa piesele: {e}")

# --- rezultate (raman afisate si dupa un click pe Descarca) ---
rez = st.session_state.get("rezultat")
if rez is not None:
    sw, sh = st.session_state.foaie
    st.divider()
    c = st.columns(4)
    c[0].metric("Piese", rez.numar_piese)
    c[1].metric("Foi necesare", len(rez.foi))
    c[2].metric("Timp total de taiere", format_timp(rez.timp_total_s))
    c[3].metric("Strategie aleasa", f"{rez.strategie[0]} / {rez.strategie[1]}")

    if rez.imposibile:
        st.error("Nu incap nici pe o foaie goala: "
                 + ", ".join(p.name for p in rez.imposibile))
    if rez.foi:
        st.download_button("Descarca toate foile (ZIP)", rez.zip_dxf(),
                           "foi_dxf.zip", "application/zip", type="primary")

    for i, foaie in enumerate(rez.foi, start=1):
        st.subheader(f"Foaia {i}")
        stanga, dreapta = st.columns([3, 1])
        fig = plot_sheet(foaie.placements, sw, sh, f"Foaia {i}: {foaie.utilizare:.1f}%")
        stanga.pyplot(fig)
        plt.close(fig)
        dreapta.metric("Utilizare", f"{foaie.utilizare:.1f}%")
        dreapta.metric("Lungime de taiere", f"{foaie.lungime_mm / 1000:.1f} m")
        dreapta.metric("Strapungeri", foaie.strapungeri)
        dreapta.metric("Timp estimat", format_timp(foaie.timp_s))
        if foaie.deplasare_naiva_mm > 0:
            economie = 100 * (1 - foaie.deplasare_mm / foaie.deplasare_naiva_mm)
            dreapta.metric("Deplasari in gol", f"{foaie.deplasare_mm / 1000:.1f} m",
                           f"-{economie:.0f}% fata de neoptimizat", delta_color="inverse")
        dreapta.download_button("Descarca DXF", foaie.dxf, f"foaia_{i}.dxf",
                                "application/dxf", key=f"dxf_{i}")