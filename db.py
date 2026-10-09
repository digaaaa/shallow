"""Database setup: where the SQLite file lives, the tables, and the seed data."""

import json
import os
import sqlite3

SEED_FILE = os.path.join(os.path.dirname(__file__), "seed.json")

# CREATE TABLE IF NOT EXISTS is safe to run on every start: it only creates
# a table the first time and never deletes existing data.
SCHEMA = """
CREATE TABLE IF NOT EXISTS roommates (
    id   INTEGER PRIMARY KEY AUTOINCREMENT,
    name TEXT NOT NULL UNIQUE
);

CREATE TABLE IF NOT EXISTS chores (
    id             INTEGER PRIMARY KEY AUTOINCREMENT,
    name           TEXT NOT NULL,
    frequency_days INTEGER NOT NULL,
    rule           TEXT NOT NULL
);

CREATE TABLE IF NOT EXISTS chore_log (
    id          INTEGER PRIMARY KEY AUTOINCREMENT,
    chore_id    INTEGER NOT NULL REFERENCES chores(id),
    roommate_id INTEGER NOT NULL REFERENCES roommates(id),
    done_on     TEXT NOT NULL
);

CREATE TABLE IF NOT EXISTS supplies (
    id   INTEGER PRIMARY KEY AUTOINCREMENT,
    name TEXT NOT NULL,
    rule TEXT NOT NULL
);

CREATE TABLE IF NOT EXISTS purchases (
    id          INTEGER PRIMARY KEY AUTOINCREMENT,
    supply_id   INTEGER NOT NULL REFERENCES supplies(id),
    roommate_id INTEGER NOT NULL REFERENCES roommates(id),
    price       REAL NOT NULL,
    bought_on   TEXT NOT NULL
);
"""


def get_db_path():
    """Return the path of the SQLite file, inside DATA_DIR (default ./data)."""
    data_dir = os.environ.get("DATA_DIR", "./data")
    os.makedirs(data_dir, exist_ok=True)
    return os.path.join(data_dir, "yourturn.db")


def connect():
    """Open a connection to the SQLite file."""
    conn = sqlite3.connect(get_db_path())
    conn.row_factory = sqlite3.Row  # lets us read row["name"] instead of row[1]
    conn.execute("PRAGMA foreign_keys = ON")  # SQLite only checks foreign keys if asked
    return conn


def is_empty(conn, table):
    count = conn.execute(f"SELECT COUNT(*) FROM {table}").fetchone()[0]
    return count == 0


def seed_if_empty(conn, seed_file=SEED_FILE):
    """Load seed.json, but only into tables that have no rows yet."""
    with open(seed_file, encoding="utf-8") as f:
        seed = json.load(f)

    if is_empty(conn, "roommates"):
        for name in seed["roommates"]:
            conn.execute("INSERT INTO roommates (name) VALUES (?)", (name,))

    if is_empty(conn, "chores"):
        for chore in seed["chores"]:
            conn.execute(
                "INSERT INTO chores (name, frequency_days, rule) VALUES (?, ?, ?)",
                (chore["name"], chore["frequency_days"], chore["rule"]),
            )

    if is_empty(conn, "supplies"):
        for supply in seed["supplies"]:
            conn.execute(
                "INSERT INTO supplies (name, rule) VALUES (?, ?)",
                (supply["name"], supply["rule"]),
            )


def init_db():
    """Create the tables if needed and load the seed data. Run once at startup."""
    conn = connect()
    conn.executescript(SCHEMA)
    seed_if_empty(conn)
    conn.commit()
    conn.close()
