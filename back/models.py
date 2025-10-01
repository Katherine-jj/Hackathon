from sqlalchemy import Column, Integer, String, Date, Time, Float, Interval
from geoalchemy2 import Geography, Geometry
from database import Base

class Flight(Base):
    __tablename__ = "flights"

    flight_id = Column(Integer, primary_key=True, index=True)
    uav_type = Column(String, nullable=True)
    reg_number = Column(String, nullable=True)
    date = Column(Date, nullable=True)
    dep_time = Column(Time, nullable=True)
    arr_time = Column(Time, nullable=True)
    duration = Column(Interval, nullable=True)
    dep_coord = Column(Geography("POINT"), nullable=True)
    dest_coord = Column(Geography("POINT"), nullable=True)
    min_alt = Column(Float, nullable=True)
    max_alt = Column(Float, nullable=True)
    route_coords = Column(Geography("LINESTRING"), nullable=True)
    city = Column(String, nullable=True)

class Region(Base):
    __tablename__ = "russia_regions"
    id = Column(Integer, primary_key=True, index=True)
    nl_name_1 = Column(String, index=True)
    geom = Column(Geometry("MULTIPOLYGON", srid=4326))