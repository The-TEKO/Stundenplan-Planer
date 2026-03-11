"""Timeslot generation utilities for the scheduling system."""

from models import Timeslot


def generate_timeslots(days=None, times=None, timeslot_definitions=None) -> list:
    """
    Generates timeslot objects.

    The function supports two modes:
    1) `timeslot_definitions` from JSON input
    2) `days` + `times` fallback generation

    Args:
        days: List of days for fallback generation.
        times: List of times for fallback generation.
        timeslot_definitions: Raw per-day timeslot definitions from input.

    Returns:
        list: A list of `Timeslot` objects.
    """

    result = []

    if timeslot_definitions is not None:
        for day_definition in timeslot_definitions:
            day = day_definition["day"]
            lesson_times = day_definition["lesson_times"]

            index = 0
            for lesson_time in lesson_times:
                result.append(Timeslot(day, lesson_time, index_in_day=index))
                index = index + 1

        return result

    if days is None:
        return result
    if times is None:
        return result

    for day in days:
        index = 0
        for time in times:
            result.append(Timeslot(day, time, index_in_day=index))
            index = index + 1

    return result