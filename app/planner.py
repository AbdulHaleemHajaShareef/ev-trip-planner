"""Trip planning logic.

Model (deliberately simple so it can be explained in 30 seconds):
  * The route is a straight line from km 0 to `route_length_km`.
  * Each charger sits at `position_km` on that line.
  * The car starts at km 0 with `start_battery_pct` charge.
  * Usable range = range_km * (battery_pct - reserve_pct) / 100.
    (Never plan to drop below the reserve.)
  * Every stop recharges the car to 100%, so usable range after a stop is
    range_km * (100 - reserve_pct) / 100.
  * Chargers with status "out_of_service" must never be used.

Algorithm (greedy):
  1. Compute how far the car can currently go.
  2. If the destination is within reach, you are done.
  3. Otherwise, among operational chargers AHEAD of the current position and
     within reach, pick the FURTHEST one. Go there and recharge.
  4. If no charger is reachable, raise NoFeasibleRouteError.
  5. Repeat.
"""

from app.schemas import Charger


class NoFeasibleRouteError(Exception):
    """Raised when the car cannot complete the trip with the available chargers."""


def plan_trip(
    route_length_km: float,
    range_km: float,
    start_battery_pct: float,
    chargers: list[Charger],
    reserve_pct: float = 10.0,
) -> list[Charger]:
    """Return the ordered list of chargers to stop at (empty list = no stops needed)."""
    # Candidates never change, so sort once up front instead of re-filtering
    # on every iteration. Sorting by position makes "furthest reachable" a
    # single scan from the end of the window.
    usable = [c for c in chargers if c.status == "operational"]
    usable.sort(key=lambda c: c.position_km)

    position = 0.0
    battery_pct = start_battery_pct
    stops: list[Charger] = []

    while True:
        # Never plan to arrive anywhere with less than the reserve.
        reachable_km = range_km * (battery_pct - reserve_pct) / 100

        if route_length_km <= position + reachable_km:
            return stops  # Destination is within reach: we are done.

        # Furthest operational charger ahead of us and within reach.
        window_end = position + reachable_km
        reachable = [c for c in usable if position < c.position_km <= window_end]
        if not reachable:
            raise NoFeasibleRouteError(
                f"No operational charger within reach at km {position:.0f} "
                f"(can travel {reachable_km:.0f} km)."
            )

        stop = reachable[-1]  # list is sorted by position, so last = furthest
        stops.append(stop)
        position = stop.position_km
        battery_pct = 100.0  # every stop recharges to 100%
