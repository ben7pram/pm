from fastapi import FastAPI, Request, Response, Cookie
from fastapi.responses import HTMLResponse, JSONResponse, FileResponse
from fastapi.staticfiles import StaticFiles
import os
from typing import Optional
from .database import init_db, get_user_by_username, get_board_for_user, update_board_for_user
from .openrouter import call_openrouter


def create_app(static_dir: Optional[str] = None) -> FastAPI:
    """Factory to create the FastAPI application.

    `static_dir` can be overridden for testing; if omitted the default
    `backend/static` directory is used.
    """
    app = FastAPI()

    # initialize database on startup
    @app.on_event("startup")
    def startup():
        init_db()

    # determine static directory
    if static_dir is None:
        static_dir = os.path.join(os.path.dirname(__file__), "static")

    # API routes
    @app.get("/api/hello")
    def hello():
        return JSONResponse(content={"message": "Hello from backend!"})

    # simple auth endpoints for fake user sign-in
    @app.post("/api/login")
    def login(credentials: dict, response: Response):
        # validate credentials against database
        username = credentials.get("username")
        password = credentials.get("password")
        user = get_user_by_username(username)
        
        # MVP: plain-text password comparison
        if user and password == "password":
            # set session cookie with user id for later board access
            response.set_cookie(
                key="session",
                value=f"user_{user['id']}",
                httponly=True,
                samesite="lax",
            )
            return {"authenticated": True}
        return JSONResponse(status_code=401, content={"authenticated": False})

    @app.post("/api/logout")
    def logout(response: Response):
        response.delete_cookie("session")
        return {"authenticated": False}

    @app.get("/api/me")
    def me(session: Optional[str] = Cookie(None)):
        # session value is now user_{id}; validate it exists
        if session and session.startswith("user_"):
            return {"authenticated": True}
        return {"authenticated": False}

    @app.get("/api/board")
    def get_board(session: Optional[str] = Cookie(None)):
        """Retrieve the kanban board for the authenticated user."""
        if not session or not session.startswith("user_"):
            return JSONResponse(status_code=401, content={"error": "Not authenticated"})
        
        user_id = int(session.split("_")[1])
        board = get_board_for_user(user_id)
        if not board:
            return JSONResponse(status_code=404, content={"error": "Board not found"})
        return {"board": board}

    @app.post("/api/board")
    def update_board(body: dict, session: Optional[str] = Cookie(None)):
        """Update the kanban board for the authenticated user."""
        if not session or not session.startswith("user_"):
            return JSONResponse(status_code=401, content={"error": "Not authenticated"})
        
        user_id = int(session.split("_")[1])
        board_data = body.get("data")
        if not board_data:
            return JSONResponse(status_code=400, content={"error": "Missing board data"})
        
        success = update_board_for_user(user_id, board_data)
        if not success:
            return JSONResponse(status_code=404, content={"error": "Board not found"})
        
        updated_board = get_board_for_user(user_id)
        return {"board": updated_board}

    @app.get("/", response_class=HTMLResponse)
    def root():
        index = os.path.join(static_dir, "index.html")
        if os.path.exists(index):
            with open(index, "r") as f:
                return HTMLResponse(content=f.read())
        return HTMLResponse(content="<h1>Backend running</h1>")

    # serve favicon if present (Next export references /favicon.ico)
    @app.get("/favicon.ico")
    def favicon():
        fav = os.path.join(static_dir, "favicon.ico")
        if os.path.exists(fav):
            from fastapi.responses import FileResponse
            return FileResponse(fav)
        return JSONResponse(status_code=404, content={})

    # finally, mount static files at /static so assets can be fetched
    if os.path.isdir(static_dir):
        app.mount("/static", StaticFiles(directory=static_dir), name="static")

    return app


# create the default app instance
app = create_app()
