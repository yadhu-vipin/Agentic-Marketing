# Docker

Container definitions and orchestration for local development and deployment.

## Status

Dockerfiles and `docker-compose.yml` will be introduced in a later commit.
The current `Dockerfile` (repo root) and `docker-compose.yml` (repo root) are
legacy files that will be moved here and updated.

## Planned structure

```
docker/
  backend.Dockerfile       # FastAPI + Playwright
  frontend.Dockerfile      # Next.js production build
  docker-compose.yml       # Full-stack orchestration
```
