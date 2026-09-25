# JobOps Roadmap

## Phase 0 — Foundation
Status: complete

- GMS-aligned structure
- candidate truth boundary
- DB migrations
- state machine
- audit events
- tests

## Phase 1 — Job intelligence
Status: complete for core

- freshness
- dedupe identity
- deterministic fit scoring
- resume selection
- ATS detection

## Phase 2 — Application dry-run
Status: complete for Greenhouse

- field scanning
- verified-value fill
- resume upload
- protected-field detection
- CAPTCHA stop
- screenshot/trace
- no Submit

## Phase 3 — Discovery to execution bridge
Status: in progress

- scheduled-job intake: complete
- discovery/canonical/application URL separation: complete
- queued execution: complete
- free hourly worker: complete
- automatic application-URL resolver: next
- connect scheduled ChatGPT Job Watch: next

## Phase 4 — Live free infrastructure
Status: in progress

- Neon Free database: waiting for project connection
- Vercel FastAPI API: ready after database
- Vercel web control room: code ready
- runtime candidate secrets: supported
- worker secrets: workflow ready

## Phase 5 — Provider coverage

- Lever
- Ashby
- generic company forms
- Workday investigation
- LinkedIn application-path investigation

## Phase 6 — Controlled submission

Only after repeated successful dry-runs:
- verified-answer gate
- explicit submission policy
- no blind retry of Submit
- confirmation evidence
- duplicate-submit protection
- allowlisted auto-submit

## Phase 7 — Feedback loop

- interview/rejection/offer tracking
- callback rate by role/source/resume
- scoring configuration versions
- recommendations for threshold changes
- hard rules remain deterministic
