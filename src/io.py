# Handles loading and validating input data from JSON files.
"""Input/output helpers for loading JSON and building model objects."""

import json
from pathlib import Path

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

# Example usage
if __name__ == "__main__":
    data = load_data("input.json")
    model_data = build_models(data)
    print(f"Classes: {len(model_data['classes'])}")
    print(f"Courses: {len(model_data['courses'])}")



