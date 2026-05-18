from __future__ import annotations

from .env import env_value
from .extraction import extract_structured_company
from .models import CompanyCandidate, StartupReport
from .reports import build_draft_report
from .search import TavilyCompanySearchProvider
from .sources import collect_company_sources


def search_company_candidates(query: str) -> list[CompanyCandidate]:
    tavily_api_key = env_value("TAVILY_API_KEY")
    if not tavily_api_key:
        raise RuntimeError("TAVILY_API_KEY is required for Python company search.")
    return TavilyCompanySearchProvider(tavily_api_key).search_companies(query)


def build_report_for_candidate(candidate: CompanyCandidate) -> StartupReport:
    sources = collect_company_sources(candidate)
    structured, used_model = extract_structured_company(
        {
            "name": candidate.name,
            "website": candidate.website,
            "description": candidate.description,
        },
        sources,
    )
    return build_draft_report(
        candidate,
        company_id=candidate.company_id,
        sources=sources,
        structured=structured,
        used_model=used_model,
    )
