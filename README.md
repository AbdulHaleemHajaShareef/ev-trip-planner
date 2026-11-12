# EV Trip Planner API

A small REST API that plans charging stops for an electric-vehicle trip along a highway, and
avoids chargers that are out of service.

Built with FastAPI, SQLite and pytest. All data in this repo is **synthetic**.

## Why I built it

<!-- WRITE THIS IN YOUR OWN WORDS (2-3 sentences). Example direction: you worked on EV
stranding-risk analysis during an internship and wanted to build the routing side as a clean,
tested backend service from scratch. Do not include any employer data. -->

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

<!-- FILL IN after you write app/planner.py: the greedy approach in your own words. -->

## Design decisions

<!-- Fill in 3-4 of these once you have made them. Suggested topics: -->
- **Greedy furthest-charger strategy:** TODO
- **`/plan-trip` returns 200 with `feasible: false` instead of an error:** TODO
- **Plain `sqlite3` instead of an ORM:** TODO
- **Reserve battery percentage:** TODO

## What I would do next

- Model a real road network (graph + Dijkstra) instead of one straight line
- Account for charging time and charger power, not just stop count
- Add a `/risk/{segment}` endpoint that flags stretches with large charger gaps
- Move to Postgres and add pagination
