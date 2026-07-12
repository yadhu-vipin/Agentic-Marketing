# Production Deployment Guide

This document describes how to deploy the **Agentic Marketing Lead Engine** to production.

## Architecture Overview
- **Frontend**: Next.js (Standalone build mode) deployed to **Vercel**.
- **Backend**: FastAPI web app (Chromium/Playwright scraping layer) deployed to **Railway** (runs via Docker container).
- **Database**: **Supabase** PostgreSQL database and PostgREST client API.

---

## 1. Database Setup (Supabase)

### A. Apply the Database Schema
Apply the authoritative schema file to your Supabase PostgreSQL instance:
1. Open the [Supabase Dashboard](https://supabase.com).
2. Go to the **SQL Editor** tab of your project.
3. Open the file `supabase/schema.sql`.
4. Copy the complete SQL statement and run it in the SQL Editor. This will create:
   - `public.products` (Product metadata and branding configs)
   - `public.campaigns` (Campaign details, platforms, and orchestrator inputs)
   - `public.campaign_assets` (Generated images, ad copy, and social media media records)

### B. Create the Storage Bucket
1. Open the Supabase Dashboard and navigate to the **Storage** tab.
2. Create a new public bucket named `product-assets` (or whatever value you configure in `SUPABASE_STORAGE_BUCKET`).
3. Ensure the bucket's access policies allow public reads (and authenticated/anonymous uploads depending on your auth scope).

---

## 2. Backend Deployment (Railway)

The backend is configured to build automatically via Docker.

### A. Deployment Configuration
The deployment configuration is defined in `railway.json`:
- Build Target: `docker/backend.Dockerfile`
- Liveness/Health Probe: `GET /health` (timeouts: 120s)
- Restart Policy: `ON_FAILURE`

### B. Required Environment Variables on Railway
Configure the following variables in the Railway service settings:

| Variable Name | Description | Example Value |
|---|---|---|
| `DATABASE_URL` | Supabase direct PostgreSQL connection string | `postgresql://postgres:[password]@db.ughladkskmwfgeadjhvt.supabase.co:5432/postgres` |
| `AI_PROVIDER` | AI provider for ad-copy and marketing content generation | `gemini` (or `openai` / `anthropic`) |
| `AI_PROVIDER_API_KEY` | API key for the AI provider | `AIzaSy...` (Gemini API key) |
| `AI_MODEL` | AI Model override (Optional) | `gemini-2.5-flash` |
| `CREATIVE_PROVIDER` | Ad-image generator provider | `pollinations` (free, no API key required) |
| `META_GRAPH_VERSION` | Version of Meta Graph API | `v21.0` |
| `META_ACCESS_TOKEN` | Meta page publishing access token | `EAAMj...` |
| `META_PAGE_ID` | Facebook page ID to publish onto | `1210131325510853` |
| `META_IG_USER_ID` | Instagram Business account user ID | `27447444248208916` |
| `INSTAGRAM_ACCESS_TOKEN`| Instagram access token | `IGAAO...` |

---

## 3. Frontend Deployment (Vercel)

Vercel compiles the frontend using Next.js standalone build optimizations.

### A. Deployment Configuration
The deployment configuration is defined in `apps/web/vercel.json`.
Set the **Root Directory** setting on Vercel to `apps/web`.

### B. Required Environment Variables on Vercel
Configure these variables in Vercel project settings:

| Variable Name | Description | Example Value |
|---|---|---|
| `NEXT_PUBLIC_SUPABASE_URL` | Supabase project HTTP gateway URL | `https://ughladkskmwfgeadjhvt.supabase.co` |
| `NEXT_PUBLIC_SUPABASE_ANON_KEY`| Supabase anon public API key | `sb_publishable_...` |
| `DATABASE_URL` | Supabase direct connection string (shared with Next.js API) | `postgresql://postgres:[password]@db...` |
| `BACKEND_API_URL` | Public HTTP URL of your deployed Railway Backend | `https://agentic-marketing-production.up.railway.app` |
| `NEXT_PUBLIC_APP_URL` | Public HTTP URL of your Vercel Frontend app | `https://agentic-marketing.vercel.app` |
| `SUPABASE_STORAGE_BUCKET` | Storage bucket name | `product-assets` |

---

## 4. End-to-End Local Verification (Docker Compose)

Verify the full stack locally:
```bash
# 1. Start the Docker containers using compose
docker compose --env-file .env -f docker/docker-compose.yml up --build

# 2. Access the frontend app
# Navigate to: http://localhost:3000

# 3. Access backend health checks
# Navigate to: http://localhost:8000/health
```
