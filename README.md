# Agentic Marketing

A social campaign generation product: upload product info and images, generate
ready-to-post content and creatives for Instagram, Facebook, and LinkedIn, then
publish or schedule to Meta platforms.

## Repository layout
```
apps/web/                 → Active MVP: Next.js social campaign studio
marketing_agent/          → Modular Python backend: FastAPI service with workflow orchestrator
supabase/                 → DB schema, migrations, and seed scripts (single source of truth)
docker/                   → Dockerfiles and docker-compose configurations
docs/                     → System documentation and guides
scripts/                  → Utility and automation scripts
AgenticMarketing_MVP Goal.pdf → Source spec for the current MVP
```

## Running the Web Frontend (apps/web)
See [`apps/web/README.md`](apps/web/README.md) for setup and usage.

```bash
cd apps/web
npm install
npm run dev    # http://localhost:3000
```

## Running the Backend API (marketing_agent)
```bash
source venv/bin/activate
pip install -e .
uvicorn marketing_agent.api.main:app --reload --port 8000
```

Flow: **Add product → Select platforms → Generate campaign → Review/edit →
Publish or schedule** (Instagram/Facebook via Meta Graph API).

## What this MVP intentionally does not include
Lead discovery, customer identification, automated DM outreach, lead scoring,
complex analytics, recommendation engines, ad budget optimization, and multi-agent
frameworks — these are out of scope per the MVP goal.
