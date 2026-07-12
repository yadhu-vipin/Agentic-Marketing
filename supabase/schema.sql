-- Agentic Marketing — Social Campaign MVP schema
-- Run in the Supabase SQL editor. Enables RLS so each user sees only their rows.

create extension if not exists "pgcrypto";

-- ── Products ─────────────────────────────────────────────────────────────────
create table if not exists public.products (
  id uuid primary key default gen_random_uuid(),
  user_id uuid not null references auth.users (id) on delete cascade,
  name text not null,
  description text not null default '',
  features jsonb not null default '[]'::jsonb,
  target_audience text not null default '',
  industry text not null default '',
  logo_url text,
  image_urls jsonb not null default '[]'::jsonb,
  created_at timestamptz not null default now()
);

-- ── Campaigns ────────────────────────────────────────────────────────────────
create table if not exists public.campaigns (
  id uuid primary key default gen_random_uuid(),
  user_id uuid not null references auth.users (id) on delete cascade,
  product_id uuid not null references public.products (id) on delete cascade,
  product_name text not null default '',
  platforms jsonb not null default '[]'::jsonb,
  status text not null default 'draft',
  created_at timestamptz not null default now(),
  
  -- Workflow orchestration columns
  workflow text not null default 'organic_campaign',
  config jsonb not null default '{}'::jsonb,
  results jsonb not null default '{}'::jsonb
);

-- ── Campaign assets (per-platform content + creative + publish state) ─────────
create table if not exists public.campaign_assets (
  id uuid primary key default gen_random_uuid(),
  campaign_id uuid not null references public.campaigns (id) on delete cascade,
  platform text not null,
  headline text not null default '',
  body text not null default '',
  hashtags jsonb not null default '[]'::jsonb,
  cta text not null default '',
  creative_prompt text not null default '',
  creative_url text,
  status text not null default 'draft',
  scheduled_time timestamptz,
  external_id text,
  error text
);



create index if not exists products_user_idx on public.products (user_id);
create index if not exists campaigns_user_idx on public.campaigns (user_id);
create index if not exists assets_campaign_idx on public.campaign_assets (campaign_id);

-- ── Row level security ───────────────────────────────────────────────────────
alter table public.products enable row level security;
alter table public.campaigns enable row level security;
alter table public.campaign_assets enable row level security;

create policy "own products" on public.products
  for all using (auth.uid() = user_id) with check (auth.uid() = user_id);

create policy "own campaigns" on public.campaigns
  for all using (auth.uid() = user_id) with check (auth.uid() = user_id);

create policy "own campaign assets" on public.campaign_assets
  for all using (
    exists (
      select 1 from public.campaigns c
      where c.id = campaign_assets.campaign_id and c.user_id = auth.uid()
    )
  )
  with check (
    exists (
      select 1 from public.campaigns c
      where c.id = campaign_assets.campaign_id and c.user_id = auth.uid()
    )
  );


-- ── Storage bucket ───────────────────────────────────────────────────────────
-- Create a public bucket named 'product-assets' in Storage, or run:
insert into storage.buckets (id, name, public)
values ('product-assets', 'product-assets', true)
on conflict (id) do nothing;
