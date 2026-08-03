# Source notes

Reviewed on **2026-08-03**. Links support tool capabilities and examples of manufacturer input requirements. Vendor pages are not endorsements.

## Primary software sources

- Cursor MCP documentation: https://cursor.com/docs/mcp
- Astral `uv` Windows installation: https://docs.astral.sh/uv/getting-started/installation/
- `build123d` PyPI (0.11.1 released 2026-07-02): https://pypi.org/project/build123d/
- `build123d` import/export documentation: https://build123d.readthedocs.io/en/latest/import_export.html
- `build123d-mcp` repository: https://github.com/pzfreo/build123d-mcp
- `build123d-mcp` PyPI (0.3.81 released 2026-08-02): https://pypi.org/project/build123d-mcp/
- `build123d-mcp` LLM reference and sandbox rules: https://github.com/pzfreo/build123d-mcp/blob/main/llms.md
- `build123d-mcp` changelog, including drawing workflow: https://github.com/pzfreo/build123d-mcp/blob/main/CHANGELOG.md
- CAD Skills repository: https://github.com/earthtojake/text-to-cad
- Current Skills CLI: https://github.com/vercel-labs/skills
- FreeCAD MCP example showing the additional GUI/add-on/RPC setup: https://github.com/neka-nat/freecad-mcp

## Manufacturer capability and file-format evidence

- Zavod №1: STEP/IGES + PDF preferred, DXF accepted for sheet parts, prototypes from one item: https://zavod1.com/
- Laser Contur: enclosure/stand fabrication and documentation assistance in the Moscow region: https://lasercontur.ru/service/proektirovanie-i-proizvodstvo-korpusov/
- GalvanoHim: accepts DXF, STEP, DWG, PDF, sketches, and specifications: https://galvanohim.ru/
- Example laser-cutting input rules (DXF 1:1, closed contours, no overlapping layers, accompanying PDF/DWG and parts list): https://prelektro.ru/calc_laser_cut/1-1-1.5
- Example explanation of bend allowance/K-factor dependence on material and tooling: https://mosmetgroup.ru/blog/gibka-listovogo-metalla-razbor-technologii

## Interpretation limits

- Manufacturer websites describe their own claimed capabilities and requirements; they do not establish comparative quality.
- Requirements vary by factory, machine, tooling, material batch, and contract.
- Software versions are intentionally pinned in the repository. Re-check upstream sources before any dependency update.

