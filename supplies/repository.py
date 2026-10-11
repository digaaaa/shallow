"""All SQL for the supplies domain. No decisions here, only reading and writing."""


class SupplyRepository:
    def __init__(self, conn):
        self.conn = conn

    def list_supplies(self):
        return self.conn.execute("SELECT id, name, rule FROM supplies ORDER BY id").fetchall()

    def get_supply(self, supply_id):
        return self.conn.execute(
            "SELECT id, name, rule FROM supplies WHERE id = ?", (supply_id,)
        ).fetchone()

    def list_roommates(self):
        return self.conn.execute("SELECT id, name FROM roommates ORDER BY id").fetchall()

    def purchases(self, supply_id):
        """Who bought this supply, for how much and when, oldest first."""
        return self.conn.execute(
            "SELECT roommate_id, price, bought_on FROM purchases "
            "WHERE supply_id = ? ORDER BY bought_on, id",
            (supply_id,),
        ).fetchall()

    def spent_since(self, start_date):
        """How much each roommate spent on all supplies from start_date onwards."""
        return self.conn.execute(
            "SELECT roommate_id, SUM(price) AS spent FROM purchases "
            "WHERE bought_on >= ? GROUP BY roommate_id",
            (start_date,),
        ).fetchall()

    def add_purchase(self, supply_id, roommate_id, price, bought_on):
        self.conn.execute(
            "INSERT INTO purchases (supply_id, roommate_id, price, bought_on) VALUES (?, ?, ?, ?)",
            (supply_id, roommate_id, price, bought_on),
        )
        self.conn.commit()
