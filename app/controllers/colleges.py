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
    # show all colleges
    colleges = get_all_colleges()
    message = request.args.get("message")
    return render_template("colleges/list.html", colleges=colleges, message=message)


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
    # search for colleges
    query = request.args.get("query", "").strip()
    colleges = search_colleges(query) if query else []
    return render_template("colleges/list.html", colleges=colleges, search_query=query)
