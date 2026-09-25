export type ApplicationState =
  | "SHORTLISTED"
  | "NEEDS_INPUT"
  | "READY_FOR_REVIEW"
  | "SUBMITTED"
  | "SKIPPED";

export type Job = {
  id: number;
  company: string;
  title: string;
  location: string;
  postedLabel: string;
  source: string;
  atsType: string;
  salaryLabel: string;
  score: number;
  classification: "STRONG_MATCH" | "REVIEW" | "SELECTIVE" | "SKIP";
  applicationState: ApplicationState;
  resumeKey: string;
  matchedSkills: string[];
  blockers: string[];
};

export type Application = {
  id: number;
  jobId: number;
  company: string;
  role: string;
  state: ApplicationState;
  fieldsDetected: number;
  fieldsFilled: number;
  protectedFields: string[];
  unknownFields: string[];
  submitClicked: boolean;
};

export type DashboardData = {
  dataSource: "demo" | "live";
  stats: {
    found: number;
    strongMatches: number;
    needsInput: number;
    ready: number;
    applied: number;
  };
  jobs: Job[];
  applications: Application[];
};
