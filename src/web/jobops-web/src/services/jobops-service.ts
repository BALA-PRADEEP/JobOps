import { demoDashboard } from "@/data/demo";
import type { DashboardData, Job } from "@/types/jobops";

const API_URL = process.env.JOBOPS_API_URL?.replace(/\/$/, "");

type ApiJob = {
  id: number;
  source: string;
  company: string;
  title: string;
  location: string;
  posted_at: string;
  ats_type: string;
  salary_min_inr?: number | null;
  salary_max_inr?: number | null;
};

function salary(min?: number | null, max?: number | null): string {
  if (!min && !max) return "Not published";
  const toLakhs = (value: number) => `₹${Math.round(value / 100000)}L`;
  if (min && max) return `${toLakhs(min)}–${toLakhs(max)}`;
  return min ? `${toLakhs(min)}+` : `Up to ${toLakhs(max as number)}`;
}

function mapJob(job: ApiJob): Job {
  return {
    id: job.id,
    company: job.company,
    title: job.title,
    location: job.location,
    postedLabel: new Date(job.posted_at).toLocaleDateString("en-IN", {
      day: "numeric",
      month: "short"
    }),
    source: job.source,
    atsType: job.ats_type,
    salaryLabel: salary(job.salary_min_inr, job.salary_max_inr),
    score: 0,
    classification: "REVIEW",
    applicationState: "SHORTLISTED",
    resumeKey: "pending",
    matchedSkills: [],
    blockers: ["Detailed score endpoint is not connected yet"]
  };
}

export async function getDashboard(): Promise<DashboardData> {
  if (!API_URL) return demoDashboard;

  try {
    const response = await fetch(`${API_URL}/v1/jobs`, {
      cache: "no-store",
      signal: AbortSignal.timeout(5000)
    });
    if (!response.ok) return demoDashboard;

    const jobs = ((await response.json()) as ApiJob[]).map(mapJob);
    return {
      dataSource: "live",
      stats: {
        found: jobs.length,
        strongMatches: 0,
        needsInput: 0,
        ready: 0,
        applied: 0
      },
      jobs,
      applications: []
    };
  } catch {
    return demoDashboard;
  }
}
