# upload.py
from fastapi import APIRouter, UploadFile, File, HTTPException
import psycopg2
from psycopg2.extras import execute_values
from parser import parse_excel

router = APIRouter()

@router.post("http://backend:8000/flights/import-xlsx")
async def upload_file(file: UploadFile = File(...)):
    try:
        contents = await file.read()
        df = parse_excel(contents)

        if df.empty:
            raise HTTPException(status_code=400, detail="Файл пустой или не удалось извлечь данные")

        conn = psycopg2.connect(
            dbname="dashboard",
            user="postgres",
            password="root",
            host="localhost",
            port="5432"
        )
        cur = conn.cursor()

        # Приводим данные: None оставляем, строки — как есть
        records = []
        for row in df.to_records(index=False):
            row = list(row)

            # dep_coord, dest_coord, route_coords — индексы 6,7,10 в df (проверь порядок!)
            for idx in [6, 7, 10]:
                if row[idx] is None:
                    row[idx] = None  # оставляем None
                else:
                    row[idx] = str(row[idx])  # WKT-строка

            records.append(tuple(row))

        sql = """
        INSERT INTO flights (
            uav_type, reg_number, flight_date, dep_time, arr_time, duration,
            dep_coord, dest_coord, min_alt, max_alt, route_coords, city
        ) VALUES %s
        """

        execute_values(
            cur, sql, records,
            template="""
                %s, %s, %s, %s, %s, %s,
                CASE WHEN %s IS NULL THEN NULL ELSE ST_GeomFromText(%s, 4326) END,
                CASE WHEN %s IS NULL THEN NULL ELSE ST_GeomFromText(%s, 4326) END,
                %s, %s,
                CASE WHEN %s IS NULL THEN NULL ELSE ST_GeomFromText(%s, 4326) END,
                %s
            """
        )

        conn.commit()
        cur.close()
        conn.close()

        return {"status": "success", "rows_inserted": len(records)}

    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
