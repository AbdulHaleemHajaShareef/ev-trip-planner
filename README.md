# EV Trip Planner API

A small REST API that plans charging stops for an electric-vehicle trip along a highway, and
avoids chargers that are out of service.

Built with FastAPI, SQLite and pytest. All data in this repo is **synthetic**.

## Why I built it

I wanted to build a model which predicts where EV drivers are most likely to run out of charge on highways. Its built basically for EV vehicles.

## Run it

```bash
python -m venv .venv
source .venv/bin/activate              # Windows PowerShell: .venv\Scripts\Activate.ps1
pip install -r requirements-dev.txt

uvicorn app.main:app --reload          # API at http://127.0.0.1:8000, docs at /docs
python -m scripts.seed                 # optional: load synthetic demo chargers
pytest                                 # run the tests
```

With Docker:

```bash
docker build -t ev-trip-planner .
docker run -p 8000:8000 -v ev-data:/data ev-trip-planner
```

## Endpoints

| Method | Path | Purpose |
|--------|------|---------|
| POST | `/chargers` | Add a charger |
| GET | `/chargers?status=operational` | List chargers (sorted by position, optional filter) |
| GET | `/chargers/{id}` | Get one charger |
| PATCH | `/chargers/{id}/status` | Mark a charger operational / out_of_service |
| POST | `/plan-trip` | Compute the charging stops for a trip |

Example:

```bash
curl -X POST localhost:8000/plan-trip -H 'content-type: application/json' \
  -d '{"route_length_km": 300, "range_km": 400, "start_battery_pct": 60}'
```

## How the planner works

The route is modelled as a straight line from km 0 to the destination, with chargers at
fixed positions along it. The car's usable range at any moment is
`range_km * (battery_pct - reserve_pct) / 100` — you never plan to dip below the reserve.
Every stop recharges to 100%.

The algorithm is greedy:

1. If the destination is within current reach, stop — return the stops so far.
2. Otherwise, look at all **operational** chargers ahead of the current position that are
   within reach, and pick the **furthest** one.
3. If none is reachable, the trip is infeasible and `NoFeasibleRouteError` is raised.
4. Otherwise "drive" there, recharge to 100%, and repeat.

Picking the furthest reachable charger is optimal for minimising the number of stops:
it leaves the car as close to the destination as possible, and any closer stop could
always be skipped in favour of the furthest one without making the rest of the trip worse.
The loop always terminates because the car's position strictly increases on every
iteration and charger positions are finite.

For a real road network you'd replace the straight line with a weighted graph and run
Dijkstra/A* with charging time in the cost, but the greedy version keeps the domain
logic small enough to test exhaustively.

## Design decisions

- **Greedy furthest-charger strategy:** minimises stop count, is O(n log n) thanks to one
  up-front sort, and is easy to reason about and test. Proven optimal for this simplified
  model by an exchange argument.
- **`/plan-trip` returns 200 with `feasible: false` instead of an error:** "no valid plan
  exists" is a valid answer to the question the client asked, not a malformed request, so
  a 4xx would be misleading. The client can still distinguish the cases via the body.
- **Plain `sqlite3` instead of an ORM:** the data model is a single table, so an ORM would
  add more code than it saves. All SQL lives in `app/db.py`, so swapping to Postgres later
  touches one file only.
- **Reserve battery percentage:** real routing never plans to arrive at 0%. A configurable
  `reserve_pct` (default 10%) keeps that safety margin explicit and testable.

## What I would do next

- Model a real road network (graph + Dijkstra) instead of one straight line
- Account for charging time and charger power, not just stop count
- Add a `/risk/{segment}` endpoint that flags stretches with large charger gaps
- Move to Postgres and add pagination
