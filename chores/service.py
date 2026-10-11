"""Chores logic: logging "I did it", whose turn is next, and overdue chores."""

from datetime import date

from chores.rules import get_rule


def days_overdue(last_done, frequency_days, today):
    """How many days late a chore is (0 if it is not late).

    last_done is a date string like "2026-10-09", or None if never done.
    """
    if last_done is None:
        return 0
    days_since = (today - date.fromisoformat(last_done)).days
    return max(0, days_since - frequency_days)


class ChoreService:
    def __init__(self, repository):
        self.repo = repository

    def roommates(self):
        return self.repo.list_roommates()

    def mark_done(self, chore_id, roommate_id, today):
        if self.repo.get_chore(chore_id) is None:
            raise ValueError("Unknown chore")
        roommate_ids = [r["id"] for r in self.repo.list_roommates()]
        if roommate_id not in roommate_ids:
            raise ValueError("Unknown roommate")
        self.repo.add_log(chore_id, roommate_id, today.isoformat())

    def next_person(self, chore_id):
        """Return the id of whoever should do this chore next."""
        chore = self.repo.get_chore(chore_id)
        if chore is None:
            raise ValueError("Unknown chore")
        rule = get_rule(chore["rule"])
        roommate_ids = [r["id"] for r in self.repo.list_roommates()]
        history = [(row["roommate_id"], row["done_on"]) for row in self.repo.history(chore_id)]
        return rule.next_person(roommate_ids, history)

    def monthly_stats(self, today):
        """Every roommate with how many chores they did this month, most first."""
        first_of_month = today.replace(day=1).isoformat()
        counts = {row["roommate_id"]: row["done"] for row in self.repo.count_done_since(first_of_month)}
        stats = []
        for roommate in self.repo.list_roommates():
            # .get(..., 0) gives 0 to roommates who did nothing this month.
            stats.append({"name": roommate["name"], "done": counts.get(roommate["id"], 0)})
        # Most chores first. Python's sort keeps the original order on a tie.
        return sorted(stats, key=lambda s: s["done"], reverse=True)

    def overview(self, today):
        """One summary per chore, ready to show on the page."""
        names = {r["id"]: r["name"] for r in self.repo.list_roommates()}
        summaries = []
        for chore in self.repo.list_chores():
            history = self.repo.history(chore["id"])
            last_done = history[-1]["done_on"] if history else None
            next_id = self.next_person(chore["id"])
            summaries.append({
                "id": chore["id"],
                "name": chore["name"],
                "frequency_days": chore["frequency_days"],
                "next_person_id": next_id,
                "next_person": names[next_id],
                "last_done": last_done,
                "days_overdue": days_overdue(last_done, chore["frequency_days"], today),
            })
        return summaries
