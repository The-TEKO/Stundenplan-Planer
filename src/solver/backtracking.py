# Implements the core backtracking algorithm for timetable generation.

def backtracking_search(sessions: list, constraints: list, domains: dict) -> dict:
    """
    Backtracking search algorithm for solving the constraint satisfaction problem of timetable generation.

    Args:
        sessions: A list of session objects that need to be scheduled.
        constraints: A list of constraint functions that must be satisfied for a valid schedule.
        domains: A dictionary mapping each session to its possible time slot and room combinations.
    Returns:
        dict: A dictionary mapping each session to its assigned time slot and room if a solution is
                found, or None if no solution exists.
    """

    yield