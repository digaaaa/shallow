"""Web pages for the supplies domain."""

from datetime import date

from flask import Blueprint, abort, redirect, render_template, request, url_for

from db import connect
from supplies.repository import SupplyRepository
from supplies.service import SupplyService

supplies_bp = Blueprint("supplies", __name__, url_prefix="/supplies")


@supplies_bp.route("/")
def supplies_page():
    conn = connect()
    try:
        service = SupplyService(SupplyRepository(conn))
        supplies = service.overview()
        roommates = service.roommates()
        spending = service.monthly_spending(date.today())
    finally:
        conn.close()
    return render_template(
        "supplies.html", supplies=supplies, roommates=roommates, spending=spending
    )


@supplies_bp.route("/<int:supply_id>/bought", methods=["POST"])
def mark_bought(supply_id):
    conn = connect()
    try:
        # float("abc") also raises ValueError, so a bad price ends up in the except too.
        roommate_id = int(request.form["roommate_id"])
        price = float(request.form["price"])
        service = SupplyService(SupplyRepository(conn))
        service.record_purchase(supply_id, roommate_id, price, date.today())
    except ValueError:
        abort(400)
    finally:
        conn.close()
    # Redirect after the form, so refreshing the page doesn't log it twice.
    return redirect(url_for("supplies.supplies_page"))
