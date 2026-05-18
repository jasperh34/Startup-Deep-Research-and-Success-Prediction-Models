from __future__ import annotations

import json
from typing import Any

from .env import env_value
from .http import request_json
from .models import (
    SourceSnippet,
    StructuredCompany,
    StructuredFounder,
    StructuredFunding,
)

STRUCTURED_COMPANY_JSON_SCHEMA: dict[str, Any] = {
    "type": "object",
    "additionalProperties": False,
    "required": [
        "company_name",
        "description",
        "sector",
        "founding_year",
        "founders",
        "funding",
        "traction_signals",
        "risk_factors",
        "recent_news",
    ],
    "properties": {
        "company_name": {"type": "string"},
        "description": {"type": "string"},
        "sector": {"type": "string"},
        "founding_year": {"type": "string"},
        "founders": {
            "type": "array",
            "items": {
                "type": "object",
                "additionalProperties": False,
                "required": ["name", "role", "background", "signals"],
                "properties": {
                    "name": {"type": "string"},
                    "role": {"type": "string"},
                    "background": {"type": "string"},
                    "signals": {"type": "array", "items": {"type": "string"}},
                },
            },
        },
        "funding": {
            "type": "object",
            "additionalProperties": False,
            "required": ["total_raised", "latest_round", "investors"],
            "properties": {
                "total_raised": {"type": "string"},
                "latest_round": {"type": "string"},
                "investors": {"type": "array", "items": {"type": "string"}},
            },
        },
        "traction_signals": {"type": "array", "items": {"type": "string"}},
        "risk_factors": {"type": "array", "items": {"type": "string"}},
        "recent_news": {"type": "array", "items": {"type": "string"}},
    },
}


def extract_structured_company(
    company: dict[str, str | None],
    sources: list[SourceSnippet],
    *,
    openai_api_key: str | None = None,
    openai_model: str | None = None,
) -> tuple[StructuredCompany, bool]:
    api_key = openai_api_key or env_value("OPENAI_API_KEY")
    if not api_key:
        return fallback_structured_company(company, sources), False

    payload = request_json(
        "https://api.openai.com/v1/responses",
        method="POST",
        headers={"Authorization": f"Bearer {api_key}"},
        payload={
            "model": openai_model or env_value("OPENAI_MODEL", "gpt-4o-mini"),
            "input": [
                {
                    "role": "system",
                    "content": (
                        "Extract investor research fields from source snippets. "
                        "Use only provided evidence. Use 'Unknown' when evidence is "
                        "missing. Pay special attention to phrases like 'founded by', "
                        "'co-founded by', 'led by', and source snippets that name "
                        "founders. If one source lists multiple founders, include every "
                        "named founder. Return only the schema."
                    ),
                },
                {
                    "role": "user",
                    "content": (
                        f"Company: {company.get('name')}\n"
                        f"Website: {company.get('website') or 'Unknown'}\n\n"
                        "Task: produce strict investor-research JSON. Do not omit "
                        "founders named in the snippets.\n\n"
                        f"Sources:\n{source_context(sources)}"
                    ),
                },
            ],
            "text": {
                "format": {
                    "type": "json_schema",
                    "name": "startup_research_extraction",
                    "strict": True,
                    "schema": STRUCTURED_COMPANY_JSON_SCHEMA,
                },
            },
        },
    )
    output_text = extract_output_text(payload)
    return structured_company_from_dict(json.loads(output_text)), True


def fallback_structured_company(
    company: dict[str, str | None],
    sources: list[SourceSnippet],
) -> StructuredCompany:
    return StructuredCompany(
        company_name=company.get("name") or "Unknown",
        description=(
            company.get("description")
            or (sources[0].snippet if sources else None)
            or "No structured description extracted yet."
        ),
        sector="Unknown",
        founding_year="Unknown",
        founders=[],
        funding=StructuredFunding(
            total_raised="Unknown",
            latest_round="Unknown",
            investors=[],
        ),
        traction_signals=[
            source.title for source in sources if source.source_type == "jobs"
        ],
        risk_factors=[],
        recent_news=[
            source.title for source in sources if source.source_type == "news"
        ][:5],
    )


def source_context(sources: list[SourceSnippet]) -> str:
    return "\n\n".join(
        (
            f"{index}. [{source.source_type}] {source.title}\n"
            f"URL: {source.url}\n"
            f"Snippet: {source.snippet}"
        )
        for index, source in enumerate(sources[:20], start=1)
    )


def extract_output_text(payload: dict[str, Any]) -> str:
    if payload.get("output_text"):
        return str(payload["output_text"])

    for output_item in payload.get("output", []):
        for content in output_item.get("content", []):
            if content.get("type") == "output_text" and content.get("text"):
                return str(content["text"])
    return ""


def structured_company_from_dict(data: dict[str, Any]) -> StructuredCompany:
    funding = data.get("funding") or {}
    return StructuredCompany(
        company_name=str(data.get("company_name", "Unknown")),
        description=str(data.get("description", "Unknown")),
        sector=str(data.get("sector", "Unknown")),
        founding_year=str(data.get("founding_year", "Unknown")),
        founders=[
            StructuredFounder(
                name=str(founder.get("name", "Unknown")),
                role=str(founder.get("role", "Unknown")),
                background=str(founder.get("background", "Unknown")),
                signals=[str(signal) for signal in founder.get("signals", [])],
            )
            for founder in data.get("founders", [])
            if isinstance(founder, dict)
        ],
        funding=StructuredFunding(
            total_raised=str(funding.get("total_raised", "Unknown")),
            latest_round=str(funding.get("latest_round", "Unknown")),
            investors=[str(investor) for investor in funding.get("investors", [])],
        ),
        traction_signals=[str(item) for item in data.get("traction_signals", [])],
        risk_factors=[str(item) for item in data.get("risk_factors", [])],
        recent_news=[str(item) for item in data.get("recent_news", [])],
    )
