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

alter table public.reports
  add column if not exists company_id uuid references public.companies(id) on delete cascade;

alter table public.reports
  add column if not exists structured_json jsonb;

alter table public.companies enable row level security;
alter table public.sources enable row level security;
