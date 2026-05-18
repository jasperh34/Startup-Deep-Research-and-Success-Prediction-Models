from __future__ import annotations

from dataclasses import asdict, dataclass, field
from typing import Any, Literal

SourceType = Literal[
    "company_website",
    "linkedin",
    "funding_reference",
    "pitchbook_reference",
    "founder_profile",
    "news",
    "product_hunt",
    "github",
    "yc_profile",
    "registry",
    "jobs",
    "other",
]

ReportStatus = Literal["draft", "ready"]
SignalTone = Literal["positive", "neutral", "negative"]


@dataclass(slots=True)
class CompanyCandidate:
    id: str
    name: str
    description: str
    confidence: float
    source: str
    website: str | None = None
    location: str | None = None
    industry: str | None = None
    company_type: str | None = None
    founding_year: str | None = None
    funding_stage: str | None = None
    match_reasons: list[str] = field(default_factory=list)
    source_types: list[str] = field(default_factory=list)
    source_url: str | None = None
    company_id: str | None = None

    def to_dict(self) -> dict[str, Any]:
        return _strip_none(asdict(self))


@dataclass(slots=True)
class SourceSnippet:
    url: str
    title: str
    snippet: str
    source_type: SourceType
    retrieved_at: str
    id: str | None = None
    company_id: str | None = None

    def to_dict(self) -> dict[str, Any]:
        return _strip_none(asdict(self))


@dataclass(slots=True)
class StructuredFounder:
    name: str
    role: str
    background: str
    signals: list[str] = field(default_factory=list)


@dataclass(slots=True)
class StructuredFunding:
    total_raised: str
    latest_round: str
    investors: list[str] = field(default_factory=list)


@dataclass(slots=True)
class StructuredCompany:
    company_name: str
    description: str
    sector: str
    founding_year: str
    founders: list[StructuredFounder] = field(default_factory=list)
    funding: StructuredFunding = field(
        default_factory=lambda: StructuredFunding(
            total_raised="Unknown",
            latest_round="Unknown",
            investors=[],
        ),
    )
    traction_signals: list[str] = field(default_factory=list)
    risk_factors: list[str] = field(default_factory=list)
    recent_news: list[str] = field(default_factory=list)

    def to_dict(self) -> dict[str, Any]:
        return _strip_none(asdict(self))


@dataclass(slots=True)
class ReportSection:
    title: str
    body: str


@dataclass(slots=True)
class ReportSignal:
    label: str
    value: str
    tone: SignalTone


@dataclass(slots=True)
class StartupReport:
    id: str
    company_name: str
    summary: str
    status: ReportStatus
    created_at: str
    sections: list[ReportSection]
    signals: list[ReportSignal]
    company_id: str | None = None
    website: str | None = None
    source_count: int | None = None
    structured_json: dict[str, Any] | None = None

    def to_dict(self) -> dict[str, Any]:
        return _strip_none(asdict(self))


def _strip_none(value: dict[str, Any]) -> dict[str, Any]:
    return {key: item for key, item in value.items() if item is not None}
