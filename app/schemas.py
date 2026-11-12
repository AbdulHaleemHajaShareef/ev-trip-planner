from typing import Literal

from pydantic import BaseModel, Field

ChargerStatus = Literal["operational", "out_of_service"]


class ChargerCreate(BaseModel):
    name: str = Field(min_length=1, max_length=100)
    position_km: float = Field(ge=0, description="Distance from the route start, in km")
    power_kw: float = Field(gt=0)
    status: ChargerStatus = "operational"


class Charger(ChargerCreate):
    id: int


class ChargerStatusUpdate(BaseModel):
    status: ChargerStatus


class TripRequest(BaseModel):
    route_length_km: float = Field(gt=0)
    range_km: float = Field(gt=0, description="Range of the car on a full battery")
    start_battery_pct: float = Field(ge=0, le=100)
    reserve_pct: float = Field(
        default=10, ge=0, le=50, description="Battery % you never want to drop below"
    )


class TripPlan(BaseModel):
    feasible: bool
    stops: list[Charger] = []
    reason: str | None = None
