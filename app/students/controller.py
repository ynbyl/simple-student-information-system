import os

import cloudinary
import cloudinary.uploader
from dotenv import load_dotenv
from flask import Blueprint, render_template, request, redirect, url_for, flash
from flask_login import login_required

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
from app.students.forms import validate_student_form

load_dotenv(override=True)

students_bp = Blueprint("students", __name__)

DEFAULT_PHOTO = (
    "data:image/svg+xml,%3Csvg xmlns='http://www.w3.org/2000/svg' viewBox='0 0 48 48'%3E"
    "%3Crect width='48' height='48' rx='4' fill='%23111'/%3E"
    "%3Ccircle cx='24' cy='17' r='9' fill='%23777'/%3E"
    "%3Cpath d='M6 43c0-9.941 8.059-18 18-18s18 8.059 18 18' fill='%23777'/%3E"
    "%3C/svg%3E"
)


ALLOWED_EXTENSIONS = {"jpg", "jpeg", "png", "webp"}
MAX_PHOTO_BYTES    = 5 * 1024 * 1024  # 5 MB


def _upload_photo(file_storage):
    if not file_storage or file_storage.filename == "":
        return None

    # validate file extension
    ext = file_storage.filename.rsplit(".", 1)[-1].lower() if "." in file_storage.filename else ""
    if ext not in ALLOWED_EXTENSIONS:
        raise ValueError(f"Invalid file type '.{ext}'. Allowed: JPG, PNG, WEBP, GIF.")

    file_bytes = file_storage.read()
    if not file_bytes:
        return None

    # validate file size
    if len(file_bytes) > MAX_PHOTO_BYTES:
        raise ValueError("Photo must be 8 MB or smaller.")

    cloudinary.config(
        cloud_name=os.getenv("CLOUDINARY_CLOUD_NAME"),
        api_key=os.getenv("CLOUDINARY_API_KEY"),
        api_secret=os.getenv("CLOUDINARY_API_SECRET"),
        secure=True,
    )

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
@login_required
def index():
    message  = request.args.get("message")
    page     = request.args.get("page", 1, type=int)
    sort     = request.args.get("sort", "id")
    order    = request.args.get("order", "asc")
    per_page = 10

    valid_sorts = {"id", "first_name", "last_name", "gender", "year_level", "coursecode"}
    if sort not in valid_sorts:
        sort = "id"
    if order not in ("asc", "desc"):
        order = "asc"

    all_students = get_all_students()
    all_students.sort(key=lambda s: (s[sort] or ""), reverse=(order == "desc"))

    total       = len(all_students)
    total_pages = max(1, (total + per_page - 1) // per_page)
    page        = max(1, min(page, total_pages))
    students    = all_students[(page - 1) * per_page: page * per_page]

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
@login_required
def addStudent():
    if request.method == "POST":
        try:
            data = validate_student_form(request.form)
        except ValueError as exc:
            courses = get_all_courses()
            return render_template("students/add.html", message=str(exc), courses=courses)

        if student_id_exists(data["id"]):
            courses = get_all_courses()
            return render_template(
                "students/add.html",
                message="A student with that ID already exists.",
                courses=courses,
            )

        photo_url = None
        try:
            photo_url = _upload_photo(request.files.get("photo"))
        except ValueError as exc:
            courses = get_all_courses()
            return render_template("students/add.html", message=str(exc), courses=courses)

        create_student(
            data["id"], data["first_name"], data["last_name"],
            data["year_level"], data["gender"], data["coursecode"], photo_url,
        )
        flash(f"Student {data['first_name']} {data['last_name']} added successfully.", "success")
        return redirect(url_for("students.index"))

    courses = get_all_courses()
    return render_template("students/add.html", courses=courses)


@students_bp.route("/updateStudent/<string:id>", methods=["GET", "POST"])
@login_required
def updateStudent(id):
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

        photo_url = None
        try:
            photo_url = _upload_photo(request.files.get("photo"))
        except ValueError as exc:
            courses = get_all_courses()
            return render_template(
                "students/update.html", message=str(exc), student=student, courses=courses,
                default_photo=DEFAULT_PHOTO,
            )

        # if no new upload:
        # - remove_photo flag set => clear to NULL
        # - otherwise keep existing (pass None so model won't touch it)
        if not photo_url:
            photo_url = "" if request.form.get("remove_photo") else None

        update_student(
            id, data["first_name"], data["last_name"],
            data["year_level"], data["gender"], data["coursecode"], photo_url,
        )
        flash(f"Student {data['first_name']} {data['last_name']} updated successfully.", "success")
        return redirect(url_for("students.index"))

    courses = get_all_courses()
    return render_template(
        "students/update.html",
        student=student,
        courses=courses,
        default_photo=DEFAULT_PHOTO,
    )


@students_bp.route("/deleteStudent/<string:id>")
@login_required
def deleteStudent(id):
    student = get_student_by_id(id)
    name = f"{student['first_name']} {student['last_name']}" if student else id
    delete_student(id)
    flash(f"Student {name} deleted successfully.", "success")
    return redirect(url_for("students.index"))


@students_bp.route("/search-students", methods=["GET"])
@login_required
def search_students_route():
    query    = request.args.get("query", "").strip()
    page     = request.args.get("page", 1, type=int)
    sort     = request.args.get("sort", "id")
    order    = request.args.get("order", "asc")
    per_page = 10

    valid_sorts = {"id", "first_name", "last_name", "gender", "year_level", "coursecode"}
    if sort not in valid_sorts:
        sort = "id"
    if order not in ("asc", "desc"):
        order = "asc"

    all_results = search_students(query) if query else []
    all_results.sort(key=lambda s: (s[sort] or ""), reverse=(order == "desc"))

    total       = len(all_results)
    total_pages = max(1, (total + per_page - 1) // per_page)
    page        = max(1, min(page, total_pages))
    students    = all_results[(page - 1) * per_page: page * per_page]

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

