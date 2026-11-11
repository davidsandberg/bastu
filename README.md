# Bastu till Paddelpalatset

3D-modeller, CAD-ritningar och visualisering för planerad bastubyggnad vid Paddelpalatset (forsstranden).

## Modeller

### 1. Hannu 44 (Polhus) – Mapp: [`hannu/`](./hannu/)
* **Interaktiv 3D-visare online:** [Öppna Hannu 44 i 3D](https://davidsandberg.github.io/bastu/hannu/)
* **Totalmått:** 4.40 m bredd × 2.70 m djup
* **Höjd:** 2.50 m (framkant) / 2.16 m (bakkant) – Pulpettak
* **Ytor:**
  * Basturum: 3.00 × 2.50 m (~7.2 m² med plats för 6–8 personer)
  * Veranda / Relax: 1.20 × 2.50 m (~3.0 m²)
* **Fasad mot forsen:** 3 stora panoramafönster (875 × 1700 mm vardera)
* **Konstruktion:** 44 mm knuttimmer med dubbelspont

#### Filer i `hannu/`:
* `index.html` / `hannu_bastu_3d_viewer.html` – WebGL 3D-visare (Three.js) med dag/kvällsbelysning, lyft av tak och mått.
* `hannu_bastu.obj` & `hannu_bastu.mtl` – 3D Wavefront-mesh för import till terrängmodellen (Blender, SketchUp, Rhino m.fl.).
* `hannu_bastu.gltf` – 3D-scen i glTF 2.0-format med PBR-material.
* `hannu_planritning.dxf` – CAD-ritning i skala 1:50 skapad med CADCraft CLI.
* `hannu_planritning.png` – Högupplöst CAD-rendering av planlösning och fasadritning mot forsen.
* `generate_bastu_assets.py` & `generate_cad_drawing.py` – Skript för att återskapa 3D- och CAD-filer.
* `1704705222-4007-s4327-hannu-44final-incl-plintplan.pdf` & `hannu1.png` – Originalritningar och foto från Polhus.
