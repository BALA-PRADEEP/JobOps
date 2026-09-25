# JobOps Free Runtime

## Why the runtime is split

Browser automation is resource-heavy and long-running compared with normal API requests. Running Playwright directly inside the web/API request path would make the system less reliable.

The free-first production topology is therefore:

```text
             ┌─────────────────────┐
             │ Vercel Next.js Web  │
             └──────────┬──────────┘
                        │
                        ↓
             ┌─────────────────────┐
             │ Vercel FastAPI API  │
             │ no browser runtime  │
             └──────────┬──────────┘
                        │
                        ↓
             ┌─────────────────────┐
             │ Neon PostgreSQL     │
             │ jobs + applications │
             │ execution queue     │
             └──────────┬──────────┘
                        │
                 hourly poll
                        ↓
             ┌─────────────────────┐
             │ GitHub Actions      │
             │ Playwright worker   │
             └──────────┬──────────┘
                        │
                        ↓
               Greenhouse / ATS
```

## API behavior

`POST /v1/jobs/{job_id}/dry-run` does not launch a browser.

It creates an `execution_requests` row:

```text
QUEUED
 -> RUNNING
 -> SUCCEEDED
 -> NEEDS_INPUT
 -> FAILED
```

The worker owns browser execution.

## Private data

The repository is public, therefore production candidate data is injected at runtime.

Expected secrets:
- `JOBOPS_DATABASE_URL`
- `JOBOPS_CANDIDATE_PROFILE_B64`
- `JOBOPS_PRODUCT_RESUME_B64`
- `JOBOPS_BACKEND_RESUME_B64`
- `JOBOPS_AI_RESUME_B64`

The committed profile is synthetic and exists only for development/tests.

## Cost policy

Use free tiers until an actual technical limitation appears.

Do not add a paid queue, always-on worker, paid database, or paid observability system merely for convenience.
