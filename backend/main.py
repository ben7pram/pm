from fastapi import FastAPI, Request, Response, Cookie
from fastapi.responses import HTMLResponse, JSONResponse, FileResponse
from fastapi.staticfiles import StaticFiles
import os
from typing import Optional


def create_app(static_dir: Optional[str] = None) -> FastAPI:
    """Factory to create the FastAPI application.

    `static_dir` can be overridden for testing; if omitted the default
    `backend/static` directory is used.
    """
    app = FastAPI()

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
        # log for debugging to confirm backend saw the request
        print("backend received login", credentials)
        # credentials expected to have `username` and `password` keys
        if (
            credentials.get("username") == "user"
            and credentials.get("password") == "password"
        ):
            # set a trivial session cookie
            response.set_cookie(
                key="session",
                value="1",
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
        return {"authenticated": session == "1"}

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
