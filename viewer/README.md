# GLB assembly viewer

Offline-capable viewer: three.js **0.170.0** is vendored under `viewer/vendor/` (no CDN).

## Environment doctor

Before first use (or when something feels broken), run:

```bash
uv run python scripts/doctor.py
```

Each check prints **PASS/FAIL** and a plain-English remedy on failure (uv/Python 3.12, repo root, pytest collection, concept artifacts, vendored three.js, port 8000, WSL `chdir(/mnt/c/...)` signature).

## First-time setup (vendored three.js)

If `viewer/vendor/three@0.170.0/` is missing, either:

```bash
uv run python viewer/vendor/fetch_three.py
```

or start the server — it auto-downloads on first launch:

```bash
uv run python scripts/serve_viewer.py --watch
```

## Run (with live reload)

```bash
uv run python scripts/serve_viewer.py --watch
```

Open **http://127.0.0.1:8000/viewer/index.html**

The viewer loads the **newest** concept revision from `output/concept/` by default. Use the **Concept revision** dropdown to switch revisions (manual switch still **fit-to-view**).

### Live reload (`--watch`)

When the server runs with `--watch`:

1. The server polls `output/concept/` file modification times every ~1 s.
2. **`GET /viewer/reload-status`** returns JSON:

   ```json
   {
     "revision": 4,
     "manifest_file": "light_plotter_tower_ASSEMBLY_CONCEPT_REFERENCE_ONLY_rev4.manifest.json",
     "glb_file": "light_plotter_tower_ASSEMBLY_CONCEPT_REFERENCE_ONLY_rev4.glb",
     "manifest_mtime_ns": 1234567890123456789,
     "glb_mtime_ns": 1234567890123456789,
     "concept_dir_mtime_ns": 1234567890123456789
   }
   ```

3. `viewer/index.html` polls that endpoint every **~2 s**. When the newest model's manifest/GLB mtime changes, it reloads the model **in place** while preserving:
   - camera position and OrbitControls target (no re-fit on automatic reload);
   - per-`part_id` visibility checkbox state (missing parts dropped; new parts default visible);
   - section-plane slider positions and enabled flags.

Regenerate geometry and views (picked up automatically by a running `--watch` server):

```bash
uv run python scripts/regenerate.py
```

## Status panel

Load progress appears in the bottom-left panel. On success (all steps green, manifest vs glTF bbox within 1%), the panel **auto-collapses after ~3 seconds** into a small badge showing **✓** and the manifest CAD dimensions (mm).

- **Click the badge** to re-expand the full log.
- Press **`i`** to toggle collapsed / expanded (preference saved in `localStorage`).
- On **failure** or **manifest vs glTF mismatch** (>1% after axis/unit conversion), the panel stays **expanded** and turns red or amber; it does not auto-collapse.

The top-right readout shows authoritative **CAD bbox** from the manifest (width X × depth Y × height Z, mm, Z-up). The status log also shows the raw **glTF scene box** (metres, Y-up) separately so the two cannot be confused.

Verify HTTP assets without a browser:

```bash
uv run python scripts/serve_viewer.py --verify
```

## Controls

- **Part-ID legend** — collapsible prefix → plain-English names in the sidebar.
- **Part visibility tree** — toggle groups or individual parts by manifest `part_id`.
- **Global opacity** — slider applies to all meshes.
- **Outer panels off** — toggles `PANEL-OUT-*` visibility (same parts as server-side `_suppress_outer_shell`); click again to restore.
- **Wireframe** — toggles mesh wireframe mode.
- **Section planes (CAD mm, Z-up)** — X width / Y depth / Z height sliders with mm readout; planes are converted to glTF metres internally.
- **Reset clipping** — disables all section planes and resets slider positions.
- **Camera** — Fit view and orthographic presets (front, rear, left, right, top, iso).

Legacy entry point (views only, no STEP):

```bash
uv run python scripts/render_validation_views.py
```
