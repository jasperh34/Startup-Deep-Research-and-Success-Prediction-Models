from __future__ import annotations

from urllib.parse import urlparse, urlunparse

from .models import CompanyCandidate


def normalize_website(value: str | None) -> str | None:
    if not value:
        return None
    try:
        parsed = urlparse(value)
        if not parsed.scheme:
            parsed = urlparse(f"https://{value}")
        cleaned = parsed._replace(query="", fragment="")
        return urlunparse(cleaned).rstrip("/")
    except ValueError:
        return value


def company_row_payload(
    candidate: CompanyCandidate,
    *,
    selected_by_user: bool,
) -> dict[str, object]:
    return {
        "name": candidate.name,
        "website": normalize_website(candidate.website),
        "description": candidate.description,
        "location": candidate.location,
        "metadata": {
            "industry": candidate.industry,
            "companyType": candidate.company_type,
            "foundingYear": candidate.founding_year,
            "fundingStage": candidate.funding_stage,
            "matchReasons": candidate.match_reasons,
            "sourceTypes": candidate.source_types,
            "source": candidate.source,
            "sourceUrl": candidate.source_url,
            "confidence": candidate.confidence,
        },
        "selected_by_user": selected_by_user,
    }


def with_company_id(candidate: CompanyCandidate, company_id: str) -> CompanyCandidate:
    return CompanyCandidate(
        **{
            **candidate.to_dict(),
            "website": normalize_website(candidate.website),
            "company_id": company_id,
        },
    )
