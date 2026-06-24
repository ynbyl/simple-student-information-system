import re


def validate_course_form(form):
    coursecode  = form.get("coursecode", "").strip()
    coursename  = form.get("coursename", "").strip()
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
        "coursecode":  coursecode.upper(),
        "coursename":  coursename,
        "collegecode": collegecode,
    }
