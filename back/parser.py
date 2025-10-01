# parser.py
import re
import pandas as pd
from datetime import datetime, timedelta, time
from io import BytesIO

# --- Словарь регион → город ---
region_to_city = {
    "Санкт-Петербургский": "Санкт-Петербург",
    "Ростовский": "Ростов-на-Дону",
    "Новосибирский": "Новосибирск",
    "Екатеринбургский": "Екатеринбург",
    "Московский": "Москва",
    "Хабаровский": "Хабаровск",
    "Красноярский": "Красноярск",
    "Иркутский": "Иркутск",
    "Якутский": "Якутск",
    "Тюменский": "Тюмень",
    "Самарский": "Самара",
    "Симферопольский": "Симферополь",
    "Магаданский": "Магадан",
    "Калининградский": "Калининград",
    "Центр ЕС ОрВД": "Москва",
}

# --- Вспомогательные функции ---
def convert_coord(coord: str) -> tuple | None:
    """DDMMNDDDMME → (lat, lon)"""
    m = re.match(r"(\d{2})(\d{2})([NS])(\d{3})(\d{2})([EW])", coord)
    if not m:
        return None

    lat_deg, lat_min, ns, lon_deg, lon_min, ew = m.groups()
    lat = int(lat_deg) + int(lat_min) / 60
    lon = int(lon_deg) + int(lon_min) / 60

    if ns == "S":
        lat = -lat
    if ew == "W":
        lon = -lon

    return lat, lon




def normalize_time(t: str | None) -> time | None:
    """Приводим строку из Excel к объекту datetime.time"""
    if not t:
        return None
    t = re.sub(r'\D', '', str(t))
    if len(t) >= 4:
        try:
            return datetime.strptime(t[:4], "%H%M").time()
        except ValueError:
            return None
    return None


def calc_duration(dep_time: time | None, arr_time: time | None, flight_date) -> timedelta | None:
    if dep_time and arr_time:
        dep_dt = datetime.combine(flight_date, dep_time)
        arr_dt = datetime.combine(flight_date, arr_time)
        if arr_dt < dep_dt:
            arr_dt += timedelta(days=1)
        return arr_dt - dep_dt
    return None

def parse_str(value):
    """Приводим к строке, даже если None"""
    return str(value) if value is not None else ""


def parse_duration(value):
    if not value or str(value).strip() in ["", "0", "0.0"]:
        return timedelta(seconds=0)
    try:
        # если значение в минутах
        minutes = int(value)
        return timedelta(minutes=minutes)
    except ValueError:
        # fallback: попробуем как строку "HH:MM:SS"
        try:
            h, m, s = map(int, str(value).split(":"))
            return timedelta(hours=h, minutes=m, seconds=s)
        except Exception:
            return timedelta(seconds=0)


# --- Парсинг одного сообщения ---
def parse_message(msg: str, region: str = None) -> dict:
    result = {
        "flight_id": None,
        "uav_type": None,
        "reg_number": "",
        "date": None,
        "dep_time": None,
        "arr_time": None,
        "duration": timedelta(seconds=0),  # <-- вместо "0"
        "dep_coord": "",
        "dest_coord": "",
        "city": region,
        "min_alt": None,
        "max_alt": None,
        "route_coords": "",
    }


    # Высоты
    if m := re.search(r"-M(\d{4})/M(\d{4})", msg):
        result["min_alt"], result["max_alt"] = map(int, m.groups())

   # Маршрут
    coords = re.findall(r"\d{4}[NS]\d{5}[EW]", msg)
    converted = [convert_coord(c) for c in coords]
    converted = [c for c in converted if c]  # убираем None

    # Если точек меньше 2, ставим None
    if len(converted) < 2:
        result["route_coords"] = None
    else:
        # Формируем LINESTRING из координат (lon lat)
        linestring = ", ".join(f"{lon} {lat}" for lat, lon in converted)
        result["route_coords"] = f"LINESTRING({linestring})"


    # Основные поля
    if m := re.search(r"SID/([\w\d]+)", msg):
        result["flight_id"] = m.group(1)
    if m := re.search(r"TYP/([\w\d]+)", msg):
        result["uav_type"] = m.group(1)
    if m := re.search(r"REG/([\w\d]+)", msg):
        result["reg_number"] = m.group(1)
    if m := re.search(r"DOF/(\d{6})", msg):
        try:
            result["date"] = datetime.strptime(m.group(1), "%y%m%d").date()
        except ValueError:
            pass

    # Время
    times = re.findall(r"ZZZZ(\d{4,5})", msg)
    if times:
        result["dep_time"] = normalize_time(times[0]) if len(times) > 0 else None
        result["arr_time"] = normalize_time(times[1]) if len(times) > 1 else None
        flight_date = result["date"] or datetime.today().date()
        result["duration"] = calc_duration(result["dep_time"], result["arr_time"], flight_date)

    # DEP / DEST
    for key, prefix in [("dep_coord", "DEP"), ("dest_coord", "DEST")]:
        if m := re.search(fr"{prefix}/(\d{{4,5}}[NS]\d{{4,5}}[EW])", msg):
            if (latlon := convert_coord(m.group(1))):
                lat, lon = latlon
                result[key] = f"POINT({lon} {lat})"

    return result


# --- Парсинг Excel ---
def parse_excel(file_bytes: bytes, sheet_name=0) -> pd.DataFrame:
    df = pd.read_excel(BytesIO(file_bytes), sheet_name=sheet_name)
    parsed_rows = []

    for _, row in df.iterrows():
        region_name = row[df.columns[0]]
        city_name = region_to_city.get(str(region_name), str(region_name))
        row_parsed = {}

        for col in df.columns[1:]:  # пропускаем первый столбец (регион)
            msg = str(row[col]) if pd.notna(row[col]) else ""
            parsed = parse_message(msg, region=city_name)
            for k, v in parsed.items():
                if row_parsed.get(k) in (None, "", "0"):
                    row_parsed[k] = v

        if row_parsed:
            parsed_rows.append(row_parsed)

    return pd.DataFrame(parsed_rows)
