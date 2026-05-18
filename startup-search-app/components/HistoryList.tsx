"use client";

import Link from "next/link";
import { useState } from "react";
import { Clock, FileText, Search } from "lucide-react";
import type { StartupReport } from "@/types/api";

const reportsStorageKey = "startup-search:reports";

export function HistoryList() {
  const [reports] = useState<StartupReport[]>(() => {
    if (typeof window === "undefined") {
      return [];
    }

    const stored = window.localStorage.getItem(reportsStorageKey);
    return stored ? (JSON.parse(stored) as StartupReport[]) : [];
  });

  if (reports.length === 0) {
    return (
      <div className="rounded-md border border-dashed border-violet-200 bg-white/75 p-10 text-center shadow-xl shadow-violet-100/60 backdrop-blur">
        <div className="mx-auto flex size-12 items-center justify-center rounded-md bg-gradient-to-br from-violet-600 to-sky-500 text-white shadow-lg shadow-violet-200">
          <FileText className="size-5" aria-hidden="true" />
        </div>
        <h2 className="mt-4 font-semibold text-slate-950">
          No saved reports yet
        </h2>
        <p className="mx-auto mt-2 max-w-md text-sm leading-6 text-slate-600">
          Confirm a company match to create your first draft report.
        </p>
        <Link
          href="/search"
          className="mt-6 inline-flex min-h-11 items-center gap-2 rounded-md bg-gradient-to-r from-violet-600 to-sky-500 px-4 text-sm font-semibold text-white shadow-lg shadow-violet-200 transition hover:-translate-y-0.5 hover:shadow-sky-200"
        >
          <Search className="size-4" aria-hidden="true" />
          Start a search
        </Link>
      </div>
    );
  }

  return (
    <div className="grid gap-3">
      {reports.map((report) => (
        <Link
          key={report.id}
          href={`/report/${report.id}`}
          className="rounded-md border border-white/80 bg-white/75 p-5 shadow-lg shadow-violet-100/40 backdrop-blur transition hover:-translate-y-0.5 hover:border-violet-200 hover:bg-white hover:shadow-xl hover:shadow-sky-100/60"
        >
          <div className="flex flex-col gap-2 sm:flex-row sm:items-start sm:justify-between">
            <div className="min-w-0">
              <h2 className="font-semibold text-slate-950">
                {report.companyName}
              </h2>
              <p className="mt-1 truncate text-sm text-slate-500">
                {report.website}
              </p>
            </div>
            <span className="inline-flex min-h-8 items-center rounded-md bg-sky-50 px-3 text-sm font-medium capitalize text-sky-700 ring-1 ring-sky-100">
              {report.status}
            </span>
          </div>
          <p className="mt-4 line-clamp-2 text-sm leading-6 text-slate-600">
            {report.summary}
          </p>
          <p className="mt-4 flex items-center gap-2 text-xs font-medium text-slate-400">
            <Clock className="size-3.5" aria-hidden="true" />
            {new Date(report.createdAt).toLocaleDateString()}
          </p>
        </Link>
      ))}
    </div>
  );
}
