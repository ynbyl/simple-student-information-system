import re


def validate_student_form(form, is_update=False):
    student_id = form.get("id", "").strip()
    first_name = form.get("first_name", "").strip()
    last_name  = form.get("last_name", "").strip()
    year_level = form.get("year_level", "").strip()
    gender     = form.get("gender", "").strip()
    coursecode = form.get("coursecode", "").strip()

    if not is_update:
        if not student_id:
            raise ValueError("Student ID is required.")
        if not re.fullmatch(r"\d{4}-\d{4}", student_id):
            raise ValueError("Student ID must follow the format YYYY-NNNN (e.g. 2021-0228).")

    if not first_name:
        raise ValueError("First name is required.")
    if re.search(r"\d", first_name):
        raise ValueError("First name must not contain numbers.")
    if not last_name:
        raise ValueError("Last name is required.")
    if re.search(r"\d", last_name):
        raise ValueError("Last name must not contain numbers.")
    if not year_level.isdigit() or int(year_level) not in range(1, 5):
        raise ValueError("Year level must be 1, 2, 3, or 4.")
    if gender not in ("Male", "Female"):
        raise ValueError("Gender must be Male or Female.")
    if not coursecode:
        raise ValueError("Course code is required.")

    return {
        "id":         student_id,
        "first_name": first_name,
        "last_name":  last_name,
        "year_level": int(year_level),
        "gender":     gender,
        "coursecode": coursecode,
    }
