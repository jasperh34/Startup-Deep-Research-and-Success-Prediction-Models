import Link from "next/link";
import {
  ArrowRight,
  Clock,
  FileSearch,
  Search,
  Sparkles,
} from "lucide-react";
import { CompanySearchForm } from "@/components/CompanySearchForm";

export default function Home() {
  return (
    <main className="min-h-screen overflow-hidden bg-slate-50 text-slate-950">
      <div className="absolute inset-0 bg-[radial-gradient(circle_at_18%_18%,rgba(186,230,253,0.9),transparent_32%),radial-gradient(circle_at_78%_8%,rgba(221,214,254,0.95),transparent_34%),radial-gradient(circle_at_70%_78%,rgba(199,210,254,0.6),transparent_34%),linear-gradient(135deg,#ffffff_0%,#f8fbff_44%,#f5f3ff_100%)]" />
      <div className="absolute left-1/2 top-24 h-72 w-[44rem] -translate-x-1/2 rounded-full bg-white/70 blur-3xl" />

      <div className="relative mx-auto flex w-full max-w-6xl flex-col gap-14 px-6 py-8 sm:px-8">
        <nav className="flex min-h-12 items-center justify-between">
          <Link href="/" className="flex items-center gap-2 font-semibold">
            <span className="flex size-9 items-center justify-center rounded-md bg-gradient-to-br from-violet-600 to-sky-500 text-white shadow-lg shadow-violet-200">
              <FileSearch className="size-4" aria-hidden="true" />
            </span>
            <span>Jasper Startup Search</span>
          </Link>
          <div className="flex items-center gap-1">
            <Link
              href="/search"
              className="inline-flex min-h-10 items-center gap-2 rounded-md px-3 text-sm font-medium text-slate-600 transition hover:bg-white/80 hover:text-slate-950 hover:shadow-sm"
            >
              <Search className="size-4" aria-hidden="true" />
              Search
            </Link>
            <Link
              href="/history"
              className="inline-flex min-h-10 items-center gap-2 rounded-md px-3 text-sm font-medium text-slate-600 transition hover:bg-white/80 hover:text-slate-950 hover:shadow-sm"
            >
              <Clock className="size-4" aria-hidden="true" />
              History
            </Link>
          </div>
        </nav>

        <section className="grid min-h-[74vh] items-center gap-10 lg:grid-cols-[1.02fr_0.98fr]">
          <div>
            <p className="inline-flex min-h-8 items-center gap-2 rounded-md border border-white/70 bg-white/70 px-3 text-sm font-medium text-violet-700 shadow-sm shadow-violet-100 backdrop-blur">
              <Sparkles className="size-4 text-sky-500" aria-hidden="true" />
              AI-powered startup diligence
            </p>
            <h1 className="mt-6 max-w-3xl text-5xl font-semibold leading-tight tracking-normal text-slate-950 sm:text-6xl">
              Research startups with sharper context before you commit.
            </h1>
            <p className="mt-6 max-w-2xl text-lg leading-8 text-slate-600">
              Resolve ambiguous company names, collect source evidence, extract
              structured founder and funding data, and generate an
              investor-style brief.
            </p>
            <div className="mt-8 flex flex-col gap-3 sm:flex-row">
              <Link
                href="/search"
                className="group inline-flex min-h-12 items-center justify-center gap-2 rounded-md bg-gradient-to-r from-violet-600 to-sky-500 px-5 text-sm font-semibold text-white shadow-lg shadow-violet-200 transition hover:-translate-y-0.5 hover:shadow-xl hover:shadow-sky-200"
              >
                Start researching
                <ArrowRight
                  className="size-4 transition group-hover:translate-x-0.5"
                  aria-hidden="true"
                />
              </Link>
              <Link
                href="/history"
                className="inline-flex min-h-12 items-center justify-center rounded-md border border-white/80 bg-white/70 px-5 text-sm font-medium text-slate-700 shadow-sm backdrop-blur transition hover:-translate-y-0.5 hover:bg-white hover:text-slate-950"
              >
                View saved reports
              </Link>
            </div>
          </div>

          <div className="relative rounded-md border border-white/80 bg-white/75 p-6 shadow-2xl shadow-violet-200/50 backdrop-blur-xl">
            <div className="absolute -right-10 -top-10 size-32 rounded-full bg-sky-300/30 blur-3xl" />
            <div className="absolute -bottom-12 left-8 size-36 rounded-full bg-violet-300/30 blur-3xl" />
            <div className="relative mb-6 flex items-start justify-between gap-4">
              <div>
                <div className="flex items-center gap-2 text-sm font-medium text-violet-700">
                  <span className="size-2 rounded-full bg-sky-400 shadow-[0_0_18px_rgba(56,189,248,0.65)]" />
                  Search workspace
                </div>
                <h2 className="mt-3 text-2xl font-semibold text-slate-950">
                  Find the right company
                </h2>
              </div>
              <span className="rounded-md border border-sky-200 bg-sky-50 px-2.5 py-1 text-xs font-medium text-sky-700">
                Ready
              </span>
            </div>
            <div className="relative">
              <CompanySearchForm variant="glass" />
            </div>
          </div>
        </section>
      </div>
    </main>
  );
}
