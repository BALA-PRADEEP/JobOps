import type { DashboardData } from "@/types/jobops";

export const demoDashboard: DashboardData = {
  dataSource: "demo",
  stats: {
    found: 14,
    strongMatches: 4,
    needsInput: 1,
    ready: 0,
    applied: 0
  },
  jobs: [
    {
      id: 1,
      company: "DigiCert",
      title: "Software Engineer",
      location: "Bengaluru, Karnataka",
      postedLabel: "Today",
      source: "LinkedIn",
      atsType: "Resolver pending",
      salaryLabel: "Not published",
      score: 88,
      classification: "STRONG_MATCH",
      applicationState: "SHORTLISTED",
      resumeKey: "product_engineering",
      matchedSkills: ["Python", "REST APIs", "React", "TypeScript", "PostgreSQL"],
      blockers: ["Official application URL has not been resolved yet"]
    },
    {
      id: 2,
      company: "Example AI",
      title: "Product Engineer - Applied AI",
      location: "Bengaluru, Karnataka",
      postedLabel: "2h ago",
      source: "Company careers",
      atsType: "Greenhouse",
      salaryLabel: "₹22L–₹35L",
      score: 91,
      classification: "STRONG_MATCH",
      applicationState: "NEEDS_INPUT",
      resumeKey: "applied_ai",
      matchedSkills: ["Python", "FastAPI", "React", "PostgreSQL", "RAG", "Playwright"],
      blockers: []
    },
    {
      id: 3,
      company: "Platform Labs",
      title: "Backend Integration Engineer",
      location: "Bengaluru, Karnataka",
      postedLabel: "9h ago",
      source: "Wellfound",
      atsType: "Lever",
      salaryLabel: "₹24L–₹32L",
      score: 78,
      classification: "REVIEW",
      applicationState: "SHORTLISTED",
      resumeKey: "backend_engineering",
      matchedSkills: ["Python", "FastAPI", "OAuth 2.0", "webhooks", "PostgreSQL"],
      blockers: ["Lever execution adapter is not implemented yet"]
    }
  ],
  applications: [
    {
      id: 101,
      jobId: 2,
      company: "Example AI",
      role: "Product Engineer - Applied AI",
      state: "NEEDS_INPUT",
      fieldsDetected: 10,
      fieldsFilled: 7,
      protectedFields: ["Expected salary"],
      unknownFields: ["Why do you want to work here?", "Notice period"],
      submitClicked: false
    }
  ]
};
