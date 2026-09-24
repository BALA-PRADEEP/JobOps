from abc import ABC, abstractmethod
from pathlib import Path

from source.schemas.ApplicationSchemas import DryRunResult


class ATSAdapter(ABC):
    """Provider-neutral ATS adapter contract.

    Adapters may inspect and fill provider forms. They never decide candidate
    eligibility and never submit in dry-run mode.
    """

    ats_type: str

    def __init__(self, profile: dict, resume_path: str | Path):
        self.profile = profile
        self.resume_path = Path(resume_path)

    @abstractmethod
    def run_dry_run(self, url: str, artifact_dir: str | None = None) -> DryRunResult:
        raise NotImplementedError
