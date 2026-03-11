# Timetable Planner

This project solves a school timetable problem using **backtracking**.
Every required lesson is modeled as a **Session**.
For each session, the solver searches a valid combination of **timeslot** and **room**.

## Goal

Find a complete, conflict-free assignment for all sessions,
or determine that no solution exists under the current constraints.

## Project Structure

- `input.json`: Source data (classes, courses, teachers, rooms, timeslots)
- `src/models.py`: Data models (`Course`, `Class`, `Teacher`, `Room`, `Timeslot`, `Session`)
- `src/io.py`: JSON loading and conversion into model objects
- `src/timeslot.py`: Timeslot object generation
- `src/constraints.py`: Constraint checks
- `src/solver/backtracking.py`: Recursive backtracking solver
- `src/solver/heuristics.py`: Simple MRV heuristic
- `src/main.py`: Orchestration + console and Excel output

## Solver Flow

1. Load data from `input.json`
2. Build sessions from course/class/lesson definitions
3. Build domains (all allowed `(Timeslot, Room)` combinations per session)
4. Run backtracking
5. Revert the last decision when a conflict is detected
6. Output solution to console and Excel

## Active Constraints

The `constraints_ok` function checks each candidate assignment:

1. **Room capacity**: the room must fit the class size
2. **Room-course compatibility**: the room must allow the course (`accepted_courses`)
3. **No room conflict**: a room cannot be used twice in the same timeslot
4. **No class conflict**: a class cannot attend two sessions in the same timeslot
5. **No teacher conflict**: a teacher cannot teach two sessions in parallel
6. **Consecutive lesson rule**: at most **2 equal lessons in a row** (per class and day)

## Installation

1. Activate a virtual environment (optional, recommended)
2. Install dependencies:

```bash
pip install -r requirements.txt
```

## Run

From the project root:

```bash
python src/main.py
```

## Output

- Console output with all assigned sessions
- Excel file: `output_schedule.xlsx`
  - one `Overview` sheet
  - one sheet per class
  - formatted headers, filters, and freeze panes

## Notes

- The code is intentionally simple and explicit (many direct `if` checks).
- Complex shorthand syntax is avoided to keep the logic easy to understand.