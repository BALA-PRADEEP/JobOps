from datetime import datetime, timezone
from sqlalchemy.orm import Session

from source.Utils.ApplicationState import ApplicationState, can_transition
from source.Utils.Errors import InvalidStateTransitionError
from source.dao.baseDao import BaseDao
from source.dal.ApplicationModels import (
    Application,
    ApplicationEvent,
    BrowserRun,
    ExecutionRequest,
)


class ApplicationRepository(BaseDao[Application]):
    def __init__(self, session: Session):
        super().__init__(session)

    def get(self, application_id: int) -> Application | None:
        return self.session.get(Application, application_id)

    def get_by_job_id(self, job_id: int) -> Application | None:
        return self.session.query(Application).filter(Application.job_id == job_id).first()

    def transition(self, application: Application, target: str | ApplicationState) -> Application:
        target_state = ApplicationState(target)
        if not can_transition(application.state, target_state):
            raise InvalidStateTransitionError(
                f"Invalid application transition: {application.state} -> {target_state.value}"
            )
        application.state = target_state.value
        application.updated_at = datetime.now(timezone.utc)
        self.session.add(application)
        return application


class ApplicationEventRepository(BaseDao[ApplicationEvent]):
    def __init__(self, session: Session):
        super().__init__(session)

    def append(self, application_id: int, event_type: str, payload_json: str = "{}") -> ApplicationEvent:
        event = ApplicationEvent(
            application_id=application_id,
            event_type=event_type,
            payload_json=payload_json,
        )
        self.session.add(event)
        return event


class BrowserRunRepository(BaseDao[BrowserRun]):
    def __init__(self, session: Session):
        super().__init__(session)

    def create(
        self,
        application_id: int,
        ats_type: str,
        status: str,
        artifact_json: str,
        submit_clicked: bool,
    ) -> BrowserRun:
        run = BrowserRun(
            application_id=application_id,
            ats_type=ats_type,
            status=status,
            artifact_json=artifact_json,
            submit_clicked=submit_clicked,
        )
        self.session.add(run)
        return run


class ExecutionRequestRepository(BaseDao[ExecutionRequest]):
    def __init__(self, session: Session):
        super().__init__(session)

    def enqueue(self, application_id: int, action: str = "DRY_RUN") -> ExecutionRequest:
        existing = (
            self.session.query(ExecutionRequest)
            .filter(
                ExecutionRequest.application_id == application_id,
                ExecutionRequest.action == action,
                ExecutionRequest.status.in_(["QUEUED", "RUNNING"]),
            )
            .order_by(ExecutionRequest.id.desc())
            .first()
        )
        if existing is not None:
            return existing
        request = ExecutionRequest(
            application_id=application_id,
            action=action,
            status="QUEUED",
        )
        self.session.add(request)
        self.session.flush()
        return request

    def get(self, request_id: int) -> ExecutionRequest | None:
        return self.session.get(ExecutionRequest, request_id)

    def next_queued(self) -> ExecutionRequest | None:
        return (
            self.session.query(ExecutionRequest)
            .filter(ExecutionRequest.status == "QUEUED")
            .order_by(ExecutionRequest.created_at.asc(), ExecutionRequest.id.asc())
            .first()
        )

    def mark_running(self, request: ExecutionRequest) -> None:
        now = datetime.now(timezone.utc)
        request.status = "RUNNING"
        request.started_at = now
        request.updated_at = now
        request.attempt_count += 1
        self.session.add(request)

    def mark_complete(self, request: ExecutionRequest, status: str) -> None:
        now = datetime.now(timezone.utc)
        request.status = status
        request.completed_at = now
        request.updated_at = now
        request.last_error = None
        self.session.add(request)

    def mark_failed(self, request: ExecutionRequest, error: str) -> None:
        request.status = "FAILED"
        request.last_error = error[:4000]
        request.updated_at = datetime.now(timezone.utc)
        self.session.add(request)
