import { AppShell } from "@/components/AppShell";
import { CompanySearchForm } from "@/components/CompanySearchForm";

export default function SearchPage() {
  return (
    <AppShell>
      <div className="grid gap-8 lg:grid-cols-[0.9fr_1.1fr] lg:items-start">
        <div className="max-w-xl">
          <p className="text-sm font-medium uppercase tracking-[0.14em] text-violet-700">
            Company lookup
          </p>
          <h1 className="mt-3 text-4xl font-semibold leading-tight text-slate-950">
            Search for a company
          </h1>
          <p className="mt-4 text-lg leading-8 text-slate-600">
            Enter a startup or company name. We will search for likely matches
            and ask you to confirm before creating a research report.
          </p>
        </div>

        <div className="rounded-md border border-white/80 bg-white/75 p-6 shadow-xl shadow-violet-100/60 backdrop-blur-xl">
          <div className="mb-5">
            <h2 className="text-lg font-semibold text-slate-950">
              New research brief
            </h2>
            <p className="mt-1 text-sm leading-6 text-slate-500">
              Best for company names, product names, and startup domains.
            </p>
          </div>
          <CompanySearchForm variant="glass" />
        </div>
      </div>
    </AppShell>
  );
}
