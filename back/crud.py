# CRUD.py - файл для работы с базой данных
# C - Create, R - Read, U - Update, D - Delete

from sqlalchemy.orm import Session
from sqlalchemy import func
import models
import schemas
import math
from geoalchemy2.shape import to_shape
from shapely.wkb import dumps
from datetime import time, timedelta
from shapely.geometry import mapping

# --- Функции для работы с данными ---

def clean_flight_data(flight_dict: dict) -> dict:
    """
    Приводит значения рейса к корректному виду для базы данных:
    - пустые строки → None
    - NaN → None
    """
    cleaned = {}
    for key, value in flight_dict.items():
        if isinstance(value, str) and value.strip() == "":
            cleaned[key] = None
        elif isinstance(value, float) and math.isnan(value):
            cleaned[key] = None
        else:
            cleaned[key] = value
    return cleaned

def create_flight(db: Session, flight: schemas.FlightCreate):
    """
    Создает новый объект Flight в базе данных.
    """
    data = clean_flight_data(flight.dict())
    db_flight = models.Flight(**data)
    db.add(db_flight)
    db.commit()
    db.refresh(db_flight)
    return db_flight

def convert_flight_for_response(flight: models.Flight) -> dict:
    """
    Преобразует объект Flight из базы в формат, подходящий для Pydantic:
    - координаты (dep_coord, dest_coord, route_coords) → WKT строки
    - duration → timedelta
    """
    result = flight.__dict__.copy()

    # Конвертация геометрии в WKT
    for geom_field in ["dep_coord", "dest_coord", "route_coords"]:
        value = getattr(flight, geom_field)
        if value is not None:
            shape = to_shape(value)
            result[geom_field] = shape.wkt
        else:
            result[geom_field] = None

    # Конвертация времени полета
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

# --- Работа с регионами ---

def get_region_by_point(db: Session, lon: float, lat: float):
    """
    Определяет регион по координатам точки (lon, lat)
    """
    point = f"POINT({lon} {lat})"
    region = db.query(models.Region).filter(
        models.Region.geom.ST_Contains(point)
    ).first()
    return region

def get_region_by_city(db: Session, city: str):
    """
    Определяет регион по городу, используя координаты взлета первого рейса в этом городе.
    """
    flight = db.query(models.Flight).filter(models.Flight.city == city).first()
    if not flight:
        return None

    # Получаем координаты взлета
    dep_coord = db.scalar(func.ST_AsText(flight.dep_coord))
    lon, lat = dep_coord.replace("POINT(", "").replace(")", "").split()

    return get_region_by_point(db, float(lon), float(lat))

# --- Получение рейсов ---

def get_flights(db: Session, skip: int = 0, limit: int = 100):
    """
    Возвращает список рейсов с возможностью пагинации.
    Результат конвертируется в формат, подходящий для Pydantic.
    """
    flights = db.query(models.Flight).offset(skip).limit(limit).all()
    return [convert_flight_for_response(f) for f in flights]

# --- Конвертация рейса в GeoJSON для фронтенда и Leaflet ---

def flight_to_geojson(flight):
    """
    Преобразует рейс в список GeoJSON features:
    - dep_coord → точка вылета
    - dest_coord → точка назначения
    - route_coords → маршрут (линия)
    """
    features = []

    # Точка вылета
    if flight.dep_coord:
        geom = to_shape(flight.dep_coord)  # WKB → shapely
        features.append({
            "type": "Feature",
            "geometry": mapping(geom),      # shapely → GeoJSON
            "properties": {
                "flight_id": flight.flight_id,
                "city": flight.city,
                "point_type": "departure"
            }
        })

    # Точка назначения
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

    # Маршрут
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
