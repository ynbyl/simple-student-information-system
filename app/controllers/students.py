# this handles all the routes for students
# add, update, delete, search students

import os

import cloudinary
import cloudinary.uploader
from dotenv import load_dotenv
from flask import Blueprint, render_template, request, redirect, url_for

from app.models import (
    get_all_students,
    get_student_by_id,
    student_id_exists,
    create_student,
    update_student,
    delete_student,
    search_students,
    get_all_courses,
)
from app.forms import validate_student_form

# load .env to get cloudinary credentials
load_dotenv(override=True)

students_bp = Blueprint("students", __name__)

# default photo if student has no profile picture
# using svg so no internet needed for the placeholder
DEFAULT_PHOTO = (
    "data:image/svg+xml,%3Csvg xmlns='http://www.w3.org/2000/svg' viewBox='0 0 48 48'%3E"
    "%3Crect width='48' height='48' rx='4' fill='%23111'/%3E"
    "%3Ccircle cx='24' cy='17' r='9' fill='%23777'/%3E"
    "%3Cpath d='M6 43c0-9.941 8.059-18 18-18s18 8.059 18 18' fill='%23777'/%3E"
    "%3C/svg%3E"
)


def _upload_photo(file_storage):
    # upload the photo to cloudinary and return the url
    # returns None if no photo was selected
    if not file_storage or file_storage.filename == "":
        return None

    # configure cloudinary using credentials from .env
    cloudinary.config(
        cloud_name=os.getenv("CLOUDINARY_CLOUD_NAME"),
        api_key=os.getenv("CLOUDINARY_API_KEY"),
        api_secret=os.getenv("CLOUDINARY_API_SECRET"),
        secure=True,
    )

    # read file as bytes so cloudinary can process it
    file_bytes = file_storage.read()
    if not file_bytes:
        return None

    result = cloudinary.uploader.upload(
        file_bytes,
        folder="ssis_students",
        resource_type="image",
        transformation=[
            {"width": 400, "height": 400, "crop": "fill", "gravity": "face"},
        ],
    )
    return result.get("secure_url")


@students_bp.route("/")
def index():
    # show the list of all students with pagination and sorting
    message = request.args.get("message")
    page = request.args.get("page", 1, type=int)
    sort = request.args.get("sort", "id")
    order = request.args.get("order", "asc")
    per_page = 10

    valid_sorts = {"id", "first_name", "last_name", "gender", "year_level", "coursecode"}
    if sort not in valid_sorts:
        sort = "id"
    if order not in ("asc", "desc"):
        order = "asc"

    all_students = get_all_students()

    # sort the list
    reverse = order == "desc"
    all_students.sort(key=lambda s: (s[sort] or ""), reverse=reverse)

    total = len(all_students)
    total_pages = max(1, (total + per_page - 1) // per_page)
    page = max(1, min(page, total_pages))

    start = (page - 1) * per_page
    students = all_students[start:start + per_page]

    return render_template(
        "students/list.html",
        students=students,
        message=message,
        default_photo=DEFAULT_PHOTO,
        page=page,
        total_pages=total_pages,
        total=total,
        sort=sort,
        order=order,
    )


@students_bp.route("/addStudent", methods=["GET", "POST"])
def addStudent():
    # add a new student
    if request.method == "POST":
        try:
            data = validate_student_form(request.form)
        except ValueError as exc:
            courses = get_all_courses()
            return render_template("students/add.html", message=str(exc), courses=courses)

        # make sure the student id isnt already taken
        if student_id_exists(data["id"]):
            courses = get_all_courses()
            return render_template(
                "students/add.html",
                message="A student with that ID already exists.",
                courses=courses,
            )

        # upload photo if one was attached
        photo_url = _upload_photo(request.files.get("photo"))

        create_student(
            data["id"],
            data["first_name"],
            data["last_name"],
            data["year_level"],
            data["gender"],
            data["coursecode"],
            photo_url,
        )
        return redirect(url_for("students.index"))

    courses = get_all_courses()
    return render_template("students/add.html", courses=courses)


@students_bp.route("/updateStudent/<string:id>", methods=["GET", "POST"])
def updateStudent(id):
    # edit an existing student
    student = get_student_by_id(id)
    if not student:
        return redirect(url_for("students.index"))

    if request.method == "POST":
        try:
            data = validate_student_form(request.form, is_update=True)
        except ValueError as exc:
            courses = get_all_courses()
            return render_template(
                "students/update.html", message=str(exc), student=student, courses=courses
            )

        # only upload if a new photo was chosen, otherwise keep the old one
        photo_url = _upload_photo(request.files.get("photo"))

        update_student(
            id,
            data["first_name"],
            data["last_name"],
            data["year_level"],
            data["gender"],
            data["coursecode"],
            photo_url,
        )
        return redirect(url_for("students.index"))

    courses = get_all_courses()
    return render_template(
        "students/update.html",
        student=student,
        courses=courses,
        default_photo=DEFAULT_PHOTO,
    )


@students_bp.route("/deleteStudent/<string:id>")
def deleteStudent(id):
    # delete a student
    delete_student(id)
    return redirect(url_for("students.index"))


@students_bp.route("/search-students", methods=["GET"])
def search_students_route():
    # search for students with pagination and sorting
    query = request.args.get("query", "").strip()
    page = request.args.get("page", 1, type=int)
    sort = request.args.get("sort", "id")
    order = request.args.get("order", "asc")
    per_page = 10

    valid_sorts = {"id", "first_name", "last_name", "gender", "year_level", "coursecode"}
    if sort not in valid_sorts:
        sort = "id"
    if order not in ("asc", "desc"):
        order = "asc"

    all_results = search_students(query) if query else []

    reverse = order == "desc"
    all_results.sort(key=lambda s: (s[sort] or ""), reverse=reverse)

    total = len(all_results)
    total_pages = max(1, (total + per_page - 1) // per_page)
    page = max(1, min(page, total_pages))

    start = (page - 1) * per_page
    students = all_results[start:start + per_page]

    return render_template(
        "students/list.html",
        students=students,
        search_query=query,
        default_photo=DEFAULT_PHOTO,
        page=page,
        total_pages=total_pages,
        total=total,
        sort=sort,
        order=order,
    )
