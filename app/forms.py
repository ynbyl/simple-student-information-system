# this file validates the form inputs before saving to database
# each function checks one type of form (student, course, college)

import re


def validate_student_form(form, is_update=False):
    # get all the values from the form
    student_id = form.get("id", "").strip()
    first_name = form.get("first_name", "").strip()
    last_name = form.get("last_name", "").strip()
    year_level = form.get("year_level", "").strip()
    gender = form.get("gender", "").strip()
    coursecode = form.get("coursecode", "").strip()

    # id is only required when adding, not when updating
    if not is_update:
        if not student_id:
            raise ValueError("Student ID is required.")
        # must match YYYY-NNNN exactly, e.g. 2021-0228
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
        "id": student_id,
        "first_name": first_name,
        "last_name": last_name,
        "year_level": int(year_level),
        "gender": gender,
        "coursecode": coursecode,
    }


def validate_course_form(form):
    # check course form fields
    coursecode = form.get("coursecode", "").strip()
    coursename = form.get("coursename", "").strip()
    collegecode = form.get("collegecode", "").strip()

    if not coursecode:
        raise ValueError("Course code is required.")
    if re.search(r"\d", coursecode):
        raise ValueError("Course code must not contain numbers.")
    if not coursename:
        raise ValueError("Course name is required.")
    if re.search(r"\d", coursename):
        raise ValueError("Course name must not contain numbers.")
    if not collegecode:
        raise ValueError("College code is required.")

    return {
        "coursecode": coursecode.upper(),
        "coursename": coursename,
        "collegecode": collegecode,
    }


def validate_college_form(form):
    # check college form fields
    collegecode = form.get("collegecode", "").strip()
    collegename = form.get("collegename", "").strip()

    if not collegecode:
        raise ValueError("College code is required.")
    if re.search(r"\d", collegecode):
        raise ValueError("College code must not contain numbers.")
    if not collegename:
        raise ValueError("College name is required.")
    if re.search(r"\d", collegename):
        raise ValueError("College name must not contain numbers.")

    return {
        "collegecode": collegecode.upper(),
        "collegename": collegename,
    }
