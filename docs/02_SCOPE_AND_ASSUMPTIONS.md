# Scope, assumptions, and exclusions

## Goal

Create a parametric, reviewable design for a light desktop tower that houses two Silhouette cutting plotters plus horizontal film storage and can progress to a one-off prototype at a Moscow/Moscow-region manufacturer.

**Superseded 2026-08-04 — pre-TZ candidate inventory (historical):** before the Light Plotter Tower TZ was adopted (decision **D-011**; authoritative equipment list in `ИИ советы/Cursor_Opus5_TZ_Light_Plotter_Tower.md`), the project explored a generic mobile-floor-stand scope. That earlier candidate inventory included:

- Bulros T-330 or T-300 heat press;
- Epson L11050 or L1800 printer;
- DNP/DS-RX1HS photo printer;
- Silhouette Cameo plotter;
- laptop, iPad, power distribution, consumables, tools, and cabling.

That list is retained as history explaining why the later fixed equipment set exists. The current configuration is two Silhouette plotters only (Cameo 4 governing + Cameo 5 slot 2); no heat press, photo printer, laptop, or iPad are enclosed (`PLT-013`).

## In scope

- structured capture of exact equipment facts;
- equipment and service-clearance envelopes;
- transport and operating configurations;
- layout concepts and trade-off comparison;
- parametric 3D assembly and parts;
- neutral STEP handoff;
- preliminary and controlled drawings;
- BOM and production package structure;
- validation evidence;
- manufacturer DFM loop;
- prototype inspection and revision.

## Out of scope until explicitly authorized and qualified

- placing a manufacturing order;
- signing a vendor quotation;
- electrical circuit design or certification;
- declaring compliance with a specific standard;
- unattended release of laser-cutting DXF;
- claiming structural or thermal certification from an AI calculation alone;
- series production before prototype validation.

## Default assumptions for software setup

- Host OS: Windows 11 native.
- Units: millimetres, kilograms, watts, degrees Celsius.
- Editable CAD source: Python `build123d`.
- Git repository starts after this archive is extracted.
- Opus 5 acts as principal orchestrator and final arbiter.
- One designated implementation agent at a time may edit geometry source.
- Reviewers and verifiers do not edit product source during their review turn.

## Unknowns that must remain visible

Use `TBD`, `UNKNOWN`, or `UNVERIFIED` in documents and configuration. Never replace a missing fit-critical fact with a plausible web value without matching the exact model/revision and obtaining user or manufacturer confirmation.

