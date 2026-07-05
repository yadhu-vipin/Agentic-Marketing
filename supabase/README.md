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

- The backend (`marketing_agent`) uses the `campaign_states` table via SQLAlchemy.
  That table is auto-created by the Python ORM on startup, but is also defined
  in `schema.sql` for completeness.
- The frontend (`apps/web`) uses the `products`, `campaigns`, and `campaign_assets`
  tables via the Supabase JS client.
