"""Basic smoke tests for the intentionally vulnerable Flask training app.

These tests check basic availability and expected unauthenticated behavior.
They do not assert that the application is secure.
"""
import pytest

from app import app


@pytest.fixture()
def client():
    app.config.update(TESTING=True)
    with app.test_client() as test_client:
        yield test_client


def test_login_page_is_available(client):
    response = client.get("/login")
    assert response.status_code == 200
    assert b"login" in response.data.lower()


def test_signup_page_is_available(client):
    response = client.get("/signup")
    assert response.status_code == 200
    assert b"signup" in response.data.lower()


def test_login_status_is_false_for_anonymous_client(client):
    response = client.get("/is_logged_in")
    assert response.status_code == 200
    assert response.get_json() == {
        "is_logged_in": False,
        "username": "-",
    }


@pytest.mark.parametrize("path", ["/", "/home", "/notes", "/account"])
def test_protected_pages_redirect_anonymous_user_to_login(client, path):
    response = client.get(path, follow_redirects=False)
    assert response.status_code == 302
    assert response.headers["Location"].endswith("/login")


def test_invalid_login_does_not_authenticate_user(client):
    response = client.post(
        "/login",
        data={"email": "missing-user@example.invalid", "password": "wrong"},
        follow_redirects=False,
    )
    assert response.status_code == 302

    status_response = client.get("/is_logged_in")
    assert status_response.get_json()["is_logged_in"] is False


def test_unknown_route_returns_404(client):
    response = client.get("/this-route-should-not-exist")
    assert response.status_code == 404


def test_seeded_user_can_log_in_and_log_out(client):
    login_response = client.post(
        "/login",
        data={"email": "user@evfa.com", "password": "user"},
        follow_redirects=False,
    )
    assert login_response.status_code == 302

    status_response = client.get("/is_logged_in")
    assert status_response.get_json() == {
        "is_logged_in": True,
        "username": "user@evfa.com",
    }

    logout_response = client.get("/logout", follow_redirects=False)
    assert logout_response.status_code == 302
    assert client.get("/is_logged_in").get_json()["is_logged_in"] is False
