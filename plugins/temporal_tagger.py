"""MiroFlow tool for turning raw pages into temporally weighted claims."""

from __future__ import annotations

import re
from datetime import datetime, timedelta
from html import unescape
from typing import Any

from schemas.interfaces import SourcedClaim, SourceType

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
    claim: str | None = None,
    confidence: float = 0.8,
) -> SourcedClaim:
    """Extract page temporal metadata and return a sourced claim.

    Args:
        page_text: Raw fetched page text or HTML.
        url: Source URL.
        source_type: Source category used for temporal decay rules.
        claim: Optional caller-supplied claim. When omitted, a concise claim is
            derived from the page title or first sentence.
        confidence: Initial confidence before temporal decay.

    Returns:
        A `SourcedClaim` with `published_at`, `retrieved_at`, confidence, and
        optional uncertainty metadata.
    """
    retrieved_at = datetime.utcnow()
    published_at = _extract_published_at(page_text) or retrieved_at
    adjusted_confidence = confidence
    uncertainty_note = None

    age = retrieved_at - published_at
    if source_type == "job_post" and age > timedelta(days=183):
        adjusted_confidence *= 0.5
    if source_type == "industry_report" and age > timedelta(days=548):
        uncertainty_note = "source may be stale"

    return SourcedClaim(
        claim=claim or _derive_claim(page_text, url),
        source_url=url,
        published_at=published_at,
        retrieved_at=retrieved_at,
        confidence=round(adjusted_confidence, 3),
        source_type=source_type,
        uncertainty_note=uncertainty_note,
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
    """Parse common ISO-like web timestamps into naive UTC datetimes."""
    cleaned = unescape(value.strip()).replace("Z", "+00:00")
    try:
        parsed = datetime.fromisoformat(cleaned)
    except ValueError:
        return None
    if parsed.tzinfo is not None:
        return parsed.astimezone().replace(tzinfo=None)
    return parsed


def _derive_claim(page_text: str, url: str) -> str:
    """Derive a short claim from page title or content."""
    title_match = re.search(r"<title[^>]*>(.*?)</title>", page_text, re.IGNORECASE | re.DOTALL)
    if title_match:
        title = re.sub(r"\s+", " ", title_match.group(1)).strip()
        return unescape(title)

    cleaned = re.sub(r"<[^>]+>", " ", page_text)
    cleaned = re.sub(r"\s+", " ", cleaned).strip()
    if cleaned:
        return cleaned[:240]
    return f"Source retrieved from {url}"
