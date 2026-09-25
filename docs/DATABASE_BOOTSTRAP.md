# JobOps Neon Database Bootstrap

## Dedicated resource

JobOps uses only the dedicated Neon project:

- Project: `JobOps-database`
- Project ID: `autumn-mouse-60910256`

No connection string from another project may be used.

## Fail-closed bootstrap

The database bootstrap checks the target before running Alembic.

Allowed pre-migration states:

1. no public application tables — fresh database;
2. only known JobOps tables — safe rerun.

If any unrelated table is present, bootstrap stops before applying migrations.

Known JobOps tables:

- `jobs`
- `job_scores`
- `applications`
- `application_events`
- `browser_runs`
- `execution_requests`
- `alembic_version`

## Secret

The production connection string is never committed.

Repository secret:

```text
JOBOPS_DATABASE_URL
```

The value must come specifically from the `JobOps-database` Neon project.

## Bootstrap

Run the GitHub Actions workflow:

```text
JobOps Database Bootstrap
```

It performs:

```text
validate Neon host
  -> inspect existing public tables
  -> fail if unrelated tables exist
  -> alembic upgrade head
  -> verify expected tables
  -> verify revision 0003_execution_queue
```

The scheduled application worker uses the same `JOBOPS_DATABASE_URL` secret after bootstrap succeeds.
