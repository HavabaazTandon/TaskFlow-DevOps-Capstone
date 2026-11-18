from app import app


def test_login_page_loads():
    client = app.test_client()
    response = client.get("/login")
    assert response.status_code == 200


def test_dashboard_requires_login():
    client = app.test_client()
    response = client.get("/dashboard")
    assert response.status_code in (302, 303)


def test_stylesheet_loads():
    client = app.test_client()
    response = client.get("/static/style.css")
    assert response.status_code == 200
