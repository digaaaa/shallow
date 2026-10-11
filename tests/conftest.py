"""Shared test setup. pytest loads this file automatically."""

import sqlite3

import pytest

from db import SCHEMA


@pytest.fixture
def conn():
    """A fresh in-memory database with the real tables, closed after each test."""
    connection = sqlite3.connect(":memory:")
    connection.row_factory = sqlite3.Row
    connection.execute("PRAGMA foreign_keys = ON")
    connection.executescript(SCHEMA)
    connection.executemany(
        "INSERT INTO roommates (id, name) VALUES (?, ?)",
        [(1, "Alex"), (2, "Sam"), (3, "Jordan")],
    )
    connection.commit()
    yield connection
    connection.close()
