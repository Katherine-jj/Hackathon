# schemas.py
# --- Pydantic схемы для валидации и сериализации данных о рейсах ---

from typing import Optional
from datetime import date, time, timedelta
from pydantic import BaseModel

# --- Базовая схема рейса ---
class FlightBase(BaseModel):
    uav_type: Optional[str] = None         # Тип БПЛА
    reg_number: Optional[str] = None       # Регистрационный номер
    date: date                             # Дата рейса
    dep_time: Optional[time] = None        # Время вылета
    arr_time: Optional[time] = None        # Время посадки
    duration: Optional[timedelta] = None   # Продолжительность рейса
    dep_coord: Optional[str] = None        # WKT "POINT(lon lat)" координаты вылета
    dest_coord: Optional[str] = None       # WKT "POINT(lon lat)" координаты посадки
    route_coords: Optional[str] = None     # WKT "LINESTRING(...)" маршрут
    min_alt: Optional[float] = None        # Минимальная высота
    max_alt: Optional[float] = None        # Максимальная высота
    city: Optional[str] = None             # Город взлета

# --- Схема для списка типов БПЛА ---
class FlightType(BaseModel):
    uav_type: str

# --- Схема для списка городов ---
class City(BaseModel):
    city: str

# --- Схема для ответа со статистикой ---
class StatsResponse(BaseModel):
    totalPeriod: int    # Всего рейсов за период
    totalYear: int      # Всего рейсов за текущий год

# --- Схема для создания рейса ---
class FlightCreate(FlightBase):
    pass

# --- Схема для ответа с рейсом (включая id) ---
class FlightResponse(FlightBase):
    flight_id: int

    # Настройка для работы с объектами SQLAlchemy
    model_config = {
        "from_attributes": True
    }

# --- Схема для региона (GeoJSON) ---
class RegionOut(BaseModel):
    name: str
    geom: str   # GeoJSON

    class Config:
        orm_mode = True  # Для сериализации из SQLAlchemy ORM объектов
