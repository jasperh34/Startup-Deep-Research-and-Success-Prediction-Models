from __future__ import annotations

import argparse
import json

from .env import load_dotenv
from .pipeline import build_report_for_candidate, search_company_candidates


def main() -> None:
    parser = argparse.ArgumentParser(description="Run the Python startup search pipeline.")
    parser.add_argument("query", help="Company name to search")
    parser.add_argument(
        "--report",
        action="store_true",
        help="Build a report for the top candidate instead of returning candidates only.",
    )
    args = parser.parse_args()

    load_dotenv()
    candidates = search_company_candidates(args.query)
    if not args.report:
        print(json.dumps([candidate.to_dict() for candidate in candidates], indent=2))
        return

    if not candidates:
        raise SystemExit("No candidates found.")
    report = build_report_for_candidate(candidates[0])
    print(json.dumps(report.to_dict(), indent=2))


if __name__ == "__main__":
    main()
