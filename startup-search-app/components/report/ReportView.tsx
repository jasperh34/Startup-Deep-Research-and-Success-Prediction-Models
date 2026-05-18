"use client";

import Link from "next/link";
import { useState } from "react";
import { Download, FileText, Save, TrendingUp } from "lucide-react";
import type { StartupReport } from "@/types/api";

const toneClasses = {
  positive: "bg-sky-50 text-sky-700 ring-sky-100",
  neutral: "bg-violet-50 text-violet-700 ring-violet-100",
  negative: "bg-red-50 text-red-700 ring-red-100",
};

export function ReportView({ id }: Readonly<{ id: string }>) {
  const [report] = useState<StartupReport | null>(() => {
    if (typeof window === "undefined") {
      return null;
    }

    const stored = window.sessionStorage.getItem(`startup-search:report:${id}`);
    const history = window.localStorage.getItem("startup-search:reports");
    const reports = history ? (JSON.parse(history) as StartupReport[]) : [];
    return stored
      ? (JSON.parse(stored) as StartupReport)
      : reports.find((item) => item.id === id) ?? null;
  });

  if (!report) {
    return (
      <div className="max-w-2xl rounded-md border border-white/80 bg-white/75 p-8 shadow-xl shadow-violet-100/60 backdrop-blur">
        <h1 className="text-3xl font-semibold text-slate-950">
          Report not found
        </h1>
        <p className="mt-4 leading-7 text-slate-600">
          This draft may only exist in your current browser session.
        </p>
        <Link
          href="/search"
          className="mt-6 inline-flex min-h-11 items-center rounded-md bg-gradient-to-r from-violet-600 to-sky-500 px-4 text-sm font-semibold text-white shadow-lg shadow-violet-200 transition hover:-translate-y-0.5 hover:shadow-sky-200"
        >
          Start a new search
        </Link>
      </div>
    );
  }

  return (
    <article className="max-w-6xl">
      <div className="rounded-md border border-white/80 bg-white/75 p-6 shadow-xl shadow-violet-100/60 backdrop-blur-xl">
        <div className="flex flex-col gap-6 lg:flex-row lg:items-start lg:justify-between">
          <div>
            <p className="inline-flex min-h-8 items-center gap-2 rounded-md bg-violet-50 px-3 text-sm font-medium text-violet-700 ring-1 ring-violet-100">
              <FileText className="size-4" aria-hidden="true" />
              Research report
            </p>
            <h1 className="mt-4 text-4xl font-semibold leading-tight text-slate-950">
              {report.companyName}
            </h1>
            {report.website ? (
              <p className="mt-2 text-sm font-medium text-sky-700">
                {report.website}
              </p>
            ) : null}
            <p className="mt-5 max-w-3xl text-lg leading-8 text-slate-600">
              {report.summary}
            </p>
          </div>
          <div className="flex gap-2">
            <button className="inline-flex min-h-10 items-center gap-2 rounded-md border border-white/80 bg-white/75 px-3 text-sm font-medium text-slate-700 shadow-sm backdrop-blur transition hover:bg-white hover:text-slate-950">
              <Save className="size-4" aria-hidden="true" />
              Saved
            </button>
            <button className="inline-flex min-h-10 items-center gap-2 rounded-md bg-gradient-to-r from-violet-600 to-sky-500 px-3 text-sm font-semibold text-white shadow-lg shadow-violet-200 transition hover:-translate-y-0.5 hover:shadow-sky-200">
              <Download className="size-4" aria-hidden="true" />
              Export
            </button>
          </div>
        </div>
      </div>

      <div className="mt-6 grid gap-3 md:grid-cols-3">
        {report.signals.map((signal) => (
          <div
            key={signal.label}
            className="rounded-md border border-white/80 bg-white/75 p-5 shadow-lg shadow-violet-100/40 backdrop-blur"
          >
            <div className="flex items-center justify-between gap-3">
              <p className="text-sm font-medium text-slate-500">
                {signal.label}
              </p>
              <span
                className={`size-2.5 rounded-full ring-4 ${
                  toneClasses[signal.tone]
                }`}
              />
            </div>
            <p className="mt-3 text-2xl font-semibold text-slate-950">
              {signal.value}
            </p>
          </div>
        ))}
      </div>

      <div className="mt-6 grid gap-6 lg:grid-cols-[1fr_320px]">
        <div className="grid gap-4">
          {report.sections.map((section) => (
            <section
              key={section.title}
              className="rounded-md border border-white/80 bg-white/75 p-6 shadow-lg shadow-violet-100/40 backdrop-blur"
            >
              <h2 className="text-xl font-semibold text-slate-950">
                {section.title}
              </h2>
              <p className="mt-4 leading-7 text-slate-600">{section.body}</p>
            </section>
          ))}
        </div>

        <aside className="h-fit rounded-md border border-white/80 bg-white/75 p-5 shadow-lg shadow-violet-100/40 backdrop-blur">
          <div className="flex items-center gap-2 text-sm font-semibold text-slate-950">
            <TrendingUp className="size-4 text-sky-500" aria-hidden="true" />
            Research status
          </div>
          <dl className="mt-5 grid gap-4 text-sm">
            <div className="flex items-center justify-between gap-4 border-b border-violet-100 pb-4">
              <dt className="text-slate-500">Status</dt>
              <dd className="font-medium capitalize text-slate-950">
                {report.status}
              </dd>
            </div>
            <div className="flex items-center justify-between gap-4 border-b border-violet-100 pb-4">
              <dt className="text-slate-500">Created</dt>
              <dd className="font-medium text-slate-950">
                {new Date(report.createdAt).toLocaleDateString()}
              </dd>
            </div>
            <div className="flex items-center justify-between gap-4">
              <dt className="text-slate-500">Sections</dt>
              <dd className="font-medium text-slate-950">
                {report.sections.length}
              </dd>
            </div>
          </dl>
        </aside>
      </div>
    </article>
  );
}
