from datetime import datetime, timezone
from sqlalchemy.orm import Session

from source.Utils.ApplicationState import ApplicationState, can_transition
from source.Utils.Errors import InvalidStateTransitionError
from source.dao.baseDao import BaseDao
from source.dal.ApplicationModels import Application, ApplicationEvent, BrowserRun


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
