# Implements all scheduling rules and constraint validation logic.

def check_constraints(schedule, current_domain) -> bool:
    """
    Validates the current schedule against all defined constraints.

    Args:
        schedule: The current schedule being evaluated.
        current_domain: The current domain of possible time slot and room combinations for the sessions.

    Returns:
        bool: True if the schedule satisfies all constraints, False otherwise.
    """

    # TODO: Check that room is not double-booked for the same time slot.

    # TODO: Check that teachers are not scheduled to teach multiple sessions at the same time.

    # TODO: Check that students are not scheduled for multiple sessions at the same time.

    # TODO: Check that a maximum of two same sessions are scheduled on the same day and that they are together in the schedule.

    yield