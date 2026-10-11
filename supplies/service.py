"""Supplies logic: logging "I bought it", whose turn to buy, and monthly spending."""

from supplies.rules import get_rule


class SupplyService:
    def __init__(self, repository):
        self.repo = repository

    def roommates(self):
        return self.repo.list_roommates()

    def record_purchase(self, supply_id, roommate_id, price, today):
        if self.repo.get_supply(supply_id) is None:
            raise ValueError("Unknown supply")
        roommate_ids = [r["id"] for r in self.repo.list_roommates()]
        if roommate_id not in roommate_ids:
            raise ValueError("Unknown roommate")
        if price <= 0:
            raise ValueError("Price must be more than 0")
        self.repo.add_purchase(supply_id, roommate_id, round(price, 2), today.isoformat())

    def next_person(self, supply_id):
        """Return the id of whoever should buy this supply next."""
        supply = self.repo.get_supply(supply_id)
        if supply is None:
            raise ValueError("Unknown supply")
        rule = get_rule(supply["rule"])
        roommate_ids = [r["id"] for r in self.repo.list_roommates()]
        purchases = [
            (row["roommate_id"], row["price"], row["bought_on"])
            for row in self.repo.purchases(supply_id)
        ]
        return rule.next_person(roommate_ids, purchases)

    def overview(self):
        """One summary per supply, ready to show on the page."""
        names = {r["id"]: r["name"] for r in self.repo.list_roommates()}
        summaries = []
        for supply in self.repo.list_supplies():
            purchases = self.repo.purchases(supply["id"])
            last = purchases[-1] if purchases else None
            next_id = self.next_person(supply["id"])
            summaries.append({
                "id": supply["id"],
                "name": supply["name"],
                "next_person_id": next_id,
                "next_person": names[next_id],
                "last_bought": last["bought_on"] if last else None,
                "last_price": last["price"] if last else None,
            })
        return summaries

    def monthly_spending(self, today):
        """Every roommate with how much they spent this month, biggest first."""
        first_of_month = today.replace(day=1).isoformat()
        totals = {row["roommate_id"]: row["spent"] for row in self.repo.spent_since(first_of_month)}
        spending = []
        for roommate in self.repo.list_roommates():
            spending.append({
                "name": roommate["name"],
                "spent": round(totals.get(roommate["id"], 0), 2),
            })
        return sorted(spending, key=lambda s: s["spent"], reverse=True)
