from __future__ import annotations

from typing import Any
from urllib.parse import quote

from .companies import company_row_payload, normalize_website, with_company_id
from .http import HttpRequestError, request_json
from .models import CompanyCandidate, SourceSnippet, StartupReport


class SupabaseRestClient:
    """Tiny Supabase REST client for Python pipeline parity.

    This intentionally covers only the tables this app uses. A future FastAPI
    backend can swap this for the official Supabase Python client if preferred.
    """

    def __init__(self, url: str, service_role_key: str):
        self.url = url.rstrip("/")
        self.headers = {
            "apikey": service_role_key,
            "Authorization": f"Bearer {service_role_key}",
            "Prefer": "return=representation",
        }

    def persist_company_candidates(
        self,
        candidates: list[CompanyCandidate],
    ) -> list[CompanyCandidate]:
        return [self._upsert_company(candidate, selected_by_user=False) for candidate in candidates]

    def confirm_company(self, candidate: CompanyCandidate) -> dict[str, Any]:
        persisted = (
            candidate
            if candidate.company_id
            else self._upsert_company(candidate, selected_by_user=False)
        )
        rows = self._patch(
            "companies",
            {"selected_by_user": True},
            f"id=eq.{quote(persisted.company_id or '')}",
        )
        if not rows:
            raise RuntimeError("Could not confirm company.")
        return rows[0]

    def save_company_sources(
        self,
        company_id: str,
        sources: list[SourceSnippet],
    ) -> list[SourceSnippet]:
        if not sources:
            return []
        rows = [
            {
                "company_id": company_id,
                "url": source.url,
                "title": source.title,
                "snippet": source.snippet,
                "source_type": source.source_type,
                "retrieved_at": source.retrieved_at,
            }
            for source in sources
        ]
        data = self._post(
            "sources",
            rows,
            query="on_conflict=company_id,url",
            extra_headers={
                "Prefer": "resolution=merge-duplicates,return=representation",
            },
        )
        return [
            SourceSnippet(
                id=row.get("id"),
                company_id=row.get("company_id"),
                url=row["url"],
                title=row["title"],
                snippet=row["snippet"],
                source_type=row["source_type"],
                retrieved_at=row["retrieved_at"],
            )
            for row in data
        ]

    def save_report(
        self,
        report: StartupReport,
        *,
        company_id: str,
    ) -> str:
        rows = self._post(
            "reports",
            {
                "id": report.id,
                "company_id": company_id,
                "company_name": report.company_name,
                "website": report.website,
                "status": report.status,
                "structured_json": report.structured_json,
                "summary": report.summary,
                "report": report.to_dict(),
            },
        )
        if not rows:
            raise RuntimeError("Could not save report.")
        return rows[0]["id"]

    def _upsert_company(
        self,
        candidate: CompanyCandidate,
        *,
        selected_by_user: bool,
    ) -> CompanyCandidate:
        website = normalize_website(candidate.website)
        existing = self._find_company(candidate.name, website)
        payload = company_row_payload(candidate, selected_by_user=selected_by_user)

        if existing:
            rows = self._patch_with_metadata_retry(
                "companies",
                payload,
                f"id=eq.{quote(existing['id'])}",
            )
            return with_company_id(candidate, rows[0]["id"] if rows else existing["id"])

        rows = self._post_with_metadata_retry("companies", payload)
        if not rows:
            raise RuntimeError("Could not create company candidate.")
        return with_company_id(candidate, rows[0]["id"])

    def _find_company(self, name: str, website: str | None) -> dict[str, Any] | None:
        if website:
            query = f"select=id&website=eq.{quote(website, safe='')}"
        else:
            query = f"select=id&name=eq.{quote(name, safe='')}&website=is.null"
        rows = self._get("companies", query)
        return rows[0] if rows else None

    def _get(self, table: str, query: str = "") -> list[dict[str, Any]]:
        suffix = f"?{query}" if query else ""
        payload = request_json(
            f"{self.url}/rest/v1/{table}{suffix}",
            headers=self.headers,
        )
        return payload if isinstance(payload, list) else [payload]

    def _post(
        self,
        table: str,
        payload: object,
        *,
        query: str = "",
        extra_headers: dict[str, str] | None = None,
    ) -> list[dict[str, Any]]:
        suffix = f"?{query}" if query else ""
        data = request_json(
            f"{self.url}/rest/v1/{table}{suffix}",
            method="POST",
            headers={**self.headers, **(extra_headers or {})},
            payload=payload,
        )
        return data if isinstance(data, list) else [data]

    def _patch(
        self,
        table: str,
        payload: dict[str, object],
        filter_query: str,
    ) -> list[dict[str, Any]]:
        data = request_json(
            f"{self.url}/rest/v1/{table}?{filter_query}",
            method="PATCH",
            headers=self.headers,
            payload=payload,
        )
        return data if isinstance(data, list) else [data]

    def _post_with_metadata_retry(
        self,
        table: str,
        payload: dict[str, object],
    ) -> list[dict[str, Any]]:
        try:
            return self._post(table, payload)
        except HttpRequestError as error:
            if not _is_missing_metadata_column(error):
                raise
            return self._post(table, _without_metadata(payload))

    def _patch_with_metadata_retry(
        self,
        table: str,
        payload: dict[str, object],
        filter_query: str,
    ) -> list[dict[str, Any]]:
        try:
            return self._patch(table, payload, filter_query)
        except HttpRequestError as error:
            if not _is_missing_metadata_column(error):
                raise
            return self._patch(table, _without_metadata(payload), filter_query)


def _is_missing_metadata_column(error: HttpRequestError) -> bool:
    return "metadata" in str(error).lower()


def _without_metadata(payload: dict[str, object]) -> dict[str, object]:
    return {key: value for key, value in payload.items() if key != "metadata"}
