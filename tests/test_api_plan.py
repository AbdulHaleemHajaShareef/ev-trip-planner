def add(client, pos, status="operational"):
    client.post(
        "/chargers",
        json={"name": f"C{pos}", "position_km": pos, "power_kw": 150, "status": status},
    )


TRIP = {"route_length_km": 500, "range_km": 400, "start_battery_pct": 100}


def test_plan_trip_returns_stops(client):
    add(client, 340)
    res = client.post("/plan-trip", json=TRIP)
    assert res.status_code == 200
    body = res.json()
    assert body["feasible"] is True
    assert [s["position_km"] for s in body["stops"]] == [340]


def test_plan_trip_reports_infeasible_without_error(client):
    add(client, 340, status="out_of_service")
    res = client.post("/plan-trip", json=TRIP)
    assert res.status_code == 200
    body = res.json()
    assert body["feasible"] is False
    assert body["stops"] == []
    assert body["reason"]


def test_plan_trip_validates_battery(client):
    res = client.post("/plan-trip", json={**TRIP, "start_battery_pct": 150})
    assert res.status_code == 422


def test_plan_trip_validates_range(client):
    res = client.post("/plan-trip", json={**TRIP, "range_km": 0})
    assert res.status_code == 422
