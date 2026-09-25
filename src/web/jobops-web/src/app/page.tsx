import { getDashboard } from "@/services/jobops-service";
import type { Job } from "@/types/jobops";

const stages = ["Discover", "Resolve", "Score", "Prepare", "Execute", "Outcome"];

function stateLabel(value: string) {
  return value.toLowerCase().replaceAll("_", " ");
}

function stageForJob(job: Job) {
  if (job.applicationState === "SUBMITTED") return 5;
  if (job.applicationState === "READY_FOR_REVIEW") return 4;
  if (job.applicationState === "NEEDS_INPUT") return 3;
  if (job.atsType.toLowerCase().includes("pending")) return 1;
  return 2;
}

function stageNote(job: Job) {
  if (job.applicationState === "SUBMITTED") return "Confirmed";
  if (job.applicationState === "READY_FOR_REVIEW") return "Ready";
  if (job.applicationState === "NEEDS_INPUT") return "Human input";
  if (job.atsType.toLowerCase().includes("pending")) return "Finding ATS";
  if (job.applicationState === "SKIPPED") return "Stopped";
  return "Qualified";
}

export default async function DashboardPage() {
  const data = await getDashboard();
  const interventions = data.applications.flatMap((application) => [
    ...application.protectedFields.map((field) => ({
      application,
      field,
      type: "Protected fact"
    })),
    ...application.unknownFields.map((field) => ({
      application,
      field,
      type: "Needs answer"
    }))
  ]);
  const interventionCount = interventions.length;
  const activeJobs = data.jobs.filter((job) => job.applicationState !== "SKIPPED");

  return (
    <div className="ops-page" id="top">
      <header className="masthead">
        <a className="wordmark" href="#top" aria-label="JobOps home">
          <span className="wordmark-mark">J/O</span>
          <span>JobOps</span>
        </a>

        <div className="watch-status">
          <span className="signal-dot" aria-hidden="true" />
          <span>Bengaluru watch</span>
          <span className="muted">hourly</span>
        </div>

        <nav className="top-nav" aria-label="Primary">
          <a href="#pipeline">Pipeline</a>
          <a href="#queue">Queue</a>
          <a href="#system">System</a>
        </nav>

        <div className="run-mode">
          <span>{data.dataSource === "live" ? "Live feed" : "Demo feed"}</span>
          <strong>Submit off</strong>
        </div>
      </header>

      <section className="command-hero" aria-labelledby="page-title">
        <div className="hero-copy">
          <p className="micro-label">Application operations / 24h window</p>
          <h1 id="page-title">
            Applications,
            <span>in motion.</span>
          </h1>
          <p className="hero-summary">
            JobOps turns fresh jobs into verified application runs. The system moves on its own
            until it reaches a decision that belongs to you.
          </p>

          <div className="hero-metrics" aria-label="Current pipeline metrics">
            <div>
              <strong>{data.stats.found.toString().padStart(2, "0")}</strong>
              <span>found</span>
            </div>
            <div>
              <strong>{data.stats.strongMatches.toString().padStart(2, "0")}</strong>
              <span>strong</span>
            </div>
            <div>
              <strong>{activeJobs.length.toString().padStart(2, "0")}</strong>
              <span>in motion</span>
            </div>
          </div>
        </div>

        <aside className="human-interrupt" aria-label="Human intervention status">
          <div className="interrupt-topline">
            <span>Human intervention</span>
            <span className="interrupt-index">01</span>
          </div>

          <div className="interrupt-count">
            <strong>{interventionCount.toString().padStart(2, "0")}</strong>
            <span>{interventionCount === 1 ? "decision needs you" : "decisions need you"}</span>
          </div>

          {interventions.length ? (
            <div className="interrupt-preview">
              {interventions.slice(0, 3).map(({ application, field, type }) => (
                <a href="#applications" key={`${application.id}-${field}`}>
                  <span>{type}</span>
                  <strong>{field}</strong>
                  <small>{application.company}</small>
                </a>
              ))}
            </div>
          ) : (
            <p className="interrupt-clear">
              Nothing is waiting on you. JobOps can continue through the current safe path.
            </p>
          )}
        </aside>
      </section>

      <section className="runway" id="pipeline" aria-labelledby="pipeline-title">
        <div className="runway-head">
          <div>
            <p className="micro-label light">Live application runway</p>
            <h2 id="pipeline-title">Where every job is now.</h2>
          </div>
          <div className="runway-legend" aria-label="Pipeline legend">
            <span><i className="legend-done" /> passed</span>
            <span><i className="legend-now" /> current</span>
            <span><i className="legend-human" /> needs you</span>
          </div>
        </div>

        {data.jobs.length ? (
          <div className="runway-table">
            <div className="runway-stage-row" aria-hidden="true">
              <div className="runway-spacer">Role / state</div>
              {stages.map((stage, index) => (
                <div key={stage}>
                  <span>{String(index + 1).padStart(2, "0")}</span>
                  {stage}
                </div>
              ))}
            </div>

            {data.jobs.map((job) => {
              const currentStage = stageForJob(job);
              const needsHuman = job.applicationState === "NEEDS_INPUT";
              return (
                <a
                  className={`runway-row ${needsHuman ? "needs-human" : ""}`}
                  href={`#job-${job.id}`}
                  key={job.id}
                >
                  <div className="runway-job">
                    <strong>{job.title}</strong>
                    <span>{job.company}</span>
                    <small>{stageNote(job)}</small>
                  </div>

                  {stages.map((stage, index) => {
                    const isCurrent = index === currentStage;
                    const isDone = index < currentStage;
                    return (
                      <div
                        className={[
                          "runway-cell",
                          isDone ? "is-done" : "",
                          isCurrent ? "is-current" : "",
                          isCurrent && needsHuman ? "is-human" : ""
                        ].filter(Boolean).join(" ")}
                        key={stage}
                      >
                        <span className="track-line" />
                        {isCurrent ? (
                          <span className="stage-marker">
                            <b>{job.score || "—"}</b>
                            <em>{needsHuman ? "YOU" : job.atsType}</em>
                          </span>
                        ) : null}
                      </div>
                    );
                  })}
                </a>
              );
            })}
          </div>
        ) : (
          <div className="runway-empty">
            <span>00</span>
            <p>No jobs are in motion. The next verified hourly discovery will appear here.</p>
          </div>
        )}
      </section>

      <section className="workbench" id="queue">
        <div className="queue-column">
          <div className="section-heading">
            <div>
              <p className="micro-label">Fresh queue</p>
              <h2>What JobOps is considering.</h2>
            </div>
            <p>Preferred under 24h · hard stop after 48h</p>
          </div>

          <div className="queue-list">
            {data.jobs.map((job) => (
              <article className="queue-row" id={`job-${job.id}`} key={job.id}>
                <div className="queue-index">{String(job.id).padStart(2, "0")}</div>
                <div className="queue-role">
                  <span>{job.company}</span>
                  <h3>{job.title}</h3>
                  <p>{job.location} · {job.postedLabel} · {job.source}</p>
                </div>
                <div className="queue-meta">
                  <span>ATS</span>
                  <strong>{job.atsType}</strong>
                  <small>{job.resumeKey.replaceAll("_", " ")}</small>
                </div>
                <div className="queue-score">
                  <strong>{job.score || "—"}</strong>
                  <span>{job.classification.replaceAll("_", " ")}</span>
                  <div className="score-track" aria-hidden="true">
                    <i style={{ width: `${job.score}%` }} />
                  </div>
                </div>
              </article>
            ))}
          </div>
        </div>

        <aside className="decision-column" id="applications">
          <div className="decision-heading">
            <p className="micro-label light">Intervention desk</p>
            <h2>Only when the machine should stop.</h2>
            <p>
              JobOps never guesses candidate-owned facts. These are the exact decisions preventing
              the current run from moving forward.
            </p>
          </div>

          {data.applications.length ? (
            data.applications.map((application) => (
              <div className="decision-case" key={application.id}>
                <div className="decision-case-head">
                  <span>{application.company}</span>
                  <strong>{application.role}</strong>
                  <small>{stateLabel(application.state)}</small>
                </div>

                <div className="field-progress">
                  <div>
                    <span>Form</span>
                    <strong>{application.fieldsFilled}/{application.fieldsDetected}</strong>
                  </div>
                  <div className="field-bar" aria-hidden="true">
                    <i
                      style={{
                        width: `${application.fieldsDetected
                          ? Math.round((application.fieldsFilled / application.fieldsDetected) * 100)
                          : 0}%`
                      }}
                    />
                  </div>
                </div>

                {[...application.protectedFields, ...application.unknownFields].map((field) => (
                  <div className="decision-field" key={field}>
                    <span>
                      {application.protectedFields.includes(field) ? "Protected" : "Unknown"}
                    </span>
                    <strong>{field}</strong>
                    <em>waiting</em>
                  </div>
                ))}

                <div className="submit-proof">
                  <span>Submit clicked</span>
                  <strong>{application.submitClicked ? "YES" : "NO"}</strong>
                </div>
              </div>
            ))
          ) : (
            <div className="decision-empty">
              <strong>Clear.</strong>
              <span>No application currently needs a human decision.</span>
            </div>
          )}
        </aside>
      </section>

      <section className="system-strip" id="system" aria-labelledby="system-title">
        <div className="system-title">
          <p className="micro-label">System contract</p>
          <h2 id="system-title">Automation with hard edges.</h2>
        </div>

        <div className="system-rule">
          <span>01</span>
          <strong>Verified facts only</strong>
          <p>Salary, notice period, authorization and declarations stop when unknown.</p>
        </div>

        <div className="system-rule">
          <span>02</span>
          <strong>Dry-run before action</strong>
          <p>Forms are inspected, filled and evidenced before submission is ever allowed.</p>
        </div>

        <div className="system-rule">
          <span>03</span>
          <strong>Provider isolation</strong>
          <p>ATS-specific behavior stays behind adapters; core JobOps logic stays deterministic.</p>
        </div>
      </section>

      <footer className="ops-footer">
        <span>JOBOPS / APPLICATION OPERATIONS</span>
        <span>{data.dataSource === "live" ? "CONNECTED" : "DEMO DATA"}</span>
        <span>AUTO-SUBMIT OFF</span>
      </footer>
    </div>
  );
}
