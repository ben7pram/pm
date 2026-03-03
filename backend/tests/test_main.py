from fastapi.testclient import TestClient
from backend import main

client = TestClient(main.app)

def test_hello():
    resp = client.get("/api/hello")
    assert resp.status_code == 200
    assert resp.json() == {"message": "Hello from backend!"}


def test_auth_endpoints():
    # initially not authenticated
    resp = client.get("/api/me")
    assert resp.status_code == 200
    assert resp.json() == {"authenticated": False}

    # wrong credentials
    resp = client.post("/api/login", json={"username": "foo", "password": "bar"})
    assert resp.status_code == 401
    assert resp.json()["authenticated"] is False

    # correct credentials
    resp = client.post("/api/login", json={"username": "user", "password": "password"})
    assert resp.status_code == 200
    assert resp.json()["authenticated"] is True
    # cookie should be set
    assert "session" in resp.cookies

    # subsequent /api/me should reflect auth when cookie passed
    cookies = {"session": resp.cookies.get("session")}
    resp2 = client.get("/api/me", cookies=cookies)
    assert resp2.json() == {"authenticated": True}

    # logout clears
    resp3 = client.post("/api/logout", cookies=cookies)
    assert resp3.status_code == 200
    assert resp3.json()["authenticated"] is False

    resp4 = client.get("/api/me", cookies={})
    assert resp4.json() == {"authenticated": False}


def test_root_static():
    # root returns HTML with either static file or default message
    resp = client.get("/")
    assert resp.status_code == 200
    assert "<h1>" in resp.text


def test_serving_exported_site(tmp_path):
    # simulate the presence of a built frontend export in static directory
    sample_html = "<html><body><h1>Kanban Studio</h1></body></html>"
    static_dir = tmp_path / "static"
    static_dir.mkdir()
    (static_dir / "index.html").write_text(sample_html)

    # create app pointing at our fake static directory
    test_app = main.create_app(static_dir=str(static_dir))
    test_client = TestClient(test_app)

    resp = test_client.get("/")
    assert resp.status_code == 200
    assert "Kanban Studio" in resp.text

    # asset paths should be served under /static
    (static_dir / "foo.txt").write_text("hello")
    resp2 = test_client.get("/static/foo.txt")
    assert resp2.status_code == 200
    assert resp2.text == "hello"

    # favicon route should forward to static directory
    (static_dir / "favicon.ico").write_text("ICON")
    resp3 = test_client.get("/favicon.ico")
    assert resp3.status_code == 200
    assert resp3.text == "ICON"
