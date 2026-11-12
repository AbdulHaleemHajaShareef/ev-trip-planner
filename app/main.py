import sqlite3
from contextlib import asynccontextmanager

from fastapi import Depends, FastAPI, HTTPException, Query

from app import db
from app.planner import NoFeasibleRouteError, plan_trip
from app.schemas import (
    Charger,
    ChargerCreate,
    ChargerStatus,
    ChargerStatusUpdate,
    TripPlan,
    TripRequest,
)


@asynccontextmanager
async def lifespan(_: FastAPI):
    db.init_db()
    yield


app = FastAPI(title="EV Trip Planner API", version="0.1.0", lifespan=lifespan)


@app.post("/chargers", response_model=Charger, status_code=201)
def create_charger(data: ChargerCreate, conn: sqlite3.Connection = Depends(db.get_conn)):
    return db.create_charger(conn, data)


@app.get("/chargers", response_model=list[Charger])
def list_chargers(
    status: ChargerStatus | None = Query(default=None),
    conn: sqlite3.Connection = Depends(db.get_conn),
):
    return db.list_chargers(conn, status)


@app.get("/chargers/{charger_id}", response_model=Charger)
def get_charger(charger_id: int, conn: sqlite3.Connection = Depends(db.get_conn)):
    charger = db.get_charger(conn, charger_id)
    if charger is None:
        raise HTTPException(status_code=404, detail="Charger not found")
    return charger


@app.patch("/chargers/{charger_id}/status", response_model=Charger)
def update_status(
    charger_id: int,
    body: ChargerStatusUpdate,
    conn: sqlite3.Connection = Depends(db.get_conn),
):
    charger = db.set_status(conn, charger_id, body.status)
    if charger is None:
        raise HTTPException(status_code=404, detail="Charger not found")
    return charger


@app.post("/plan-trip", response_model=TripPlan)
def plan(req: TripRequest, conn: sqlite3.Connection = Depends(db.get_conn)):
    chargers = db.list_chargers(conn)
    try:
        stops = plan_trip(
            route_length_km=req.route_length_km,
            range_km=req.range_km,
            start_battery_pct=req.start_battery_pct,
            chargers=chargers,
            reserve_pct=req.reserve_pct,
        )
    except NoFeasibleRouteError as exc:
        # "No plan exists" is a valid answer, not a client error, so it is a 200.
        return TripPlan(feasible=False, reason=str(exc))
    return TripPlan(feasible=True, stops=stops)
