"""Rules that decide whose turn it is to do a chore (Strategy pattern).

Each rule gets plain data, never the database:
- roommates: list of roommate ids in rotation order, e.g. [1, 2, 3]
- history:   list of (roommate_id, done_on) pairs, oldest first,
             where done_on is a date string like "2026-10-09"
"""

from abc import ABC, abstractmethod


class ChoreRule(ABC):
    """Every chore rule must be able to say who is next."""

    @abstractmethod
    def next_person(self, roommates, history):
        ...


class TakeTurns(ChoreRule):
    """Fixed rotation: the person after whoever did it last."""

    def next_person(self, roommates, history):
        if not roommates:
            raise ValueError("There are no roommates")
        if not history:
            return roommates[0]

        last_person = history[-1][0]
        if last_person not in roommates:
            return roommates[0]

        position = roommates.index(last_person)
        # % wraps around: after the last roommate comes the first one again.
        return roommates[(position + 1) % len(roommates)]


class LeastRecent(ChoreRule):
    """Whoever did it longest ago. People who never did it go first."""

    def next_person(self, roommates, history):
        if not roommates:
            raise ValueError("There are no roommates")

        last_done = {}
        for roommate_id, done_on in history:
            last_done[roommate_id] = done_on  # later entries overwrite earlier ones

        for roommate_id in roommates:
            if roommate_id not in last_done:
                return roommate_id

        # min() picks the roommate with the oldest date; on a tie it keeps
        # the first one in rotation order.
        return min(roommates, key=lambda roommate_id: last_done[roommate_id])


# Turns the rule name stored in the database into a rule object.
factory_map = {
    "take_turns": TakeTurns,
    "least_recent": LeastRecent,
}


def get_rule(name):
    if name not in factory_map:
        raise ValueError(f"Unknown chore rule: {name}")
    return factory_map[name]()
