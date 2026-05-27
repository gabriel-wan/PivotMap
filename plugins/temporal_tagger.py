"""MiroFlow tool for extracting temporal source metadata."""

from __future__ import annotations

import re
from datetime import UTC, datetime
from html import unescape
from typing import Any
from uuid import uuid5, NAMESPACE_URL

from schemas.interfaces import Source, SourceType

try:
    from miroflow import register
except ImportError:  # pragma: no cover - local scaffold fallback

    def register(func: Any) -> Any:
        """Fallback decorator used when MiroFlow is not installed."""
        return func


@register
def temporal_tagger(
    page_text: str,
    url: str,
    source_type: SourceType = "industry_report",
    title: str | None = None,
) -> Source:
    """Extract temporal metadata from raw web text into a Source object."""
    retrieved_at = datetime.now(UTC)
    published_at = _extract_published_at(page_text)
    return Source(
        id=f"source-{uuid5(NAMESPACE_URL, url).hex[:12]}",
        source_url=url,
        source_type=source_type,
        title=title or _derive_title(page_text, url),
        published_at=published_at,
        retrieved_at=retrieved_at,
        metadata={"temporal_quality": _temporal_quality(source_type, published_at, retrieved_at)},
    )


def _extract_published_at(page_text: str) -> datetime | None:
    """Extract published time from Open Graph, JSON-LD, or visible metadata."""
    patterns = [
        r'<meta[^>]+property=["\']article:published_time["\'][^>]+content=["\']([^"\']+)["\']',
        r'<meta[^>]+property=["\']og:article:published_time["\'][^>]+content=["\']([^"\']+)["\']',
        r'<meta[^>]+name=["\']date["\'][^>]+content=["\']([^"\']+)["\']',
        r'"datePublished"\s*:\s*"([^"]+)"',
        r"<time[^>]+datetime=[\"']([^\"']+)[\"']",
    ]
    for pattern in patterns:
        match = re.search(pattern, page_text, flags=re.IGNORECASE)
        if match:
            parsed = _parse_datetime(match.group(1))
            if parsed:
                return parsed
    return None


def _parse_datetime(value: str) -> datetime | None:
    """Parse common ISO-like web timestamps."""
    cleaned = unescape(value.strip()).replace("Z", "+00:00")
    try:
        parsed = datetime.fromisoformat(cleaned)
    except ValueError:
        return None
    if parsed.tzinfo is not None:
        return parsed.astimezone(UTC)
    return parsed.replace(tzinfo=UTC)


def _derive_title(page_text: str, url: str) -> str:
    """Derive a source title from HTML title or URL."""
    title_match = re.search(r"<title[^>]*>(.*?)</title>", page_text, re.IGNORECASE | re.DOTALL)
    if title_match:
        title = re.sub(r"\s+", " ", title_match.group(1)).strip()
        return unescape(title)
    return url


def _temporal_quality(
    source_type: SourceType,
    published_at: datetime | None,
    retrieved_at: datetime,
) -> str:
    """Describe freshness for downstream verifier agents."""
    if published_at is None:
        return "unknown"
    age_days = (retrieved_at - published_at).days
    if source_type == "job_post" and age_days > 183:
        return "stale_job_post"
    if source_type == "industry_report" and age_days > 548:
        return "possibly_stale_report"
    return "fresh"
