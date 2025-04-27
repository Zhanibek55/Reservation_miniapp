import sqlite3
from contextlib import contextmanager

DB_PATH = 'reservation.sqlite3'

def init_db():
    with sqlite3.connect(DB_PATH) as conn:
        c = conn.cursor()
        # Users
        c.execute('''CREATE TABLE IF NOT EXISTS users (
            telegram_id INTEGER PRIMARY KEY,
            first_name TEXT,
            last_name TEXT,
            phone TEXT,
            is_admin INTEGER DEFAULT 0
        )''')
        # Tables
        c.execute('''CREATE TABLE IF NOT EXISTS tables (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            number INTEGER,
            active INTEGER DEFAULT 1
        )''')
        # Reservations
        c.execute('''CREATE TABLE IF NOT EXISTS reservations (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            user_id INTEGER,
            table_id INTEGER,
            date TEXT,
            time_start TEXT,
            time_end TEXT,
            status TEXT,
            FOREIGN KEY(user_id) REFERENCES users(telegram_id),
            FOREIGN KEY(table_id) REFERENCES tables(id)
        )''')
        conn.commit()

@contextmanager
def get_db():
    conn = sqlite3.connect(DB_PATH)
    try:
        yield conn
    finally:
        conn.close()

# Инициализация при первом запуске
if __name__ == "__main__":
    init_db()
    print("DB initialized!")
