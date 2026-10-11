from datetime import date

import pytest

from chores.repository import ChoreRepository
from chores.service import ChoreService, days_overdue

TODAY = date(2026, 10, 11)


@pytest.fixture
def service(conn):
    conn.executemany(
        "INSERT INTO chores (id, name, frequency_days, rule) VALUES (?, ?, ?, ?)",
        [(1, "Dishes", 1, "take_turns"), (2, "Bathroom", 7, "least_recent")],
    )
    conn.commit()
    return ChoreService(ChoreRepository(conn))


# --- days_overdue ----------------------------------------------------------

@pytest.mark.parametrize(
    "last_done, frequency_days, expected",
    [
        (None, 3, 0),            # never done: not counted as overdue
        ("2026-10-10", 3, 0),    # done yesterday, not due yet
        ("2026-10-08", 3, 0),    # exactly due today
        ("2026-10-05", 3, 3),    # 6 days ago, every 3 days -> 3 days late
    ],
)
def test_days_overdue(last_done, frequency_days, expected):
    assert days_overdue(last_done, frequency_days, TODAY) == expected


# --- roommates -------------------------------------------------------------

def test_roommates_are_listed_in_id_order(service):
    assert [r["name"] for r in service.roommates()] == ["Alex", "Sam", "Jordan"]


# --- mark_done -------------------------------------------------------------

def test_mark_done_saves_a_log_entry(service, conn):
    service.mark_done(1, 2, TODAY)
    rows = conn.execute("SELECT chore_id, roommate_id, done_on FROM chore_log").fetchall()
    assert [tuple(r) for r in rows] == [(1, 2, "2026-10-11")]


def test_mark_done_rejects_an_unknown_chore(service):
    with pytest.raises(ValueError, match="Unknown chore"):
        service.mark_done(99, 1, TODAY)


def test_mark_done_rejects_an_unknown_roommate(service):
    with pytest.raises(ValueError, match="Unknown roommate"):
        service.mark_done(1, 99, TODAY)


# --- next_person -----------------------------------------------------------

def test_next_person_uses_the_chores_own_rule(service):
    # Dishes uses take_turns: after Alex (1) comes Sam (2).
    service.mark_done(1, 1, TODAY)
    assert service.next_person(1) == 2
    # Bathroom uses least_recent: Alex did it, so someone who never did it is next.
    service.mark_done(2, 1, TODAY)
    assert service.next_person(2) == 2


def test_next_person_rejects_an_unknown_chore(service):
    with pytest.raises(ValueError, match="Unknown chore"):
        service.next_person(99)


# --- monthly_stats ---------------------------------------------------------

def test_monthly_stats_counts_only_this_month_and_includes_everyone(service):
    service.mark_done(1, 2, date(2026, 9, 30))   # last month: not counted
    service.mark_done(1, 2, date(2026, 10, 1))   # first day of the month: counted
    service.mark_done(2, 2, date(2026, 10, 5))
    service.mark_done(1, 3, date(2026, 10, 9))

    stats = service.monthly_stats(TODAY)

    assert stats == [
        {"name": "Sam", "done": 2},
        {"name": "Jordan", "done": 1},
        {"name": "Alex", "done": 0},
    ]


# --- overview --------------------------------------------------------------

def test_overview_summarises_every_chore(service):
    service.mark_done(1, 1, date(2026, 10, 8))  # dishes, 3 days ago, daily -> 2 days late

    dishes, bathroom = service.overview(TODAY)

    assert dishes["name"] == "Dishes"
    assert dishes["next_person_id"] == 2
    assert dishes["next_person"] == "Sam"
    assert dishes["last_done"] == "2026-10-08"
    assert dishes["days_overdue"] == 2
    assert bathroom["last_done"] is None
    assert bathroom["next_person"] == "Alex"
    assert bathroom["days_overdue"] == 0
