from pathlib import Path

from source.Utils.Config import settings


class ResumeSelectionService:
    _RESUME_FILES = {
        "product_engineering": "product_engineering.pdf",
        "backend_engineering": "backend_engineering.pdf",
        "applied_ai": "applied_ai.pdf",
    }

    @classmethod
    def select_key(cls, title: str, description: str) -> str:
        text = f"{title} {description}".lower()
        if any(keyword in text for keyword in ["applied ai", "ai engineer", "rag", "llm", "agent"]):
            return "applied_ai"
        if any(keyword in text for keyword in ["integration", "backend", "api"]):
            return "backend_engineering"
        return "product_engineering"

    @classmethod
    def get_path(cls, resume_key: str) -> Path:
        try:
            filename = cls._RESUME_FILES[resume_key]
        except KeyError as exc:
            raise ValueError(f"Unknown resume key: {resume_key}") from exc
        return settings.resumes_dir / filename
