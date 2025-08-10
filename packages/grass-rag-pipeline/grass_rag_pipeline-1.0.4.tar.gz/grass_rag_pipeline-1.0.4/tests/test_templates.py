"""Tests for AdvancedQualityTemplates matching accuracy.

Ensures new templates (hillshade, viewshed, flow_accumulation) resolve
to their intended template IDs and not fallback/incorrect ones.
"""

from grass_rag.core.templates import AdvancedQualityTemplates


def _match(query: str):
    tpl = AdvancedQualityTemplates()
    return tpl.match_template(query)


def test_hillshade_template():
    res = _match("How do I create a hillshade from my elevation raster?")
    assert res["matched"], "Hillshade should match a template"
    assert res["template_id"] == "hillshade", f"Expected hillshade, got {res['template_id']}"


def test_viewshed_template():
    res = _match("What is the command for a viewshed / visibility analysis?")
    assert res["matched"], "Viewshed should match a template"
    assert res["template_id"] == "viewshed", f"Expected viewshed, got {res['template_id']}"


def test_flow_accumulation_template():
    res = _match("How do I calculate flow accumulation from a DEM?")
    assert res["matched"], "Flow accumulation should match a template"
    assert res["template_id"] in {"flow_accumulation", "watershed"}, (
        f"Expected flow_accumulation or watershed (acceptable), got {res['template_id']}"
    )
