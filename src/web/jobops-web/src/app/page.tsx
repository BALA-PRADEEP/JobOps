import { getDashboard } from "@/services/jobops-service";

function stateLabel(value: string) {
  return value.toLowerCase().replaceAll("_", " ");
}

export default async function DashboardPage() {
  const data = await getDashboard();

  return (
    <div className="page" id="overview">
      <header className="hero">
        <div>
          <p className="eyebrow">JobOps / Overview</p>
          <h1>Application control room</h1>
          <p className="subtitle">
            Fresh jobs in, verified applications out. No blind submissions.
          </p>
        </div>
        <span className="mode">Auto-submit off</span>
      </header>

      <div className={`source ${data.dataSource === "live" ? "live" : ""}`}>
        <strong>{data.dataSource === "live" ? "Live API connected." : "Demo mode."}</strong>
        <span>
          {data.dataSource === "live"
            ? "The dashboard is reading from the JobOps backend."
            : "The UI is ready; cloud API and scheduled-job ingestion are not connected yet."}
        </span>
      </div>

      <section className="stats">
        <article><span>Jobs found</span><strong>{data.stats.found}</strong><small>Current watch window</small></article>
        <article><span>Strong matches</span><strong>{data.stats.strongMatches}</strong><small>High-priority applications</small></article>
        <article><span>Needs input</span><strong>{data.stats.needsInput}</strong><small>Waiting on a verified answer</small></article>
        <article><span>Ready</span><strong>{data.stats.ready}</strong><small>Safe to review</small></article>
        <article><span>Applied</span><strong>{data.stats.applied}</strong><small>Submission confirmed</small></article>
      </section>

      <section className="panel" id="jobs">
        <div className="section-title">
          <div><p className="eyebrow">Pipeline</p><h2>Fresh job queue</h2></div>
          <span>Preferred &lt;24h · Hard stop &gt;48h</span>
        </div>
        <div className="table-wrap">
          <table>
            <thead>
              <tr><th>Role</th><th>Fit</th><th>ATS</th><th>Application</th><th>Resume</th></tr>
            </thead>
            <tbody>
              {data.jobs.map((job) => (
                <tr key={job.id}>
                  <td><strong>{job.title}</strong><small>{job.company} · {job.location}</small></td>
                  <td><strong>{job.score ? `${job.score}%` : "—"}</strong><span className={`badge ${job.classification.toLowerCase()}`}>{job.classification.replaceAll("_", " ")}</span></td>
                  <td>{job.atsType}</td>
                  <td><span className="state">{stateLabel(job.applicationState)}</span></td>
                  <td>{job.resumeKey.replaceAll("_", " ")}</td>
                </tr>
              ))}
            </tbody>
          </table>
        </div>
      </section>

      <div className="grid">
        <section className="panel" id="applications">
          <div className="section-title">
            <div><p className="eyebrow">Applications</p><h2>Execution review</h2></div>
          </div>
          {data.applications.length ? data.applications.map((application) => (
            <article className="application" key={application.id}>
              <div className="application-head">
                <div><strong>{application.role}</strong><span>{application.company}</span></div>
                <span className="state attention">{stateLabel(application.state)}</span>
              </div>
              <div className="metrics">
                <div><span>Detected</span><strong>{application.fieldsDetected}</strong></div>
                <div><span>Filled</span><strong>{application.fieldsFilled}</strong></div>
                <div><span>Protected</span><strong>{application.protectedFields.length}</strong></div>
                <div><span>Submit clicked</span><strong>{application.submitClicked ? "Yes" : "No"}</strong></div>
              </div>
              {application.protectedFields.map((field) => (
                <div className="issue danger" key={field}><strong>Protected</strong><span>{field}</span></div>
              ))}
              {application.unknownFields.map((field) => (
                <div className="issue" key={field}><strong>Needs input</strong><span>{field}</span></div>
              ))}
            </article>
          )) : <p className="empty">No application runs yet.</p>}
        </section>

        <section className="panel" id="system">
          <p className="eyebrow">System</p>
          <h2>Execution safety</h2>
          <div className="rules">
            <div><b>✓</b><p><strong>Verified facts only</strong><span>Unknown salary, notice period, authorization and declarations stay blocked.</span></p></div>
            <div><b>✓</b><p><strong>Dry-run first</strong><span>Forms can be scanned and filled without clicking Submit.</span></p></div>
            <div><b>✓</b><p><strong>Provider isolation</strong><span>Greenhouse logic stays behind the ATS adapter boundary.</span></p></div>
          </div>
        </section>
      </div>
    </div>
  );
}
