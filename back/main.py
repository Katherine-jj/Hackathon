from fastapi import FastAPI, UploadFile, File, Depends, Query
from sqlalchemy.orm import Session
from sqlalchemy import extract, func
from fastapi.middleware.cors import CORSMiddleware
from typing import List, Literal
from datetime import datetime
from geoalchemy2 import functions as geofunc

import database
import crud
from database import SessionLocal, engine, Base
from models import Flight
from crud import create_flight, get_flights
from parser import parse_excel
import schemas
from schemas import FlightType, City, StatsResponse,  FlightResponse


Base.metadata.create_all(bind=engine)

app = FastAPI()


# --- CORS ---
origins = [
    "http://localhost:5173",  # адрес React dev server
]
app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


# --- Dependency для сессии ---
def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()



# --- Получение всех рейсов ---
@app.get("/flights/", response_model=List[FlightResponse])
def read_flights(db: Session = Depends(get_db)):
    flights = get_flights(db)
    return flights

@app.get("/flights/types", response_model=list[FlightType])
def get_uav_types(db: Session = Depends(get_db)):
    types = db.query(Flight.uav_type).distinct().all()
    return [{"uav_type": t[0]} for t in types]

# --- Эндпоинт: города ---
@app.get("/flights/cities", response_model=list[City])
def get_cities(db: Session = Depends(get_db)):
    cities = db.query(Flight.city).distinct().all()
    return [{"city": c[0]} for c in cities]

# --- Эндпоинт: статистика ---
@app.get("/flights/stats", response_model=StatsResponse)
def get_stats(
    uav_type: str = None,
    city: str = None,
    startDate: str = None,
    endDate: str = None,
    db: Session = Depends(get_db),
):
    query = db.query(Flight)

    if uav_type:
        query = query.filter(Flight.uav_type == uav_type)
    if city:
        query = query.filter(Flight.city == city)
    if startDate:
        start_date_obj = datetime.fromisoformat(startDate).date()
        query = query.filter(Flight.date >= start_date_obj)
    if endDate:
        end_date_obj = datetime.fromisoformat(endDate).date()
        query = query.filter(Flight.date <= end_date_obj)

    total_period = query.count()
    total_year = db.query(Flight).filter(extract('year', Flight.date) == datetime.now().year).count()

    return {"totalPeriod": total_period, "totalYear": total_year}
@app.get("/flights/stats/yearly")
def get_yearly_stats(
    uav_type: str = None,
    city: str = None,
    startDate: str = None,
    endDate: str = None,
    db: Session = Depends(get_db),
):
    query = db.query(Flight)

    if uav_type:
        query = query.filter(Flight.uav_type == uav_type)
    if city:
        query = query.filter(Flight.city == city)
    if startDate:
        query = query.filter(Flight.date >= datetime.fromisoformat(startDate))
    if endDate:
        query = query.filter(Flight.date <= datetime.fromisoformat(endDate))

    results = (
        query.with_entities(
            func.to_char(Flight.date, 'Mon').label("month"),
            func.date_trunc('month', Flight.date).label("month_start"),
            func.count(Flight.flight_id).label("count"),
        )
        .group_by("month", "month_start")
        .order_by("month_start")   # 🔑 сортировка по времени
        .all()
    )

    return [{"name": r.month, "value": r.count} for r in results]

# --- Эндпоинт: по месяцам ---
@app.get("/flights/monthly")
def get_flights_monthly(
    uav_type: str = None,
    city: str = None,
    startDate: str = None,
    endDate: str = None,
    db: Session = Depends(get_db),
):
    query = db.query(
        func.to_char(Flight.date, 'YYYY-MM'),  # SQLite
        func.count(Flight.flight_id)
    )

    if uav_type:
        query = query.filter(Flight.uav_type == uav_type)
    if city:
        query = query.filter(Flight.city == city)
    if startDate:
        query = query.filter(Flight.date >= datetime.fromisoformat(startDate))
    if endDate:
        query = query.filter(Flight.date <= datetime.fromisoformat(endDate))

    query = query.group_by(func.to_char(Flight.date, 'YYYY-MM')).order_by(func.to_char(Flight.date, 'YYYY-MM'))
    results = query.all()

    return [{"month": r[0], "count": r[1]} for r in results]

@app.get("/flights/top")
def get_top_metrics(
    groupBy: Literal["city", "uav_type", "date"] = Query("date", description="Группировка"),
    uav_type: str | None = None,
    city: str | None = None,
    startDate: str | None = None,
    endDate: str | None = None,
    db: Session = Depends(get_db),
):
    query = db.query(Flight)

    if uav_type:
        query = query.filter(Flight.uav_type == uav_type)
    if city:
        query = query.filter(Flight.city == city)
    if startDate:
        query = query.filter(Flight.date >= datetime.fromisoformat(startDate))
    if endDate:
        query = query.filter(Flight.date <= datetime.fromisoformat(endDate))

    if groupBy == "city":
        results = (
            query.with_entities(Flight.city, func.count(Flight.flight_id))
            .group_by(Flight.city)
            .order_by(func.count(Flight.flight_id).desc())
            .limit(10)
            .all()
        )
        return [{"name": r[0], "value": r[1]} for r in results]

    elif groupBy == "uav_type":
        results = (
            query.with_entities(Flight.uav_type, func.count(Flight.flight_id))
            .group_by(Flight.uav_type)
            .order_by(func.count(Flight.flight_id).desc())
            .limit(10)
            .all()
        )
        return [{"name": r[0], "value": r[1]} for r in results]

    elif groupBy == "date":
        results = (
            query.with_entities(
                func.to_char(Flight.date, 'YYYY-MM'),
                func.count(Flight.flight_id)
            )
            .group_by(func.to_char(Flight.date, 'YYYY-MM'))
            .order_by(func.count(Flight.flight_id).desc())
            .limit(10)
            .all()
        )
        return [{"name": r[0], "value": r[1]} for r in results]

"""@app.get("/region/by_city", response_model=schemas.RegionOut)
def get_region(city: str, db: Session = Depends(get_db)):
    region = crud.get_region_by_city(db, city)
    if not region:
        return {"name": "Не найден", "geom": None}

    geom = db.scalar(func.ST_AsGeoJSON(region.geom))
    return {"name": region.name, "geom": geom}
"""

# --- Загрузка Excel ---
@app.post("/upload/")
async def upload_file(
    file: UploadFile = File(...),
    db: Session = Depends(get_db)
):
    contents = await file.read()
    df = parse_excel(contents)

    # нормализация df в соответствии с FlightCreate
    for _, row in df.iterrows():
        flight_data = schemas.FlightCreate(
            uav_type=row['uav_type'],
            reg_number=row['reg_number'],
            date=row['date'],
            dep_time=row['dep_time'],
            arr_time=row['arr_time'],
            duration=row['duration'],
            dep_coord=row['dep_coord'],       # уже WKT ("POINT(...)")
            dest_coord=row['dest_coord'],     # уже WKT
            min_alt=row['min_alt'],
            max_alt=row['max_alt'],
            route_coords=row['route_coords'], # уже WKT ("LINESTRING(...)")
            city=row['city']
        )
        create_flight(db, flight_data)

    return {"status": "ok"}
