# Supabase — Database Schema & Migrations

This directory is the **single source of truth** for the database schema used by
both the Next.js frontend and the FastAPI backend.

## Files

| File | Purpose |
|:---|:---|
| `schema.sql` | Authoritative DDL — run once in the Supabase SQL editor to bootstrap a new project |
| `migrations/` | Incremental migration scripts (chronological) |

## Setup

1. Create a Supabase project at https://supabase.com.
2. Open the SQL editor and run `schema.sql`.
3. The script creates all tables, indexes, RLS policies, and the storage bucket.

## Notes

- The frontend (`apps/web`) and backend (`marketing_agent`) both use the `products`, `campaigns`, and `campaign_assets` tables as their source of truth.
