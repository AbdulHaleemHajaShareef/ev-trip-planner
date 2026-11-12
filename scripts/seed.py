"""Fill the database with SYNTHETIC chargers along a 300 km highway.

All data here is made up for demo purposes.
Run from the project root:  python -m scripts.seed
"""

import sqlite3

from app import db
from app.schemas import ChargerCreate

SYNTHETIC_CHARGERS = [
    ("Oasis Stop A", 45, 150, "operational"),
    ("Desert Rest B", 110, 150, "operational"),
    ("Highway Hub C", 175, 350, "out_of_service"),
    ("Dune Plaza D", 190, 50, "operational"),
    ("Coastal Stop E", 260, 150, "operational"),
]


def main() -> None:
    db.init_db()
    conn = sqlite3.connect(db.db_path())
    conn.row_factory = sqlite3.Row
    for name, pos, power, status in SYNTHETIC_CHARGERS:
        db.create_charger(
            conn, ChargerCreate(name=name, position_km=pos, power_kw=power, status=status)
        )
    conn.close()
    print(f"Seeded {len(SYNTHETIC_CHARGERS)} chargers into {db.db_path()}")


if __name__ == "__main__":
    main()
