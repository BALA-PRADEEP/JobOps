from enum import StrEnum


class ApplicationState(StrEnum):
    DISCOVERED = "DISCOVERED"
    ANALYZED = "ANALYZED"
    SKIPPED = "SKIPPED"
    SHORTLISTED = "SHORTLISTED"
    PREPARING = "PREPARING"
    NEEDS_INPUT = "NEEDS_INPUT"
    READY_FOR_REVIEW = "READY_FOR_REVIEW"
    APPLYING = "APPLYING"
    SUBMITTED = "SUBMITTED"
    SUBMISSION_UNCONFIRMED = "SUBMISSION_UNCONFIRMED"
    FAILED_RETRYABLE = "FAILED_RETRYABLE"
    FAILED_FINAL = "FAILED_FINAL"
    INTERVIEW = "INTERVIEW"
    REJECTED = "REJECTED"
    OFFER = "OFFER"


_ALLOWED_TRANSITIONS: dict[ApplicationState, frozenset[ApplicationState]] = {
    ApplicationState.DISCOVERED: frozenset({ApplicationState.ANALYZED}),
    ApplicationState.ANALYZED: frozenset({ApplicationState.SKIPPED, ApplicationState.SHORTLISTED}),
    ApplicationState.SHORTLISTED: frozenset({ApplicationState.PREPARING}),
    ApplicationState.PREPARING: frozenset({ApplicationState.NEEDS_INPUT, ApplicationState.READY_FOR_REVIEW}),
    ApplicationState.NEEDS_INPUT: frozenset({ApplicationState.READY_FOR_REVIEW, ApplicationState.FAILED_FINAL}),
    ApplicationState.READY_FOR_REVIEW: frozenset({
        ApplicationState.NEEDS_INPUT,
        ApplicationState.APPLYING,
        ApplicationState.FAILED_FINAL,
    }),
    ApplicationState.APPLYING: frozenset({
        ApplicationState.SUBMITTED,
        ApplicationState.SUBMISSION_UNCONFIRMED,
        ApplicationState.FAILED_RETRYABLE,
        ApplicationState.FAILED_FINAL,
    }),
    ApplicationState.SUBMISSION_UNCONFIRMED: frozenset({
        ApplicationState.APPLYING,
        ApplicationState.FAILED_FINAL,
    }),
    ApplicationState.FAILED_RETRYABLE: frozenset({ApplicationState.APPLYING, ApplicationState.FAILED_FINAL}),
    ApplicationState.SUBMITTED: frozenset({
        ApplicationState.INTERVIEW,
        ApplicationState.REJECTED,
        ApplicationState.OFFER,
    }),
    ApplicationState.INTERVIEW: frozenset({ApplicationState.REJECTED, ApplicationState.OFFER}),
    ApplicationState.SKIPPED: frozenset(),
    ApplicationState.FAILED_FINAL: frozenset(),
    ApplicationState.REJECTED: frozenset(),
    ApplicationState.OFFER: frozenset(),
}


def can_transition(current: str | ApplicationState, target: str | ApplicationState) -> bool:
    current_state = ApplicationState(current)
    target_state = ApplicationState(target)
    return target_state in _ALLOWED_TRANSITIONS[current_state]
