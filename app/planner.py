"""Trip planning logic. THIS IS THE PART YOU WRITE.

Model (kept deliberately simple so you can explain it in 30 seconds):
  * The route is a straight line from km 0 to `route_length_km`.
  * Each charger sits at `position_km` on that line.
  * The car starts at km 0 with `start_battery_pct` charge.
  * Usable range = range_km * (battery_pct - reserve_pct) / 100.
    (Never plan to drop below the reserve.)
  * Every stop recharges the car to 100%, so usable range after a stop is
    range_km * (100 - reserve_pct) / 100.
  * Chargers with status "out_of_service" must never be used.

Algorithm to implement (greedy):
  1. Compute how far the car can currently go.
  2. If the destination is within reach, you are done.
  3. Otherwise, among operational chargers AHEAD of the current position and
     within reach, pick the FURTHEST one. Go there and recharge.
  4. If no charger is reachable, raise NoFeasibleRouteError.
  5. Repeat.

Be ready to explain on camera:
  * Why picking the furthest reachable charger minimises the number of stops.
  * Why the loop always terminates (position strictly increases).
  * What you would change for a real map (graph + Dijkstra, charge time, etc.).
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
    # TODO: implement the greedy algorithm described in the module docstring.
    raise NotImplementedError("Write the planner, then run: pytest")
