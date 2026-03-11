# Implements all scheduling rules and constraint validation logic.

from collections.abc import Callable, Mapping, Sequence
from typing import Any


def constraints_ok(
    schedule: Mapping[Any, tuple[Any, Any]],
    session: Any,
    timeslot: Any,
    room: Any,
    teachers: Sequence[Any],
    *,
    max_same_session_per_day: int = 2,
    require_consecutive_same_day: bool = True,
    extra_constraints: Sequence[Callable[..., bool]] | None = None,
) -> bool:
    """
    Prüft, ob eine neue Belegung (session, timeslot, room) mit dem aktuellen
    (partiellen) Schedule vereinbar ist.

    Args:
        schedule: Aktuelle Belegung als Mapping
            {session: (timeslot, room)}.
        session: Die Session, die als Nächstes eingeplant werden soll.
        timeslot: Ziel-Zeitfenster für ``session``.
        room: Ziel-Raum für ``session``.
        teachers: Alle verfügbaren Lehrer-Objekte (mit ``name`` und ``courses``).
        max_same_session_per_day: Maximal erlaubte Anzahl gleicher Sessions pro Tag.
        require_consecutive_same_day: Wenn True, müssen doppelte Sessions am
            selben Tag direkt aufeinander folgen.
        extra_constraints: Optional zusätzliche Constraint-Funktionen für Tests.
            Jede Funktion erhält denselben Kontext wie diese Funktion
            (über Keyword-Argumente) und muss ``bool`` zurückgeben.

    Returns:
        bool: True, wenn alle Constraints erfüllt sind, sonst False.
    """

    # Kandidat als neue Belegung auf den aktuellen Zustand projizieren.
    # In Unit-Tests kannst du so gezielt einen einzelnen Schritt validieren.
    proposed = dict(schedule)
    proposed[session] = (timeslot, room)

    # TODO 1: Raum darf im selben Timeslot nur einmal belegt sein.
    # Idee:
    # - Baue einen Index mit Key = (timeslot.day, timeslot.time, room.name).
    # - Sobald ein Key doppelt vorkommt -> False.

    # TODO 2: Lehrer darf nicht zwei Sessions gleichzeitig unterrichten.
    # Benötigt:
    # - Hilfsfunktion: teacher_for_session(session, teachers)
    # - Index mit Key = (timeslot.day, timeslot.time, teacher.name)
    # - Duplikat -> False.

    # TODO 3: Klasse/Schüler dürfen nicht in zwei Sessions gleichzeitig sein.
    # Benötigt:
    # - Key = (timeslot.day, timeslot.time, session.class_.name)
    # - Duplikat -> False.

    # TODO 4: Maximal zwei identische Sessions pro Tag und ggf. zusammenhängend.
    # Vorschlag für Session-Identität:
    # - (session.course.name, session.class_.name)
    # Prüfung:
    # - Pro (Tag, Session-Identität) zählen und gegen max_same_session_per_day prüfen.
    # - Bei require_consecutive_same_day=True: Stundenliste sortieren und nur
    #   direkte Nachbarschaft zulassen.

    if extra_constraints:
        context = {
            "schedule": schedule,
            "proposed": proposed,
            "session": session,
            "timeslot": timeslot,
            "room": room,
            "teachers": teachers,
            "max_same_session_per_day": max_same_session_per_day,
            "require_consecutive_same_day": require_consecutive_same_day,
        }
        for constraint in extra_constraints:
            if not constraint(**context):
                return False

    return True