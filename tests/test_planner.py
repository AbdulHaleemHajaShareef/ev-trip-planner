import pytest

from app.planner import NoFeasibleRouteError, plan_trip
from app.schemas import Charger

# Reference numbers used below: range_km=400, reserve 10%.
#   full battery usable range = 400 * 90 / 100 = 360 km


def ch(id_, pos, status="operational"):
    return Charger(id=id_, name=f"C{id_}", position_km=pos, power_kw=150, status=status)


def positions(stops):
    return [s.position_km for s in stops]


def test_no_stops_needed_when_destination_in_range():
    assert plan_trip(100, 400, 100, [ch(1, 50)]) == []


def test_one_stop_needed():
    stops = plan_trip(500, 400, 100, [ch(1, 200), ch(2, 340)])
    assert positions(stops) == [340]


def test_picks_furthest_reachable_charger():
    stops = plan_trip(500, 400, 100, [ch(1, 100), ch(2, 200), ch(3, 300)])
    assert positions(stops) == [300]


def test_skips_out_of_service_chargers():
    stops = plan_trip(500, 400, 100, [ch(1, 340, "out_of_service"), ch(2, 300)])
    assert positions(stops) == [300]


def test_multiple_stops():
    stops = plan_trip(1000, 400, 100, [ch(1, 350), ch(2, 700)])
    assert positions(stops) == [350, 700]


def test_low_starting_battery_uses_nearby_charger():
    # 20% battery, 10% reserve -> only 40 km of usable range at the start.
    stops = plan_trip(300, 400, 20, [ch(1, 30)])
    assert positions(stops) == [30]


def test_low_starting_battery_with_no_charger_in_reach_fails():
    with pytest.raises(NoFeasibleRouteError):
        plan_trip(300, 400, 20, [ch(1, 50)])


def test_battery_at_or_below_reserve_cannot_move_without_charger():
    with pytest.raises(NoFeasibleRouteError):
        plan_trip(300, 400, 5, [ch(1, 10)])


def test_fails_when_only_charger_is_out_of_range():
    with pytest.raises(NoFeasibleRouteError):
        plan_trip(500, 400, 100, [ch(1, 400)])


def test_fails_when_gap_after_a_stop_is_too_big():
    # Stop at 300 -> can reach 660, but the next charger is at 700.
    with pytest.raises(NoFeasibleRouteError):
        plan_trip(1000, 400, 100, [ch(1, 300), ch(2, 700)])


def test_out_of_service_charger_breaks_an_otherwise_valid_trip():
    # Mirrors the "single broken charger" idea: with it working the trip is fine.
    ok = plan_trip(500, 400, 100, [ch(1, 340)])
    assert positions(ok) == [340]
    with pytest.raises(NoFeasibleRouteError):
        plan_trip(500, 400, 100, [ch(1, 340, "out_of_service")])


def test_does_not_mutate_input_list():
    chargers = [ch(2, 340), ch(1, 200)]
    plan_trip(500, 400, 100, chargers)
    assert [c.id for c in chargers] == [2, 1]
