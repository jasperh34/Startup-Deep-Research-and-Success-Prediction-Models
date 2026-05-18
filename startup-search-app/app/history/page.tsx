import { AppShell } from "@/components/AppShell";
import { HistoryList } from "@/components/HistoryList";

export default function HistoryPage() {
  return (
    <AppShell>
      <div className="flex flex-col gap-4 border-b border-white/70 pb-8 sm:flex-row sm:items-end sm:justify-between">
        <div className="max-w-3xl">
          <p className="text-sm font-medium uppercase tracking-[0.14em] text-violet-700">
            Saved reports
          </p>
          <h1 className="mt-3 text-4xl font-semibold text-slate-950">
            History
          </h1>
          <p className="mt-4 text-lg leading-8 text-slate-600">
            Review previously generated briefs and continue research from your
            saved report list.
          </p>
        </div>
      </div>

      <div className="mt-8">
        <HistoryList />
      </div>
    </AppShell>
  );
}
