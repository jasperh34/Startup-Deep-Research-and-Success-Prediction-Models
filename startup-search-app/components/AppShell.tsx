import Link from "next/link";
import { Clock, FileSearch, Search } from "lucide-react";

const navItems = [
  { href: "/search", label: "Search", icon: Search },
  { href: "/history", label: "History", icon: Clock },
];

export function AppShell({ children }: Readonly<{ children: React.ReactNode }>) {
  return (
    <main className="min-h-screen bg-[radial-gradient(circle_at_12%_12%,rgba(186,230,253,0.75),transparent_30%),radial-gradient(circle_at_88%_0%,rgba(221,214,254,0.85),transparent_32%),linear-gradient(135deg,#ffffff_0%,#f8fbff_46%,#f5f3ff_100%)] text-slate-950">
      <header className="sticky top-0 z-10 border-b border-white/70 bg-white/75 backdrop-blur-xl">
        <div className="mx-auto flex min-h-16 w-full max-w-6xl items-center justify-between gap-4 px-6 sm:px-8">
          <Link href="/" className="flex items-center gap-2 font-semibold">
            <span className="flex size-9 items-center justify-center rounded-md bg-gradient-to-br from-violet-600 to-sky-500 text-white shadow-lg shadow-violet-200">
              <FileSearch className="size-4" aria-hidden="true" />
            </span>
            <span>Jasper Startup Search</span>
          </Link>
          <nav className="flex items-center gap-1">
            {navItems.map((item) => (
              <Link
                key={item.href}
                href={item.href}
                className="inline-flex min-h-10 items-center gap-2 rounded-md px-3 text-sm font-medium text-slate-600 transition hover:bg-white/80 hover:text-slate-950 hover:shadow-sm"
              >
                <item.icon className="size-4" aria-hidden="true" />
                {item.label}
              </Link>
            ))}
          </nav>
        </div>
      </header>
      <div className="mx-auto w-full max-w-6xl px-6 py-10 sm:px-8">
        {children}
      </div>
    </main>
  );
}
