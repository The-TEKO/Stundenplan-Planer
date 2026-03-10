# Entry point of the application that coordinates input, solving and output.
from models import Session

def create_sessions(courses) -> list:
    """
    Creates session objects based on the Courses.
    These Sessions then have to be assigned to time slots and rooms while respecting the constraints.
    
    Args:       
        courses: The list of courses to create sessions for.

    Returns:
        list: A list of session objects created from the courses.
    """


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

    

    yield

if __name__ == "__main__":
    main()