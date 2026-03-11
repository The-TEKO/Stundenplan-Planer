from constraints import constraints_ok
from models import Class, Course, Room, Session, Teacher, Timeslot


def _create_base_objects():
    class_a = Class("10A", 25)
    math_course = Course("Math", 3, ["10A"])
    teacher = Teacher("Teacher One", ["Math"])
    room = Room("R1", 30, ["Math"])
    return class_a, math_course, teacher, room


def test_constraints_reject_room_with_too_small_capacity():
    class_a = Class("10A", 28)
    math_course = Course("Math", 1, ["10A"])
    teacher = Teacher("Teacher One", ["Math"])
    small_room = Room("R1", 10, ["Math"])
    session = Session(math_course, class_a, teacher=teacher, lesson_number=1)
    timeslot = Timeslot("Monday", "08:00-08:45", index_in_day=0)

    valid = constraints_ok({}, session, timeslot, small_room, [teacher])
    assert valid is False


def test_constraints_reject_teacher_conflict_in_same_timeslot():
    class_a, math_course, teacher, room = _create_base_objects()
    class_b = Class("10B", 22)

    first_session = Session(math_course, class_a, teacher=teacher, lesson_number=1)
    second_session = Session(math_course, class_b, teacher=teacher, lesson_number=1)

    timeslot = Timeslot("Monday", "08:00-08:45", index_in_day=0)
    schedule = {first_session: (timeslot, room)}

    valid = constraints_ok(schedule, second_session, timeslot, room, [teacher])
    assert valid is False


def test_constraints_allow_two_equal_lessons_in_row():
    class_a, math_course, teacher, room = _create_base_objects()

    first_session = Session(math_course, class_a, teacher=teacher, lesson_number=1)
    second_session = Session(math_course, class_a, teacher=teacher, lesson_number=2)

    first_slot = Timeslot("Monday", "08:00-08:45", index_in_day=0)
    second_slot = Timeslot("Monday", "08:45-09:30", index_in_day=1)

    schedule = {first_session: (first_slot, room)}

    valid = constraints_ok(schedule, second_session, second_slot, room, [teacher])
    assert valid is True


def test_constraints_reject_three_equal_lessons_in_row():
    class_a, math_course, teacher, room = _create_base_objects()

    first_session = Session(math_course, class_a, teacher=teacher, lesson_number=1)
    second_session = Session(math_course, class_a, teacher=teacher, lesson_number=2)
    third_session = Session(math_course, class_a, teacher=teacher, lesson_number=3)

    first_slot = Timeslot("Monday", "08:00-08:45", index_in_day=0)
    second_slot = Timeslot("Monday", "08:45-09:30", index_in_day=1)
    third_slot = Timeslot("Monday", "09:30-10:15", index_in_day=2)

    schedule = {
        first_session: (first_slot, room),
        second_session: (second_slot, room),
    }

    valid = constraints_ok(schedule, third_session, third_slot, room, [teacher])
    assert valid is False
