# Abu Naseeb Al-Baghdaddiya Family House — 3D Web Viewer

> Interactive web-based 3D documentation viewer for a historic family residence in Jeddah, Saudi Arabia. Combines a photogrammetric point cloud (3.9M points) with a BIM model reconstructed in Autodesk Revit, delivered entirely as a static site with no backend.

**Live:** [abu-naseeb-viewer.vercel.app](https://abu-naseeb-viewer.vercel.app)

---

## Features

### Landing Page
- Mapbox GL JS satellite basemap with terrain
- Exact site boundary polygon with gold highlight and surrounding dim mask
- Cinematic fly-in on load
- Clickable boundary opens a slide-in side panel with:
  - 4-photo DJI drone image gallery with thumbnail switcher
  - Site metadata (capture method, BIM software, point count, elevation)
  - One-click entry to 3D viewer

### 3D Viewer
- **Point Cloud** — 3,907,305 points loaded from a single pre-decoded `.pcbn` binary (34MB, 1 HTTP request)
- **BIM Model** — Revit GLB with element-type colour coding (walls, floors, doors, windows, columns, railings)
- Layer toggles for Point Cloud and BIM
- ViewCube navigation (Top, Home, Front, Back, Left, Right, Reset)
- Toolbar: Fullscreen · Point Size slider · Colour Mode (RGB / Elevation gradient)

---

## Tech Stack

| | |
|---|---|
| Map | Mapbox GL JS v3.3.0 |
| 3D Rendering | Three.js r134 |
| BIM Loading | GLTFLoader |
| Hosting | Vercel (static) |

No backend. No build step. Pure HTML/CSS/JS.

---

## Data Pipeline

### Point Cloud
```
Field capture (drone photogrammetry)
  → Agisoft Metashape — dense cloud reconstruction
  → Potree 1.7 export (360 .bin files, 63MB)
  → scripts/convert_pcbn.py
  → pointcloud.pcbn (34MB, single file)
```

#### `.pcbn` Format
Custom single-file binary replacing 360 Potree HTTP requests:

```
Bytes 0–3    char[4]    Magic "PCBN"
Bytes 4–7    uint32     Point count
Bytes 8–31   float32×6  TightBoundingBox: lx, ux, ly, uy, lz, uz
Bytes 32+    N × 9B     Per point:
                          x, y, z  uint16  quantized coords (0–65535)
                          r, g, b  uint8   colour
```

Coordinate system: Potree Z-up → Three.js Y-up on decode.

### BIM Model
```
Autodesk Revit → FBX → Blender → GLB (9.4MB)
```
No embedded materials in export. Colours assigned at runtime from a node-name lookup table.

---

## Project Structure

```
abu-naseeb-viewer/
├── index.html              # Landing page
├── viewer.html             # 3D viewer
├── bim_model.glb           # BIM model (9.4MB)
├── pointcloud.pcbn         # Point cloud binary (34MB)
├── drone.JPG               # Aerial photo (primary)
├── DJI_0147.JPG
├── DJI_0163.JPG
├── DJI_0182.JPG
├── scripts/
│   └── convert_pcbn.py     # Potree → .pcbn converter
├── README.md
├── SETUP.md
└── NOTES.md
```

---

## Setup

See [SETUP.md](SETUP.md) for local development and deployment instructions.

---

## Known Limitations

- Point cloud and BIM model alignment is approximate — modelling origin discrepancies from the initial Revit workflow
- BIM element colours are inferred from node names; non-standard names fall back to default stone colour
- This is a prototype/portfolio version; a production version with corrected alignment is planned

---

## Author

**Hassan Gegu (Gegz)**  
GIS & Web Mapping Developer · Full Stack Developer  
[upwork.com/freelancers/hassangegu](https://www.upwork.com/freelancers/hassangegu)

---

*Point cloud and drone imagery © Hassan Gegu. BIM model reconstructed from field survey. Site: Abu Naseeb Al-Baghdaddiya Family House, Makkah Al-Mukarramah, Saudi Arabia.*
