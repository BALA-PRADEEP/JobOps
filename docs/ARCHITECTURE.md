# JobOps Architecture

The canonical coding/dependency structure is defined in `CODING_STRUCTURE.md`.

## Runtime flow

```text
Hourly discovery
  -> JobSourceProvider
  -> JobIngestionService
  -> freshness + duplicate policy
  -> JobAnalysisService
  -> ResumeSelectionService
  -> repositories + event log
  -> ApplicationPreparationService
  -> ApplicationExecutionService
  -> ATSAdapterRegistry
  -> provider adapter
  -> BrowserRun + application events
```

## Trust boundaries

- LLMs may later extract/classify requirements or draft narrative text.
- Deterministic code owns freshness, dedupe, hard stops, score thresholds, protected fields, state transitions, and submission eligibility.
- Unknown personal facts are never inferred.
- Browser automation stops on CAPTCHA, unexpected authentication, or unsupported anti-automation barriers.
- `SUBMITTED` is recorded only after confirmation evidence is captured.
