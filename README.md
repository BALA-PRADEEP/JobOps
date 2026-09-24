# JobOps

JobOps is a production-oriented job discovery, fit-analysis, application preparation, browser automation, and application tracking system.

## Architecture direction

The repository follows the same high-level separation as the layered application architecture used as the structural reference:

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

The important rule is architectural, not cosmetic:

```text
Web UI
  -> JobOps HTTP service client
  -> API boundary
  -> application service
  -> repositories / provider interfaces
  -> ATS or job-source provider
```

Provider-specific behavior never leaks into UI, persistence, or core scoring logic.

See `docs/CODING_STRUCTURE.md` for the detailed dependency rules and extension model.

## Current milestone

The current branch restructures the MVP into the long-term code organization before adding more automation.

Implemented:
- verified candidate source of truth with unknown personal facts preserved as null;
- strict freshness policy: prefer <24h, reject >48h;
- deterministic explainable fit scoring;
- resume selection;
- job/application persistence and event history;
- centralized application state machine;
- versioned FastAPI endpoints;
- Greenhouse dry-run adapter behind a generic ATS interface;
- browser-run persistence model;
- protected-field blocking;
- web client isolated under `src/web/jobops-web`;
- unit, integration, and browser tests.

Intentionally not enabled yet:
- automatic submission;
- CAPTCHA bypass;
- Lever/Ashby execution adapters;
- live job-source ingestion;
- LLM-generated answers affecting eligibility or state transitions.

## Run backend

```bash
make api
```

Open `http://127.0.0.1:8000/docs`.

## Run web

```bash
cd src/web/jobops-web
npm install
npm run dev
```

## Run tests

```bash
make test
```

## Core correctness rules

- Unknown personal facts are never inferred.
- Browser automation stops on CAPTCHA or unsupported authentication barriers.
- Provider-specific DOM/API behavior stays in `externalService` adapters.
- API routes stay thin.
- Services own workflows and state transitions.
- DAL owns persistence only.
- `SUBMITTED` will only be recorded after confirmation evidence exists.
