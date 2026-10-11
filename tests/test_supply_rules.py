import pytest

from supplies.rules import LeastSpent, TakeTurns, get_rule

ROOMMATES = [1, 2, 3]


# --- TakeTurns -------------------------------------------------------------

def test_take_turns_starts_with_first_roommate_when_nobody_bought_it():
    assert TakeTurns().next_person(ROOMMATES, []) == 1


def test_take_turns_picks_the_person_after_the_last_buyer():
    purchases = [(1, 3.0, "2026-10-01"), (2, 3.0, "2026-10-04")]
    assert TakeTurns().next_person(ROOMMATES, purchases) == 3


def test_take_turns_wraps_around_to_the_first_roommate():
    purchases = [(3, 3.0, "2026-10-01")]
    assert TakeTurns().next_person(ROOMMATES, purchases) == 1


def test_take_turns_restarts_if_last_buyer_moved_out():
    purchases = [(99, 3.0, "2026-10-01")]
    assert TakeTurns().next_person(ROOMMATES, purchases) == 1


# --- LeastSpent ------------------------------------------------------------

def test_least_spent_picks_someone_who_never_bought_it():
    purchases = [(1, 5.0, "2026-10-01"), (3, 2.0, "2026-10-02")]
    assert LeastSpent().next_person(ROOMMATES, purchases) == 2


def test_least_spent_adds_up_all_purchases_per_person():
    # Arrange: 1 bought twice cheaply (2 + 2 = 4), 2 once (5), 3 once (3)
    purchases = [
        (1, 2.0, "2026-10-01"),
        (2, 5.0, "2026-10-02"),
        (3, 3.0, "2026-10-03"),
        (1, 2.0, "2026-10-04"),
    ]
    # Act
    result = LeastSpent().next_person(ROOMMATES, purchases)
    # Assert: 3 has spent the least in total
    assert result == 3


def test_least_spent_tie_goes_to_rotation_order():
    purchases = [(3, 4.0, "2026-10-01"), (2, 4.0, "2026-10-02"), (1, 4.0, "2026-10-03")]
    assert LeastSpent().next_person(ROOMMATES, purchases) == 1


# --- Both rules ------------------------------------------------------------

@pytest.mark.parametrize("rule", [TakeTurns(), LeastSpent()])
def test_rules_refuse_an_empty_flat(rule):
    with pytest.raises(ValueError, match="no roommates"):
        rule.next_person([], [])


# --- factory_map / get_rule ------------------------------------------------

@pytest.mark.parametrize(
    "name, expected_class",
    [("take_turns", TakeTurns), ("least_spent", LeastSpent)],
)
def test_get_rule_turns_a_name_into_the_right_rule(name, expected_class):
    assert isinstance(get_rule(name), expected_class)


def test_get_rule_rejects_an_unknown_name():
    with pytest.raises(ValueError, match="Unknown supply rule"):
        get_rule("least_recent")  # a chores rule, not a supplies one
