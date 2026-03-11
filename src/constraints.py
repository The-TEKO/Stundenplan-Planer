"""Constraint checks for timetable generation.

This module intentionally uses explicit, easy-to-read `if` blocks.
Every new assignment is validated against the current partial schedule.
"""


def teacher_for_course(course_name, teachers):
    """Finds the teacher for a given course name.

    Args:
        course_name: Name of the course.
        teachers: List of Teacher objects.

    Returns:
        The matching Teacher object, or None if no match is found.
    """
    for teacher in teachers:
        for teacher_course in teacher.courses:
            if teacher_course == course_name:
                return teacher
    return None


def _course_streak_would_exceed_limit(schedule, candidate_session, candidate_timeslot, max_streak):
    """Checks the rule "maximum same course in a row".

    For one class on one day, all assigned lessons are ordered by period.
    If a sequence of the same course becomes longer than `max_streak`,
    the candidate assignment is invalid.
    """
    same_class_same_day_rows = []

    for existing_session, existing_assignment in schedule.items():
        existing_timeslot = existing_assignment[0]

        if existing_session.class_.name != candidate_session.class_.name:
            continue
        if existing_timeslot.day != candidate_timeslot.day:
            continue

        same_class_same_day_rows.append((existing_timeslot, existing_session))

    same_class_same_day_rows.append((candidate_timeslot, candidate_session))

    same_class_same_day_rows_with_keys = []
    for row in same_class_same_day_rows:
        row_key = row[0].index_in_day
        same_class_same_day_rows_with_keys.append((row_key, row))

    same_class_same_day_rows_with_keys.sort(key=_first_tuple_value)

    ordered_rows = []
    for key_and_row in same_class_same_day_rows_with_keys:
        ordered_rows.append(key_and_row[1])

    current_streak_course = None
    current_streak_count = 0
    previous_index = None

    for ordered_row in ordered_rows:
        current_timeslot = ordered_row[0]
        current_session = ordered_row[1]
        current_course_name = current_session.course.name
        current_index = current_timeslot.index_in_day

        if current_streak_course is None:
            current_streak_course = current_course_name
            current_streak_count = 1
        else:
            is_adjacent_to_previous = False
            if previous_index is not None:
                if current_index == previous_index + 1:
                    is_adjacent_to_previous = True

            if is_adjacent_to_previous and current_course_name == current_streak_course:
                current_streak_count = current_streak_count + 1
            else:
                current_streak_course = current_course_name
                current_streak_count = 1

        previous_index = current_index

        if current_streak_count > max_streak:
            return True

    return False


def _first_tuple_value(item):
    """Helper for simple explicit sorting."""
    return item[0]


def constraints_ok(
    schedule,
    session,
    timeslot,
    room,
    teachers,
    max_same_course_in_row=2,
):
    """Checks whether a new assignment is valid.

    Rules checked:
    1) Room capacity must be large enough for the class.
    2) Room must allow the course (if `accepted_courses` is configured).
    3) A room cannot be double-booked in the same timeslot.
    4) A class cannot have two sessions in the same timeslot.
    5) A teacher cannot teach two sessions in the same timeslot.
    6) Per class/day, at most 2 equal lessons may appear consecutively.

    Args:
        schedule: Current assignments {Session: (Timeslot, Room)}.
        session: Candidate session to assign.
        timeslot: Candidate timeslot for the session.
        room: Candidate room for the session.
        teachers: List of available teachers.
        max_same_course_in_row: Maximum allowed consecutive lessons of the same course.

    Returns:
        True if all rules are satisfied, otherwise False.
    """
    reason = constraint_failure_reason(
        schedule,
        session,
        timeslot,
        room,
        teachers,
        max_same_course_in_row=max_same_course_in_row,
    )
    if reason is None:
        return True
    return False


def constraint_failure_reason(
    schedule,
    session,
    timeslot,
    room,
    teachers,
    max_same_course_in_row=2,
):
    """Returns a machine-friendly reason key when an assignment is invalid.

    Returns:
        None if valid, otherwise one of:
        - room_capacity
        - room_course_not_allowed
        - room_double_booked
        - class_double_booked
        - teacher_double_booked
        - max_same_course_in_row
    """
    if room.capacity < session.class_.student_count:
        return "room_capacity"

    if len(room.accepted_courses) > 0:
        room_supports_course = False
        for accepted_course in room.accepted_courses:
            if accepted_course == session.course.name:
                room_supports_course = True
                break
        if not room_supports_course:
            return "room_course_not_allowed"

    candidate_teacher = session.teacher
    if candidate_teacher is None:
        candidate_teacher = teacher_for_course(session.course.name, teachers)

    for existing_session, existing_assignment in schedule.items():
        existing_timeslot = existing_assignment[0]
        existing_room = existing_assignment[1]

        same_timeslot = False
        if existing_timeslot.day == timeslot.day:
            if existing_timeslot.time == timeslot.time:
                same_timeslot = True

        if same_timeslot:
            if existing_room.name == room.name:
                return "room_double_booked"

            if existing_session.class_.name == session.class_.name:
                return "class_double_booked"

            existing_teacher = existing_session.teacher
            if existing_teacher is None:
                existing_teacher = teacher_for_course(existing_session.course.name, teachers)

            if existing_teacher is not None and candidate_teacher is not None:
                if existing_teacher.name == candidate_teacher.name:
                    return "teacher_double_booked"

    streak_exceeded = _course_streak_would_exceed_limit(
        schedule=schedule,
        candidate_session=session,
        candidate_timeslot=timeslot,
        max_streak=max_same_course_in_row,
    )
    if streak_exceeded:
        return "max_same_course_in_row"

    return None