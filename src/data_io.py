# Handles loading and validating input data from JSON files.
"""Input/output helpers for loading JSON and building model objects."""

import json
from pathlib import Path

from openpyxl import Workbook
from openpyxl.styles import Alignment, Border, Font, PatternFill, Side

from models import Class, Course, Room, Teacher


def load_data(file_path):
    """
    Loads data from a JSON file and validates its structure.

    Args:
        file_path: The path to the JSON file containing the input data.
    Returns:
        dict: A dictionary containing the loaded and validated data.
    Raises:
        ValueError: If the JSON file is malformed or missing required fields.
    """
    try:
        path = Path(file_path)
        with open(path, 'r', encoding='utf-8') as f:
            data = json.load(f)

        if "Classes" not in data:
            raise ValueError("Missing key: Classes")
        if "Courses" not in data:
            raise ValueError("Missing key: Courses")
        if "Teachers" not in data:
            raise ValueError("Missing key: Teachers")
        if "Rooms" not in data:
            raise ValueError("Missing key: Rooms")
        if "Timeslots" not in data:
            raise ValueError("Missing key: Timeslots")

        return data
    except Exception as e:
        raise ValueError(f"Error loading JSON: {e}")


def build_models(data):
    """Converts raw JSON data into internal model objects.

    Args:
        data: Parsed JSON dictionary from `input.json`.

    Returns:
        A dictionary containing all built objects and lookup maps.
    """
    classes = []
    classes_by_name = {}

    for class_data in data["Classes"]:
        class_name = class_data["name"]
        student_count = class_data["student_count"]
        class_obj = Class(class_name, student_count)
        classes.append(class_obj)
        classes_by_name[class_name] = class_obj

    courses = []
    for course_data in data["Courses"]:
        lessons_per_week = 0
        if "lessons_per_week" in course_data:
            lessons_per_week = course_data["lessons_per_week"]
        elif "courses_per_weak" in course_data:
            lessons_per_week = course_data["courses_per_weak"]
        else:
            raise ValueError(f"Course '{course_data.get('name')}' misses lessons key")

        class_names = []
        if "classes" in course_data:
            for class_name in course_data["classes"]:
                class_names.append(class_name)

        course_obj = Course(course_data["name"], lessons_per_week, class_names)
        courses.append(course_obj)

    teachers = []
    for teacher_data in data["Teachers"]:
        abbreviation = None
        if "abbreviation" in teacher_data:
            abbreviation = teacher_data["abbreviation"]

        teacher_obj = Teacher(
            teacher_data["name"],
            teacher_data["courses"],
            abbreviation=abbreviation,
        )
        teachers.append(teacher_obj)

    rooms = []
    for room_data in data["Rooms"]:
        accepted_courses = []
        if "accepted_courses" in room_data:
            for accepted_course in room_data["accepted_courses"]:
                accepted_courses.append(accepted_course)

        room_obj = Room(room_data["name"], room_data["capacity"], accepted_courses)
        rooms.append(room_obj)

    return {
        "classes": classes,
        "classes_by_name": classes_by_name,
        "courses": courses,
        "teachers": teachers,
        "rooms": rooms,
        "timeslots": data["Timeslots"],
    }


def _sort_assignments_key(item):
    session = item[0]
    assignment = item[1]
    timeslot = assignment[0]
    return (session.class_.name, timeslot.day, timeslot.index_in_day, timeslot.time, session.course.name)


def _sort_class_row_key(item, day_order):
    session = item[0]
    assignment = item[1]
    timeslot = assignment[0]
    return (
        day_order.get(timeslot.day, 999),
        timeslot.index_in_day,
        timeslot.time,
        session.course.name,
    )


def _first_tuple_value(item):
    return item[0]


def export_schedule_to_excel(schedule, output_path):
    """Exports the solution as a formatted Excel workbook.

    Structure:
    - one `Overview` sheet with all lessons
    - one sheet per class
    - formatted headers, borders, filters, and frozen header row
    """
    if schedule is None:
        return

    workbook = Workbook()
    overview_sheet = workbook.active
    overview_sheet.title = "Übersicht"

    day_order = {
        "Monday": 1,
        "Tuesday": 2,
        "Wednesday": 3,
        "Thursday": 4,
        "Friday": 5,
        "Saturday": 6,
        "Sunday": 7,
    }

    thin_border = Border(
        left=Side(style="thin", color="D9D9D9"),
        right=Side(style="thin", color="D9D9D9"),
        top=Side(style="thin", color="D9D9D9"),
        bottom=Side(style="thin", color="D9D9D9"),
    )
    header_fill = PatternFill(fill_type="solid", fgColor="1F4E78")
    header_font = Font(color="FFFFFF", bold=True)
    title_fill = PatternFill(fill_type="solid", fgColor="D9E1F2")
    title_font = Font(size=14, bold=True)

    sorted_items = list(schedule.items())
    sorted_items.sort(key=_sort_assignments_key)

    overview_sheet.merge_cells("A1:G1")
    overview_sheet["A1"] = "Stundenplan"
    overview_sheet["A1"].font = title_font
    overview_sheet["A1"].fill = title_fill
    overview_sheet["A1"].alignment = Alignment(horizontal="center", vertical="center")

    headers = ["Klasse", "Tag", "Zeit", "Fach", "Lektion", "Raum", "Lehrperson"]
    header_row = 3
    column_index = 1
    for header in headers:
        cell = overview_sheet.cell(row=header_row, column=column_index, value=header)
        cell.font = header_font
        cell.fill = header_fill
        cell.alignment = Alignment(horizontal="center", vertical="center")
        cell.border = thin_border
        column_index = column_index + 1

    row = 4
    class_names = set()
    for session, assignment in sorted_items:
        timeslot = assignment[0]
        room = assignment[1]
        teacher_name = "-"
        if session.teacher is not None:
            teacher_name = session.teacher.name

        class_names.add(session.class_.name)

        values = [
            session.class_.name,
            timeslot.day,
            timeslot.time,
            session.course.name,
            session.lesson_number,
            room.name,
            teacher_name,
        ]

        col = 1
        for value in values:
            cell = overview_sheet.cell(row=row, column=col, value=value)
            cell.border = thin_border
            cell.alignment = Alignment(vertical="center")
            col = col + 1
        row = row + 1

    overview_sheet.freeze_panes = "A4"
    overview_sheet.auto_filter.ref = f"A3:G{row - 1}"
    overview_sheet.column_dimensions["A"].width = 12
    overview_sheet.column_dimensions["B"].width = 14
    overview_sheet.column_dimensions["C"].width = 16
    overview_sheet.column_dimensions["D"].width = 20
    overview_sheet.column_dimensions["E"].width = 10
    overview_sheet.column_dimensions["F"].width = 10
    overview_sheet.column_dimensions["G"].width = 24

    sorted_class_names = list(class_names)
    sorted_class_names.sort()

    for class_name in sorted_class_names:
        safe_sheet_name = class_name
        if len(safe_sheet_name) > 31:
            safe_sheet_name = safe_sheet_name[:31]

        class_sheet = workbook.create_sheet(title=safe_sheet_name)
        class_sheet.merge_cells("A1:F1")
        class_sheet["A1"] = f"Stundenplan {class_name}"
        class_sheet["A1"].font = title_font
        class_sheet["A1"].fill = title_fill
        class_sheet["A1"].alignment = Alignment(horizontal="center", vertical="center")

        class_headers = ["Tag", "Zeit", "Fach", "Lektion", "Raum", "Lehrperson"]
        header_col = 1
        for class_header in class_headers:
            header_cell = class_sheet.cell(row=3, column=header_col, value=class_header)
            header_cell.font = header_font
            header_cell.fill = header_fill
            header_cell.alignment = Alignment(horizontal="center", vertical="center")
            header_cell.border = thin_border
            header_col = header_col + 1

        class_rows = []
        for session, assignment in sorted_items:
            if session.class_.name == class_name:
                class_rows.append((session, assignment))

        class_rows_with_keys = []
        for class_row in class_rows:
            sort_key = _sort_class_row_key(class_row, day_order)
            class_rows_with_keys.append((sort_key, class_row))

        class_rows_with_keys.sort(key=_first_tuple_value)

        class_rows = []
        for key_and_row in class_rows_with_keys:
            class_rows.append(key_and_row[1])

        current_row = 4
        for session, assignment in class_rows:
            timeslot = assignment[0]
            room = assignment[1]
            teacher_name = "-"
            if session.teacher is not None:
                teacher_name = session.teacher.name

            row_values = [
                timeslot.day,
                timeslot.time,
                session.course.name,
                session.lesson_number,
                room.name,
                teacher_name,
            ]

            current_col = 1
            for row_value in row_values:
                row_cell = class_sheet.cell(row=current_row, column=current_col, value=row_value)
                row_cell.border = thin_border
                row_cell.alignment = Alignment(vertical="center")
                current_col = current_col + 1

            current_row = current_row + 1

        class_sheet.freeze_panes = "A4"
        if current_row > 4:
            class_sheet.auto_filter.ref = f"A3:F{current_row - 1}"

        class_sheet.column_dimensions["A"].width = 14
        class_sheet.column_dimensions["B"].width = 16
        class_sheet.column_dimensions["C"].width = 20
        class_sheet.column_dimensions["D"].width = 10
        class_sheet.column_dimensions["E"].width = 10
        class_sheet.column_dimensions["F"].width = 24

    workbook.save(output_path)


# Example usage
if __name__ == "__main__":
    data = load_data("data/input.json")
    model_data = build_models(data)
    print(f"Classes: {len(model_data['classes'])}")
    print(f"Courses: {len(model_data['courses'])}")
