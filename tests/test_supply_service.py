from datetime import date

import pytest

from supplies.repository import SupplyRepository
from supplies.service import SupplyService

TODAY = date(2026, 10, 11)


@pytest.fixture
def service(conn):
    conn.executemany(
        "INSERT INTO supplies (id, name, rule) VALUES (?, ?, ?)",
        [(1, "Eggs", "take_turns"), (2, "Coffee pods", "least_spent")],
    )
    conn.commit()
    return SupplyService(SupplyRepository(conn))


def test_roommates_are_listed_in_id_order(service):
    assert [r["name"] for r in service.roommates()] == ["Alex", "Sam", "Jordan"]


# --- record_purchase -------------------------------------------------------

def test_record_purchase_saves_it_rounded_to_cents(service, conn):
    service.record_purchase(1, 2, 3.456, TODAY)
    rows = conn.execute("SELECT supply_id, roommate_id, price, bought_on FROM purchases").fetchall()
    assert [tuple(r) for r in rows] == [(1, 2, 3.46, "2026-10-11")]


def test_record_purchase_rejects_an_unknown_supply(service):
    with pytest.raises(ValueError, match="Unknown supply"):
        service.record_purchase(99, 1, 2.0, TODAY)


def test_record_purchase_rejects_an_unknown_roommate(service):
    with pytest.raises(ValueError, match="Unknown roommate"):
        service.record_purchase(1, 99, 2.0, TODAY)


@pytest.mark.parametrize("price", [0, -1.5])
def test_record_purchase_rejects_a_price_that_is_not_positive(service, price):
    with pytest.raises(ValueError, match="more than 0"):
        service.record_purchase(1, 1, price, TODAY)


# --- next_person -----------------------------------------------------------

def test_next_person_uses_the_supplys_own_rule(service):
    # Eggs uses take_turns: after Alex (1) comes Sam (2).
    service.record_purchase(1, 1, 2.0, TODAY)
    assert service.next_person(1) == 2
    # Coffee uses least_spent: Alex paid 10, Sam paid 4, Jordan paid nothing yet.
    service.record_purchase(2, 1, 10.0, TODAY)
    service.record_purchase(2, 2, 4.0, TODAY)
    assert service.next_person(2) == 3


def test_next_person_rejects_an_unknown_supply(service):
    with pytest.raises(ValueError, match="Unknown supply"):
        service.next_person(99)


# --- overview --------------------------------------------------------------

def test_overview_summarises_every_supply(service):
    service.record_purchase(1, 1, 2.5, date(2026, 10, 9))

    eggs, coffee = service.overview()

    assert eggs["name"] == "Eggs"
    assert eggs["next_person_id"] == 2
    assert eggs["next_person"] == "Sam"
    assert eggs["last_bought"] == "2026-10-09"
    assert eggs["last_price"] == 2.5
    assert coffee["last_bought"] is None
    assert coffee["last_price"] is None
    assert coffee["next_person"] == "Alex"


# --- monthly_spending ------------------------------------------------------

def test_monthly_spending_counts_only_this_month_and_includes_everyone(service):
    service.record_purchase(1, 2, 50.0, date(2026, 9, 30))  # last month: not counted
    service.record_purchase(1, 2, 2.10, date(2026, 10, 1))
    service.record_purchase(2, 2, 4.20, date(2026, 10, 5))
    service.record_purchase(2, 3, 9.99, date(2026, 10, 9))

    spending = service.monthly_spending(TODAY)

    assert spending == [
        {"name": "Jordan", "spent": 9.99},
        {"name": "Sam", "spent": 6.3},
        {"name": "Alex", "spent": 0},
    ]
