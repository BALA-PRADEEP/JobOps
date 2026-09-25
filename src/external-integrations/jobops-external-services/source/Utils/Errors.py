class JobOpsError(Exception):
    """Base domain/application error."""


class NotFoundError(JobOpsError):
    pass


class ConflictError(JobOpsError):
    pass


class InvalidStateTransitionError(JobOpsError):
    pass


class UnsupportedATSError(JobOpsError):
    pass
