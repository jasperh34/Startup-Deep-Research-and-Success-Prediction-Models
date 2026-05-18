from __future__ import annotations

from .models import SourceType


def classify_source(url: str, title: str = "") -> SourceType:
    lower_url = url.lower()
    lower_title = title.lower()
    joined = f"{lower_url} {lower_title}"

    if "linkedin.com" in lower_url:
        return "linkedin"
    if "crunchbase.com" in lower_url:
        return "funding_reference"
    if "pitchbook.com" in lower_url:
        return "pitchbook_reference"
    if "producthunt.com" in lower_url:
        return "product_hunt"
    if "github.com" in lower_url:
        return "github"
    if "tech.eu" in lower_url or "pressrelease" in lower_url:
        return "news"
    if "ycombinator.com/companies" in lower_url:
        return "yc_profile"
    if "sec.gov" in lower_url or "companieshouse.gov.uk" in lower_url:
        return "registry"
    if any(token in joined for token in ["founder", "co-founder", "founded by", "profile"]):
        return "founder_profile"
    if "career" in joined or "jobs" in joined:
        return "jobs"
    if any(token in joined for token in ["news", "raises", "funding", "series "]):
        return "news"

    return "other"
