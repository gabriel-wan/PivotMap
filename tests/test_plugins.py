"""Tests for Career Proof Graph plugin helpers."""

from plugins.module_db_query import module_db_query
from plugins.temporal_tagger import temporal_tagger
from schemas.interfaces import Source


def test_temporal_tagger_extracts_source_metadata() -> None:
    """Temporal tagger should return a Source object."""
    html = """
    <html>
      <head>
        <meta property="article:published_time" content="2026-02-01T00:00:00+00:00" />
        <title>Grab Product Analyst</title>
      </head>
    </html>
    """

    source = temporal_tagger(html, "https://example.com/job", source_type="job_post")

    assert isinstance(source, Source)
    assert source.title == "Grab Product Analyst"
    assert source.published_at is not None
    assert source.published_at.year == 2026


def test_module_db_query_fuzzy_matches_evidence() -> None:
    """Module query should return likely module evidence."""
    result = module_db_query("visualisation")

    assert result["gap_note"] is None
    assert result["evidence_node"]["id"] == "module-nus-bt2102"
