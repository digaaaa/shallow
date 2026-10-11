"""All SQL for the chores domain. No decisions here, only reading and writing."""


class ChoreRepository:
    def __init__(self, conn):
        self.conn = conn

    def list_chores(self):
        return self.conn.execute(
            "SELECT id, name, frequency_days, rule FROM chores ORDER BY id"
        ).fetchall()

    def get_chore(self, chore_id):
        return self.conn.execute(
            "SELECT id, name, frequency_days, rule FROM chores WHERE id = ?",
            (chore_id,),
        ).fetchone()

    def list_roommates(self):
        return self.conn.execute("SELECT id, name FROM roommates ORDER BY id").fetchall()

    def history(self, chore_id):
        """Who did this chore and when, oldest first."""
        return self.conn.execute(
            "SELECT roommate_id, done_on FROM chore_log WHERE chore_id = ? ORDER BY done_on, id",
            (chore_id,),
        ).fetchall()

    def count_done_since(self, start_date):
        """How many chores each roommate did from start_date onwards."""
        return self.conn.execute(
            "SELECT roommate_id, COUNT(*) AS done FROM chore_log "
            "WHERE done_on >= ? GROUP BY roommate_id",
            (start_date,),
        ).fetchall()

    def add_log(self, chore_id, roommate_id, done_on):
        self.conn.execute(
            "INSERT INTO chore_log (chore_id, roommate_id, done_on) VALUES (?, ?, ?)",
            (chore_id, roommate_id, done_on),
        )
        self.conn.commit()
