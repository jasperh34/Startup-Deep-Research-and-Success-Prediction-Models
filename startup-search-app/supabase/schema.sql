create extension if not exists pgcrypto;

create table if not exists public.companies (
  id uuid primary key default gen_random_uuid(),
  name text not null,
  website text,
  description text not null default '',
  location text,
  metadata jsonb not null default '{}'::jsonb,
  selected_by_user boolean not null default false,
  created_at timestamptz not null default now()
);

create index if not exists companies_name_idx on public.companies (lower(name));
create index if not exists companies_website_idx on public.companies (website);

alter table public.companies
  add column if not exists metadata jsonb not null default '{}'::jsonb;

create table if not exists public.sources (
  id uuid primary key default gen_random_uuid(),
  company_id uuid not null references public.companies(id) on delete cascade,
  url text not null,
  title text not null,
  snippet text not null default '',
  source_type text not null default 'other',
  retrieved_at timestamptz not null default now(),
  unique (company_id, url)
);

create index if not exists sources_company_id_idx on public.sources (company_id);
create index if not exists sources_source_type_idx on public.sources (source_type);

create table if not exists public.reports (
  id uuid primary key default gen_random_uuid(),
  company_id uuid references public.companies(id) on delete cascade,
  user_id uuid references auth.users(id) on delete cascade,
  company_name text not null,
  website text,
  status text not null default 'draft',
  structured_json jsonb,
  summary text not null,
  report jsonb not null,
  created_at timestamptz not null default now(),
  updated_at timestamptz not null default now()
);

alter table public.reports add column if not exists company_id uuid references public.companies(id) on delete cascade;
alter table public.reports add column if not exists structured_json jsonb;

alter table public.companies enable row level security;
alter table public.sources enable row level security;
alter table public.reports enable row level security;

drop policy if exists "Users can read their own companies" on public.companies;
drop policy if exists "Users can insert their own companies" on public.companies;
drop policy if exists "Users can update their own companies" on public.companies;
drop policy if exists "Users can read sources through own reports" on public.sources;
drop policy if exists "Users can insert sources through own reports" on public.sources;
drop policy if exists "Users can read their own reports" on public.reports;
drop policy if exists "Users can insert their own reports" on public.reports;
drop policy if exists "Users can update their own reports" on public.reports;

create policy "Users can read their own companies"
  on public.companies
  for select
  using (
    exists (
      select 1
      from public.reports
      where reports.company_id = companies.id
        and reports.user_id = auth.uid()
    )
  );

create policy "Users can insert their own companies"
  on public.companies
  for insert
  with check (true);

create policy "Users can update their own companies"
  on public.companies
  for update
  using (true)
  with check (true);

create policy "Users can read sources through own reports"
  on public.sources
  for select
  using (
    exists (
      select 1
      from public.reports
      where reports.company_id = sources.company_id
        and reports.user_id = auth.uid()
    )
  );

create policy "Users can insert sources through own reports"
  on public.sources
  for insert
  with check (true);

create policy "Users can read their own reports"
  on public.reports
  for select
  using (auth.uid() = user_id or user_id is null);

create policy "Users can insert their own reports"
  on public.reports
  for insert
  with check (auth.uid() = user_id or user_id is null);

create policy "Users can update their own reports"
  on public.reports
  for update
  using (auth.uid() = user_id or user_id is null)
  with check (auth.uid() = user_id or user_id is null);
