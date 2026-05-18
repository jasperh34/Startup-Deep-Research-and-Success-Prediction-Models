from __future__ import annotations

import json
import os
import sys
from http import HTTPStatus
from http.server import BaseHTTPRequestHandler, ThreadingHTTPServer
from typing import Any

from .api_serialization import candidate_from_api, candidate_to_api, report_to_api
from .env import env_value, load_dotenv, normalized_url
from .extraction import extract_structured_company
from .mock import mock_search_companies
from .models import CompanyCandidate
from .reports import build_draft_report
from .search import TavilyCompanySearchProvider
from .sources import collect_company_sources
from .supabase_rest import SupabaseRestClient


def create_server(host: str = "127.0.0.1", port: int = 8000) -> ThreadingHTTPServer:
    load_dotenv()
    return ThreadingHTTPServer((host, port), StartupSearchHandler)


class StartupSearchHandler(BaseHTTPRequestHandler):
    server_version = "JasperStartupSearchPython/0.1"
    protocol_version = "HTTP/1.1"

    def do_OPTIONS(self) -> None:
        self._send_json({}, status=HTTPStatus.NO_CONTENT)

    def do_GET(self) -> None:
        if self.path == "/health":
            self._send_json({"ok": True})
            return
        self._send_json({"error": "Not found."}, status=HTTPStatus.NOT_FOUND)

    def do_POST(self) -> None:
        try:
            if self.path == "/api/company-search":
                self._handle_company_search()
                return
            if self.path == "/api/reports":
                self._handle_reports()
                return
            self._send_json({"error": "Not found."}, status=HTTPStatus.NOT_FOUND)
        except Exception as error:
            print(f"API error: {error}", file=sys.stderr)
            self._send_json(
                {"error": str(error) or "Request failed."},
                status=HTTPStatus.INTERNAL_SERVER_ERROR,
            )

    def _handle_company_search(self) -> None:
        body = self._read_json()
        query = str(body.get("query", "")).strip()
        if len(query) < 2:
            self._send_json(
                {"error": "Enter at least 2 characters."},
                status=HTTPStatus.BAD_REQUEST,
            )
            return

        candidates = search_companies(query)
        supabase = create_supabase_client()
        if supabase:
            try:
                candidates = supabase.persist_company_candidates(candidates)
            except Exception as error:
                print(f"Could not persist company candidates: {error}", file=sys.stderr)

        self._send_json(
            {
                "query": query,
                "candidates": [candidate_to_api(candidate) for candidate in candidates],
                "needsConfirmation": len(candidates) > 1,
            },
        )

    def _handle_reports(self) -> None:
        body = self._read_json()
        query = str(body.get("query", "")).strip()
        candidate_data = body.get("candidate")
        if len(query) < 2 or not isinstance(candidate_data, dict):
            self._send_json(
                {"error": "Choose a company before creating a report."},
                status=HTTPStatus.BAD_REQUEST,
            )
            return

        candidate = candidate_from_api(candidate_data)
        supabase = create_supabase_client()
        company_id = candidate.company_id
        report_candidate = candidate

        if supabase:
            company = supabase.confirm_company(candidate)
            company_id = str(company["id"])
            report_candidate = CompanyCandidate(
                **{
                    **candidate.to_dict(),
                    "company_id": company_id,
                    "name": str(company.get("name") or candidate.name),
                    "website": company.get("website") or candidate.website,
                    "description": str(
                        company.get("description") or candidate.description,
                    ),
                    "location": company.get("location") or candidate.location,
                },
            )

        sources = collect_company_sources(report_candidate)
        if supabase and company_id:
            sources = supabase.save_company_sources(company_id, sources)

        structured, used_model = extract_structured_company(
            {
                "name": report_candidate.name,
                "website": report_candidate.website,
                "description": report_candidate.description,
            },
            sources,
        )
        report = build_draft_report(
            report_candidate,
            company_id=company_id,
            sources=sources,
            structured=structured,
            used_model=used_model,
        )

        if supabase and company_id:
            report.id = supabase.save_report(report, company_id=company_id)

        self._send_json({"report": report_to_api(report)})

    def _read_json(self) -> dict[str, Any]:
        length = int(self.headers.get("content-length", "0"))
        if length <= 0:
            return {}
        raw_body = self.rfile.read(length).decode("utf-8")
        payload = json.loads(raw_body)
        return payload if isinstance(payload, dict) else {}

    def _send_json(
        self,
        payload: dict[str, Any],
        *,
        status: HTTPStatus = HTTPStatus.OK,
    ) -> None:
        body = b"" if status == HTTPStatus.NO_CONTENT else json.dumps(payload).encode("utf-8")
        self.send_response(status)
        self.send_header("Access-Control-Allow-Origin", env_value("CORS_ORIGIN", "*") or "*")
        self.send_header("Access-Control-Allow-Headers", "Content-Type")
        self.send_header("Access-Control-Allow-Methods", "GET,POST,OPTIONS")
        self.send_header("Content-Type", "application/json")
        self.send_header("Content-Length", str(len(body)))
        self.send_header("Connection", "close")
        self.end_headers()
        if body:
            self.wfile.write(body)


def search_companies(query: str) -> list[CompanyCandidate]:
    tavily_api_key = env_value("TAVILY_API_KEY")
    if not tavily_api_key:
        return mock_search_companies(query)
    return TavilyCompanySearchProvider(tavily_api_key).search_companies(query)


def create_supabase_client() -> SupabaseRestClient | None:
    supabase_url = normalized_url(env_value("NEXT_PUBLIC_SUPABASE_URL"))
    service_role_key = env_value("SUPABASE_SERVICE_ROLE_KEY")
    if not supabase_url or not service_role_key:
        return None
    return SupabaseRestClient(supabase_url, service_role_key)


def main() -> None:
    host = os.environ.get("PYTHON_API_HOST", "127.0.0.1")
    port = int(os.environ.get("PORT", os.environ.get("PYTHON_API_PORT", "8000")))
    server = create_server(host, port)
    print(f"Python API listening on http://{host}:{port}")
    server.serve_forever()


if __name__ == "__main__":
    main()
