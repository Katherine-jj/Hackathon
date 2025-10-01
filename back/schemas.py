from typing import Optional
from datetime import date, time, timedelta
from pydantic import BaseModel

class FlightBase(BaseModel):
    uav_type: Optional[str] = None
    reg_number: Optional[str] = None
    date: date
    dep_time: Optional[time] = None
    arr_time: Optional[time] = None
    duration: Optional[timedelta] = None
    dep_coord: Optional[str] = None  # WKT "POINT(lon lat)"
    dest_coord: Optional[str] = None
    route_coords: Optional[str]  = None # WKT LINESTRING
    min_alt: Optional[float] = None
    max_alt: Optional[float] = None
    city: Optional[str] = None


class FlightType(BaseModel):
    uav_type: str

class City(BaseModel):
    city: str

class StatsResponse(BaseModel):
    totalPeriod: int
    totalYear: int


class FlightCreate(FlightBase):
    pass

class FlightResponse(FlightBase):
    flight_id: int

    model_config = {
        "from_attributes": True
    }

class RegionOut(BaseModel):
    name: str
    geom: str   # GeoJSON

    class Config:
        orm_mode = True