# Entry point of the application that coordinates input, solving and output.
from models import Course, Session, Teacher, Room, Timeslot
from timeslot import generate_timeslots
from io import load_data
from debug import debug

def create_sessions(courses) -> list:
    """
    Creates session objects based on the Courses.
    These Sessions then have to be assigned to time slots and rooms while respecting the constraints.
    
    Args:       
        courses: The list of courses to create sessions for.

    Returns:
        list: A list of session objects created from the courses.
    """

    sessions = []
    for course in courses:
        for i in range(course.lessons_per_week):
            _course = Course(str(i) + course.name, course.lessons_per_week)
            debug(f"Created session for course: {_course.name} with {course.lessons_per_week} lessons per week")
            sessions.append(Session(_course, None))  # TODO: The class_ attribute should be assigned properly based on the input data


    yield

def create_domains(sessions, timeslots, rooms) -> list:
    """
    Creates all possible time slot and room combinations for the sessions. This will be used as the domain for the constraint satisfaction problem.

    Args:
        sessions: The list of session objects for which to create the domains.
        timeslots: The list of available time slots.
        rooms: The list of available rooms.

    Returns:
        list: A list of all possible time slot and room combinations.
    """

    yield


def main():

    data = load_data("input.json")
    timeslots = generate_timeslots(days=["Monday", "Tuesday", "Wednesday", "Thursday", "Friday"], times=["08:00-09:00", "09:00-10:00", "10:00-11:00", "11:00-12:00"])



    yield

if __name__ == "__main__":
    main()