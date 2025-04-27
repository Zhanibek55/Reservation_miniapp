# CRUD-операции для работы с моделями
# Заполняется на этапе реализации логики
# Реализованы CRUD-операции для всех моделей: User (с фамилией), Table, Reservation, ClubSettings. Есть функции для добавления, получения и листинга сущностей, а также для настройки клуба.

from typing import Optional, List
from .database import get_connection
from .models import User, Table, Reservation, ClubSettings
from datetime import datetime, time

# --- User CRUD ---
def add_user(user: User):
    conn = get_connection()
    cur = conn.cursor()
    cur.execute('''INSERT OR REPLACE INTO users (telegram_id, first_name, last_name, phone, is_admin)
                   VALUES (?, ?, ?, ?, ?)''',
                (user.telegram_id, user.first_name, user.last_name, user.phone, user.is_admin))
    conn.commit()
    conn.close()

def get_user(telegram_id: int) -> Optional[User]:
    conn = get_connection()
    cur = conn.cursor()
    cur.execute('SELECT telegram_id, first_name, last_name, phone, is_admin FROM users WHERE telegram_id=?', (telegram_id,))
    row = cur.fetchone()
    conn.close()
    if row:
        return User(telegram_id=row[0], first_name=row[1], last_name=row[2], phone=row[3], is_admin=bool(row[4]))
    return None

# --- Table CRUD ---
def add_table(table: Table):
    conn = get_connection()
    cur = conn.cursor()
    cur.execute('''INSERT OR REPLACE INTO tables (id, status) VALUES (?, ?)''', (table.id, table.status))
    conn.commit()
    conn.close()

def get_table(table_id: int) -> Optional[Table]:
    conn = get_connection()
    cur = conn.cursor()
    cur.execute('SELECT id, status FROM tables WHERE id=?', (table_id,))
    row = cur.fetchone()
    conn.close()
    if row:
        return Table(id=row[0], status=row[1])
    return None

def list_tables() -> List[Table]:
    conn = get_connection()
    cur = conn.cursor()
    cur.execute('SELECT id, status FROM tables')
    rows = cur.fetchall()
    conn.close()
    return [Table(id=row[0], status=row[1]) for row in rows]

# --- Reservation CRUD ---
def add_reservation(res: Reservation):
    conn = get_connection()
    cur = conn.cursor()
    cur.execute('''INSERT INTO reservations
        (user_id, table_id, date, time_start, time_end, status)
        VALUES (?, ?, ?, ?, ?, ?)''',
        (res.user_id, res.table_id, res.date.isoformat(), res.time_start.isoformat(), res.time_end.isoformat(), res.status))
    conn.commit()
    conn.close()

def get_reservation(res_id: int) -> Optional[Reservation]:
    conn = get_connection()
    cur = conn.cursor()
    cur.execute('''SELECT id, user_id, table_id, date, time_start, time_end, status FROM reservations WHERE id=?''', (res_id,))
    row = cur.fetchone()
    conn.close()
    if row:
        return Reservation(
            id=row[0], user_id=row[1], table_id=row[2],
            date=datetime.fromisoformat(row[3]),
            time_start=time.fromisoformat(row[4]),
            time_end=time.fromisoformat(row[5]),
            status=row[6]
        )
    return None

def list_reservations_for_user(user_id: int) -> List[Reservation]:
    conn = get_connection()
    cur = conn.cursor()
    cur.execute('''SELECT id, user_id, table_id, date, time_start, time_end, status FROM reservations WHERE user_id=?''', (user_id,))
    rows = cur.fetchall()
    conn.close()
    return [Reservation(
        id=row[0], user_id=row[1], table_id=row[2],
        date=datetime.fromisoformat(row[3]),
        time_start=time.fromisoformat(row[4]),
        time_end=time.fromisoformat(row[5]),
        status=row[6]
    ) for row in rows]

# Для статусов бронирования:
RESERVATION_STATUS_LABELS = {
    'pending': 'На рассмотрении',
    'confirmed': 'Подтверждена',
    'declined': 'Отклонена',
    'cancelled': 'Отменена'
}

# --- ClubSettings CRUD ---
def get_club_settings() -> Optional[ClubSettings]:
    conn = get_connection()
    cur = conn.cursor()
    cur.execute('''SELECT id, open_time, close_time, slot_duration_minutes, tables_count, other FROM club_settings WHERE id=1''')
    row = cur.fetchone()
    conn.close()
    if row:
        return ClubSettings(
            id=row[0],
            open_time=time.fromisoformat(row[1]),
            close_time=time.fromisoformat(row[2]),
            slot_duration_minutes=row[3],
            tables_count=row[4],
            other=row[5]
        )
    return None

def set_club_settings(settings: ClubSettings):
    conn = get_connection()
    cur = conn.cursor()
    cur.execute('''INSERT OR REPLACE INTO club_settings
        (id, open_time, close_time, slot_duration_minutes, tables_count, other)
        VALUES (?, ?, ?, ?, ?, ?)''',
        (settings.id, settings.open_time.isoformat(), settings.close_time.isoformat(),
         settings.slot_duration_minutes, settings.tables_count, settings.other))
    conn.commit()
    conn.close()
