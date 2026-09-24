from dataclasses import dataclass
from pathlib import Path
import os


REPO_ROOT = Path(__file__).resolve().parents[5]


@dataclass(frozen=True)
class Settings:
    database_url: str = os.getenv("DATABASE_URL", "sqlite:///./jobops.db")
    fresh_preferred_hours: int = int(os.getenv("JOBOPS_FRESH_PREFERRED_HOURS", "24"))
    fresh_max_hours: int = int(os.getenv("JOBOPS_FRESH_MAX_HOURS", "48"))
    auto_submit: bool = os.getenv("JOBOPS_AUTO_SUBMIT", "false").lower() == "true"
    candidate_profile_path: Path = Path(
        os.getenv(
            "JOBOPS_CANDIDATE_PROFILE_PATH",
            str(REPO_ROOT / "config" / "candidate" / "verified_profile.json"),
        )
    )
    answer_bank_path: Path = Path(
        os.getenv(
            "JOBOPS_ANSWER_BANK_PATH",
            str(REPO_ROOT / "config" / "candidate" / "answer_bank.json"),
        )
    )
    resumes_dir: Path = Path(os.getenv("JOBOPS_RESUMES_DIR", str(REPO_ROOT / "resumes")))


settings = Settings()
