from source.Utils.ApplicationState import ApplicationState, can_transition


def test_ready_for_review_can_move_back_to_needs_input_after_form_scan():
    assert can_transition(
        ApplicationState.READY_FOR_REVIEW,
        ApplicationState.NEEDS_INPUT,
    )


def test_submitted_cannot_transition_back_to_applying():
    assert not can_transition(
        ApplicationState.SUBMITTED,
        ApplicationState.APPLYING,
    )
