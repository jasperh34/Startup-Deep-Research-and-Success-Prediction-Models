from __future__ import annotations

from datetime import UTC, datetime
from urllib.parse import urlparse, urlunparse

from .env import env_value
from .http import HttpRequestError, request_json
from .models import CompanyCandidate, SourceSnippet
from .source_types import classify_source

PREFERRED_SOURCE_TYPES = [
    "company_website",
    "founder_profile",
    "funding_reference",
    "news",
    "linkedin",
    "yc_profile",
    "product_hunt",
    "github",
    "jobs",
    "registry",
    "pitchbook_reference",
    "other",
]


def company_name_variants(name: str, website: str | None = None) -> list[str]:
    variants = [name]
    compact = "".join(name.split())
    if compact != name and compact not in variants:
        variants.append(compact)
    if website:
        host = urlparse(website).hostname or ""
        domain_name = host.removeprefix("www.").split(".")[0]
        if domain_name and domain_name not in variants:
            variants.append(domain_name)
    return [variant for variant in variants if variant]


def build_source_queries(name: str, website: str | None = None) -> list[str]:
    company = company_name_variants(name, website)[0]
    return [
        f"{company} official website company",
        f"{company} founders co-founders founded by leadership team",
        f"{company} raised funding investors pre-seed seed series",
        f"{company} recent news press release funding",
        f"{company} LinkedIn company",
        f"{company} Crunchbase funding founders",
        f"{company} PitchBook funding investors",
        f"{company} Product Hunt launch",
        f"{company} GitHub",
        f"{company} Y Combinator company profile",
        f"{company} jobs careers hiring",
        f"{company} SEC Companies House filing registry",
    ]


def collect_company_sources(
    company: CompanyCandidate,
    *,
    tavily_api_key: str | None = None,
) -> list[SourceSnippet]:
    retrieved_at = datetime.now(UTC).isoformat()
    initial_sources: list[SourceSnippet] = []

    if company.website:
        initial_sources.append(
            SourceSnippet(
                url=company.website,
                title=f"{company.name} website",
                snippet=company.description,
                source_type="company_website",
                retrieved_at=retrieved_at,
            ),
        )

    context_query = " ".join(
        value
        for value in [company.industry, company.funding_stage, company.description]
        if value
    )
    queries = [
        *build_source_queries(company.name, company.website),
        f"{company.name} {context_query} founders funding",
        f"{company.name} {context_query} Tech.eu press release",
        f"{company.name} {context_query} Theon Expeditions",
    ]
    search_results = [
        result
        for query in queries
        for result in _tavily_search(query, tavily_api_key=tavily_api_key)
    ]

    search_sources: list[SourceSnippet] = []
    for result in search_results:
        url = result.get("url")
        if not url:
            continue
        title = (result.get("title") or _title_from_url(url)).strip()
        snippet = (result.get("content") or f"Search result for {company.name}.").strip()
        search_sources.append(
            SourceSnippet(
                url=url,
                title=title,
                snippet=snippet,
                source_type=classify_source(url, f"{title} {snippet}"),
                retrieved_at=retrieved_at,
            ),
        )

    return dedupe_sources(
        [
            source
            for source in [*initial_sources, *search_sources]
            if is_relevant_to_confirmed_company(source, company)
        ],
    )


def dedupe_sources(sources: list[SourceSnippet]) -> list[SourceSnippet]:
    by_url: dict[str, SourceSnippet] = {}
    for source in sources:
        key = _normalize_url(source.url)
        existing = by_url.get(key)
        if not existing or len(source.snippet) > len(existing.snippet):
            by_url[key] = SourceSnippet(
                **{
                    **source.to_dict(),
                    "url": key,
                },
            )
    return sorted(by_url.values(), key=_score_source, reverse=True)[:20]


def is_relevant_to_confirmed_company(
    source: SourceSnippet,
    company: CompanyCandidate,
) -> bool:
    context = f"{company.description} {company.industry or ''} {company.funding_stage or ''}".lower()
    text = f"{source.title} {source.snippet} {source.url}".lower()
    stale_signals = [
        "salesforce acquires",
        "operating status closed",
        "mobile data",
        "app acceleration",
    ]
    has_stale_signal = any(signal in text for signal in stale_signals)

    wants_defense_ai = any(
        signal in context
        for signal in ["defence", "defense", "national security", "frontier ai"]
    )
    has_defense_ai_context = any(
        signal in text
        for signal in [
            "defence",
            "defense",
            "national security",
            "theon",
            "expeditions",
            "frontier",
            "sensor",
        ]
    )

    if not wants_defense_ai:
        return not has_stale_signal
    if source.source_type == "company_website":
        return source.url.startswith(company.website) if company.website else True
    if not has_defense_ai_context:
        return False
    if any(
        signal in text
        for signal in [
            "salesforce",
            "mobile data",
            "app acceleration",
            "twin prime media",
            "kartik chandrayana",
            "satish raghunath",
        ]
    ):
        return False
    return has_defense_ai_context


def _tavily_search(
    query: str,
    *,
    tavily_api_key: str | None = None,
) -> list[dict[str, str]]:
    api_key = tavily_api_key or env_value("TAVILY_API_KEY")
    if not api_key:
        return []
    safe_query = " ".join(query.split())[:380]
    try:
        payload = request_json(
            "https://api.tavily.com/search",
            method="POST",
            headers={"Authorization": f"Bearer {api_key}"},
            payload={
                "query": safe_query,
                "search_depth": "basic",
                "topic": "general",
                "max_results": 5,
                "include_answer": False,
                "include_raw_content": False,
                "include_images": False,
            },
        )
    except HttpRequestError:
        return []
    return payload.get("results", [])


def _score_source(source: SourceSnippet) -> int:
    try:
        source_type_score = len(PREFERRED_SOURCE_TYPES) - PREFERRED_SOURCE_TYPES.index(
            source.source_type,
        )
    except ValueError:
        source_type_score = 0
    text = f"{source.title} {source.snippet}".lower()
    score = source_type_score
    if any(token in text for token in ["founder", "co-founder", "founded by"]):
        score += 8
    if any(token in text for token in ["raised", "funding", "pre-seed", "series "]):
        score += 6
    if "investor" in text or "led by" in text:
        score += 4
    if source.source_type == "company_website":
        score += 5
    return score


def _title_from_url(url: str) -> str:
    return urlparse(url).hostname or url


def _normalize_url(value: str) -> str:
    parsed = urlparse(value)
    cleaned = parsed._replace(fragment="")
    return urlunparse(cleaned).rstrip("/")
