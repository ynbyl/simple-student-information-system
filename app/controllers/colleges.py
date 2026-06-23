# this handles all the routes for colleges
# add, update, delete, search colleges

from flask import Blueprint, render_template, request, redirect, url_for

from app.models import (
    get_all_colleges,
    get_college_by_code,
    college_code_exists,
    create_college,
    update_college,
    delete_college,
    search_colleges,
)
from app.forms import validate_college_form

colleges_bp = Blueprint("colleges", __name__)


@colleges_bp.route("/listColleges")
def listColleges():
    # show all colleges with pagination and sorting
    message = request.args.get("message")
    page = request.args.get("page", 1, type=int)
    sort = request.args.get("sort", "collegecode")
    order = request.args.get("order", "asc")
    per_page = 10

    valid_sorts = {"collegecode", "collegename"}
    if sort not in valid_sorts:
        sort = "collegecode"
    if order not in ("asc", "desc"):
        order = "asc"

    all_colleges = get_all_colleges()

    reverse = order == "desc"
    all_colleges.sort(key=lambda c: (c.get(sort) or ""), reverse=reverse)

    total = len(all_colleges)
    total_pages = max(1, (total + per_page - 1) // per_page)
    page = max(1, min(page, total_pages))

    start = (page - 1) * per_page
    colleges = all_colleges[start:start + per_page]

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
def addCollege():
    # add a new college
    if request.method == "POST":
        try:
            data = validate_college_form(request.form)
        except ValueError as exc:
            return render_template("colleges/add.html", message=str(exc))

        # check if that college code is already taken
        if college_code_exists(data["collegecode"]):
            return render_template(
                "colleges/add.html",
                message="A college with that code already exists.",
            )

        create_college(data["collegecode"], data["collegename"])
        return redirect(url_for("colleges.listColleges"))

    # show empty form
    return render_template("colleges/add.html")


@colleges_bp.route("/updateCollege/<string:collegecode>", methods=["GET", "POST"])
def updateCollege(collegecode):
    # edit an existing college
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

    # show form prefilled with current data
    return render_template("colleges/update.html", college=college)


@colleges_bp.route("/deleteCollege/<string:collegecode>")
def deleteCollege(collegecode):
    # delete a college, its courses and students will also get deleted
    delete_college(collegecode)
    return redirect(url_for("colleges.listColleges"))


@colleges_bp.route("/search", methods=["GET"])
def search_colleges_route():
    # search for colleges with pagination and sorting
    query = request.args.get("query", "").strip()
    page = request.args.get("page", 1, type=int)
    sort = request.args.get("sort", "collegecode")
    order = request.args.get("order", "asc")
    per_page = 10

    valid_sorts = {"collegecode", "collegename"}
    if sort not in valid_sorts:
        sort = "collegecode"
    if order not in ("asc", "desc"):
        order = "asc"

    all_results = search_colleges(query) if query else []

    reverse = order == "desc"
    all_results.sort(key=lambda c: (c.get(sort) or ""), reverse=reverse)

    total = len(all_results)
    total_pages = max(1, (total + per_page - 1) // per_page)
    page = max(1, min(page, total_pages))

    start = (page - 1) * per_page
    colleges = all_results[start:start + per_page]

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
