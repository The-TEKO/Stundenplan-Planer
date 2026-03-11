import json

from data_io import build_models, load_data


def test_load_data_reads_valid_json(tmp_path):
    input_file = tmp_path / "input.json"
    payload = {
        "Classes": [{"name": "10A", "student_count": 25}],
        "Courses": [{"name": "Math", "courses_per_weak": 2, "classes": ["10A"]}],
        "Teachers": [{"name": "T1", "abbreviation": "T1", "courses": ["Math"]}],
        "Rooms": [{"name": "R1", "capacity": 30, "accepted_courses": ["Math"]}],
        "Timeslots": [{"day": "Monday", "lesson_times": ["08:00-08:45"]}],
    }

    input_file.write_text(json.dumps(payload), encoding="utf-8")

    loaded = load_data(input_file)
    assert loaded["Classes"][0]["name"] == "10A"
    assert loaded["Courses"][0]["name"] == "Math"


def test_build_models_creates_expected_objects():
    raw_data = {
        "Classes": [{"name": "10A", "student_count": 25}],
        "Courses": [{"name": "Math", "courses_per_weak": 2, "classes": ["10A"]}],
        "Teachers": [{"name": "Teacher One", "abbreviation": "TO", "courses": ["Math"]}],
        "Rooms": [{"name": "R1", "capacity": 30, "accepted_courses": ["Math"]}],
        "Timeslots": [{"day": "Monday", "lesson_times": ["08:00-08:45"]}],
    }

    model_data = build_models(raw_data)

    assert len(model_data["classes"]) == 1
    assert len(model_data["courses"]) == 1
    assert len(model_data["teachers"]) == 1
    assert len(model_data["rooms"]) == 1

    built_course = model_data["courses"][0]
    assert built_course.name == "Math"
    assert built_course.lessons_per_week == 2
    assert built_course.class_names == ["10A"]
