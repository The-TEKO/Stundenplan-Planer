# Defines the core data structures such as Course, Teacher, Room and Timeslot.
"""Core domain models used by the timetable solver."""

class Course:
    """Represents a school course and its weekly lesson count."""
    def __init__(self, name, lessons_per_week, class_names=None):
        self.name = name
        self.lessons_per_week = lessons_per_week
        if class_names is None:
            self.class_names = []
        else:
            self.class_names = class_names

class Class:
    """Represents one school class and its student count."""
    def __init__(self, name, student_count):
        self.name = name
        self.student_count = student_count

class Teacher:
    """Represents a teacher and the courses they can teach."""
    def __init__(self, name, courses, abbreviation=None):
        self.name = name
        self.courses = courses
        self.abbreviation = abbreviation

class Room:
    """Represents a classroom with capacity and allowed courses."""
    def __init__(self, name, capacity, accepted_courses=None):
        self.name = name
        self.capacity = capacity
        if accepted_courses is None:
            self.accepted_courses = []
        else:
            self.accepted_courses = accepted_courses

class Timeslot:
    """Represents one period in a specific day."""
    def __init__(self, day, time, index_in_day=0):
        self.day = day
        self.time = time
        self.index_in_day = index_in_day

class Session:
    """Represents one concrete lesson instance that must be scheduled."""
    def __init__(self, course, class_, teacher=None, lesson_number=1):
        self.course = course
        self.class_ = class_
        self.teacher = teacher
        self.lesson_number = lesson_number