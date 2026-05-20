"""Tests for MiroFlow plugin stubs."""

from plugins.module_db_query import module_db_query
from plugins.temporal_tagger import temporal_tagger
from schemas.interfaces import SourcedClaim


def test_temporal_tagger_extracts_metadata() -> None:
    """Temporal tagger should return a sourced claim with published metadata."""
    html = """
    <html>
      <head>
        <meta property="article:published_time" content="2026-02-01T00:00:00+00:00" />
        <title>Grab Product Analyst</title>
      </head>
    </html>
    """

    claim = temporal_tagger(html, "https://example.com/job", source_type="job_post")

    assert isinstance(claim, SourcedClaim)
    assert claim.claim == "Grab Product Analyst"
    assert claim.published_at.year == 2026


def test_module_db_query_fuzzy_matches() -> None:
    """Module query should return likely records."""
    result = module_db_query("visualisation")

    assert result["gap_note"] is None
    assert result["module"].code == "BT2102"
