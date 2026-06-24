from flask import Blueprint, render_template, request, redirect, url_for
from flask_login import login_required

from app.models import (
    get_all_colleges,
    get_college_by_code,
    college_code_exists,
    create_college,
    update_college,
    delete_college,
    search_colleges,
    college_has_courses,
)
from app.colleges.forms import validate_college_form

colleges_bp = Blueprint("colleges", __name__)


@colleges_bp.route("/listColleges")
@login_required
def listColleges():
    message  = request.args.get("message")
    page     = request.args.get("page", 1, type=int)
    sort     = request.args.get("sort", "collegecode")
    order    = request.args.get("order", "asc")
    per_page = 10

    valid_sorts = {"collegecode", "collegename"}
    if sort not in valid_sorts:
        sort = "collegecode"
    if order not in ("asc", "desc"):
        order = "asc"

    all_colleges = get_all_colleges()
    all_colleges.sort(key=lambda c: (c.get(sort) or ""), reverse=(order == "desc"))

    total       = len(all_colleges)
    total_pages = max(1, (total + per_page - 1) // per_page)
    page        = max(1, min(page, total_pages))
    colleges    = all_colleges[(page - 1) * per_page: page * per_page]

    return render_template(
        "colleges/list.html",
        colleges=colleges,
        message=message,
        page=page,
        total_pages=total_pages,
        total=total,
        sort=sort,
        order=order,
    )


@colleges_bp.route("/addCollege", methods=["GET", "POST"])
@login_required
def addCollege():
    if request.method == "POST":
        try:
            data = validate_college_form(request.form)
        except ValueError as exc:
            return render_template("colleges/add.html", message=str(exc))

        if college_code_exists(data["collegecode"]):
            return render_template(
                "colleges/add.html",
                message="A college with that code already exists.",
            )

        create_college(data["collegecode"], data["collegename"])
        return redirect(url_for("colleges.listColleges"))

    return render_template("colleges/add.html")


@colleges_bp.route("/updateCollege/<string:collegecode>", methods=["GET", "POST"])
@login_required
def updateCollege(collegecode):
    college = get_college_by_code(collegecode)
    if not college:
        return redirect(url_for("colleges.listColleges"))

    if request.method == "POST":
        try:
            data = validate_college_form(request.form)
        except ValueError as exc:
            return render_template(
                "colleges/update.html", message=str(exc), college=college
            )

        update_college(collegecode, data["collegename"])
        return redirect(url_for("colleges.listColleges"))

    return render_template("colleges/update.html", college=college)


@colleges_bp.route("/deleteCollege/<string:collegecode>")
@login_required
def deleteCollege(collegecode):
    if college_has_courses(collegecode):
        return redirect(url_for(
            "colleges.listColleges",
            message=f"Cannot delete college '{collegecode}' — it still has courses assigned to it. Remove or reassign those courses first."
        ))
    delete_college(collegecode)
    return redirect(url_for("colleges.listColleges"))


@colleges_bp.route("/search", methods=["GET"])
@login_required
def search_colleges_route():
    query    = request.args.get("query", "").strip()
    page     = request.args.get("page", 1, type=int)
    sort     = request.args.get("sort", "collegecode")
    order    = request.args.get("order", "asc")
    per_page = 10

    valid_sorts = {"collegecode", "collegename"}
    if sort not in valid_sorts:
        sort = "collegecode"
    if order not in ("asc", "desc"):
        order = "asc"

    all_results = search_colleges(query) if query else []
    all_results.sort(key=lambda c: (c.get(sort) or ""), reverse=(order == "desc"))

    total       = len(all_results)
    total_pages = max(1, (total + per_page - 1) // per_page)
    page        = max(1, min(page, total_pages))
    colleges    = all_results[(page - 1) * per_page: page * per_page]

    return render_template(
        "colleges/list.html",
        colleges=colleges,
        search_query=query,
        page=page,
        total_pages=total_pages,
        total=total,
        sort=sort,
        order=order,
    )

