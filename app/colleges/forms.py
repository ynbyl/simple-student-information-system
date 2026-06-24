import re


def validate_college_form(form):
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
