"""Rules that decide whose turn it is to buy a shared supply (Strategy pattern).

Each rule gets plain data, never the database:
- roommates: list of roommate ids in rotation order, e.g. [1, 2, 3]
- purchases: list of (roommate_id, price, bought_on) for this supply, oldest first
"""

from abc import ABC, abstractmethod


class SupplyRule(ABC):
    """Every supply rule must be able to say who buys next."""

    @abstractmethod
    def next_person(self, roommates, purchases):
        ...


class TakeTurns(SupplyRule):
    """Fixed rotation: the person after whoever bought it last."""

    def next_person(self, roommates, purchases):
        if not roommates:
            raise ValueError("There are no roommates")
        if not purchases:
            return roommates[0]

        last_buyer = purchases[-1][0]
        if last_buyer not in roommates:
            return roommates[0]

        position = roommates.index(last_buyer)
        return roommates[(position + 1) % len(roommates)]


class LeastSpent(SupplyRule):
    """Whoever has spent the least money on this supply so far."""

    def next_person(self, roommates, purchases):
        if not roommates:
            raise ValueError("There are no roommates")

        spent = {}
        for roommate_id, price, bought_on in purchases:
            spent[roommate_id] = spent.get(roommate_id, 0) + price

        # Someone who never bought it has spent 0, so they come first.
        # On a tie, min() keeps the first one in rotation order.
        return min(roommates, key=lambda roommate_id: spent.get(roommate_id, 0))


# Turns the rule name stored in the database into a rule object.
factory_map = {
    "take_turns": TakeTurns,
    "least_spent": LeastSpent,
}


def get_rule(name):
    if name not in factory_map:
        raise ValueError(f"Unknown supply rule: {name}")
    return factory_map[name]()
