from source.dal.db_session import session_scope
from source.service.ApplicationExecutionService import (
    ApplicationExecutionService,
)


class ApplicationWorker:
    """Queue-agnostic application worker entrypoint."""

    def run_dry_run(
        self,
        job_id: int,
        artifact_dir: str | None = None,
    ):
        with session_scope() as session:
            return ApplicationExecutionService(session).run_dry_run(
                job_id,
                artifact_dir,
            )
