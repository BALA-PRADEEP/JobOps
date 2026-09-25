from sqlalchemy.orm import Session

from source.dao.baseDao import BaseDao
from source.dal.JobModels import Job, JobScore


class JobRepository(BaseDao[Job]):
    def __init__(self, session: Session):
        super().__init__(session)

    def get(self, job_id: int) -> Job | None:
        return self.session.get(Job, job_id)

    def get_by_source_identity(self, source: str, source_job_id: str) -> Job | None:
        return (
            self.session.query(Job)
            .filter(Job.source == source, Job.source_job_id == source_job_id)
            .first()
        )

    def list_recent(self, limit: int = 100) -> list[Job]:
        return self.session.query(Job).order_by(Job.posted_at.desc()).limit(limit).all()


class JobScoreRepository(BaseDao[JobScore]):
    def __init__(self, session: Session):
        super().__init__(session)

    def get_latest_for_job(self, job_id: int) -> JobScore | None:
        return (
            self.session.query(JobScore)
            .filter(JobScore.job_id == job_id)
            .order_by(JobScore.id.desc())
            .first()
        )
