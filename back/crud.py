# CRUD.py - файл для работы с базой данных C-create R - read U- update D-delete

from sqlalchemy.orm import Session
from sqlalchemy import func
import models
import schemas
import math
from geoalchemy2.shape import to_shape
from shapely.wkb import dumps
from datetime import time, timedelta
from shapely.geometry import mapping

# чистка значений для загрузки в БД
def clean_flight_data(flight_dict: dict) -> dict:
    cleaned = {}
    for key, value in flight_dict.items():
        # пустая строка → None
        if isinstance(value, str) and value.strip() == "":
            cleaned[key] = None
        # NaN → None
        elif isinstance(value, float) and math.isnan(value):
            cleaned[key] = None
        else:
            cleaned[key] = value
    return cleaned

# функция загрузки в БД
def create_flight(db: Session, flight: schemas.FlightCreate):
    data = clean_flight_data(flight.dict())
    db_flight = models.Flight(**data)
    db.add(db_flight)
    db.commit()
    db.refresh(db_flight)
    return db_flight

# перевод координатов и времени
def convert_flight_for_response(flight: models.Flight) -> dict:
    """
    Преобразует объект Flight из базы в формат, подходящий для Pydantic:
    - координаты → WKT строки
    - duration → timedelta
    """
    result = flight.__dict__.copy()

    # Геометрия
    for geom_field in ["dep_coord", "dest_coord", "route_coords"]:
        value = getattr(flight, geom_field)
        if value is not None:
            shape = to_shape(value)
            result[geom_field] = shape.wkt
        else:
            result[geom_field] = None

    # Продолжительность
    duration_value = getattr(flight, "duration")
    if isinstance(duration_value, time):
        result["duration"] = timedelta(
            hours=duration_value.hour,
            minutes=duration_value.minute,
            seconds=duration_value.second
        )
    else:
        result["duration"] = duration_value

    return result

def get_region_by_point(db: Session, lon: float, lat: float):
    point = f"POINT({lon} {lat})"
    region = db.query(models.Region).filter(
        models.Region.geom.ST_Contains(point)
    ).first()
    return region

def get_region_by_city(db: Session, city: str):
    flight = db.query(models.Flight).filter(models.Flight.city == city).first()
    if not flight:
        return None

    # берем координаты взлета
    dep_coord = db.scalar(func.ST_AsText(flight.dep_coord))
    lon, lat = dep_coord.replace("POINT(", "").replace(")", "").split()

    return get_region_by_point(db, float(lon), float(lat))

def get_flights(db: Session, skip: int = 0, limit: int = 100):
    flights = db.query(models.Flight).offset(skip).limit(limit).all()
    # конвертируем для Pydantic
    return [convert_flight_for_response(f) for f in flights]

# функция перевода в json для работы с leaflet и фронтом
def flight_to_geojson(flight):
    features = []

    if flight.dep_coord:
        geom = to_shape(flight.dep_coord)  # WKB → shapely geometry
        features.append({
            "type": "Feature",
            "geometry": mapping(geom),      # shapely → GeoJSON
            "properties": {
                "flight_id": flight.flight_id,
                "city": flight.city,
                "point_type": "departure"
            }
        })

    if flight.dest_coord:
        geom = to_shape(flight.dest_coord)
        features.append({
            "type": "Feature",
            "geometry": mapping(geom),
            "properties": {
                "flight_id": flight.flight_id,
                "point_type": "destination"
            }
        })

    if flight.route_coords:
        geom = to_shape(flight.route_coords)
        features.append({
            "type": "Feature",
            "geometry": mapping(geom),
            "properties": {
                "flight_id": flight.flight_id,
                "type": "route"
            }
        })

    return features