"use client";

import { FormEvent, useState } from "react";
import { useRouter } from "next/navigation";
import { AlertCircle, Loader2, Search } from "lucide-react";
import type { CompanySearchResponse } from "@/types/api";

export function CompanySearchForm({
  variant = "light",
}: Readonly<{ variant?: "light" | "glass" }>) {
  const router = useRouter();
  const [query, setQuery] = useState("");
  const [isSearching, setIsSearching] = useState(false);
  const [error, setError] = useState<string | null>(null);

  async function handleSubmit(event: FormEvent<HTMLFormElement>) {
    event.preventDefault();
    setError(null);
    setIsSearching(true);

    try {
      const response = await fetch("/api/company-search", {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({ query }),
      });

      const payload = await response.json();

      if (!response.ok) {
        throw new Error(payload.error ?? "Search failed.");
      }

      const data = payload as CompanySearchResponse;
      window.sessionStorage.setItem(
        "startup-search:last-search",
        JSON.stringify(data),
      );
      router.push("/clarify");
    } catch (searchError) {
      setError(
        searchError instanceof Error
          ? searchError.message
          : "Something went wrong.",
      );
    } finally {
      setIsSearching(false);
    }
  }

  return (
    <section className="w-full max-w-3xl">
      <form
        onSubmit={handleSubmit}
        className={
          variant === "glass"
            ? "flex flex-col gap-3 rounded-md border border-white/80 bg-white/70 p-2 shadow-lg shadow-violet-100/60 backdrop-blur sm:flex-row"
            : "flex flex-col gap-3 rounded-md border border-white/80 bg-white/80 p-2 shadow-sm shadow-violet-100/50 backdrop-blur sm:flex-row"
        }
      >
        <div className="relative flex-1">
          <label className="sr-only" htmlFor="company-name">
            Company name
          </label>
          <Search
            className={`pointer-events-none absolute left-4 top-1/2 size-4 -translate-y-1/2 ${
              variant === "glass" ? "text-sky-500" : "text-slate-400"
            }`}
            aria-hidden="true"
          />
          <input
            id="company-name"
            type="search"
            value={query}
            onChange={(event) => setQuery(event.target.value)}
            placeholder="Enter a company name"
            className={
              variant === "glass"
                ? "min-h-12 w-full rounded-md border border-transparent bg-white/70 px-10 text-base text-slate-950 outline-none transition placeholder:text-slate-400 focus:bg-white focus:ring-4 focus:ring-sky-200/70"
                : "min-h-12 w-full rounded-md border border-transparent bg-white/70 px-10 text-base text-slate-950 outline-none transition placeholder:text-slate-400 focus:bg-white focus:ring-4 focus:ring-violet-100"
            }
          />
        </div>
        <button
          type="submit"
          disabled={isSearching}
          className={
            variant === "glass"
              ? "inline-flex min-h-12 items-center justify-center gap-2 rounded-md bg-gradient-to-r from-violet-600 to-sky-500 px-5 text-sm font-semibold text-white shadow-lg shadow-violet-200 transition hover:-translate-y-0.5 hover:shadow-sky-200 disabled:cursor-not-allowed disabled:from-slate-300 disabled:to-slate-300 disabled:text-slate-500 disabled:shadow-none"
              : "inline-flex min-h-12 items-center justify-center gap-2 rounded-md bg-gradient-to-r from-violet-600 to-sky-500 px-5 text-sm font-semibold text-white shadow-sm shadow-violet-200 transition hover:-translate-y-0.5 hover:shadow-md disabled:cursor-not-allowed disabled:from-slate-300 disabled:to-slate-300 disabled:text-slate-500"
          }
        >
          {isSearching ? (
            <Loader2 className="size-4 animate-spin" aria-hidden="true" />
          ) : (
            <Search className="size-4" aria-hidden="true" />
          )}
          Search
        </button>
      </form>

      {error ? (
        <p className="mt-4 inline-flex items-center gap-2 rounded-md border border-red-200 bg-red-50 px-3 py-2 text-sm font-medium text-red-700">
          <AlertCircle className="size-4" aria-hidden="true" />
          {error}
        </p>
      ) : null}
    </section>
  );
}
