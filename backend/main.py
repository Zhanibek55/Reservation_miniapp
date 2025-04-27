import os
import json
import httpx
import logging
from typing import Optional, Dict, Any, List
from fastapi import FastAPI, HTTPException, Depends
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
import hmac
import hashlib
import time
from dotenv import load_dotenv
from fastapi import Request
from fastapi.staticfiles import StaticFiles
from fastapi.responses import FileResponse, JSONResponse, PlainTextResponse

# Настройка логирования
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger("reservation-app")

load_dotenv()
TELEGRAM_BOT_TOKEN = os.getenv("TELEGRAM_BOT_TOKEN")

app = FastAPI()

# CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Middleware для логирования всех запросов
@app.middleware("http")
async def log_requests(request: Request, call_next):
    logger.info(f"Request path: {request.url.path}")
    logger.info(f"Request method: {request.method}")
    logger.info(f"Request headers: {request.headers}")
    
    try:
        response = await call_next(request)
        logger.info(f"Response status code: {response.status_code}")
        return response
    except Exception as e:
        logger.error(f"Error processing request: {str(e)}")
        return PlainTextResponse(
            content=f"Internal Server Error: {str(e)}",
            status_code=500
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
    date: str
    time_start: str
    time_end: str
    status: str  # pending, confirmed, declined, cancelled

# Корневой маршрут для проверки работы API
@app.get("/api/health")
async def health_check():
    logger.info("Health check endpoint called")
    return {"status": "ok", "message": "API is working"}

# Маршрут для проверки структуры директорий
@app.get("/api/debug/dirs")
async def debug_dirs():
    logger.info("Debug dirs endpoint called")
    result = {}
    
    # Проверяем текущую директорию
    try:
        current_dir = os.getcwd()
        result["current_dir"] = current_dir
        result["current_dir_files"] = os.listdir(current_dir)
    except Exception as e:
        result["current_dir_error"] = str(e)
    
    # Проверяем родительскую директорию
    try:
        parent_dir = os.path.dirname(current_dir)
        result["parent_dir"] = parent_dir
        result["parent_dir_files"] = os.listdir(parent_dir)
    except Exception as e:
        result["parent_dir_error"] = str(e)
    
    # Проверяем директорию static
    try:
        static_dir = os.path.join(current_dir, "static")
        result["static_dir"] = static_dir
        result["static_exists"] = os.path.exists(static_dir)
        if os.path.exists(static_dir):
            result["static_files"] = os.listdir(static_dir)
    except Exception as e:
        result["static_dir_error"] = str(e)
    
    # Проверяем директорию ../static
    try:
        static_parent_dir = os.path.join(parent_dir, "static")
        result["static_parent_dir"] = static_parent_dir
        result["static_parent_exists"] = os.path.exists(static_parent_dir)
        if os.path.exists(static_parent_dir):
            result["static_parent_files"] = os.listdir(static_parent_dir)
    except Exception as e:
        result["static_parent_dir_error"] = str(e)
    
    return result

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
def get_tables_status(date: str, time_start: str, time_end: str):
    with get_db() as conn:
        c = conn.cursor()
        c.execute("""
            SELECT table_id FROM reservations
            WHERE date=? AND NOT (time_end<=? OR time_start>=?)
        """, (date, time_start, time_end))
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
        """, (res.table_id, res.date, res.time_start, res.time_end))
        if c.fetchone():
            raise HTTPException(409, "Table is already booked for this slot")
        c.execute("""
            INSERT INTO reservations (user_id, table_id, date, time_start, time_end, status)
            VALUES (?, ?, ?, ?, ?, ?)
        """, (res.user_id, res.table_id, res.date, res.time_start, res.time_end, res.status))
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

# Главная страница и SPA-маршруты - должны быть ПОСЛЕ всех API-маршрутов
@app.get("/{full_path:path}")
async def serve_spa(full_path: str):
    logger.info(f"Serving SPA for path: {full_path}")
    
    # Проверяем, не является ли запрос API-запросом
    if full_path.startswith("api/"):
        logger.warning(f"API endpoint not found: {full_path}")
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
            logger.info(f"Trying path: {path}")
            if os.path.exists(path):
                logger.info(f"Found index.html at: {path}")
                return FileResponse(path)
            else:
                logger.warning(f"Path does not exist: {path}")
        except Exception as e:
            logger.error(f"Error serving {path}: {str(e)}")
            continue
    
    # Если не нашли index.html, возвращаем информативную ошибку
    logger.error("Frontend files not found after trying all paths")
    return JSONResponse(
        status_code=500,
        content={"detail": "Frontend files not found. Please check build process and file paths."}
    )

# Монтируем статические файлы ПОСЛЕ определения всех маршрутов
# Пробуем разные пути к статическим файлам
try:
    logger.info("Trying to mount static files from ../static")
    app.mount("/static", StaticFiles(directory="../static"), name="static")
    logger.info("Successfully mounted ../static")
except Exception as e:
    logger.error(f"Error mounting ../static: {str(e)}")
    try:
        logger.info("Trying to mount static files from ./static")
        app.mount("/static", StaticFiles(directory="static"), name="static")
        logger.info("Successfully mounted ./static")
    except Exception as e:
        logger.error(f"Error mounting ./static: {str(e)}")
        try:
            logger.info("Trying to mount static files from /opt/render/project/src/static")
            app.mount("/static", StaticFiles(directory="/opt/render/project/src/static"), name="static")
            logger.info("Successfully mounted /opt/render/project/src/static")
        except Exception as e:
            logger.error(f"Error mounting /opt/render/project/src/static: {str(e)}")

try:
    logger.info("Trying to mount root files from ../static")
    app.mount("/", StaticFiles(directory="../static", html=True), name="root")
    logger.info("Successfully mounted ../static as root")
except Exception as e:
    logger.error(f"Error mounting ../static as root: {str(e)}")
    try:
        logger.info("Trying to mount root files from ./static")
        app.mount("/", StaticFiles(directory="static", html=True), name="root")
        logger.info("Successfully mounted ./static as root")
    except Exception as e:
        logger.error(f"Error mounting ./static as root: {str(e)}")
        try:
            logger.info("Trying to mount root files from /opt/render/project/src/static")
            app.mount("/", StaticFiles(directory="/opt/render/project/src/static", html=True), name="root")
            logger.info("Successfully mounted /opt/render/project/src/static as root")
        except Exception as e:
            logger.error(f"Error mounting /opt/render/project/src/static as root: {str(e)}")

# --- TODO: админка, ручное управление столами, статистика и т.д. ---
