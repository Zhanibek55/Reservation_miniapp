# Инициализация соединения с БД
# Будет реализовано после проектирования моделей

import sqlite3
from pathlib import Path

DB_PATH = Path(__file__).parent.parent / "reservation.db"

def get_connection():
    return sqlite3.connect(DB_PATH)

def init_db():
    conn = get_connection()
    cur = conn.cursor()
    # User
    cur.execute('''
    CREATE TABLE IF NOT EXISTS users (
        telegram_id INTEGER PRIMARY KEY,
        first_name TEXT NOT NULL,
        last_name TEXT NOT NULL,
        phone TEXT NOT NULL,
        is_admin BOOLEAN DEFAULT 0
    )''')
    # Table
    cur.execute('''
    CREATE TABLE IF NOT EXISTS tables (
        id INTEGER PRIMARY KEY,
        status TEXT NOT NULL
    )''')
    # Reservation
    cur.execute('''
    CREATE TABLE IF NOT EXISTS reservations (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        user_id INTEGER,
        table_id INTEGER,
        date TEXT NOT NULL,
        time_start TEXT NOT NULL,
        time_end TEXT NOT NULL,
        status TEXT NOT NULL,
        FOREIGN KEY(user_id) REFERENCES users(telegram_id),
        FOREIGN KEY(table_id) REFERENCES tables(id)
    )''')
    # ClubSettings (singleton)
    cur.execute('''
    CREATE TABLE IF NOT EXISTS club_settings (
        id INTEGER PRIMARY KEY CHECK (id = 1),
        open_time TEXT NOT NULL,
        close_time TEXT NOT NULL,
        slot_duration_minutes INTEGER NOT NULL,
        tables_count INTEGER NOT NULL,
        other TEXT
    )''')
    conn.commit()
    conn.close()

if __name__ == "__main__":
    init_db()
    print("DB initialized.")
