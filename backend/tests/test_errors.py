from fastapi import FastAPI
from fastapi.testclient import TestClient

from app.api.errors import register_error_handlers
from app.exceptions import CVNotFound


def _app() -> FastAPI:
    app = FastAPI()
    register_error_handlers(app)

    @app.get("/boom")
    async def boom():
        raise CVNotFound("CV not found.")

    return app


def test_app_error_renders_envelope():
    client = TestClient(_app())
    r = client.get("/boom")
    assert r.status_code == 404
    assert r.json() == {"error": {"code": "cv_not_found", "message": "CV not found."}}