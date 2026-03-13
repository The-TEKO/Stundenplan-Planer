# Implements the core backtracking algorithm for timetable generation.
"""Backtracking solver for the timetable problem.

The solver assigns one (timeslot, room) combination per session.
If a later step becomes impossible, the last decision is reverted
and the next option is tried (classic backtracking).
"""

from constraints import constraint_failure_reason, constraints_ok


def solve_timetable(
    sessions: list,
    domains: dict,
    teachers: list,
    progress_callback=None,
    stats_out=None,
    aggressive_pruning=True,
    force_probe_backtrack=True,
    target_probe_backtracks=5,
    probe_backtrack_start_ratio=0.8,
) -> dict | None:
    """
    Backtracking search algorithm for solving the constraint satisfaction problem of timetable generation.

    Args:
        sessions: A list of session objects that need to be scheduled.
        domains: A dictionary mapping each session to its possible time slot and room combinations.
        teachers: All available teachers.
        progress_callback: Optional function receiving solver stats.
        stats_out: Optional dict that will be filled with final solver stats.
    Returns:
        dict: A dictionary mapping each session to its assigned time slot and room if a solution is
                found, or None if no solution exists.
    """
    schedule = {}
    stats = {
        "total": len(sessions),
        "assigned": 0,
        "max_assigned": 0,
        "attempts": 0,
        "backtracks": 0,
        "nodes": 0,
        "reason_counts": {},
        "dead_end_count": 0,
        "last_dead_end": None,
        "forward_prunes": 0,
        "probe_backtrack_done": False,
        "probe_backtrack_count": 0,
        "probe_backtrack_start_ratio": probe_backtrack_start_ratio,
    }
    result = _search_recursive(
        schedule,
        sessions,
        domains,
        teachers,
        progress_callback,
        stats,
        aggressive_pruning,
        force_probe_backtrack,
        target_probe_backtracks,
        probe_backtrack_start_ratio,
    )

    if stats_out is not None:
        stats_out.clear()
        for key, value in stats.items():
            stats_out[key] = value

    return result


def backtracking_search(
    sessions: list,
    domains: dict,
    teachers: list,
    progress_callback=None,
    stats_out=None,
    aggressive_pruning=True,
    force_probe_backtrack=True,
    target_probe_backtracks=5,
    probe_backtrack_start_ratio=0.8,
) -> dict | None:
    """Backward-compatible alias for solve_timetable."""
    return solve_timetable(
        sessions=sessions,
        domains=domains,
        teachers=teachers,
        progress_callback=progress_callback,
        stats_out=stats_out,
        aggressive_pruning=aggressive_pruning,
        force_probe_backtrack=force_probe_backtrack,
        target_probe_backtracks=target_probe_backtracks,
        probe_backtrack_start_ratio=probe_backtrack_start_ratio,
    )


def _search_recursive(
    schedule,
    sessions,
    domains,
    teachers,
    progress_callback,
    stats,
    aggressive_pruning,
    force_probe_backtrack,
    target_probe_backtracks,
    probe_backtrack_start_ratio,
):
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

    session_to_assign, ordered_values = _select_session_and_values(schedule, sessions, domains, teachers, stats)
    if session_to_assign is None:
        return None

    if len(ordered_values) == 0:
        stats["backtracks"] = stats["backtracks"] + 1
        _emit_progress(progress_callback, stats)
        return None

    for value_index, value in enumerate(ordered_values):
        timeslot = value[0]
        room = value[1]
        stats["attempts"] = stats["attempts"] + 1

        is_valid = constraints_ok(schedule, session_to_assign, timeslot, room, teachers)
        if is_valid:
            schedule[session_to_assign] = (timeslot, room)
            stats["nodes"] = stats["nodes"] + 1
            stats["assigned"] = len(schedule)
            if stats["assigned"] > stats["max_assigned"]:
                stats["max_assigned"] = stats["assigned"]
            _emit_progress(progress_callback, stats)

            if aggressive_pruning:
                still_possible = _forward_check_has_values(
                    schedule=schedule,
                    sessions=sessions,
                    domains=domains,
                    teachers=teachers,
                    current_session=session_to_assign,
                    stats=stats,
                )
                if not still_possible:
                    del schedule[session_to_assign]
                    stats["assigned"] = len(schedule)
                    stats["backtracks"] = stats["backtracks"] + 1
                    stats["forward_prunes"] = stats["forward_prunes"] + 1
                    _emit_progress(progress_callback, stats)
                    continue

            if force_probe_backtrack:
                should_probe = False
                assigned_ratio = 0.0
                if stats["total"] > 0:
                    assigned_ratio = stats["assigned"] / stats["total"]

                if stats["probe_backtrack_count"] < target_probe_backtracks:
                    if assigned_ratio >= probe_backtrack_start_ratio:
                        if len(ordered_values) > 1:
                            if value_index == 0:
                                should_probe = True

                if should_probe:
                    stats["probe_backtrack_done"] = True
                    stats["probe_backtrack_count"] = stats["probe_backtrack_count"] + 1
                    del schedule[session_to_assign]
                    stats["assigned"] = len(schedule)
                    stats["backtracks"] = stats["backtracks"] + 1
                    _emit_progress(progress_callback, stats)
                    continue

            result = _search_recursive(
                schedule,
                sessions,
                domains,
                teachers,
                progress_callback,
                stats,
                aggressive_pruning,
                force_probe_backtrack,
                target_probe_backtracks,
                probe_backtrack_start_ratio,
            )
            if result is not None:
                return result

            del schedule[session_to_assign]
            stats["assigned"] = len(schedule)
            stats["backtracks"] = stats["backtracks"] + 1
            _emit_progress(progress_callback, stats)

    return None


def _backtrack(
    schedule,
    sessions,
    domains,
    teachers,
    progress_callback,
    stats,
    aggressive_pruning,
    force_probe_backtrack,
    target_probe_backtracks,
    probe_backtrack_start_ratio,
):
    """Backward-compatible alias for _search_recursive."""
    return _search_recursive(
        schedule,
        sessions,
        domains,
        teachers,
        progress_callback,
        stats,
        aggressive_pruning,
        force_probe_backtrack,
        target_probe_backtracks,
        probe_backtrack_start_ratio,
    )


def _forward_check_has_values(
    schedule,
    sessions,
    domains,
    teachers,
    current_session,
    stats,
):
    """Fast fail check after each assignment.

    Returns False immediately if any remaining session has no valid value left.
    This enforces earlier backtracking and avoids exploring deep doomed branches.
    """
    for other_session in sessions:
        if other_session in schedule:
            continue

        has_valid_value = False
        local_reason_counts = {}

        for other_value in domains[other_session]:
            other_timeslot = other_value[0]
            other_room = other_value[1]

            reason = constraint_failure_reason(
                schedule,
                other_session,
                other_timeslot,
                other_room,
                teachers,
            )
            if reason is None:
                has_valid_value = True
                break

            if reason not in local_reason_counts:
                local_reason_counts[reason] = 0
            local_reason_counts[reason] = local_reason_counts[reason] + 1

            if reason not in stats["reason_counts"]:
                stats["reason_counts"][reason] = 0
            stats["reason_counts"][reason] = stats["reason_counts"][reason] + 1

        if not has_valid_value:
            stats["dead_end_count"] = stats["dead_end_count"] + 1
            stats["last_dead_end"] = {
                "class": other_session.class_.name,
                "course": other_session.course.name,
                "domain_size": len(domains[other_session]),
                "reason_counts": local_reason_counts,
                "triggered_by": {
                    "class": current_session.class_.name,
                    "course": current_session.course.name,
                },
            }
            return False

    return True


def _emit_progress(progress_callback, stats):
    if progress_callback is None:
        return
    progress_callback(dict(stats))


def _select_session_and_values(schedule, sessions, domains, teachers, stats):
    unassigned = []
    for session in sessions:
        if session not in schedule:
            unassigned.append(session)

    if len(unassigned) == 0:
        return None, []

    best_session = None
    best_valid_values = []

    for candidate_session in unassigned:
        valid_values = []
        local_reason_counts = {}
        for value in domains[candidate_session]:
            timeslot = value[0]
            room = value[1]
            reason = constraint_failure_reason(schedule, candidate_session, timeslot, room, teachers)
            if reason is None:
                valid_values.append(value)
            else:
                if reason not in local_reason_counts:
                    local_reason_counts[reason] = 0
                local_reason_counts[reason] = local_reason_counts[reason] + 1

                if reason not in stats["reason_counts"]:
                    stats["reason_counts"][reason] = 0
                stats["reason_counts"][reason] = stats["reason_counts"][reason] + 1

        if best_session is None:
            best_session = candidate_session
            best_valid_values = valid_values
        else:
            if len(valid_values) < len(best_valid_values):
                best_session = candidate_session
                best_valid_values = valid_values

        if len(valid_values) == 0:
            stats["dead_end_count"] = stats["dead_end_count"] + 1
            stats["last_dead_end"] = {
                "class": candidate_session.class_.name,
                "course": candidate_session.course.name,
                "domain_size": len(domains[candidate_session]),
                "reason_counts": local_reason_counts,
            }
            return candidate_session, []

    ordered_values = _order_values_least_constraining(
        schedule,
        best_session,
        best_valid_values,
        unassigned,
        domains,
        teachers,
    )
    return best_session, ordered_values


def _order_values_least_constraining(
    schedule,
    session,
    candidate_values,
    unassigned,
    domains,
    teachers,
):
    value_scores = []

    for candidate_value in candidate_values:
        timeslot = candidate_value[0]
        room = candidate_value[1]

        simulated_schedule = dict(schedule)
        simulated_schedule[session] = (timeslot, room)

        blocked_count = 0
        for other_session in unassigned:
            if other_session == session:
                continue

            for other_value in domains[other_session]:
                other_timeslot = other_value[0]
                other_room = other_value[1]
                still_valid = constraints_ok(
                    simulated_schedule,
                    other_session,
                    other_timeslot,
                    other_room,
                    teachers,
                )
                if not still_valid:
                    blocked_count = blocked_count + 1

        soft_score = _soft_score_for_value(
            schedule,
            session,
            timeslot,
            unassigned,
            domains,
        )

        value_scores.append((blocked_count, soft_score, candidate_value))

    value_scores.sort(key=_first_tuple_value)

    ordered = []
    for score_and_value in value_scores:
        ordered.append(score_and_value[2])

    return ordered


def _first_tuple_value(item):
    return item[0], item[1]


def _soft_score_for_value(schedule, session, timeslot, unassigned, domains):
    """Returns a soft preference score for one candidate assignment.

    Lower score is better.
    Goals:
    - distribute lessons of a class across days
    - keep free periods at edges by preferring central lesson placement
    """
    class_name = session.class_.name
    target_day = timeslot.day
    target_index = timeslot.index_in_day

    day_counts = {}
    max_index_per_day = {}

    for existing_session, existing_assignment in schedule.items():
        if existing_session.class_.name != class_name:
            continue

        existing_timeslot = existing_assignment[0]
        day = existing_timeslot.day

        if day not in day_counts:
            day_counts[day] = 0
        day_counts[day] = day_counts[day] + 1

        if day not in max_index_per_day:
            max_index_per_day[day] = existing_timeslot.index_in_day
        else:
            if existing_timeslot.index_in_day > max_index_per_day[day]:
                max_index_per_day[day] = existing_timeslot.index_in_day

    for other_session in unassigned:
        if other_session.class_.name != class_name:
            continue

        for value in domains[other_session]:
            other_timeslot = value[0]
            day = other_timeslot.day

            if day not in max_index_per_day:
                max_index_per_day[day] = other_timeslot.index_in_day
            else:
                if other_timeslot.index_in_day > max_index_per_day[day]:
                    max_index_per_day[day] = other_timeslot.index_in_day

    if target_day not in day_counts:
        day_counts[target_day] = 0
    day_counts[target_day] = day_counts[target_day] + 1

    counts = list(day_counts.values())
    spread_penalty = 0
    if len(counts) > 0:
        spread_penalty = max(counts) - min(counts)

    heavy_day_penalty = day_counts[target_day]

    if target_day in max_index_per_day:
        max_index = max_index_per_day[target_day]
    else:
        max_index = target_index

    center = max_index / 2
    edge_penalty = abs(target_index - center)

    same_day_same_class_indexes = []
    for existing_session, existing_assignment in schedule.items():
        if existing_session.class_.name != class_name:
            continue
        existing_timeslot = existing_assignment[0]
        if existing_timeslot.day != target_day:
            continue
        same_day_same_class_indexes.append(existing_timeslot.index_in_day)
    same_day_same_class_indexes.append(target_index)

    same_day_same_class_indexes.sort()
    gap_penalty = 0
    for index_pos in range(1, len(same_day_same_class_indexes)):
        previous_index = same_day_same_class_indexes[index_pos - 1]
        current_index = same_day_same_class_indexes[index_pos]
        if current_index - previous_index > 1:
            gap_penalty = gap_penalty + 1

    return (
        spread_penalty,
        heavy_day_penalty,
        gap_penalty,
        edge_penalty,
    )