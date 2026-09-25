# JobOps

JobOps is the execution system for the scheduled job search.

## Objective

The intended production flow is:

```text
Hourly Job Watch
  -> fresh jobs from the internet
  -> JobOps intake
  -> normalize + deduplicate
  -> verify freshness
  -> resolve official job/application URL
  -> score against the verified candidate profile
  -> choose the correct resume
  -> prepare answers
  -> execute the correct ATS adapter
  -> ask only when a required candidate-owned fact is unknown
  -> submit only when the application is safe
  -> verify the submission
  -> track Applied / Interview / Rejected / Offer
```

The goal is not a generic job board and not a blind mass-apply bot. The goal is to turn the existing scheduled job watch into a controlled, observable application pipeline.

## Coding rule

JobOps follows the GMS-style separation used as the structural reference:

```text
src/
  web/
    jobops-web/

  external-integrations/
    jobops-external-services/
      source/
        api/
        service/
        dal/
        dao/
        externalService/
        worker/
        schemas/
        Utils/
```

The architecture must stay generic:

```text
Web
 -> JobOps service client
 -> API
 -> application service
 -> repositories / provider interfaces
 -> ATS / job-source provider
```

Provider-specific Greenhouse/Lever/Ashby logic must not leak into scoring, persistence, candidate profile, or React components.

## Free-first runtime

Initial production runtime is intentionally free-tier friendly:

```text
Vercel Hobby
  -> Next.js control room

Vercel Hobby
  -> lightweight FastAPI API
  -> no Chromium/browser execution

Neon Free
  -> PostgreSQL system of record

GitHub Actions
  -> hourly Playwright application worker
  -> reads queued execution requests from Neon
  -> stores short-lived execution artifacts
```

This split prevents Playwright from running inside a serverless request and keeps the browser worker replaceable later.

## Current implementation

Implemented:
- GMS-aligned repository structure;
- deterministic freshness and fit scoring;
- verified candidate profile boundary;
- protected/unknown candidate-fact blocking;
- resume selection;
- application state machine and audit events;
- discovery URL vs canonical job URL vs application URL separation;
- scheduled-job intake endpoint;
- application URL resolution endpoint;
- Greenhouse dry-run adapter;
- CAPTCHA stop behavior;
- field-level execution traces;
- queued browser execution;
- hourly GitHub Actions worker;
- Next.js control room;
- SQLite local support and Alembic/PostgreSQL migrations.

Still to connect:
- Neon production project;
- Vercel API environment variables;
- Vercel web -> live API;
- hourly ChatGPT Job Watch -> JobOps intake;
- automatic application-URL resolver;
- Lever adapter;
- Ashby adapter;
- controlled submission and confirmation verification.

See:
- `docs/PRODUCT_OBJECTIVE.md`
- `docs/CURRENT_STATUS.md`
- `docs/CODING_STRUCTURE.md`
- `docs/FREE_RUNTIME.md`
- `docs/ROADMAP.md`

## Safety rules

- `JOBOPS_AUTO_SUBMIT=false` remains the default.
- Unknown candidate-owned facts are never guessed.
- Real candidate data and real resumes must not be committed to this public repository.
- CAPTCHA and unsupported authentication barriers stop automation.
- A dry-run never clicks Submit.
- `SUBMITTED` will only be recorded after confirmation evidence is captured.
