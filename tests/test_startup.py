"""Tests for the deployment contract: PORT, DATA_DIR, schema creation and seeding."""

import os
import sqlite3

import pytest

import db
from app import get_port

TABLES = ["roommates", "chores", "chore_log", "supplies", "purchases"]


def row_counts():
    conn = db.connect()
    counts = {table: conn.execute(f"SELECT COUNT(*) FROM {table}").fetchone()[0] for table in TABLES}
    conn.close()
    return counts


@pytest.fixture
def data_dir(tmp_path, monkeypatch):
    monkeypatch.setenv("DATA_DIR", str(tmp_path))
    return tmp_path


# --- PORT ------------------------------------------------------------------

def test_port_defaults_to_8000(monkeypatch):
    monkeypatch.delenv("PORT", raising=False)
    assert get_port() == 8000


def test_port_is_read_from_the_environment(monkeypatch):
    monkeypatch.setenv("PORT", "9123")
    assert get_port() == 9123


# --- DATA_DIR --------------------------------------------------------------

def test_db_file_lives_in_data_dir(data_dir):
    assert db.get_db_path() == os.path.join(str(data_dir), "yourturn.db")


def test_data_dir_defaults_to_local_data_folder(monkeypatch, tmp_path):
    monkeypatch.delenv("DATA_DIR", raising=False)
    monkeypatch.chdir(tmp_path)  # so ./data is created in a temp folder, not the repo
    assert db.get_db_path() == os.path.join("./data", "yourturn.db")
    assert (tmp_path / "data").is_dir()


# --- init_db / seeding -----------------------------------------------------

def test_first_boot_creates_tables_and_loads_seed(data_dir):
    db.init_db()
    counts = row_counts()
    assert counts["roommates"] > 0
    assert counts["chores"] > 0
    assert counts["supplies"] > 0
    assert counts["chore_log"] == 0
    assert counts["purchases"] == 0


def test_booting_twice_does_not_duplicate_rows(data_dir):
    db.init_db()
    first = row_counts()
    db.init_db()
    assert row_counts() == first


def test_seed_does_not_touch_a_table_that_already_has_rows(data_dir):
    conn = db.connect()
    conn.executescript(db.SCHEMA)
    conn.execute("INSERT INTO roommates (name) VALUES ('Only Me')")
    conn.commit()
    conn.close()

    db.init_db()

    conn = db.connect()
    names = [row["name"] for row in conn.execute("SELECT name FROM roommates")]
    conn.close()
    assert names == ["Only Me"]


def test_foreign_keys_are_enforced(data_dir):
    db.init_db()
    conn = db.connect()
    with pytest.raises(sqlite3.IntegrityError):
        conn.execute(
            "INSERT INTO chore_log (chore_id, roommate_id, done_on) VALUES (1, 99, '2026-10-12')"
        )
    conn.close()
