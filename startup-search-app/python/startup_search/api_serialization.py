from __future__ import annotations

from .models import CompanyCandidate, StartupReport


def candidate_from_api(data: dict[str, object]) -> CompanyCandidate:
    return CompanyCandidate(
        id=str(data.get("id", "")),
        company_id=_optional_string(data.get("companyId")),
        name=str(data.get("name", "")),
        website=_optional_string(data.get("website")),
        description=str(data.get("description", "")),
        location=_optional_string(data.get("location")),
        industry=_optional_string(data.get("industry")),
        company_type=_optional_string(data.get("companyType")),
        founding_year=_optional_string(data.get("foundingYear")),
        funding_stage=_optional_string(data.get("fundingStage")),
        match_reasons=_string_list(data.get("matchReasons")),
        source_types=_string_list(data.get("sourceTypes")),
        confidence=float(data.get("confidence", 0.5)),
        source=str(data.get("source", "api")),
        source_url=_optional_string(data.get("sourceUrl")),
    )


def candidate_to_api(candidate: CompanyCandidate) -> dict[str, object]:
    payload: dict[str, object] = {
        "id": candidate.id,
        "name": candidate.name,
        "description": candidate.description,
        "confidence": candidate.confidence,
        "source": candidate.source,
    }
    optional_values = {
        "companyId": candidate.company_id,
        "website": candidate.website,
        "location": candidate.location,
        "industry": candidate.industry,
        "companyType": candidate.company_type,
        "foundingYear": candidate.founding_year,
        "fundingStage": candidate.funding_stage,
        "matchReasons": candidate.match_reasons or None,
        "sourceTypes": candidate.source_types or None,
        "sourceUrl": candidate.source_url,
    }
    payload.update(
        {key: value for key, value in optional_values.items() if value is not None},
    )
    return payload


def report_to_api(report: StartupReport) -> dict[str, object]:
    payload: dict[str, object] = {
        "id": report.id,
        "companyName": report.company_name,
        "summary": report.summary,
        "status": report.status,
        "createdAt": report.created_at,
        "sections": [
            {"title": section.title, "body": section.body}
            for section in report.sections
        ],
        "signals": [
            {"label": signal.label, "value": signal.value, "tone": signal.tone}
            for signal in report.signals
        ],
    }
    optional_values = {
        "companyId": report.company_id,
        "website": report.website,
        "sourceCount": report.source_count,
        "structuredJson": report.structured_json,
    }
    payload.update(
        {key: value for key, value in optional_values.items() if value is not None},
    )
    return payload


def _optional_string(value: object) -> str | None:
    if value is None:
        return None
    text = str(value)
    return text or None


def _string_list(value: object) -> list[str]:
    if not isinstance(value, list):
        return []
    return [str(item) for item in value]
