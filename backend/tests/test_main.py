from fastapi.testclient import TestClient
from backend import main
from backend.database import init_db

# Initialize database before running tests
init_db()

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


def test_board_endpoints():
    """Test /api/board GET and POST endpoints."""
    from fastapi.testclient import TestClient
    test_client = TestClient(main.app)
    
    # Unauthenticated GET should fail
    resp = test_client.get("/api/board")
    assert resp.status_code == 401

    # Log in
    login_resp = test_client.post(
        "/api/login", json={"username": "user", "password": "password"}
    )
    assert login_resp.status_code == 200
    session_cookie = login_resp.cookies.get("session")
    assert session_cookie is not None

    # Authenticated GET should return the board
    resp = test_client.get("/api/board")
    assert resp.status_code == 200
    board_data = resp.json()
    assert "board" in board_data
    board = board_data["board"]
    assert "id" in board
    assert "user_id" in board
    assert "title" in board
    assert "data" in board
    assert "columns" in board["data"]
    assert "cards" in board["data"]
    assert len(board["data"]["columns"]) == 5

    # Update the board (POST)
    new_board_data = board["data"].copy()
    new_board_data["columns"][0]["title"] = "Updated Backlog"

    update_resp = test_client.post(
        "/api/board", json={"data": new_board_data}
    )
    assert update_resp.status_code == 200
    updated = update_resp.json()["board"]
    assert updated["data"]["columns"][0]["title"] == "Updated Backlog"
    assert "updated_at" in updated

    # Missing data field should fail
    resp = test_client.post("/api/board", json={})
    assert resp.status_code == 400


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
