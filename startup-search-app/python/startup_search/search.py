from __future__ import annotations

import re
from dataclasses import dataclass
from urllib.parse import urlparse

from .http import HttpRequestError, head_url, request_json
from .models import CompanyCandidate
from .source_types import classify_source

NOISY_HOST_PARTS = [
    "crunchbase",
    "linkedin",
    "facebook",
    "twitter",
    "x.com",
    "youtube",
    "wikipedia",
    "techcrunch",
    "reuters",
    "support.",
]

NOISY_PATH_PARTS = [
    "/blog/",
    "/news",
    "/newsroom",
    "/resources/",
    "/support/",
    "/help",
    "/careers",
    "/jobs",
    "/directory/",
    "/company/",
]

LIKELY_OFFICIAL_TLDS = ["com", "ai", "app", "io", "co"]


@dataclass(slots=True)
class TavilyResult:
    title: str | None = None
    url: str | None = None
    content: str | None = None
    score: float | None = None


class TavilyCompanySearchProvider:
    name = "tavily"

    def __init__(self, api_key: str):
        self.api_key = api_key

    def search_companies(self, query: str) -> list[CompanyCandidate]:
        payload = request_json(
            "https://api.tavily.com/search",
            method="POST",
            headers={"Authorization": f"Bearer {self.api_key}"},
            payload={
                "query": f"{query} official company website startup founders funding",
                "search_depth": "basic",
                "topic": "general",
                "max_results": 8,
                "include_answer": False,
                "include_raw_content": False,
                "include_images": False,
            },
        )
        results = [
            TavilyResult(
                title=result.get("title"),
                url=result.get("url"),
                content=result.get("content"),
                score=result.get("score"),
            )
            for result in payload.get("results", [])
        ]

        tavily_candidates = [
            candidate
            for index, result in enumerate(results)
            if (candidate := _map_result_to_candidate(result, query, index)) is not None
        ]
        probed_candidates: list[CompanyCandidate] = []
        if not _has_exact_domain_candidate(tavily_candidates, query):
            probed_candidates = _enrich_probed_candidates(
                _probe_likely_official_domains(query)[:2],
                tavily_candidates,
                query,
            )

        return _dedupe_and_rank([*probed_candidates, *tavily_candidates])


def _hostname(url: str) -> str | None:
    try:
        return (urlparse(url).hostname or "").lower().removeprefix("www.") or None
    except ValueError:
        return None


def _url_path(url: str) -> str:
    try:
        return urlparse(url).path.lower()
    except ValueError:
        return ""


def _slugify(value: str) -> str:
    return re.sub(r"[^a-z0-9]+", "", value.lower())


def _domain_slug(value: str) -> str:
    return _slugify(value)[:40]


def _domain_name(host: str) -> str:
    return host.split(".")[0] if host else host


def _title_to_company_name(title: str, query: str) -> str:
    before_verb = re.split(
        r"\s+(lands|raises|secures|announces|launches|closes|gets|bags)\b",
        title,
        maxsplit=1,
        flags=re.IGNORECASE,
    )[0]
    first_part = re.split(r"[-|:]", before_verb, maxsplit=1)[0]
    cleaned = re.sub(
        r"\b(official site|homepage|funding|investor insights)\b",
        "",
        first_part,
        flags=re.IGNORECASE,
    ).strip()
    return cleaned or query


def _infer_company_name(result: TavilyResult, query: str) -> str:
    if result.url:
        host = _hostname(result.url)
        path = _url_path(result.url)
        if host and _slugify(_domain_name(host)) == _slugify(query) and len(path) <= 1:
            return query
    return _title_to_company_name((result.title or query).strip(), query)


def _is_noisy_result(result: TavilyResult) -> bool:
    if not result.url:
        return False
    host = _hostname(result.url) or ""
    path = _url_path(result.url)
    return any(part in host for part in NOISY_HOST_PARTS) or any(
        part in path for part in NOISY_PATH_PARTS
    )


def _is_exact_company_domain(result: TavilyResult, query: str) -> bool:
    if not result.url:
        return False
    host = _hostname(result.url)
    return bool(host and _slugify(_domain_name(host)) == _slugify(query))


def _is_likely_official_site(result: TavilyResult, query: str) -> bool:
    if not result.url:
        return False
    host = _hostname(result.url)
    path = _url_path(result.url)
    if not host:
        return False

    query_slug = _slugify(query)
    host_slug = _slugify(_domain_name(host))
    title_slug = _slugify(result.title or "")
    shallow_page = path in {"", "/"}
    return host_slug == query_slug or (
        query_slug in title_slug and shallow_page and not _is_noisy_result(result)
    )


def _score_result(result: TavilyResult, query: str) -> float:
    score = result.score if result.score is not None else 0.5
    host = _hostname(result.url) if result.url else None
    host_slug = _slugify(_domain_name(host)) if host else ""
    query_slug = _slugify(query)
    text_slug = _slugify(f"{result.title or ''} {result.content or ''}")

    if host_slug == query_slug:
        score += 0.28
    if _is_likely_official_site(result, query):
        score += 0.18
    if query_slug in text_slug:
        score += 0.08
    if _is_noisy_result(result):
        score -= 0.22
    if not _is_exact_company_domain(result, query):
        score = min(score, 0.84)
    if _is_noisy_result(result):
        score = min(score, 0.72)
    if _is_exact_company_domain(result, query):
        score = max(score, 0.94)

    return max(0.2, min(score, 0.98))


def _includes_any(text: str, values: list[str]) -> bool:
    return any(value in text for value in values)


def _infer_industry(text: str) -> str | None:
    if _includes_any(text, ["defence", "defense", "national security", "aerospace"]):
        return "Defense and security"
    if _includes_any(text, ["banking", "bank account", "fintech", "financial"]):
        return "Fintech"
    if _includes_any(text, ["insurance", "insurtech"]):
        return "Insurance technology"
    if _includes_any(text, ["artificial intelligence", " ai ", "frontier ai"]):
        return "Artificial intelligence"
    if _includes_any(text, ["developer", "software", "saas"]):
        return "Software"
    if _includes_any(text, ["venture capital", "vc firm", "investor"]):
        return "Venture capital"
    return None


def _infer_company_type(text: str) -> str:
    if _includes_any(text, ["public company", "nasdaq", "nyse"]):
        return "Public company"
    if _includes_any(text, ["startup", "pre-seed", "seed", "series a", "founder"]):
        return "Startup"
    if _includes_any(text, ["venture capital", "vc firm", "investor"]):
        return "Investment firm"
    if "insurance" in text:
        return "Insurance company"
    return "Company"


def _infer_funding_stage(text: str) -> str | None:
    if "pre-seed" in text:
        return "Pre-seed"
    if "seed" in text:
        return "Seed"
    if "series a" in text:
        return "Series A"
    if "series b" in text:
        return "Series B"
    if "series c" in text:
        return "Series C"
    if "ipo" in text or "public company" in text:
        return "Public"
    return None


def _infer_founding_year(text: str) -> str | None:
    match = re.search(r"\bfounded (?:in )?(20\d{2}|19\d{2})\b", text)
    return match.group(1) if match else None


def _infer_match_reasons(result: TavilyResult, query: str) -> list[str]:
    text = f"{result.title or ''} {result.content or ''}".lower()
    reasons: list[str] = []
    if _is_exact_company_domain(result, query):
        reasons.append("Exact company domain")
    if "founder" in text or "founded" in text:
        reasons.append("Founder evidence")
    if any(token in text for token in ["funding", "raised", "pre-seed", "series "]):
        reasons.append("Funding evidence")
    if "startup" in text:
        reasons.append("Startup context")
    if result.url:
        reasons.append(f"{classify_source(result.url, result.title or '')} source")
    return reasons[:4]


def _map_result_to_candidate(
    result: TavilyResult,
    query: str,
    index: int,
) -> CompanyCandidate | None:
    if not result.url:
        return None

    host = _hostname(result.url)
    score = _score_result(result, query)
    official = _is_likely_official_site(result, query)
    text = f"{result.title or ''} {result.content or ''} {result.url}".lower()

    return CompanyCandidate(
        id=f"{query.lower()}-{index}-{host or 'result'}",
        name=query if official else _infer_company_name(result, query),
        website=f"https://{host}" if official and host else result.url,
        description=(result.content or "").strip()
        or f"Search result for {query}{f' from {host}' if host else ''}.",
        confidence=score,
        industry=_infer_industry(text),
        company_type=_infer_company_type(text),
        founding_year=_infer_founding_year(text),
        funding_stage=_infer_funding_stage(text),
        match_reasons=_infer_match_reasons(result, query),
        source_types=[classify_source(result.url, result.title or "")],
        source="tavily",
        source_url=result.url,
    )


def _dedupe_and_rank(candidates: list[CompanyCandidate]) -> list[CompanyCandidate]:
    by_website: dict[str, CompanyCandidate] = {}
    for candidate in candidates:
        key = (
            _hostname(candidate.website) or candidate.website
            if candidate.website
            else candidate.name.lower()
        )
        existing = by_website.get(key)
        if not existing or candidate.confidence > existing.confidence:
            by_website[key] = candidate
    return sorted(by_website.values(), key=lambda item: item.confidence, reverse=True)[:5]


def _enrich_probed_candidates(
    probed_candidates: list[CompanyCandidate],
    evidence_candidates: list[CompanyCandidate],
    query: str,
) -> list[CompanyCandidate]:
    query_slug = _slugify(query)

    def evidence_score(candidate: CompanyCandidate) -> float:
        candidate_slug = _slugify(candidate.name)
        text = f"{candidate.name} {candidate.description} {candidate.website or ''}".lower()
        if (
            candidate_slug != query_slug
            and not candidate_slug.startswith(query_slug)
            and not query_slug.startswith(candidate_slug)
        ):
            return -1
        score = candidate.confidence
        if candidate.industry:
            score += 0.35
        if candidate.funding_stage:
            score += 0.25
        if "news" in candidate.source_types:
            score += 0.25
        if "Founder evidence" in candidate.match_reasons:
            score += 0.2
        if "Funding evidence" in candidate.match_reasons:
            score += 0.2
        if "closed" in text:
            score -= 0.5
        if "funding_reference" in candidate.source_types:
            score -= 0.05
        return score

    scored_evidence = [
        (evidence_score(candidate), candidate) for candidate in evidence_candidates
    ]
    scored_evidence.sort(key=lambda item: item[0], reverse=True)
    best_evidence = next(
        (candidate for score, candidate in scored_evidence if score >= 0),
        None,
    )
    if not best_evidence:
        return probed_candidates

    enriched: list[CompanyCandidate] = []
    for candidate in probed_candidates:
        enriched.append(
            CompanyCandidate(
                **{
                    **candidate.to_dict(),
                    "name": best_evidence.name,
                    "description": candidate.description
                    if len(candidate.description) > len(best_evidence.description)
                    else best_evidence.description,
                    "industry": best_evidence.industry,
                    "company_type": best_evidence.company_type,
                    "founding_year": best_evidence.founding_year,
                    "funding_stage": best_evidence.funding_stage,
                    "match_reasons": [
                        "Likely official domain",
                        *best_evidence.match_reasons,
                    ][:5],
                    "source_types": sorted(
                        {"company_website", *best_evidence.source_types},
                    ),
                },
            ),
        )
    return enriched


def _has_exact_domain_candidate(candidates: list[CompanyCandidate], query: str) -> bool:
    query_slug = _slugify(query)
    for candidate in candidates:
        if not candidate.website:
            continue
        host = _hostname(candidate.website)
        if host and _slugify(_domain_name(host)) == query_slug:
            return True
    return False


def _probe_likely_official_domains(query: str) -> list[CompanyCandidate]:
    slug = _domain_slug(query)
    if not slug:
        return []

    candidates: list[CompanyCandidate] = []
    for index, tld in enumerate(LIKELY_OFFICIAL_TLDS):
        url = f"https://{slug}.{tld}"
        try:
            status, final_url = head_url(url, timeout=2.5)
        except HttpRequestError:
            continue
        final_host = _hostname(final_url)
        if 200 <= status < 400 and final_host and _slugify(_domain_name(final_host)) == slug:
            candidates.append(
                CompanyCandidate(
                    id=f"{slug}-domain-{tld}",
                    name=query,
                    website=f"https://{final_host}",
                    description="Likely official company website found by checking common startup domains.",
                    confidence=0.96 - index * 0.01,
                    source="domain-probe",
                    source_url=final_url,
                ),
            )
    return candidates
