import pytest
from fastapi.testclient import TestClient

from app.main import app


@pytest.fixture
def client(tmp_path, monkeypatch):
    """A test client backed by a fresh temporary SQLite database."""
    monkeypatch.setenv("EV_DB_PATH", str(tmp_path / "test.db"))
    with TestClient(app) as c:  # `with` runs the startup hook that creates tables
        yield c
