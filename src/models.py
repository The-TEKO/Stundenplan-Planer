# Defines the core data structures such as Course, Teacher, Room and Timeslot.

class Course:
    def __init__(self, name, lessons_per_week):
        self.name = name
        self.lessons_per_week = lessons_per_week

class Class:
    def __init__(self, name, student_count):
        self.name = name
        self.student_count = student_count

class Teacher:
    # TODO: The Teacher class should also include information about their availability
    def __init__(self, name, courses):
        self.name = name
        self.courses = courses

class Room:
    def __init__(self, name, capacity):
        self.name = name
        self.capacity = capacity

class Timeslot:
    def __init__(self, day, time):
        self.day = day
        self.time = time

class Session:
    def __init__(self, course, class_):
        self.course = course
        self.class_ = class_