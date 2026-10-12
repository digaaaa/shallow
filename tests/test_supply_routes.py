import pytest

from app import app
from db import init_db


@pytest.fixture
def client(tmp_path, monkeypatch):
    """The real app, using a temporary DATA_DIR filled from seed.json."""
    monkeypatch.setenv("DATA_DIR", str(tmp_path))
    init_db()
    return app.test_client()


def test_home_page_links_to_supplies(client):
    assert b"/supplies/" in client.get("/").data


def test_supplies_page_lists_seeded_supplies(client):
    response = client.get("/supplies/")
    assert response.status_code == 200
    assert b"Eggs" in response.data
    assert b"Spent this month" in response.data


def test_i_bought_it_logs_the_purchase_and_redirects(client):
    response = client.post("/supplies/1/bought", data={"roommate_id": "1", "price": "2.5"})
    assert response.status_code == 302  # redirect back to the supplies page

    page = client.get("/supplies/").data
    assert "€2.50".encode() in page


@pytest.mark.parametrize("price", ["abc", "-2", "0", "5000", "nan"])
def test_i_bought_it_with_a_bad_price_is_rejected(client, price):
    response = client.post("/supplies/1/bought", data={"roommate_id": "1", "price": price})
    assert response.status_code == 400
