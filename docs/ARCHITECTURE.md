# JobOps Architecture

The canonical coding/dependency structure is defined in `CODING_STRUCTURE.md`.

## Runtime flow

```text
Hourly discovery
  -> Job Watch / JobSourceProvider
  -> POST /v1/jobs/intake
  -> JobIntakeService
  -> persist discovery URL separately
  -> Job resolver
  -> POST /v1/jobs/{id}/resolve
  -> canonical job URL + actual application URL
  -> ATS detection
  -> JobAnalysisService
  -> ResumeSelectionService
  -> ApplicationPreparationService
  -> ApplicationExecutionService
  -> ATSAdapterRegistry
  -> provider adapter
  -> BrowserRun + application events
```

## URL model

A discovered job has three different URL concepts:

- `discovery_url`: where JobOps found it, such as LinkedIn or Wellfound.
- `canonical_job_url`: the official company job page when available.
- `application_url`: the actual form or ATS destination used for execution.

The discovery URL must never be assumed to be the application form.

## Trust boundaries

- LLMs may later extract/classify requirements or draft narrative text.
- Deterministic code owns freshness, dedupe, hard stops, score thresholds, protected fields, state transitions, and submission eligibility.
- Unknown personal facts are never inferred.
- Browser automation stops on CAPTCHA, unexpected authentication, or unsupported anti-automation barriers.
- `SUBMITTED` is recorded only after confirmation evidence is captured.
