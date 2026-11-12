"""Interfata web pentru Laser Nesting Optimizer. Pornire: streamlit run app.py"""
import csv
import io
import re
import tempfile
from datetime import date
from pathlib import Path

import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
from matplotlib.patches import Rectangle
import streamlit as st

from nesting.cutting_time import ParametriLaser, format_timp
from nesting.exemple import genereaza_exemple
from nesting.pipeline import proceseaza

_CANTITATE = re.compile(r"^(?P<nume>.+?)_x(?P<n>\d+)$")

ACCENT = "#FF6B35"   # portocaliu laser
OTEL = "#4C9BE8"     # albastru otel
PANOU = "#1A2129"
LINIE = "#8FA3B5"
GITHUB = "https://github.com/marc22w/laser-nesting-optimizer"

# Valori orientative pentru un laser cu fibra de ~3 kW
MATERIALE = {
    "Otel S235 · 2 mm":     dict(grosime=2.0, densitate=7850, viteza=3000, strapungere=0.5),
    "Otel S235 · 5 mm":     dict(grosime=5.0, densitate=7850, viteza=1500, strapungere=1.2),
    "Inox 304 · 1.5 mm":    dict(grosime=1.5, densitate=8000, viteza=4000, strapungere=0.3),
    "Aluminiu 5754 · 3 mm": dict(grosime=3.0, densitate=2700, viteza=3500, strapungere=0.4),
}
FORMATE = {
    "2000 × 1000 mm (format mic)":   (2000, 1000),
    "2500 × 1250 mm (format mediu)": (2500, 1250),
    "3000 × 1500 mm (format mare)":  (3000, 1500),
}

CSS = """
<style>
@import url('https://fonts.googleapis.com/css2?family=Barlow+Condensed:wght@500;600;700&family=JetBrains+Mono:wght@400;600&display=swap');

.stApp {
    background-color: #0F1419;
    background-image:
        linear-gradient(rgba(143,163,181,0.05) 1px, transparent 1px),
        linear-gradient(90deg, rgba(143,163,181,0.05) 1px, transparent 1px),
        linear-gradient(rgba(143,163,181,0.025) 1px, transparent 1px),
        linear-gradient(90deg, rgba(143,163,181,0.025) 1px, transparent 1px);
    background-size: 100px 100px, 100px 100px, 20px 20px, 20px 20px;
}
.block-container { padding-top: 2.5rem; }
[data-testid="stSidebarUserContent"] { padding-top: 1.5rem; }
.stAppDeployButton { display: none; }

h1, h2, h3 { font-family: 'Barlow Condensed', sans-serif !important; letter-spacing: 0.02em; }

[data-testid="stSidebar"] {
    background: #1A2129;
    border-right: 1px solid rgba(255,255,255,0.06);
}
[data-testid="stMetric"] {
    background: #1A2129;
    border: 1px solid rgba(255,255,255,0.08);
    border-left: 3px solid #FF6B35;
    border-radius: 8px;
    padding: 12px 16px;
}
[data-testid="stMetricValue"] { font-family: 'JetBrains Mono', monospace; font-size: 1.6rem; }
[data-testid="stMetricLabel"] { text-transform: uppercase; letter-spacing: 0.08em; font-size: 0.75rem; }
[data-testid="stFileUploaderDropzone"] {
    border: 1.5px dashed rgba(255,107,53,0.5);
    background: rgba(255,107,53,0.04);
}

/* banner */
.hero {
    display: flex; align-items: center; gap: 24px;
    padding: 26px 30px; border-radius: 12px; margin-bottom: 18px;
    background: linear-gradient(135deg, rgba(255,107,53,0.14), rgba(76,155,232,0.08));
    border: 1px solid rgba(255,255,255,0.08);
}
.hero-text { flex: 1; }
.hero .eticheta {
    font-family: 'JetBrains Mono', monospace; font-size: 0.75rem;
    letter-spacing: 0.18em; color: #8FA3B5;
}
.hero .titlu {
    font-family: 'Barlow Condensed', sans-serif; font-weight: 700;
    font-size: 3rem; line-height: 1.05; margin: 4px 0 6px; text-transform: uppercase;
}
.hero .titlu span { color: #FF6B35; }
.hero .descriere { color: #AEB6BF; font-size: 1.02rem; margin-bottom: 14px; }
.hero-svg { width: 340px; flex-shrink: 0; }
@media (max-width: 1000px) { .hero-svg { display: none; } }
.badge {
    display: inline-block; margin: 0 6px 6px 0; padding: 4px 11px;
    border-radius: 4px; font-size: 0.8rem; color: #E6E9EC;
    font-family: 'JetBrains Mono', monospace;
    background: rgba(255,255,255,0.05); border: 1px solid rgba(255,255,255,0.12);
}
.cap-laser { animation: deplasare 3.5s ease-in-out infinite alternate; }
@keyframes deplasare { from { transform: translateX(-95px); } to { transform: translateX(95px); } }
.scantei { animation: licar 0.12s steps(2) infinite; }
@keyframes licar { 0% { opacity: 1; } 100% { opacity: 0.2; } }

/* titlu de sectiune in stil linie de cota */
.cota {
    display: flex; align-items: center; gap: 14px; margin: 30px 0 14px;
    font-family: 'Barlow Condensed', sans-serif; font-weight: 600;
    letter-spacing: 0.2em; color: #8FA3B5; font-size: 1rem;
}
.cota::before, .cota::after {
    content: ""; flex: 1; height: 1px; background: #5B6773;
    border-left: 1px solid #8FA3B5; border-right: 1px solid #8FA3B5;
}

/* pasi */
.pas {
    background: #1A2129; border: 1px solid rgba(255,255,255,0.08);
    border-radius: 10px; padding: 18px 20px; height: 100%;
}
.pas .nr { font-family: 'JetBrains Mono', monospace; color: #FF6B35; font-size: 1.6rem; font-weight: 600; }
.pas .titlu-pas { font-family: 'Barlow Condensed', sans-serif; font-weight: 700; font-size: 1.3rem; margin: 2px 0 6px; text-transform: uppercase; }
.pas .text-pas { color: #AEB6BF; font-size: 0.92rem; }

/* cartus (indicatorul desenului tehnic) */
.cartus {
    display: grid; grid-template-columns: repeat(4, 1fr);
    border: 1.5px solid #8FA3B5; margin-top: 6px;
}
.cartus div { border: 1px solid rgba(143,163,181,0.35); padding: 5px 10px; }
.cartus span {
    display: block; font-size: 0.65rem; letter-spacing: 0.1em;
    text-transform: uppercase; color: #8FA3B5;
}
.cartus b { font-family: 'JetBrains Mono', monospace; font-weight: 400; font-size: 0.85rem; color: #E6E9EC; }

.subsol { text-align: center; color: #6B7680; font-size: 0.82rem; margin-top: 40px; font-family: 'JetBrains Mono', monospace; }
.subsol a { color: #FF6B35; text-decoration: none; }
</style>
"""

HERO = """
<div class="hero">
<div class="hero-text">
<div class="eticheta">INSTRUMENT CAM · TABLA TAIATA CU LASER</div>
<div class="titlu">Laser <span>Nesting</span> Optimizer</div>
<div class="descriere">Incarca piese DXF, aranjeaza-le pe foi de tabla si descarca planurile de taiere gata pentru masina.</div>
<span class="badge">MaxRects + rotire 90°</span>
<span class="badge">15 strategii</span>
<span class="badge">Multi-foaie</span>
<span class="badge">Gauri inaintea conturului</span>
<span class="badge">Timp · masa · cost</span>
</div>
<svg class="hero-svg" viewBox="0 0 320 190" xmlns="http://www.w3.org/2000/svg">
<defs>
<marker id="sageata" viewBox="0 0 10 10" refX="5" refY="5" markerWidth="6" markerHeight="6" orient="auto-start-reverse"><path d="M0,0 L10,5 L0,10 z" fill="#8FA3B5"/></marker>
<filter id="stralucire"><feGaussianBlur stdDeviation="2.5"/></filter>
</defs>
<circle cx="42" cy="42" r="22" fill="none" stroke="#2F3B47" stroke-width="9" stroke-dasharray="7 5"/>
<circle cx="42" cy="42" r="10" fill="none" stroke="#2F3B47" stroke-width="3"/>
<circle cx="282" cy="40" r="13" fill="none" stroke="#2F3B47" stroke-width="6" stroke-dasharray="5 4"/>
<rect x="20" y="120" width="280" height="14" fill="#2A3440" stroke="#5B6773"/>
<line x1="20" y1="136" x2="20" y2="168" stroke="#5B6773" stroke-width="0.8"/>
<line x1="300" y1="136" x2="300" y2="168" stroke="#5B6773" stroke-width="0.8"/>
<line x1="20" y1="160" x2="300" y2="160" stroke="#8FA3B5" stroke-width="1" marker-start="url(#sageata)" marker-end="url(#sageata)"/>
<text x="160" y="180" fill="#C9D3DC" font-size="11" text-anchor="middle" font-family="monospace">2000</text>
<g class="cap-laser">
<rect x="145" y="12" width="30" height="46" rx="3" fill="#3A4552" stroke="#5B6773"/>
<rect x="150" y="20" width="20" height="4" fill="#FF6B35" opacity="0.85"/>
<polygon points="148,58 172,58 165,82 155,82" fill="#4A5563" stroke="#5B6773"/>
<line x1="160" y1="82" x2="160" y2="120" stroke="#FF6B35" stroke-width="7" opacity="0.5" filter="url(#stralucire)"/>
<line x1="160" y1="82" x2="160" y2="120" stroke="#FFD2BF" stroke-width="1.6"/>
<g class="scantei" stroke="#FFB347" stroke-width="1.4" stroke-linecap="round">
<line x1="160" y1="120" x2="146" y2="109"/>
<line x1="160" y1="120" x2="175" y2="107"/>
<line x1="160" y1="120" x2="152" y2="103"/>
<line x1="160" y1="120" x2="171" y2="114"/>
</g>
</g>
</svg>
</div>
"""


def sectiune(text):
    st.markdown(f'<div class="cota">{text}</div>', unsafe_allow_html=True)


def pas(nr, titlu, text):
    return (f'<div class="pas"><div class="nr">{nr:02d}</div>'
            f'<div class="titlu-pas">{titlu}</div><div class="text-pas">{text}</div></div>')


def masa_foaie_kg(ctx):
    """Masa unei foi: latime x inaltime x grosime (mm3) -> m3, ori densitatea."""
    return ctx["sw"] * ctx["sh"] * ctx["grosime"] * 1e-9 * ctx["densitate"]


def cartus(i, n, foaie, ctx, strategie):
    celule = [
        ("Denumire", f"Plan de taiere · foaia {i}/{n}"),
        ("Material", ctx["material"]),
        ("Format", f"{ctx['sw']} × {ctx['sh']} mm"),
        ("Masa foaie", f"{masa_foaie_kg(ctx):.1f} kg"),
        ("Piese", len(foaie.placements)),
        ("Utilizare", f"{foaie.utilizare:.1f} %"),
        ("Strategie", f"{strategie[0]} / {strategie[1]}"),
        ("Data", date.today().strftime("%d.%m.%Y")),
    ]
    html = "".join(f"<div><span>{k}</span><b>{v}</b></div>" for k, v in celule)
    return f'<div class="cartus">{html}</div>'


def deseneaza_foaie(placements, sw, sh):
    """Foaia in stil de desen tehnic: contur fin, piese hasurate, cote cu sageti."""
    m = max(sw, sh) * 0.06
    inaltime = max(3.5, min(9.5, 12 * (sh + 2 * m) / (sw + 2 * m)))
    fig, ax = plt.subplots(figsize=(12, inaltime))
    fig.patch.set_facecolor(PANOU)
    ax.set_facecolor(PANOU)

    ax.add_patch(Rectangle((0, 0), sw, sh, facecolor="#22303C", edgecolor=LINIE, lw=1.4))
    for pl in placements:
        culoare = ACCENT if pl.rotated else OTEL
        ax.add_patch(Rectangle((pl.x, pl.y), pl.w, pl.h, facecolor=culoare,
                               alpha=0.30, edgecolor=culoare, lw=1.3, hatch="////"))
        if min(pl.w, pl.h) > 60:
            ax.text(pl.x + pl.w / 2, pl.y + pl.h / 2, pl.part.name, ha="center",
                    va="center", fontsize=7, color="#E6E9EC", family="monospace",
                    bbox=dict(facecolor=PANOU, edgecolor="none", alpha=0.7, pad=1.5))

    sageata = dict(arrowstyle="<|-|>", color=LINIE, lw=0.9, shrinkA=0, shrinkB=0,
                   mutation_scale=9)
    y = -m * 0.6
    for xx in (0, sw):
        ax.plot([xx, xx], [0, y - m * 0.2], color="#5B6773", lw=0.6)
    ax.annotate("", xy=(0, y), xytext=(sw, y), arrowprops=sageata)
    ax.text(sw / 2, y - m * 0.15, f"{sw:g}", ha="center", va="top", color="#C9D3DC",
            fontsize=9, family="monospace")
    x = -m * 0.6
    for yy in (0, sh):
        ax.plot([0, x - m * 0.2], [yy, yy], color="#5B6773", lw=0.6)
    ax.annotate("", xy=(x, 0), xytext=(x, sh), arrowprops=sageata)
    ax.text(x - m * 0.15, sh / 2, f"{sh:g}", ha="right", va="center", rotation=90,
            color="#C9D3DC", fontsize=9, family="monospace")

    ax.set_xlim(-m * 1.4, sw + m * 0.3)
    ax.set_ylim(-m * 1.4, sh + m * 0.3)
    ax.set_aspect("equal")
    ax.axis("off")
    fig.tight_layout()
    return fig


def raport_csv(rez, ctx):
    buf = io.StringIO()
    w = csv.writer(buf)
    w.writerow(["foaie", "piese", "utilizare_%", "lungime_taiere_m", "strapungeri",
                "timp_s", "deplasari_gol_m", "masa_foaie_kg"])
    for i, f in enumerate(rez.foi, start=1):
        w.writerow([i, len(f.placements), round(f.utilizare, 1), round(f.lungime_mm / 1000, 2),
                    f.strapungeri, round(f.timp_s), round(f.deplasare_mm / 1000, 2),
                    round(masa_foaie_kg(ctx), 2)])
    w.writerow([])
    w.writerow(["piesa", "foaie", "x_mm", "y_mm", "latime_mm", "inaltime_mm", "rotita"])
    for i, f in enumerate(rez.foi, start=1):
        for pl in f.placements:
            w.writerow([pl.part.name, i, round(pl.x, 1), round(pl.y, 1),
                        pl.w, pl.h, "da" if pl.rotated else "nu"])
    return buf.getvalue().encode("utf-8")


# ======================= pagina =======================
st.set_page_config(page_title="Laser Nesting Optimizer", page_icon="⚙️", layout="wide")
st.markdown(CSS, unsafe_allow_html=True)
st.markdown(HERO, unsafe_allow_html=True)

# --- parametri ---
with st.sidebar:
    st.header("Foaia de tabla")
    fmt = st.selectbox("Format", [*FORMATE, "Personalizat"])
    if fmt == "Personalizat":
        sheet_w = st.number_input("Latime (mm)", 100, 6000, 2000, step=100)
        sheet_h = st.number_input("Inaltime (mm)", 100, 3000, 1000, step=100)
    else:
        sheet_w, sheet_h = FORMATE[fmt]
    gap = st.number_input("Distanta intre piese (mm)", 0.0, 50.0, 2.0, step=0.5)

    st.header("Material")
    material = st.selectbox("Material si grosime", [*MATERIALE, "Personalizat"])
    preset = MATERIALE.get(material, MATERIALE["Otel S235 · 2 mm"])
    if material == "Personalizat":
        grosime = st.number_input("Grosime (mm)", 0.5, 30.0, 2.0, step=0.5)
        densitate = st.number_input("Densitate (kg/m³)", 1000, 20000, 7850, step=50)
        nume_material = f"Personalizat · {grosime:g} mm"
    else:
        grosime, densitate = preset["grosime"], preset["densitate"]
        nume_material = material

    st.header("Laser")
    viteza = st.number_input("Viteza de taiere (mm/min)", 100, 50000, preset["viteza"],
                             step=100, key=f"v_{material}")
    strapungere = st.number_input("Timp de strapungere (s)", 0.0, 10.0, preset["strapungere"],
                                  step=0.1, key=f"s_{material}")
    st.caption("Valori orientative pentru un laser cu fibra de ~3 kW. "
               "Ajusteaza-le dupa masina ta.")

    with st.expander("Costuri"):
        pret_kg = st.number_input("Pret material (lei/kg)", 0.0, 500.0, 6.0, step=0.5)
        tarif_min = st.number_input("Tarif laser (lei/min)", 0.0, 500.0, 8.0, step=0.5)
        st.caption("Introdu tarifele tale pentru o estimare realista.")

    st.divider()
    st.caption(f"Cod sursa si documentatie: [GitHub]({GITHUB})")

# --- piese ---
sectiune("PIESE")
fisiere = st.file_uploader("Fisiere DXF, cate unul pe piesa (ex: flansa_x3.dxf = 3 bucati)",
                           type=["dxf"], accept_multiple_files=True)
cantitati = {}
if fisiere:
    coloane = st.columns(min(len(fisiere), 4))
    for i, f in enumerate(fisiere):
        stem = Path(f.name).stem
        m = _CANTITATE.match(stem)
        nume, n = (m["nume"], int(m["n"])) if m else (stem, 1)
        bucati = coloane[i % len(coloane)].number_input(f"{nume} (buc)", 1, 500, n,
                                                        key=f"q_{f.name}")
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
            st.session_state.ctx = dict(sw=sheet_w, sh=sheet_h, grosime=grosime,
                                        densitate=densitate, material=nume_material,
                                        pret_kg=pret_kg, tarif_min=tarif_min)
        except Exception as e:  # fisier DXF stricat, fara geometrie etc.
            st.session_state.rezultat = None
            st.error(f"Nu am putut procesa piesele: {e}")

rez = st.session_state.get("rezultat")

# --- ghid, cat timp nu exista rezultate ---
if rez is None:
    sectiune("CUM FUNCTIONEAZA")
    a, b, c = st.columns(3)
    a.markdown(pas(1, "Incarca piesele",
                   "Exporta fiecare piesa din Fusion ca DXF. Cantitatea o scrii in numele "
                   "fisierului sau o setezi aici."), unsafe_allow_html=True)
    b.markdown(pas(2, "Aranjeaza",
                   "Algoritmul testeaza 15 strategii si pastreaza aranjarea cu cele mai "
                   "putine foi si cel mai mare rest refolosibil."), unsafe_allow_html=True)
    c.markdown(pas(3, "Descarca",
                   "Primesti planul de taiere pe fiecare foaie, cu geometria reala, ordinea "
                   "de taiere optimizata, timpul, masa si costul estimat."),
               unsafe_allow_html=True)

# --- rezultate (raman afisate si dupa un click pe Descarca) ---
else:
    ctx = st.session_state.ctx
    material_kg = len(rez.foi) * masa_foaie_kg(ctx)
    cost = material_kg * ctx["pret_kg"] + rez.timp_total_s / 60 * ctx["tarif_min"]

    sectiune("REZULTATE")
    c = st.columns(5)
    c[0].metric("Piese", rez.numar_piese)
    c[1].metric("Foi necesare", len(rez.foi))
    c[2].metric("Material", f"{material_kg:.1f} kg")
    c[3].metric("Timp de taiere", format_timp(rez.timp_total_s))
    c[4].metric("Cost estimat", f"{cost:,.0f} lei")
    st.caption(f"{ctx['material']} · foaie {ctx['sw']} × {ctx['sh']} mm · "
               f"strategie: sortare dupa {rez.strategie[0]}, regula {rez.strategie[1]}")

    if rez.imposibile:
        st.error("Nu incap nici pe o foaie goala: "
                 + ", ".join(p.name for p in rez.imposibile))
    if rez.foi:
        d1, d2, _ = st.columns([1, 1, 2])
        d1.download_button("⬇️ Toate foile (ZIP)", rez.zip_dxf(), "foi_dxf.zip",
                           "application/zip", type="primary", use_container_width=True)
        d2.download_button("📄 Raport (CSV)", raport_csv(rez, ctx), "raport_nesting.csv",
                           "text/csv", use_container_width=True)

    sectiune("PLANURI DE TAIERE")
    for i, foaie in enumerate(rez.foi, start=1):
        with st.container(border=True):
            st.subheader(f"Foaia {i} din {len(rez.foi)}")
            stanga, dreapta = st.columns([3, 1])
            fig = deseneaza_foaie(foaie.placements, ctx["sw"], ctx["sh"])
            stanga.pyplot(fig)
            plt.close(fig)
            stanga.caption("🟦 piesa normala   🟧 piesa rotita cu 90°   · cote in mm")
            stanga.markdown(cartus(i, len(rez.foi), foaie, ctx, rez.strategie),
                            unsafe_allow_html=True)
            dreapta.metric("Utilizare", f"{foaie.utilizare:.1f}%")
            dreapta.metric("Lungime de taiere", f"{foaie.lungime_mm / 1000:.1f} m")
            dreapta.metric("Strapungeri", foaie.strapungeri)
            dreapta.metric("Timp estimat", format_timp(foaie.timp_s))
            if foaie.deplasare_naiva_mm > 0:
                economie = 100 * (1 - foaie.deplasare_mm / foaie.deplasare_naiva_mm)
                dreapta.metric("Deplasari in gol", f"{foaie.deplasare_mm / 1000:.1f} m",
                               f"-{economie:.0f}% fata de neoptimizat",
                               delta_color="inverse")
            dreapta.download_button("⬇️ Descarca DXF", foaie.dxf, f"foaia_{i}.dxf",
                                    "application/dxf", key=f"dxf_{i}",
                                    use_container_width=True)

st.markdown(f'<div class="subsol">LASER NESTING OPTIMIZER · M. VINTILA · '
            f'<a href="{GITHUB}">COD SURSA PE GITHUB</a></div>', unsafe_allow_html=True)