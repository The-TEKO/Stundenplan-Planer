# Handels the generation of time slots for the scheduling system.

def generate_timeslots(days, times) -> list:
    """
    Generates time slot objects based on the provided days and times.

    Args:
        days: A list of days for which to generate time slots.
        times: A list of times for which to generate time slots.
    Returns:
        list: A list of time slot objects generated from the days and times.
    """

    yield