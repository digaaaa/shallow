import pytest

from app import app
from db import init_db


@pytest.fixture
def client(tmp_path, monkeypatch):
    """The real app, using a temporary DATA_DIR filled from seed.json."""
    monkeypatch.setenv("DATA_DIR", str(tmp_path))
    init_db()
    return app.test_client()


def test_home_page_links_to_chores(client):
    response = client.get("/")
    assert response.status_code == 200
    assert b"/chores/" in response.data


def test_chores_page_lists_seeded_chores(client):
    response = client.get("/chores/")
    assert response.status_code == 200
    assert b"Dishes" in response.data
    assert b"never" in response.data


def test_i_did_it_logs_the_chore_and_redirects(client):
    response = client.post("/chores/1/done", data={"roommate_id": "1"})
    assert response.status_code == 302  # redirect back to the chores page

    page = client.get("/chores/").data
    assert b"never" in page  # other chores are still never done
    assert page.count(b"on time") == 4


def test_i_did_it_with_unknown_roommate_is_rejected(client):
    response = client.post("/chores/1/done", data={"roommate_id": "99"})
    assert response.status_code == 400
