def make(client, **overrides):
    body = {"name": "Stop", "position_km": 100, "power_kw": 150}
    body.update(overrides)
    return client.post("/chargers", json=body)


def test_create_charger_defaults_to_operational(client):
    res = make(client)
    assert res.status_code == 201
    data = res.json()
    assert data["id"] == 1
    assert data["status"] == "operational"


def test_create_charger_rejects_negative_position(client):
    assert make(client, position_km=-5).status_code == 422


def test_create_charger_rejects_zero_power(client):
    assert make(client, power_kw=0).status_code == 422


def test_create_charger_rejects_unknown_status(client):
    assert make(client, status="broken").status_code == 422


def test_list_is_sorted_by_position(client):
    make(client, name="Far", position_km=200)
    make(client, name="Near", position_km=50)
    names = [c["name"] for c in client.get("/chargers").json()]
    assert names == ["Near", "Far"]


def test_list_filters_by_status(client):
    make(client, name="Ok")
    make(client, name="Dead", status="out_of_service")
    res = client.get("/chargers", params={"status": "out_of_service"})
    assert [c["name"] for c in res.json()] == ["Dead"]


def test_get_charger_404(client):
    assert client.get("/chargers/999").status_code == 404


def test_patch_status(client):
    make(client)
    res = client.patch("/chargers/1/status", json={"status": "out_of_service"})
    assert res.status_code == 200
    assert res.json()["status"] == "out_of_service"


def test_patch_status_404(client):
    res = client.patch("/chargers/999/status", json={"status": "operational"})
    assert res.status_code == 404
