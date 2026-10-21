import pytest
from fastapi.testclient import TestClient

from app.database import Database
from app.dependencies import get_session
from app.main import create_app


@pytest.fixture
def client():
    """Fresh in-memory database for every test."""
    test_db = Database("sqlite:///:memory:")
    test_db.create_tables()
    app = create_app()
    app.dependency_overrides[get_session] = test_db.get_session
    return TestClient(app)  # no `with`, so the real tickets.db is never created


def make_ticket(client, title="Printer broken", **extra):
    response = client.post("/tickets", json={"title": title, **extra})
    assert response.status_code == 201
    return response.json()


def test_create_ticket_without_title(client):
    response = client.post("/tickets", json={"description": "no title"})
    assert response.status_code == 422


def test_update_ticket_that_does_not_exist(client):
    response = client.patch("/tickets/999", json={"status": "Resolved"})
    assert response.status_code == 404
    assert response.json() == {"detail": "Ticket 999 not found"}


def test_update_ticket_with_invalid_status(client):
    ticket = make_ticket(client)
    response = client.patch(f"/tickets/{ticket['id']}", json={"status": "Done"})
    assert response.status_code == 422


def test_summary_when_no_tickets(client):
    response = client.get("/tickets/summary")
    assert response.status_code == 200
    assert response.json() == {
        "total": 0, "open": 0, "in_progress": 0, "resolved": 0,
        "high_priority": 0, "oldest_unresolved": None,
    }


def test_create_uses_defaults(client):
    ticket = make_ticket(client)
    assert ticket["id"] == 1
    assert ticket["status"] == "Open"
    assert ticket["priority"] == "Medium"
    assert ticket["description"] is None
    assert ticket["created_at"]


def test_title_longer_than_100_is_rejected(client):
    assert client.post("/tickets", json={"title": "x" * 101}).status_code == 422


def test_blank_title_is_rejected(client):
    assert client.post("/tickets", json={"title": "   "}).status_code == 422


def test_invalid_priority_is_rejected(client):
    assert client.post("/tickets", json={"title": "a", "priority": "Urgent"}).status_code == 422


def test_get_one_and_missing(client):
    ticket = make_ticket(client)
    assert client.get(f"/tickets/{ticket['id']}").json()["title"] == "Printer broken"
    assert client.get("/tickets/999").status_code == 404


def test_list_and_filter_by_status(client):
    a = make_ticket(client, "A")
    make_ticket(client, "B")
    client.patch(f"/tickets/{a['id']}", json={"status": "Resolved"})
    assert len(client.get("/tickets").json()) == 2
    resolved = client.get("/tickets", params={"status": "Resolved"}).json()
    assert [t["title"] for t in resolved] == ["A"]


def test_patch_updates_status_and_priority(client):
    ticket = make_ticket(client)
    response = client.patch(f"/tickets/{ticket['id']}",
                            json={"status": "In Progress", "priority": "High"})
    assert response.status_code == 200
    assert response.json()["status"] == "In Progress"
    assert response.json()["priority"] == "High"


def test_patch_cannot_change_title_or_be_empty(client):
    ticket = make_ticket(client)
    assert client.patch(f"/tickets/{ticket['id']}", json={"title": "new"}).status_code == 422
    assert client.patch(f"/tickets/{ticket['id']}", json={}).status_code == 422


def test_delete_then_missing(client):
    ticket = make_ticket(client)
    assert client.delete(f"/tickets/{ticket['id']}").status_code == 204
    assert client.delete(f"/tickets/{ticket['id']}").status_code == 404


def test_summary_follows_create_edit_delete(client):
    first = make_ticket(client, "Unable to login", priority="High")
    second = make_ticket(client, "Slow page")
    make_ticket(client, "Typo")

    summary = client.get("/tickets/summary").json()
    assert summary["total"] == 3
    assert summary["open"] == 3
    assert summary["high_priority"] == 1
    assert summary["oldest_unresolved"] == {"id": first["id"], "title": "Unable to login"}

    client.patch(f"/tickets/{first['id']}", json={"status": "Resolved"})
    client.patch(f"/tickets/{second['id']}", json={"status": "In Progress"})
    summary = client.get("/tickets/summary").json()
    assert (summary["open"], summary["in_progress"], summary["resolved"]) == (1, 1, 1)
    assert summary["oldest_unresolved"]["id"] == second["id"]  # first is resolved now

    client.delete(f"/tickets/{second['id']}")
    summary = client.get("/tickets/summary").json()
    assert summary["total"] == 2
    assert summary["in_progress"] == 0


def test_oldest_unresolved_is_null_when_all_resolved(client):
    ticket = make_ticket(client)
    client.patch(f"/tickets/{ticket['id']}", json={"status": "Resolved"})
    assert client.get("/tickets/summary").json()["oldest_unresolved"] is None
