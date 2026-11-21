from app import app


def setup_test_app():
    app.config["TESTING"] = True
    app.config["SECRET_KEY"] = "test-only-secret-key"
    return app.test_client()


def test_login_page_loads():
    client = setup_test_app()
    response = client.get("/login")
    assert response.status_code == 200


def test_dashboard_requires_login():
    client = setup_test_app()
    response = client.get("/dashboard")
    assert response.status_code in (302, 303)


def test_stylesheet_loads():
    client = setup_test_app()
    response = client.get("/static/style.css")
    assert response.status_code == 200
