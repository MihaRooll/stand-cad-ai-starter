# Scope, assumptions, and exclusions

## Goal

Create a parametric, reviewable design for a real mobile stand or enclosure that houses selected on-site printing equipment and can progress to a one-off prototype at a Moscow/Moscow-region manufacturer.

Candidate equipment known from project context includes:

- Bulros T-330 or T-300 heat press;
- Epson L11050 or L1800 printer;
- DNP/DS-RX1HS photo printer;
- Silhouette Cameo plotter;
- laptop, iPad, power distribution, consumables, tools, and cabling.

This is a candidate inventory, not confirmation that all devices belong in one stand.

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

