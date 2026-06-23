# this handles all the routes for courses
# add, update, delete, search courses

from flask import Blueprint, render_template, request, redirect, url_for

from app.models import (
    get_all_courses,
    get_course_by_code,
    course_code_exists,
    create_course,
    update_course,
    delete_course,
    search_courses,
    get_all_colleges,
    course_has_students,
)
from app.forms import validate_course_form

courses_bp = Blueprint("courses", __name__)


@courses_bp.route("/listCourses")
def listCourses():
    # show all courses with pagination and sorting
    message = request.args.get("message")
    page = request.args.get("page", 1, type=int)
    sort = request.args.get("sort", "coursecode")
    order = request.args.get("order", "asc")
    per_page = 10

    valid_sorts = {"coursecode", "coursename", "collegecode"}
    if sort not in valid_sorts:
        sort = "coursecode"
    if order not in ("asc", "desc"):
        order = "asc"

    all_courses = get_all_courses()

    reverse = order == "desc"
    all_courses.sort(key=lambda c: (c.get(sort) or ""), reverse=reverse)

    total = len(all_courses)
    total_pages = max(1, (total + per_page - 1) // per_page)
    page = max(1, min(page, total_pages))

    start = (page - 1) * per_page
    courses = all_courses[start:start + per_page]

    return render_template(
        "courses/list.html",
        courses=courses,
        message=message,
        page=page,
        total_pages=total_pages,
        total=total,
        sort=sort,
        order=order,
    )


@courses_bp.route("/addCourse", methods=["GET", "POST"])
def addCourse():
    # add a new course
    if request.method == "POST":
        try:
            data = validate_course_form(request.form)
        except ValueError as exc:
            colleges = get_all_colleges()
            return render_template("courses/add.html", message=str(exc), colleges=colleges)

        # check if course code already exists
        if course_code_exists(data["coursecode"]):
            colleges = get_all_colleges()
            return render_template(
                "courses/add.html",
                message="That course code already exists.",
                colleges=colleges,
            )

        create_course(data["coursecode"], data["coursename"], data["collegecode"])
        return redirect(url_for("courses.listCourses"))

    # show empty form
    colleges = get_all_colleges()
    return render_template("courses/add.html", colleges=colleges)


@courses_bp.route("/updateCourse/<string:coursecode>", methods=["GET", "POST"])
def updateCourse(coursecode):
    # edit an existing course
    course = get_course_by_code(coursecode)
    if not course:
        return redirect(url_for("courses.listCourses"))

    if request.method == "POST":
        try:
            data = validate_course_form(request.form)
        except ValueError as exc:
            colleges = get_all_colleges()
            return render_template(
                "courses/update.html", message=str(exc), course=course, colleges=colleges
            )

        update_course(coursecode, data["coursename"], data["collegecode"])
        return redirect(url_for("courses.listCourses"))

    # show form prefilled with current data
    colleges = get_all_colleges()
    return render_template("courses/update.html", course=course, colleges=colleges)


@courses_bp.route("/deleteCourse/<string:coursecode>")
def deleteCourse(coursecode):
    # block delete if students are still enrolled in this course
    if course_has_students(coursecode):
        return redirect(url_for(
            "courses.listCourses",
            message=f"Cannot delete course '{coursecode}' — there are students enrolled in it. Remove or reassign them first."
        ))
    delete_course(coursecode)
    return redirect(url_for("courses.listCourses"))


@courses_bp.route("/search-courses", methods=["GET"])
def search_courses_route():
    # search for courses with pagination and sorting
    query = request.args.get("query", "").strip()
    page = request.args.get("page", 1, type=int)
    sort = request.args.get("sort", "coursecode")
    order = request.args.get("order", "asc")
    per_page = 10

    valid_sorts = {"coursecode", "coursename", "collegecode"}
    if sort not in valid_sorts:
        sort = "coursecode"
    if order not in ("asc", "desc"):
        order = "asc"

    all_results = search_courses(query) if query else []

    reverse = order == "desc"
    all_results.sort(key=lambda c: (c.get(sort) or ""), reverse=reverse)

    total = len(all_results)
    total_pages = max(1, (total + per_page - 1) // per_page)
    page = max(1, min(page, total_pages))

    start = (page - 1) * per_page
    courses = all_results[start:start + per_page]

    return render_template(
        "courses/list.html",
        courses=courses,
        search_query=query,
        page=page,
        total_pages=total_pages,
        total=total,
        sort=sort,
        order=order,
    )
