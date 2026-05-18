from __future__ import annotations

from .models import CompanyCandidate


def mock_search_companies(query: str) -> list[CompanyCandidate]:
    normalized = query.lower()
    slug = "".join(normalized.split())
    return [
        CompanyCandidate(
            id=f"{normalized}-primary",
            name=query,
            website=f"https://www.{slug}.com",
            description="Placeholder company match. Real web search will replace this mock candidate.",
            confidence=0.72,
            source="mock",
        ),
        CompanyCandidate(
            id=f"{normalized}-labs",
            name=f"{query} Labs",
            description="Alternative placeholder match to test the confirmation workflow.",
            confidence=0.48,
            source="mock",
        ),
    ]
