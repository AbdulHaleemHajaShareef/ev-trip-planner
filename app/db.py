"""Tiny SQLite data layer using the standard library.

Why plain sqlite3 instead of an ORM? The data model is one table, so an ORM
would add more code than it saves. Swapping to Postgres later only touches
this file.
"""

import os
import sqlite3
from collections.abc import Iterator
from contextlib import closing

from app.schemas import Charger, ChargerCreate

SCHEMA = """
CREATE TABLE IF NOT EXISTS chargers (
    id          INTEGER PRIMARY KEY AUTOINCREMENT,
    name        TEXT    NOT NULL,
    position_km REAL    NOT NULL CHECK (position_km >= 0),
    power_kw    REAL    NOT NULL CHECK (power_kw > 0),
    status      TEXT    NOT NULL CHECK (status IN ('operational', 'out_of_service'))
);
"""


def db_path() -> str:
    # Read on every call so tests can point the app at a temporary database.
    return os.environ.get("EV_DB_PATH", "chargers.db")


def init_db() -> None:
    with closing(sqlite3.connect(db_path())) as conn:
        conn.execute(SCHEMA)
        conn.commit()


def get_conn() -> Iterator[sqlite3.Connection]:
    """FastAPI dependency: one connection per request."""
    conn = sqlite3.connect(db_path(), check_same_thread=False)
    conn.row_factory = sqlite3.Row
    try:
        yield conn
    finally:
        conn.close()


def _to_charger(row: sqlite3.Row) -> Charger:
    return Charger(**dict(row))


def create_charger(conn: sqlite3.Connection, data: ChargerCreate) -> Charger:
    cur = conn.execute(
        "INSERT INTO chargers (name, position_km, power_kw, status) VALUES (?, ?, ?, ?)",
        (data.name, data.position_km, data.power_kw, data.status),
    )
    conn.commit()
    return get_charger(conn, cur.lastrowid)  # type: ignore[arg-type]


def get_charger(conn: sqlite3.Connection, charger_id: int) -> Charger | None:
    row = conn.execute("SELECT * FROM chargers WHERE id = ?", (charger_id,)).fetchone()
    return _to_charger(row) if row else None


def list_chargers(conn: sqlite3.Connection, status: str | None = None) -> list[Charger]:
    if status:
        rows = conn.execute(
            "SELECT * FROM chargers WHERE status = ? ORDER BY position_km", (status,)
        ).fetchall()
    else:
        rows = conn.execute("SELECT * FROM chargers ORDER BY position_km").fetchall()
    return [_to_charger(r) for r in rows]


def set_status(conn: sqlite3.Connection, charger_id: int, status: str) -> Charger | None:
    cur = conn.execute("UPDATE chargers SET status = ? WHERE id = ?", (status, charger_id))
    conn.commit()
    if cur.rowcount == 0:
        return None
    return get_charger(conn, charger_id)
