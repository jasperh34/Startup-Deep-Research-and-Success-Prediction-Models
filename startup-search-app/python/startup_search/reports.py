from __future__ import annotations

from datetime import UTC, datetime
from uuid import uuid4

from .models import (
    CompanyCandidate,
    ReportSection,
    ReportSignal,
    SourceSnippet,
    StartupReport,
    StructuredCompany,
)


def build_draft_report(
    candidate: CompanyCandidate,
    *,
    company_id: str | None = None,
    sources: list[SourceSnippet] | None = None,
    structured: StructuredCompany | None = None,
    used_model: bool = False,
) -> StartupReport:
    source_count = len(sources or [])

    return StartupReport(
        id=str(uuid4()),
        company_id=company_id,
        company_name=candidate.name,
        website=candidate.website,
        status="ready" if structured else "draft",
        created_at=datetime.now(UTC).isoformat(),
        source_count=source_count,
        structured_json=structured.to_dict() if structured else None,
        summary=(
            structured.description
            if structured
            else (
                "Research brief scaffold created from the confirmed company match. "
                "Raw sources have been collected and are ready for structured extraction."
            )
        ),
        sections=[
            ReportSection(
                title="Executive Summary",
                body=(
                    f"{structured.company_name} operates in {structured.sector}. "
                    f"{structured.description}"
                    if structured
                    else candidate.description
                ),
            ),
            ReportSection(
                title="Company Snapshot",
                body=(
                    f"Sector: {structured.sector}\n"
                    f"Founded: {structured.founding_year}\n"
                    f"Website: {candidate.website or 'Unknown'}\n\n"
                    f"{structured.description}"
                    if structured
                    else candidate.description
                ),
            ),
            ReportSection(
                title="Founder Assessment",
                body=(
                    "\n".join(
                        (
                            f"{founder.name} - {founder.role}. "
                            f"{founder.background}. Signals: "
                            f"{', '.join(founder.signals) or 'No signals found'}."
                        )
                        for founder in structured.founders
                    )
                    if structured and structured.founders
                    else "No founder details extracted yet."
                ),
            ),
            ReportSection(
                title="Market And Product Signals",
                body=(
                    _list_or_fallback(
                        structured.traction_signals,
                        "No traction signals extracted.",
                    )
                    if structured
                    else "Traction signals have not been extracted yet."
                ),
            ),
            ReportSection(
                title="Funding",
                body=(
                    f"Total raised: {structured.funding.total_raised}\n"
                    f"Latest round: {structured.funding.latest_round}\n"
                    f"Investors: {_list_or_fallback(structured.funding.investors, 'Unknown')}"
                    if structured
                    else "Funding details have not been extracted yet."
                ),
            ),
            ReportSection(
                title="Recent News",
                body=(
                    _list_or_fallback(
                        structured.recent_news,
                        "No recent news extracted.",
                    )
                    if structured
                    else "Raw news sources have been saved for extraction."
                ),
            ),
            ReportSection(
                title="Risks",
                body=(
                    _list_or_fallback(
                        structured.risk_factors,
                        "No risk factors extracted.",
                    )
                    if structured
                    else "Risk factors have not been extracted yet."
                ),
            ),
            ReportSection(
                title="Sources Reviewed",
                body=_source_notes(sources),
            ),
        ],
        signals=[
            ReportSignal(
                label="Match Confidence",
                value=f"{round(candidate.confidence * 100)}%",
                tone="positive" if candidate.confidence >= 0.7 else "neutral",
            ),
            ReportSignal(
                label="Sector",
                value=structured.sector if structured else candidate.industry or "Unknown",
                tone="neutral",
            ),
            ReportSignal(
                label="Sources",
                value=str(source_count),
                tone="positive" if source_count >= 8 else "neutral",
            ),
            ReportSignal(
                label="Extraction",
                value="LLM complete" if used_model else "Fallback",
                tone="positive" if used_model else "neutral",
            ),
        ],
    )


def _list_or_fallback(values: list[str], fallback: str) -> str:
    return "\n".join(values) if values else fallback


def _source_notes(sources: list[SourceSnippet] | None) -> str:
    if not sources:
        return "No sources were saved for this report."
    return "\n".join(
        f"- [{source.source_type}] {source.title}\n  {source.url}\n  {source.snippet}"
        for source in sources[:10]
    )
