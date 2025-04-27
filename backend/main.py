from fastapi import FastAPI, HTTPException, Depends
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from typing import List, Optional
from datetime import date, time, datetime
import sqlite3
from db import get_db, init_db
import os
import hmac
import hashlib
from dotenv import load_dotenv
from fastapi import Request
from fastapi.staticfiles import StaticFiles
from fastapi.responses import FileResponse, JSONResponse

load_dotenv()
TELEGRAM_BOT_TOKEN = os.getenv("TELEGRAM_BOT_TOKEN")

app = FastAPI()

# CORS (для фронта)
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# --- МОДЕЛИ ---
class User(BaseModel):
    telegram_id: int
    first_name: str
    last_name: str
    phone: str
    is_admin: bool = False

class Table(BaseModel):
    id: int
    number: int
    active: bool = True

class Reservation(BaseModel):
    id: int
    user_id: int
    table_id: int
    date: date
    time_start: time
    time_end: time
    status: str  # pending, confirmed, declined, cancelled

# --- ЭНДПОИНТЫ с SQLite ---
@app.on_event("startup")
def on_startup():
    init_db()

@app.post("/register", response_model=User)
def register(user: User):
    with get_db() as conn:
        c = conn.cursor()
        c.execute("SELECT * FROM users WHERE telegram_id=?", (user.telegram_id,))
        row = c.fetchone()
        if row:
            return User(
                telegram_id=row[0], first_name=row[1], last_name=row[2], phone=row[3], is_admin=bool(row[4])
            )
        c.execute("INSERT INTO users (telegram_id, first_name, last_name, phone, is_admin) VALUES (?, ?, ?, ?, ?)" ,
                  (user.telegram_id, user.first_name, user.last_name, user.phone, int(user.is_admin)))
        conn.commit()
        return user

@app.get("/tables", response_model=List[Table])
def get_tables():
    with get_db() as conn:
        c = conn.cursor()
        c.execute("SELECT id, number, active FROM tables")
        return [Table(id=row[0], number=row[1], active=bool(row[2])) for row in c.fetchall()]

@app.get("/tables/status")
def get_tables_status(date: date, time_start: time, time_end: time):
    with get_db() as conn:
        c = conn.cursor()
        c.execute("""
            SELECT table_id FROM reservations
            WHERE date=? AND NOT (time_end<=? OR time_start>=?)
        """, (str(date), str(time_start), str(time_end)))
        busy = {row[0] for row in c.fetchall()}
        return {"busy": list(busy)}

@app.post("/reservations")
def create_reservation(res: Reservation):
    with get_db() as conn:
        c = conn.cursor()
        # Проверка занятости
        c.execute("""
            SELECT 1 FROM reservations
            WHERE table_id=? AND date=? AND NOT (time_end<=? OR time_start>=?)
        """, (res.table_id, str(res.date), str(res.time_start), str(res.time_end)))
        if c.fetchone():
            raise HTTPException(409, "Table is already booked for this slot")
        c.execute("""
            INSERT INTO reservations (user_id, table_id, date, time_start, time_end, status)
            VALUES (?, ?, ?, ?, ?, ?)
        """, (res.user_id, res.table_id, str(res.date), str(res.time_start), str(res.time_end), res.status))
        conn.commit()
        return {"ok": True}

@app.get("/reservations", response_model=List[Reservation])
def list_reservations():
    with get_db() as conn:
        c = conn.cursor()
        c.execute("SELECT id, user_id, table_id, date, time_start, time_end, status FROM reservations")
        return [Reservation(
            id=row[0], user_id=row[1], table_id=row[2], date=row[3], time_start=row[4], time_end=row[5], status=row[6]
        ) for row in c.fetchall()]

@app.get("/users", response_model=List[User])
def list_users():
    with get_db() as conn:
        c = conn.cursor()
        c.execute("SELECT telegram_id, first_name, last_name, phone, is_admin FROM users")
        return [User(
            telegram_id=row[0], first_name=row[1], last_name=row[2], phone=row[3], is_admin=bool(row[4])
        ) for row in c.fetchall()]

@app.post("/auth/telegram")
async def telegram_auth(payload: dict):
    if not TELEGRAM_BOT_TOKEN:
        raise HTTPException(status_code=500, detail="No bot token set")
    auth_data = {k: v for k, v in payload.items() if k != "hash"}
    data_check_string = "\n".join([f"{k}={v}" for k, v in sorted(auth_data.items())])
    secret_key = hashlib.sha256(TELEGRAM_BOT_TOKEN.encode()).digest()
    h = hmac.new(secret_key, data_check_string.encode(), hashlib.sha256).hexdigest()
    if h != payload.get("hash"):
        raise HTTPException(status_code=403, detail="Invalid Telegram auth")
    # По telegram_id ищем или создаём пользователя
    user_data = payload.get("user") or payload
    with get_db() as conn:
        c = conn.cursor()
        c.execute("SELECT * FROM users WHERE telegram_id=?", (user_data["id"],))
        row = c.fetchone()
        if not row:
            c.execute(
                "INSERT INTO users (telegram_id, first_name, last_name, phone, is_admin) VALUES (?, ?, ?, ?, ?)",
                (user_data["id"], user_data.get("first_name", ""), user_data.get("last_name", ""), user_data.get("phone", ""), 0)
            )
            conn.commit()
        # Можно сразу возвращать данные пользователя (или JWT, если нужно)
    return {"status": "ok", "telegram_id": user_data["id"]}

# --- API МАРШРУТЫ ---

# Раздача статики (React build)
# Важно: сначала определяем API-маршруты, затем статику
# Иначе FastAPI будет перехватывать все запросы статикой

# Главная страница и SPA-маршруты - должны быть ПОСЛЕ всех API-маршрутов
@app.get("/{full_path:path}")
async def serve_spa(full_path: str):
    # Проверяем, не является ли запрос API-запросом
    if full_path.startswith("api/"):
        raise HTTPException(status_code=404, detail="API endpoint not found")
    
    # Пробуем разные пути к index.html
    possible_paths = [
        "../static/index.html",
        "static/index.html",
        "../miniapp-frontend/build/index.html",
        "miniapp-frontend/build/index.html",
        "/opt/render/project/src/static/index.html"
    ]
    
    for path in possible_paths:
        try:
            return FileResponse(path)
        except:
            continue
    
    # Если не нашли index.html, возвращаем информативную ошибку
    return JSONResponse(
        status_code=500,
        content={"detail": "Frontend files not found. Please check build process and file paths."}
    )

# Монтируем статические файлы ПОСЛЕ определения всех маршрутов
# Пробуем разные пути к статическим файлам
try:
    app.mount("/static", StaticFiles(directory="../static"), name="static")
except:
    try:
        app.mount("/static", StaticFiles(directory="static"), name="static")
    except:
        try:
            app.mount("/static", StaticFiles(directory="/opt/render/project/src/static"), name="static")
        except Exception as e:
            print(f"Error mounting static files: {e}")

try:
    app.mount("/", StaticFiles(directory="../static", html=True), name="root")
except:
    try:
        app.mount("/", StaticFiles(directory="static", html=True), name="root")
    except:
        try:
            app.mount("/", StaticFiles(directory="/opt/render/project/src/static", html=True), name="root")
        except Exception as e:
            print(f"Error mounting root files: {e}")

# --- TODO: админка, ручное управление столами, статистика и т.д. ---
