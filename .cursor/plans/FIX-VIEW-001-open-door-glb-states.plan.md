# FIX-VIEW-001 — open-door GLB viewer states

**contract_id:** FIX-VIEW-001-open-door-glb-states  
**decision_id:** D-101  
**tier:** T1

## Scope

Export and expose `service_plotter_1` and `service_plotter_2` GLB+manifest pairs alongside transport in `output/concept/`. Viewer dropdown shows human labels; default and reload-watch prefer transport at the same revision.

## Owned paths

- `src/stand_cad/geometry/export.py`
- `scripts/render_validation_views.py`, `scripts/regenerate.py`, `scripts/serve_viewer.py`
- `viewer/index.html`, `viewer/README.md`
- `tests/test_viewer_models.py`, `tests/test_export_mesh_states.py`
- `state/DECISION_LOG.md`, `state/AUTONOMOUS_STATUS.md`, `state/PROJECT_STATE.md`

## Stems (rev15)

| State | Stem |
|---|---|
| transport | `light_plotter_tower_ASSEMBLY_CONCEPT_REFERENCE_ONLY_rev15` |
| service_plotter_1 | `light_plotter_tower_SERVICE_PLOTTER_1_CONCEPT_REFERENCE_ONLY_rev15` |
| service_plotter_2 | `light_plotter_tower_SERVICE_PLOTTER_2_CONCEPT_REFERENCE_ONLY_rev15` |

STL: transport only.
