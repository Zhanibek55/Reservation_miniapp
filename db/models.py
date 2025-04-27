# Модели данных (User, Table, Reservation, ClubSettings)
# Заполняется на этапе проектирования БД

from typing import Optional
from datetime import datetime, time
from pydantic import BaseModel

# --- User ---
class User(BaseModel):
    telegram_id: int
    first_name: str
    last_name: str
    phone: str
    is_admin: bool = False

# --- Table ---
class Table(BaseModel):
    id: int  # номер стола (primary key)
    status: str  # 'available', 'busy', 'inactive'

# --- Reservation ---
class Reservation(BaseModel):
    id: int
    user_id: int  # telegram_id пользователя
    table_id: int
    date: datetime  # дата и время бронирования
    time_start: time
    time_end: time
    status: str  # 'pending', 'confirmed', 'declined', 'cancelled'

# --- ClubSettings ---
class ClubSettings(BaseModel):
    id: int = 1  # singleton
    open_time: time  # часы работы (от)
    close_time: time  # часы работы (до)
    slot_duration_minutes: int  # длительность слота в минутах
    tables_count: int
    other: Optional[str] = None
