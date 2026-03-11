# Entry point of the application that coordinates input, solving and output.
"""Main workflow of the timetable planner.

This module orchestrates all steps:
- load input data
- create sessions and domains
- run the backtracking solver
- output results to console and Excel
"""

from pathlib import Path
import time

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


class CuteProgressBar:
    """Small console progress view for the backtracking search."""

    def __init__(self, total):
        self.total = total
        self.started_at = time.time()
        self.last_render_at = 0.0
        self.max_assigned_seen = 0

    def __call__(self, stats):
        now = time.time()
        if now - self.last_render_at < 0.08:
            return

        self.last_render_at = now

        assigned = stats.get("assigned", 0)
        attempts = stats.get("attempts", 0)
        backtracks = stats.get("backtracks", 0)
        max_assigned = stats.get("max_assigned", 0)

        if max_assigned > self.max_assigned_seen:
            self.max_assigned_seen = max_assigned

        percent = 0
        if self.total > 0:
            percent = int((self.max_assigned_seen / self.total) * 100)

        bar_length = 24
        filled = 0
        if self.total > 0:
            filled = int((self.max_assigned_seen / self.total) * bar_length)

        if filled < 0:
            filled = 0
        if filled > bar_length:
            filled = bar_length

        bar = "🩷" * filled + "·" * (bar_length - filled)
        elapsed = time.time() - self.started_at

        text = (
            f"\rPlanning {bar} {percent:>3}% | "
            f"placed {assigned}/{self.total} | tries {attempts} | backtracks {backtracks} | "
            f"{elapsed:0.1f}s ૮ ˶ᵔ ᵕ ᵔ˶ ა"
        )
        print(text, end="", flush=True)

    def finish(self, solved):
        elapsed = time.time() - self.started_at
        if solved:
            print(f"\rPlanning complete in {elapsed:0.2f}s ✨{' ' * 40}")
        else:
            print(f"\rPlanning finished without solution in {elapsed:0.2f}s 🥲{' ' * 20}")


def _reason_count_sort_key(item):
    return item[1]


def print_solver_diagnostics(stats):
    """Prints why assignments were rejected, to analyze dead-ends."""
    if stats is None:
        return

    reason_counts = stats.get("reason_counts", {})
    dead_end_count = stats.get("dead_end_count", 0)

    print("Solver diagnostics:")
    print(
        f"  attempts={stats.get('attempts', 0)}, "
        f"backtracks={stats.get('backtracks', 0)}, "
        f"forward_prunes={stats.get('forward_prunes', 0)}, "
        f"probe_backtrack={stats.get('probe_backtrack_done', False)}, "
        f"probe_backtrack_count={stats.get('probe_backtrack_count', 0)}, "
        f"probe_start_ratio={stats.get('probe_backtrack_start_ratio', 'n/a')}, "
        f"dead_ends={dead_end_count}, "
        f"max_assigned={stats.get('max_assigned', 0)}/{stats.get('total', 0)}"
    )

    if len(reason_counts) > 0:
        reason_labels = {
            "room_capacity": "Room too small",
            "room_course_not_allowed": "Course not allowed in room",
            "room_double_booked": "Room already occupied",
            "class_double_booked": "Class already occupied",
            "teacher_double_booked": "Teacher already occupied",
            "max_same_course_in_row": "More than 2 equal lessons in a row",
        }

        reason_items = list(reason_counts.items())
        reason_items.sort(key=_reason_count_sort_key, reverse=True)

        print("  top_reasons:")
        top_n = 6
        for index, reason_and_count in enumerate(reason_items):
            if index >= top_n:
                break
            reason_key = reason_and_count[0]
            count = reason_and_count[1]
            label = reason_key
            if reason_key in reason_labels:
                label = reason_labels[reason_key]
            print(f"    - {label}: {count}")

    last_dead_end = stats.get("last_dead_end")
    if last_dead_end is not None:
        triggered_by = last_dead_end.get("triggered_by")
        triggered_text = ""
        if triggered_by is not None:
            triggered_text = (
                f", triggered_by={triggered_by.get('class')}:{triggered_by.get('course')}"
            )
        print(
            f"  last_dead_end: class={last_dead_end.get('class')}, "
            f"course={last_dead_end.get('course')}, "
            f"domain={last_dead_end.get('domain_size')}"
            f"{triggered_text}"
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

    progress_bar = CuteProgressBar(total=len(sessions))
    solver_stats = {}
    solution = backtracking_search(
        sessions,
        domains,
        model_data["teachers"],
        progress_callback=progress_bar,
        stats_out=solver_stats,
    )
    progress_bar.finish(solution is not None)
    print_solver_diagnostics(solver_stats)

    print_schedule(solution)

    output_excel = data_dir / "output_schedule.xlsx"
    export_schedule_to_excel(
        schedule=solution,
        output_path=output_excel,
        timeslots=timeslots,
        classes=model_data["classes"],
    )
    print(f"Excel export erstellt: {output_excel}")

if __name__ == "__main__":
    main()