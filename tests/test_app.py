import os
import pytest

# Use an isolated in-memory database for tests.
os.environ["TASKFLOW_DATABASE_URI"] = "sqlite://"
os.environ.setdefault("SECRET_KEY", "test-only-secret-key")

from app import app, db


@pytest.fixture
def client():
    app.config["TESTING"] = True
    app.config["SECRET_KEY"] = "test-only-secret-key"

    with app.app_context():
        db.create_all()

        try:
            with app.test_client() as test_client:
                yield test_client
        finally:
            db.session.remove()
            db.drop_all()


def test_login_page_loads(client):
    response = client.get("/login")
    assert response.status_code == 200


def test_dashboard_requires_login(client):
    response = client.get("/dashboard")
    assert response.status_code in (302, 303)


def test_stylesheet_loads(client):
    response = client.get("/static/style.css")
    assert response.status_code == 200
