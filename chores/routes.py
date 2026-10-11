"""Web pages for the chores domain."""

from datetime import date

from flask import Blueprint, abort, redirect, render_template, request, url_for

from chores.repository import ChoreRepository
from chores.service import ChoreService
from db import connect

chores_bp = Blueprint("chores", __name__, url_prefix="/chores")


@chores_bp.route("/")
def chores_page():
    conn = connect()
    try:
        service = ChoreService(ChoreRepository(conn))
        today = date.today()
        chores = service.overview(today)
        roommates = service.roommates()
        stats = service.monthly_stats(today)
    finally:
        conn.close()
    return render_template("chores.html", chores=chores, roommates=roommates, stats=stats)


@chores_bp.route("/<int:chore_id>/done", methods=["POST"])
def mark_done(chore_id):
    roommate_id = int(request.form["roommate_id"])
    conn = connect()
    try:
        service = ChoreService(ChoreRepository(conn))
        service.mark_done(chore_id, roommate_id, date.today())
    except ValueError:
        abort(400)
    finally:
        conn.close()
    # Redirect after the form, so refreshing the page doesn't log it twice.
    return redirect(url_for("chores.chores_page"))
