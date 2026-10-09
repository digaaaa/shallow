import pytest

from chores.rules import LeastRecent, TakeTurns, get_rule

ROOMMATES = [1, 2, 3]


# --- TakeTurns -------------------------------------------------------------

def test_take_turns_starts_with_first_roommate_when_nobody_did_it():
    assert TakeTurns().next_person(ROOMMATES, []) == 1


def test_take_turns_picks_the_person_after_the_last_one():
    history = [(1, "2026-10-01"), (2, "2026-10-02")]
    assert TakeTurns().next_person(ROOMMATES, history) == 3


def test_take_turns_wraps_around_to_the_first_roommate():
    history = [(3, "2026-10-03")]
    assert TakeTurns().next_person(ROOMMATES, history) == 1


def test_take_turns_follows_whoever_did_it_out_of_turn():
    # It was 2's turn, but 3 did it, so the rotation continues after 3.
    history = [(1, "2026-10-01"), (3, "2026-10-02")]
    assert TakeTurns().next_person(ROOMMATES, history) == 1


def test_take_turns_restarts_if_last_person_moved_out():
    history = [(99, "2026-10-01")]
    assert TakeTurns().next_person(ROOMMATES, history) == 1


# --- LeastRecent -----------------------------------------------------------

def test_least_recent_picks_someone_who_never_did_it():
    history = [(1, "2026-10-01"), (3, "2026-10-02")]
    assert LeastRecent().next_person(ROOMMATES, history) == 2


def test_least_recent_picks_who_did_it_longest_ago():
    # Arrange: 1 did it most recently, 2 did it longest ago
    history = [(2, "2026-10-01"), (3, "2026-10-03"), (1, "2026-10-05")]
    # Act
    result = LeastRecent().next_person(ROOMMATES, history)
    # Assert
    assert result == 2


def test_least_recent_uses_each_persons_latest_date():
    # 2 did it first but also again most recently, so 1 is waiting longest.
    history = [(2, "2026-10-01"), (1, "2026-10-02"), (3, "2026-10-03"), (2, "2026-10-04")]
    assert LeastRecent().next_person(ROOMMATES, history) == 1


def test_least_recent_tie_goes_to_rotation_order():
    history = [(3, "2026-10-01"), (2, "2026-10-01"), (1, "2026-10-01")]
    assert LeastRecent().next_person(ROOMMATES, history) == 1


# --- Both rules ------------------------------------------------------------

@pytest.mark.parametrize("rule", [TakeTurns(), LeastRecent()])
def test_rules_refuse_an_empty_flat(rule):
    with pytest.raises(ValueError, match="no roommates"):
        rule.next_person([], [])


# --- factory_map / get_rule ------------------------------------------------

@pytest.mark.parametrize(
    "name, expected_class",
    [("take_turns", TakeTurns), ("least_recent", LeastRecent)],
)
def test_get_rule_turns_a_name_into_the_right_rule(name, expected_class):
    assert isinstance(get_rule(name), expected_class)


def test_get_rule_rejects_an_unknown_name():
    with pytest.raises(ValueError, match="Unknown chore rule"):
        get_rule("coin_flip")
