# Implements the core backtracking algorithm for timetable generation.
"""Backtracking solver for the timetable problem.

The solver assigns one (timeslot, room) combination per session.
If a later step becomes impossible, the last decision is reverted
and the next option is tried (classic backtracking).
"""

from constraints import constraints_ok
from solver.heuristics import mrv_heuristic


def backtracking_search(sessions: list, domains: dict, teachers: list) -> dict | None:
    """
    Backtracking search algorithm for solving the constraint satisfaction problem of timetable generation.

    Args:
        sessions: A list of session objects that need to be scheduled.
        domains: A dictionary mapping each session to its possible time slot and room combinations.
        teachers: All available teachers.
    Returns:
        dict: A dictionary mapping each session to its assigned time slot and room if a solution is
                found, or None if no solution exists.
    """
    schedule = {}
    return _backtrack(schedule, sessions, domains, teachers)


def _backtrack(schedule, sessions, domains, teachers):
    """Recursive core of the solver.

    Args:
        schedule: Current partial schedule.
        sessions: All sessions that must be assigned.
        domains: Available values per session.
        teachers: Teachers used in constraint checks.

    Returns:
        Complete schedule as dict, or None.
    """
    if len(schedule) == len(sessions):
        return dict(schedule)

    unassigned = []
    for session in sessions:
        if session not in schedule:
            unassigned.append(session)

    ordered_unassigned = mrv_heuristic(unassigned, domains)
    if len(ordered_unassigned) == 0:
        return None

    session_to_assign = ordered_unassigned[0]

    for value in domains[session_to_assign]:
        timeslot = value[0]
        room = value[1]

        is_valid = constraints_ok(schedule, session_to_assign, timeslot, room, teachers)
        if is_valid:
            schedule[session_to_assign] = (timeslot, room)
            result = _backtrack(schedule, sessions, domains, teachers)
            if result is not None:
                return result
            del schedule[session_to_assign]

    return None