# JobOps Product Objective

## Single overall objective

Use the existing scheduled job watch to automatically move strong, fresh jobs toward completed applications with minimal manual work.

```text
Scheduled job search
       ↓
Fresh matching jobs
       ↓
JobOps
       ↓
Evaluate
       ↓
Resolve where the real application lives
       ↓
Prepare
       ↓
Apply safely
       ↓
Verify
       ↓
Track outcome
```

## What the user should eventually experience

The normal path should require no action:

```text
Hourly run
  14 jobs found
   4 strong matches
   3 applications prepared
   2 submitted safely
   1 needs one verified answer
```

The exception path asks only for missing facts that belong to the candidate, such as:
- expected salary;
- notice period;
- sponsorship/work authorization;
- relocation;
- legal declarations;
- demographic/self-identification fields;
- company-specific narrative answers when human review is required.

Once a reusable candidate fact is explicitly verified, JobOps can reuse it according to policy.

## Job sources are not application systems

A job may be found on LinkedIn but applied to on a completely different system.

JobOps therefore models:

```text
discovery_url
  LinkedIn / Wellfound / YC / company index

canonical_job_url
  official company job page

application_url
  actual application form / ATS destination
```

The application adapter is selected from the application URL, not the discovery URL.

## Generic execution model

```text
JobOps
  -> ATSAdapter
      -> Greenhouse
      -> Lever
      -> Ashby
      -> Workday
      -> LinkedIn
      -> GenericCompanyForm
```

Only adapters understand provider DOM/API details.

## Non-goals

JobOps must not:
- blindly apply to every listing;
- invent candidate experience or personal facts;
- bypass CAPTCHA or security controls;
- submit the same role twice;
- treat a reindexed/reposted duplicate as a new opportunity;
- put provider-specific code inside core services;
- depend on paid infrastructure before free limits are genuinely insufficient.
