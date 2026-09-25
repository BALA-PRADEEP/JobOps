import re
from datetime import datetime, timezone

from source.Utils.ATSDetector import detect_ats
from source.Utils.Config import settings
from source.Utils.Constants import GAP_KEYWORDS, SKILL_ALIASES, SUPPORTED_DRY_RUN_ATS, TARGET_TITLES
from source.schemas.JobSchemas import JobAnalysis, JobCreate
from source.service.CandidateProfileService import CandidateProfileService
from source.service.ResumeSelectionService import ResumeSelectionService


class JobAnalysisService:
    WEIGHTS = {
        "role": 20,
        "experience": 15,
        "backend": 20,
        "integration": 15,
        "frontend": 10,
        "ai": 10,
        "compensation": 5,
        "location": 5,
    }

    def __init__(self, now_provider=None):
        self.now_provider = now_provider or (lambda: datetime.now(timezone.utc))
        self.profile = CandidateProfileService.get_profile()

    @staticmethod
    def _normalize(text: str) -> str:
        return re.sub(r"\s+", " ", text.lower())

    @staticmethod
    def _contains_any(text: str, values: list[str] | tuple[str, ...]) -> bool:
        return any(value.lower() in text for value in values)

    @staticmethod
    def _experience_range(text: str) -> tuple[int | None, int | None]:
        patterns = [
            r"(\d+)\s*[-–]\s*(\d+)\s*(?:\+\s*)?(?:years|yrs|year)",
            r"(\d+)\s*(?:to)\s*(\d+)\s*(?:years|yrs|year)",
            r"(\d+)\s*\+\s*(?:years|yrs|year)",
            r"minimum\s*(?:of\s*)?(\d+)\s*(?:years|yrs|year)",
        ]
        for i, pattern in enumerate(patterns):
            match = re.search(pattern, text)
            if not match:
                continue
            if i <= 1:
                return int(match.group(1)), int(match.group(2))
            return int(match.group(1)), None
        return None, None

    def _freshness(self, posted_at: datetime) -> tuple[str, float, list[str]]:
        if posted_at.tzinfo is None:
            posted_at = posted_at.replace(tzinfo=timezone.utc)
        age = max(0.0, (self.now_provider() - posted_at.astimezone(timezone.utc)).total_seconds() / 3600)
        failures: list[str] = []
        if age > settings.fresh_max_hours:
            failures.append(f"job_older_than_{settings.fresh_max_hours}_hours")
            return "expired", age, failures
        if age <= settings.fresh_preferred_hours:
            return "preferred", age, failures
        return "fallback", age, failures

    def _role_score(self, title: str, description: str) -> float:
        text = self._normalize(f"{title} {description[:1000]}")
        hits = sum(1 for role in TARGET_TITLES if role in text)
        if hits >= 2:
            return self.WEIGHTS["role"]
        if hits == 1:
            return self.WEIGHTS["role"] * 0.85
        if "engineer" in text and any(x in text for x in ["python", "ai", "api", "integration"]):
            return self.WEIGHTS["role"] * 0.6
        return 0.0

    def _experience_score(self, text: str, hard_failures: list[str], gaps: list[str]) -> float:
        required_min, required_max = self._experience_range(text)
        candidate_years = float(self.profile["experience"]["years"])
        max_points = self.WEIGHTS["experience"]
        if required_min is None:
            return max_points * 0.8
        if required_min <= candidate_years:
            return max_points
        delta = required_min - candidate_years
        if delta <= 1:
            gaps.append(f"experience_stretch_{required_min}_years")
            return max_points * 0.7
        if delta <= 2:
            gaps.append(f"experience_stretch_{required_min}_years")
            return max_points * 0.35
        hard_failures.append(f"experience_requires_{required_min}_years")
        return 0.0

    def _skill_groups(self, text: str) -> tuple[list[str], list[str]]:
        matched: list[str] = []
        for display, aliases in SKILL_ALIASES.items():
            if any(alias in text for alias in aliases):
                matched.append(display)
        gaps: list[str] = []
        for display, aliases in GAP_KEYWORDS.items():
            if any(alias in text for alias in aliases):
                owned = any(alias in self._normalize(" ".join(sum(self.profile["skills"].values(), []))) for alias in aliases)
                if not owned:
                    gaps.append(display)
        return matched, gaps

    def _domain_score(self, matched: set[str], category: str) -> float:
        buckets = {
            "backend": {"Python", "FastAPI", "REST APIs", "PostgreSQL", "MongoDB", "SQLAlchemy"},
            "integration": {"OAuth 2.0", "webhooks", "multi-tenant SaaS", "reconciliation"},
            "frontend": {"React", "TypeScript"},
            "ai": {"RAG", "embeddings", "vector search"},
        }
        possible = buckets[category]
        hits = len(matched & possible)
        ratio = min(1.0, hits / max(1, len(possible) * 0.6))
        return self.WEIGHTS[category] * ratio

    def _compensation_score(self, job: JobCreate) -> float:
        if job.salary_max_inr is None:
            return self.WEIGHTS["compensation"] * 0.5
        if job.salary_max_inr >= 2_000_000:
            return self.WEIGHTS["compensation"]
        if job.salary_max_inr >= 1_500_000:
            return self.WEIGHTS["compensation"] * 0.65
        return self.WEIGHTS["compensation"] * 0.25

    def _location_score(self, job: JobCreate) -> float:
        text = self._normalize(f"{job.location} {job.work_mode or ''}")
        if "bengaluru" in text or "bangalore" in text:
            return self.WEIGHTS["location"]
        if "remote" in text and "india" in self._normalize(job.description):
            return self.WEIGHTS["location"] * 0.8
        return 0.0

    def analyze(self, job: JobCreate) -> JobAnalysis:
        text = self._normalize(f"{job.title} {job.description}")
        hard_failures: list[str] = []
        gaps: list[str] = []
        blockers: list[str] = []

        freshness, age_hours, freshness_failures = self._freshness(job.posted_at)
        hard_failures.extend(freshness_failures)
        ats_type = detect_ats(str(job.apply_url))
        if ats_type not in SUPPORTED_DRY_RUN_ATS:
            blockers.append("unsupported_or_unverified_ats")

        role_score = self._role_score(job.title, job.description)
        experience_score = self._experience_score(text, hard_failures, gaps)
        matched, skill_gaps = self._skill_groups(text)
        gaps.extend(skill_gaps)
        matched_set = set(matched)

        backend_score = self._domain_score(matched_set, "backend")
        integration_score = self._domain_score(matched_set, "integration")
        frontend_score = self._domain_score(matched_set, "frontend")
        ai_score = self._domain_score(matched_set, "ai")
        compensation_score = self._compensation_score(job)
        location_score = self._location_score(job)

        total = round(
            role_score
            + experience_score
            + backend_score
            + integration_score
            + frontend_score
            + ai_score
            + compensation_score
            + location_score,
            1,
        )
        if hard_failures:
            classification = "SKIP"
        elif total >= 85:
            classification = "STRONG_MATCH"
        elif total >= 70:
            classification = "REVIEW"
        elif total >= 55:
            classification = "SELECTIVE"
        else:
            classification = "SKIP"

        resume_key = ResumeSelectionService.select_key(job.title, job.description)
        auto_apply_eligible = (
            classification in {"STRONG_MATCH", "REVIEW"}
            and freshness in {"preferred", "fallback"}
            and not hard_failures
            and ats_type in SUPPORTED_DRY_RUN_ATS
        )

        return JobAnalysis(
            freshness=freshness,
            age_hours=round(age_hours, 2),
            ats_type=ats_type,
            role_score=round(role_score, 1),
            experience_score=round(experience_score, 1),
            backend_score=round(backend_score, 1),
            integration_score=round(integration_score, 1),
            frontend_score=round(frontend_score, 1),
            ai_score=round(ai_score, 1),
            compensation_score=round(compensation_score, 1),
            location_score=round(location_score, 1),
            total_score=total,
            classification=classification,
            matched_skills=sorted(matched),
            gaps=sorted(set(gaps)),
            hard_failures=hard_failures,
            blockers=blockers,
            resume_key=resume_key,
            auto_apply_eligible=auto_apply_eligible,
        )
