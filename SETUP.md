# Setup & Deployment

## Local Development

No npm, no build step — fully static project.

### Option 1: VS Code Live Server (recommended)
1. Install the [Live Server](https://marketplace.visualstudio.com/items?itemName=ritwickdey.LiveServer) extension
2. Right-click `index.html` → **Open with Live Server**
3. Open `http://127.0.0.1:5500`

### Option 2: Python
```bash
python -m http.server 8080
# Open http://localhost:8080
```

> You must serve from a local server — not `file://` — because browsers block cross-origin fetches of `.pcbn` and `.glb` files from the filesystem.

---

## Mapbox Token

The token in `index.html` is restricted to the production Vercel domain. For local dev, either:

**A)** Add `http://localhost:*` and `http://127.0.0.1:*` to the token's allowed URLs in the [Mapbox dashboard](https://account.mapbox.com/access-tokens/).

**B)** Temporarily swap in the unrestricted public token for local testing, then revert before pushing.

---

## Deployment (Vercel)

Auto-deploys on every push to `main`.

**First-time setup:**
1. Vercel → Add New Project → Import GitHub repo
2. Framework Preset: **Other**
3. Build Command: *(empty)*
4. Output Directory: *(empty)*
5. Deploy

**File size notes:**
- `pointcloud.pcbn` (34MB) and DJI photos (~17MB each) — push via GitHub web UI if GitHub Desktop struggles
- Vercel is **case-sensitive**: `drone.JPG` ≠ `drone.jpg`

---

## Regenerating the Point Cloud Binary

If you update the point cloud, regenerate `pointcloud.pcbn`:

```bash
cd scripts
python convert_pcbn.py
```

Edit the input/output paths at the top of the script. Requires `numpy`:
```bash
pip install numpy
```

---

## Updating the BIM Model

1. Export from Revit as **FBX**
2. Open in Blender → Import FBX → Export as **GLB** (geometry only)
3. Replace `bim_model.glb` and push
