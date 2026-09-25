# JobOps Current Status

## Overall progress

The system is past the architecture-only stage, but it is not yet a fully live auto-application product.

| Area | Status |
| --- | --- |
| GMS-style architecture | Done |
| Candidate profile boundary | Done |
| Freshness policy | Done |
| Deduplication foundation | Done |
| Fit scoring | Done |
| Resume selection | Done |
| Application state machine | Done |
| Discovery/application URL separation | Done |
| Scheduled job intake API | Done |
| Greenhouse dry-run adapter | Done |
| Protected-field / CAPTCHA blocking | Done |
| Execution trace | Done |
| Execution queue | Done |
| Hourly GitHub Actions browser worker | Done |
| JobOps control-room UI | Done |
| Neon production database | Waiting for project connection |
| Vercel live API | Ready after Neon |
| Vercel web -> live API | Ready after API URL |
| Scheduled Job Watch -> intake | Next integration |
| Automatic URL resolver | Next implementation |
| Lever | Not started |
| Ashby | Not started |
| Auto-submit | Deliberately disabled |

## Current execution flow

```text
Job discovery data
  -> /v1/jobs/intake
  -> PENDING resolver state
  -> /v1/jobs/{id}/resolve
  -> scoring + resume selection
  -> /v1/jobs/{id}/dry-run
  -> QUEUED execution request
  -> hourly GitHub Actions worker
  -> Playwright ATS adapter
  -> BrowserRun + trace
  -> READY_FOR_REVIEW / NEEDS_INPUT
```

## What is left before the first live automatic run

1. Create/connect the Neon Free project.
2. Run Alembic migrations.
3. Configure the API with the Neon connection string and private candidate profile secret.
4. Deploy the API.
5. Point the web control room at the API.
6. Connect the scheduled job watch to `POST /v1/jobs/intake`.
7. Resolve a real job to its official application destination.
8. Queue and execute the first real dry-run.
