"""Python business-logic mirror for Jasper Startup Search.

The Next.js app remains the production path for now. These modules mirror the
portable search, research, extraction, and report-building logic so the project
can grow toward a FastAPI/Python backend without a risky rewrite.
"""

from .models import (
    CompanyCandidate,
    SourceSnippet,
    StartupReport,
    StructuredCompany,
)
from .reports import build_draft_report
from .search import TavilyCompanySearchProvider
from .sources import collect_company_sources

__all__ = [
    "CompanyCandidate",
    "SourceSnippet",
    "StartupReport",
    "StructuredCompany",
    "TavilyCompanySearchProvider",
    "build_draft_report",
    "collect_company_sources",
]
