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
)
from app.forms import validate_course_form

courses_bp = Blueprint("courses", __name__)


@courses_bp.route("/listCourses")
def listCourses():
    # show all courses
    courses = get_all_courses()
    message = request.args.get("message")
    return render_template("courses/list.html", courses=courses, message=message)


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
    # delete a course and all students under it will also be deleted
    delete_course(coursecode)
    return redirect(url_for("courses.listCourses"))


@courses_bp.route("/search-courses", methods=["GET"])
def search_courses_route():
    # search for courses
    query = request.args.get("query", "").strip()
    courses = search_courses(query) if query else []
    return render_template("courses/list.html", courses=courses, search_query=query)
