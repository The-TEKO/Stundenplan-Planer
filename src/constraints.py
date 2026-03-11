# Implements all scheduling rules and constraint validation logic.

from collections.abc import Callable, Mapping, Sequence
from typing import Any


def constraints_ok(
    schedule: Mapping[Any, tuple[Any, Any]],
    session: Any,
    timeslot: Any,
    room: Any,
    teachers: Sequence[Any],
    *,
    max_same_session_per_day: int = 2,
    require_consecutive_same_day: bool = True,
    extra_constraints: Sequence[Callable[..., bool]] | None = None,
) -> bool:
    """
    Checks whether a new assignment (session, timeslot, room) is compatible
    with the current (partial) schedule.

    Args:
        schedule: Current assignment as a mapping {session: (timeslot, room)}.
        session: The session to be scheduled next.
        timeslot: Target timeslot for ``session``.
        room: Target room for ``session``.
        teachers: All available teacher objects (with ``name`` and ``courses``).
        max_same_session_per_day: Maximum number of identical sessions allowed per day.
        require_consecutive_same_day: If True, duplicate sessions on the same day
            must be scheduled in consecutive periods.
        extra_constraints: Optional additional constraint functions for testing.
            Each function receives the same context as this function
            (via keyword arguments) and must return ``bool``.

    Returns:
        bool: True if all constraints are satisfied, False otherwise.
    """

    # Project the candidate onto the current state.
    # In unit tests this lets you validate a single scheduling step in isolation.
    proposed = dict(schedule)
    proposed[session] = (timeslot, room)

    # TODO 1: A room must not be double-booked in the same timeslot.
    # Approach:
    # - Build an index with key = (timeslot.day, timeslot.time, room.name).
    # - If any key appears more than once -> return False.

    # TODO 2: A teacher must not teach two sessions at the same time.
    # Requires:
    # - Helper: teacher_for_session(session, teachers)
    # - Index with key = (timeslot.day, timeslot.time, teacher.name)
    # - Duplicate -> return False.

    # TODO 3: A class/student group must not attend two sessions at the same time.
    # Requires:
    # - Key = (timeslot.day, timeslot.time, session.class_.name)
    # - Duplicate -> return False.

    # TODO 4: The same session may appear at most max_same_session_per_day times per day.
    # Session identity:
    # - (session.course.name, session.class_.name)
    # Check:
    # - Count per (day, session identity) and compare against max_same_session_per_day.
    # - If require_consecutive_same_day=True: sort periods and only allow direct neighbours.

    if extra_constraints:
        context = {
            "schedule": schedule,
            "proposed": proposed,
            "session": session,
            "timeslot": timeslot,
            "room": room,
            "teachers": teachers,
            "max_same_session_per_day": max_same_session_per_day,
            "require_consecutive_same_day": require_consecutive_same_day,
        }
        for constraint in extra_constraints:
            if not constraint(**context):
                return False

    return True