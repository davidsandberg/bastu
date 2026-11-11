# Bastu till Paddelpalatset – Hannu 44

3D-modell, CAD-underlag och visualisering för planerad bastubyggnad vid Paddelpalatset (forsstranden), baserad på **Polhus Hannu 44**.

## Projektöversikt

* **Totalmått:** 4.40 m bredd × 2.70 m djup
* **Höjd:** 2.50 m (framkant) / 2.16 m (bakkant) – Pulpettak
* **Ytor:**
  * Basturum: 3.00 × 2.50 m (~7.2 m² med plats för 6–8 personer)
  * Veranda / Relax: 1.20 × 2.50 m (~3.0 m²)
* **Fasad mot forsen:** 3 stora panoramafönster (875 × 1700 mm vardera)
* **Konstruktion:** 44 mm knuttimmer med dubbelspont

## Filer i projektet

### 3D-modeller & Visualisering
* `hannu_bastu_3d_viewer.html` – Interaktiv 3D-visare i WebGL (Three.js). Öppna direkt i valfri webbläsare för att rotera, växla mellan dag/kvällsbelysning, lyfta av taket och inspektera mått.
* `hannu_bastu.obj` & `hannu_bastu.mtl` – 3D Wavefront-mesh med materialdefinitioner för import till terrängmodellen i Blender, SketchUp, Rhino, Unreal Engine m.fl.
* `hannu_bastu.gltf` – 3D-scen i standard glTF 2.0-format med PBR-material och transparens.

### CAD-ritningar (CADCraft)
* `hannu_planritning.dxf` – 2D/3D CAD-ritning i skala 1:50 med lager (`A-WALL`, `A-GLAZ`, `A-DOOR`, `A-FURN`, `A-ROOF`, `A-DIMS`, `A-TEXT`).
* `hannu_planritning.png` – Högupplöst rendering av planlösning och fasadritning mot forsen.
* `generate_cad_drawing.py` – Skript som bygger CAD-underlaget med CADCraft CLI.
* `hannu_cad_script.scr` – CAD-skript / kommandosekvens.

### Originalunderlag från Polhus
* `1704705222-4007-s4327-hannu-44final-incl-plintplan.pdf` – Originalritningar, sektioner, fasader och plintplan.
* `hannu1.png` – Referensfoto på färdigmonterad Hannu 44 i skymningsljus.

### Generatorer
* `generate_bastu_assets.py` – Skript för att generera `.obj`, `.mtl` och `.gltf`.
