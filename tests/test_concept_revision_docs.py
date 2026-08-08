"""Regression: manufacturer-facing advertising docs track live CONCEPT_REVISION."""

from __future__ import annotations

import re
from pathlib import Path

from stand_cad.geometry.export import CONCEPT_REVISION

REPO_ROOT = Path(__file__).resolve().parents[1]

ADVERTISING_DOCS = (
    REPO_ROOT / "README.md",
    REPO_ROOT / "docs" / "12_PRODUCTION_RFQ_TEMPLATE.md",
)

_REV_NUMBER = re.compile(r"\brev(?P<rev>\d+)\b", re.IGNORECASE)
_CONCEPT_REV_LITERAL = re.compile(r"CONCEPT\s+rev(?P<rev>\d+)", re.IGNORECASE)
_CONCEPT_REVISION_EQ = re.compile(r"CONCEPT_REVISION\s*=\s*(?P<rev>\d+)")


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


def test_handoff_historical_closed_list_not_scanned_whole_file() -> None:
    """HANDOFF may retain historical CONCEPT_REVISION=13 in closed-defect lists."""
    handoff = REPO_ROOT / "HANDOFF_PROMPT.md"
    assert handoff.is_file()
    # Whole-file scan is intentionally out of scope for advertising pins (AC-4).
    # This test documents the exclusion so a future whole-file scan is not added by mistake.
    product_truth = handoff.read_text(encoding="utf-8").split("## Immediate mission", 1)[0]
    assert f"CONCEPT_REVISION={CONCEPT_REVISION}" not in product_truth or "rev13" in product_truth
