from pathlib import Path
import os

from source.dal.ApplicationRepository import ExecutionRequestRepository
from source.dal.db_session import session_scope
from source.service.ApplicationExecutionService import ApplicationExecutionService


def process_queue(limit: int = 3) -> int:
    processed = 0
    artifact_root = Path(os.getenv("JOBOPS_ARTIFACT_DIR", "artifacts"))
    artifact_root.mkdir(parents=True, exist_ok=True)

    while processed < limit:
        with session_scope() as session:
            requests = ExecutionRequestRepository(session)
            request = requests.next_queued()
            if request is None:
                return processed

            requests.mark_running(request)
            session.flush()

            application_id = request.application_id
            request_id = request.id

        try:
            with session_scope() as session:
                from source.dal.ApplicationRepository import ApplicationRepository

                application = ApplicationRepository(session).get(application_id)
                if application is None:
                    raise RuntimeError("Application not found for execution request")

                result = ApplicationExecutionService(session).run_dry_run(
                    application.job_id,
                    artifact_dir=str(artifact_root / str(request_id)),
                )
                request = ExecutionRequestRepository(session).get(request_id)
                assert request is not None
                terminal = (
                    "NEEDS_INPUT"
                    if result.status in {"NEEDS_INPUT", "HUMAN_ACTION_REQUIRED"}
                    else "SUCCEEDED"
                )
                ExecutionRequestRepository(session).mark_complete(request, terminal)
        except Exception as exc:
            with session_scope() as session:
                request = ExecutionRequestRepository(session).get(request_id)
                if request is not None:
                    ExecutionRequestRepository(session).mark_failed(request, str(exc))
        processed += 1

    return processed


if __name__ == "__main__":
    count = process_queue(limit=int(os.getenv("JOBOPS_WORKER_LIMIT", "3")))
    print(f"processed={count}")
