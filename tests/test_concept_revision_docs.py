"""Regression: manufacturer-facing advertising docs track live CONCEPT_REVISION."""

from __future__ import annotations

import re
from pathlib import Path

from stand_cad.geometry.analysis import empty_case_mass_kg, part_mass_kg, stability_report_inputs
from stand_cad.geometry.assembly import build_transport_assembly
from stand_cad.geometry.export import CONCEPT_REVISION
from stand_cad.parameters import load_parameters

REPO_ROOT = Path(__file__).resolve().parents[1]
PARAMETERS_PATH = REPO_ROOT / "config" / "parameters.yaml"

ADVERTISING_DOCS = (
    REPO_ROOT / "README.md",
    REPO_ROOT / "docs" / "12_PRODUCTION_RFQ_TEMPLATE.md",
)

_REV_NUMBER = re.compile(r"\brev(?P<rev>\d+)\b", re.IGNORECASE)
_CONCEPT_REV_LITERAL = re.compile(r"CONCEPT\s+rev(?P<rev>\d+)", re.IGNORECASE)
_CONCEPT_REVISION_EQ = re.compile(r"CONCEPT_REVISION\s*=\s*(?P<rev>\d+)")
_STALE_SOLE_CURRENT_ENVELOPE = re.compile(
    r"650\s*[×x]\s*420\s*[×x]\s*529",
    re.IGNORECASE,
)


def _live_advertising_figures() -> tuple[int, str, str, str]:
    """Envelope height plus formatted structural mass, all-parts mass, lower tip factor."""
    params = load_parameters(PARAMETERS_PATH)
    parts = build_transport_assembly(params).parts
    height_mm = int(float(params.value("case.height")))
    structural_kg = empty_case_mass_kg(parts, params)
    all_parts_kg = sum(part_mass_kg(record, params) for record in parts.values())
    lower_tip = stability_report_inputs(params, parts, extended_level="lower").factor
    return (
        height_mm,
        f"{structural_kg:.3f}",
        f"{all_parts_kg:.3f}",
        f"{lower_tip:.3f}",
    )


def _envelope_tag(height_mm: int) -> str:
    return f"650 × 420 × {height_mm} mm"


def _handoff_current_zones(text: str) -> str:
    """Startup, Product truth, Open list, and Immediate mission — excludes Already closed."""
    before_closed, _, after_closed = text.partition("## Already closed")
    _, _, after_open_hdr = after_closed.partition("## Open / next product work")
    open_body, _, after_open = after_open_hdr.partition("\n## Operating model")
    _, _, after_mission_hdr = after_open.partition("## Immediate mission")
    mission_body = after_mission_hdr.split("\n---\n", 1)[0]
    return (
        before_closed
        + "## Open / next product work\n"
        + open_body
        + "## Immediate mission"
        + mission_body
    )


def _stale_revision_hits(text: str) -> list[str]:
    """Return human-readable hits where a parsed revision != live CONCEPT_REVISION."""
    hits: list[str] = []
    for pattern in (_REV_NUMBER, _CONCEPT_REV_LITERAL, _CONCEPT_REVISION_EQ):
        for match in pattern.finditer(text):
            rev = int(match.group("rev"))
            if rev != CONCEPT_REVISION:
                hits.append(match.group(0))
    return hits


def test_advertising_docs_pin_to_live_concept_revision() -> None:
    live_tag = f"rev{CONCEPT_REVISION}"
    for path in ADVERTISING_DOCS:
        text = path.read_text(encoding="utf-8")
        stale = _stale_revision_hits(text)
        assert not stale, (
            f"{path.relative_to(REPO_ROOT)} advertises stale revision(s): "
            f"{sorted(set(stale))}; live CONCEPT_REVISION={CONCEPT_REVISION}"
        )
        assert live_tag in text, f"{path.relative_to(REPO_ROOT)} missing {live_tag!r}"
        if path.name == "README.md":
            assert f"CONCEPT_REVISION={CONCEPT_REVISION}" in text, (
                f"{path.relative_to(REPO_ROOT)} missing CONCEPT_REVISION={CONCEPT_REVISION}"
            )
        else:
            assert re.search(
                rf"CONCEPT rev{CONCEPT_REVISION}\b", text, re.IGNORECASE
            ), f"{path.relative_to(REPO_ROOT)} missing CONCEPT rev{CONCEPT_REVISION}"


def test_advertising_docs_pin_live_envelope_height_and_figures() -> None:
    """README + docs/12 must advertise live envelope H and indicative mass/tip."""
    height_mm, structural_kg, all_parts_kg, lower_tip = _live_advertising_figures()
    envelope = _envelope_tag(height_mm)
    for path in ADVERTISING_DOCS:
        text = path.read_text(encoding="utf-8")
        assert envelope in text, (
            f"{path.relative_to(REPO_ROOT)} missing live envelope {envelope!r}"
        )
        assert not _STALE_SOLE_CURRENT_ENVELOPE.search(text), (
            f"{path.relative_to(REPO_ROOT)} still advertises stale sole-current "
            f"650×420×529 envelope"
        )
        if path.name == "12_PRODUCTION_RFQ_TEMPLATE.md":
            assert structural_kg in text, (
                f"{path.relative_to(REPO_ROOT)} missing live structural mass {structural_kg} kg"
            )
            assert all_parts_kg in text, (
                f"{path.relative_to(REPO_ROOT)} missing live all-parts mass {all_parts_kg} kg"
            )
            assert lower_tip in text, (
                f"{path.relative_to(REPO_ROOT)} missing live lower tip factor {lower_tip}"
            )


def test_handoff_current_zones_pin_live_concept_revision() -> None:
    """HANDOFF startup / Product truth / Open / Immediate mission must advertise live revision."""
    handoff = REPO_ROOT / "HANDOFF_PROMPT.md"
    text = handoff.read_text(encoding="utf-8")
    current = _handoff_current_zones(text)
    live_tag = f"rev{CONCEPT_REVISION}"
    assert live_tag in current, f"HANDOFF current zones missing {live_tag!r}"
    assert f"CONCEPT_REVISION = {CONCEPT_REVISION}" in current, (
        f"HANDOFF current zones missing CONCEPT_REVISION = {CONCEPT_REVISION}"
    )
    stale_assign = _CONCEPT_REVISION_EQ.findall(current)
    assert all(int(rev) == CONCEPT_REVISION for rev in stale_assign), (
        f"HANDOFF current zones stale CONCEPT_REVISION assignment(s): {stale_assign}"
    )
    stale = _stale_revision_hits(current)
    assert not stale, (
        f"HANDOFF current zones advertise stale revision(s): {sorted(set(stale))}"
    )
    assert "validation/rev13/" not in current, (
        "HANDOFF current zones still advertise rev13 evidence pack paths"
    )
    assert "REFERENCE_ONLY_rev13" not in current, (
        "HANDOFF current zones still advertise rev13 concept artifact names"
    )
    assert "210600" not in current.replace(",", "").replace(" ", ""), (
        "HANDOFF current zones still cite stale 210600 mm³ lid/shuttle volume"
    )
    assert "lid/shuttle" not in current.lower(), (
        "HANDOFF current zones still narrate live lid/shuttle clash"
    )
    assert "50 mm" in current, (
        "HANDOFF current zones missing tier-2 50 mm headroom (§M canary)"
    )


def test_handoff_current_zones_pin_live_envelope_mass_tip_honesty() -> None:
    """HANDOFF current zones must track live envelope/mass/tip and not claim PLT-012 PASSING."""
    height_mm, structural_kg, all_parts_kg, lower_tip = _live_advertising_figures()
    current = _handoff_current_zones(
        (REPO_ROOT / "HANDOFF_PROMPT.md").read_text(encoding="utf-8")
    )
    envelope = _envelope_tag(height_mm)
    assert envelope in current, f"HANDOFF current zones missing live envelope {envelope!r}"
    assert not _STALE_SOLE_CURRENT_ENVELOPE.search(current), (
        "HANDOFF current zones still advertise stale sole-current 650×420×529 envelope"
    )
    assert structural_kg in current, (
        f"HANDOFF current zones missing live structural mass {structural_kg} kg"
    )
    assert all_parts_kg in current, (
        f"HANDOFF current zones missing live all-parts mass {all_parts_kg} kg"
    )
    assert lower_tip in current, (
        f"HANDOFF current zones missing live lower tip factor {lower_tip}"
    )
    assert "PLT-012 PASSING" not in current, (
        "HANDOFF current zones must not claim PLT-012 PASSING"
    )
    assert "PLT-012 `IN_PROGRESS`" in current, (
        "HANDOFF current zones must advertise PLT-012 IN_PROGRESS honestly"
    )


def _rfq_owner_blocker_table(text: str) -> str:
    """Owner-decision blocker table in docs/12 — §F/§M/§N/§A rows only."""
    marker = "### Owner-decision blockers"
    start = text.index(marker)
    section, _, _ = text[start:].partition("### DFM / manufacturer-quotation questions")
    return section


def test_rfq_owner_blocker_table_pins_live_blockers() -> None:
    """docs/12 RFQ owner blockers must advertise sole-current §F/§M facts only."""
    rfq = REPO_ROOT / "docs" / "12_PRODUCTION_RFQ_TEMPLATE.md"
    blockers = _rfq_owner_blocker_table(rfq.read_text(encoding="utf-8"))
    normalized = blockers.replace(",", "").replace(" ", "").lower()

    assert "210600" not in normalized, (
        "docs/12 owner blockers still cite stale 210600 mm³ lid/shuttle volume"
    )
    assert "lid/shuttle" not in blockers.lower(), (
        "docs/12 owner blockers still narrate live lid/shuttle clash"
    )

    f_row = next(line for line in blockers.splitlines() if "| §F |" in line)
    assert "1.39" not in f_row, "docs/12 §F still advertises stale ~1.39×10⁶ intrusion"
    assert "1,502,833" in f_row or "1,502,834" in f_row or "1.50" in f_row, (
        "docs/12 §F missing current intrusion ≈1,502,833 / 1.50×10⁶"
    )
    assert "181.3" in f_row, "docs/12 §F missing balance-point Y=181.3"

    m_row = next(line for line in blockers.splitlines() if "| §M |" in line)
    assert "27 mm" in m_row, "docs/12 §M missing tier-1 27 mm headroom"
    assert "50 mm" in m_row, "docs/12 §M missing tier-2 50 mm headroom"
    assert "80 mm" in m_row, "docs/12 §M missing 80 mm provisional lid envelope"

    n_row = next(line for line in blockers.splitlines() if "| §N |" in line)
    assert "Transport retention" in n_row
    assert "**OPEN**" in n_row

    a_row = next(line for line in blockers.splitlines() if "| §A |" in line)
    assert "Real-equipment measurements" in a_row
    assert "**OPEN**" in a_row
