# Entry point of the application that coordinates input, solving and output.
"""Main workflow of the timetable planner.

This module orchestrates all steps:
- load input data
- create sessions and domains
- run the backtracking solver
- output results to console and Excel
"""

from pathlib import Path

from data_io import build_models, export_schedule_to_excel, load_data
from constraints import teacher_for_course
from models import Session
from solver.backtracking import backtracking_search
from timeslot import generate_timeslots
from debug import debug


def create_sessions(courses, classes_by_name, teachers) -> list:
    """
    Creates session objects based on the Courses.
    These Sessions then have to be assigned to time slots and rooms while respecting the constraints.
    
    Args:       
        courses: The list of courses to create sessions for.
        classes_by_name: Mapping from class name to class object.
        teachers: Teacher list used to resolve session teacher.

    Returns:
        list: A list of session objects created from the courses.
    """

    sessions = []
    for course in courses:
        teacher = teacher_for_course(course.name, teachers)

        for class_name in course.class_names:
            if class_name not in classes_by_name:
                continue

            class_obj = classes_by_name[class_name]

            lesson_number = 1
            while lesson_number <= course.lessons_per_week:
                session = Session(
                    course=course,
                    class_=class_obj,
                    teacher=teacher,
                    lesson_number=lesson_number,
                )
                sessions.append(session)
                lesson_number = lesson_number + 1

    return sessions

def create_domains(sessions, timeslots, rooms) -> list:
    """
    Creates all possible time slot and room combinations for the sessions. This will be used as the domain for the constraint satisfaction problem.

    Args:
        sessions: The list of session objects for which to create the domains.
        timeslots: The list of available time slots.
        rooms: The list of available rooms.

    Returns:
        list: A dictionary with session as key and list[(timeslot, room)] as value.
    """

    domains = {}

    for session in sessions:
        domains[session] = []

        for timeslot in timeslots:
            for room in rooms:
                if room.capacity < session.class_.student_count:
                    continue

                if len(room.accepted_courses) > 0:
                    accepted = False
                    for accepted_course in room.accepted_courses:
                        if accepted_course == session.course.name:
                            accepted = True
                            break
                    if not accepted:
                        continue

                domains[session].append((timeslot, room))

    return domains


def _sort_assignments_key(item):
    """Sort key for stable, readable console output."""
    session = item[0]
    assignment = item[1]
    timeslot = assignment[0]
    return (session.class_.name, timeslot.day, timeslot.index_in_day, timeslot.time, session.course.name)


def print_schedule(schedule):
    """Prints the generated timetable to the console."""
    if schedule is None:
        print("Keine Lösung gefunden.")
        return

    print("Lösung gefunden. Belegte Sessions:")
    sorted_items = list(schedule.items())
    sorted_items.sort(key=_sort_assignments_key)

    for session, assignment in sorted_items:
        timeslot = assignment[0]
        room = assignment[1]
        teacher_name = "-"
        if session.teacher is not None:
            teacher_name = session.teacher.name

        print(
            f"{session.class_.name} | {timeslot.day} {timeslot.time} | "
            f"{session.course.name} (Lektion {session.lesson_number}) | "
            f"Raum {room.name} | Lehrperson {teacher_name}"
        )


def main():
    """Runs the full planning process and writes the Excel output."""
    project_root = Path(__file__).resolve().parent.parent
    data_dir = project_root / "data"
    data_dir.mkdir(parents=True, exist_ok=True)

    input_path = data_dir / "input.json"

    data = load_data(input_path)
    model_data = build_models(data)

    timeslots = generate_timeslots(timeslot_definitions=model_data["timeslots"])
    sessions = create_sessions(
        courses=model_data["courses"],
        classes_by_name=model_data["classes_by_name"],
        teachers=model_data["teachers"],
    )
    domains = create_domains(sessions, timeslots, model_data["rooms"])

    debug(f"Timeslots: {len(timeslots)}")
    debug(f"Sessions: {len(sessions)}")

    solution = backtracking_search(sessions, domains, model_data["teachers"])
    print_schedule(solution)

    output_excel = data_dir / "output_schedule.xlsx"
    export_schedule_to_excel(solution, output_excel)
    print(f"Excel export erstellt: {output_excel}")

if __name__ == "__main__":
    main()