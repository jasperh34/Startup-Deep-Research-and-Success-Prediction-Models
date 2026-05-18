"use client";

import Link from "next/link";
import { useRouter } from "next/navigation";
import { useState } from "react";
import { ArrowLeft, Building2, ExternalLink, Loader2 } from "lucide-react";
import type {
  CompanyCandidate,
  CompanySearchResponse,
  StartupReport,
} from "@/types/api";

const searchStorageKey = "startup-search:last-search";
const reportsStorageKey = "startup-search:reports";

export function ClarifyCompanyMatches() {
  const router = useRouter();
  const [search] = useState<CompanySearchResponse | null>(() => {
    if (typeof window === "undefined") {
      return null;
    }

    const stored = window.sessionStorage.getItem(searchStorageKey);
    return stored ? (JSON.parse(stored) as CompanySearchResponse) : null;
  });
  const [selectedId, setSelectedId] = useState<string | null>(null);
  const [error, setError] = useState<string | null>(null);

  async function confirmCompany(candidate: CompanyCandidate) {
    if (!search) {
      return;
    }

    setError(null);
    setSelectedId(candidate.id);

    try {
      const response = await fetch("/api/reports", {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({ query: search.query, candidate }),
      });
      const payload = await response.json();

      if (!response.ok) {
        throw new Error(payload.error ?? "Could not create report.");
      }

      const report = payload.report as StartupReport;
      const storedReports = window.localStorage.getItem(reportsStorageKey);
      const reports = storedReports
        ? (JSON.parse(storedReports) as StartupReport[])
        : [];
      window.localStorage.setItem(
        reportsStorageKey,
        JSON.stringify([
          report,
          ...reports.filter((item) => item.id !== report.id),
        ]),
      );
      window.sessionStorage.setItem(
        `startup-search:report:${report.id}`,
        JSON.stringify(report),
      );
      router.push(`/report/${report.id}`);
    } catch (confirmError) {
      setSelectedId(null);
      setError(
        confirmError instanceof Error
          ? confirmError.message
          : "Something went wrong.",
      );
    }
  }

  if (!search) {
    return (
      <div className="max-w-2xl rounded-md border border-white/80 bg-white/75 p-8 shadow-xl shadow-violet-100/60 backdrop-blur">
        <h1 className="text-3xl font-semibold text-slate-950">
          No search to clarify
        </h1>
        <p className="mt-4 leading-7 text-slate-600">
          Start with a company name so we can collect possible matches.
        </p>
        <Link
          href="/search"
          className="mt-6 inline-flex min-h-11 items-center gap-2 rounded-md bg-gradient-to-r from-violet-600 to-sky-500 px-4 text-sm font-semibold text-white shadow-lg shadow-violet-200 transition hover:-translate-y-0.5 hover:shadow-sky-200"
        >
          <ArrowLeft className="size-4" aria-hidden="true" />
          Back to search
        </Link>
      </div>
    );
  }

  return (
    <div className="max-w-5xl">
      <div className="mb-8 flex flex-col gap-5 border-b border-white/70 pb-8 lg:flex-row lg:items-end lg:justify-between">
        <div>
          <p className="text-sm font-medium uppercase tracking-[0.14em] text-violet-700">
            Confirm company
          </p>
          <h1 className="mt-3 text-4xl font-semibold text-slate-950">
            Which company did you mean?
          </h1>
          <p className="mt-4 max-w-2xl leading-7 text-slate-600">
            Search found {search.candidates.length} possible matches for{" "}
            <span className="font-medium text-slate-950">{search.query}</span>.
            Choose the best match before generating the draft brief.
          </p>
        </div>
        <div className="rounded-md border border-white/80 bg-white/75 px-4 py-3 text-sm text-slate-600 shadow-lg shadow-violet-100/50 backdrop-blur">
          <span className="font-semibold text-slate-950">
            {search.candidates.length}
          </span>{" "}
          candidates found
        </div>
      </div>

      <div className="mb-4 flex items-center gap-2 text-sm font-medium text-slate-500">
        <Building2 className="size-4 text-sky-500" aria-hidden="true" />
        Candidate matches
      </div>

      {error ? (
        <p className="mb-4 rounded-md border border-red-200 bg-red-50 px-4 py-3 text-sm font-medium text-red-700 shadow-sm">
          {error}
        </p>
      ) : null}

      <div className="grid gap-3">
        {search.candidates.map((candidate, index) => (
          <button
            key={candidate.id}
            type="button"
            onClick={() => confirmCompany(candidate)}
            disabled={selectedId !== null}
            className="group rounded-md border border-white/80 bg-white/75 p-5 text-left shadow-lg shadow-violet-100/40 backdrop-blur transition hover:-translate-y-0.5 hover:border-violet-200 hover:bg-white hover:shadow-xl hover:shadow-sky-100/60 disabled:cursor-wait disabled:opacity-70"
          >
            <div className="flex flex-col gap-4 sm:flex-row sm:items-start sm:justify-between">
              <div className="flex min-w-0 gap-4">
                <div className="flex size-11 shrink-0 items-center justify-center rounded-md bg-gradient-to-br from-violet-600 to-sky-500 text-sm font-semibold text-white shadow-lg shadow-violet-200">
                  {index + 1}
                </div>
                <div className="min-w-0">
                  <h2 className="font-semibold text-slate-950">
                    {candidate.name}
                  </h2>
                  {candidate.website ? (
                    <p className="mt-1 flex min-w-0 items-center gap-1 text-sm text-slate-500">
                      <ExternalLink
                        className="size-3.5 shrink-0"
                        aria-hidden="true"
                      />
                      <span className="truncate">{candidate.website}</span>
                    </p>
                  ) : null}
                </div>
              </div>
              <span className="inline-flex min-h-8 shrink-0 items-center gap-2 rounded-md bg-sky-50 px-3 text-sm font-semibold text-sky-700 ring-1 ring-sky-100">
                {selectedId === candidate.id ? (
                  <Loader2 className="size-4 animate-spin" aria-hidden="true" />
                ) : null}
                {Math.round(candidate.confidence * 100)}% match
              </span>
            </div>
            <p className="mt-4 line-clamp-3 text-sm leading-6 text-slate-600">
              {candidate.description}
            </p>
            <div className="mt-4 flex flex-wrap gap-2">
              {[
                candidate.companyType,
                candidate.industry,
                candidate.fundingStage,
                candidate.foundingYear
                  ? `Founded ${candidate.foundingYear}`
                  : undefined,
                ...(candidate.matchReasons ?? []),
              ]
                .filter(Boolean)
                .slice(0, 7)
                .map((item) => (
                  <span
                    key={item}
                    className="rounded-md bg-violet-50 px-2.5 py-1 text-xs font-medium text-violet-700 ring-1 ring-violet-100"
                  >
                    {item}
                  </span>
                ))}
            </div>
          </button>
        ))}
      </div>
    </div>
  );
}
