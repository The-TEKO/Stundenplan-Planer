from models import Class, Course, Room, Session, Teacher, Timeslot
from solver.backtracking import solve_timetable


def test_backtracking_finds_solution_for_simple_case():
    class_a = Class("10A", 20)
    course_math = Course("Math", 2, ["10A"])
    teacher = Teacher("Teacher One", ["Math"])
    room = Room("R1", 30, ["Math"])

    session_1 = Session(course_math, class_a, teacher=teacher, lesson_number=1)
    session_2 = Session(course_math, class_a, teacher=teacher, lesson_number=2)

    slot_1 = Timeslot("Monday", "08:00-08:45", index_in_day=0)
    slot_2 = Timeslot("Monday", "08:45-09:30", index_in_day=1)

    sessions = [session_1, session_2]
    domains = {
        session_1: [(slot_1, room), (slot_2, room)],
        session_2: [(slot_1, room), (slot_2, room)],
    }

    solution = solve_timetable(sessions, domains, [teacher])

    assert solution is not None
    assert len(solution) == 2

    first_assignment = solution[session_1]
    second_assignment = solution[session_2]
    first_timeslot = first_assignment[0]
    second_timeslot = second_assignment[0]

    assert first_timeslot.time != second_timeslot.time
