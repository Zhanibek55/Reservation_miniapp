# Скрипт для добавления тестовых броней пользователю Жанибек (telegram_id=639199607)
from pathlib import Path
import sqlite3
from datetime import datetime, time

DB_PATH = Path(__file__).parent.parent / "reservation.db"

reservations = [
    # table_id, date (ISO), time_start, time_end, status
    (1, "2025-04-24T15:00:00", "15:00", "16:00", "pending"),
    (2, "2025-04-25T18:00:00", "18:00", "19:00", "confirmed"),
    (3, "2025-04-26T20:00:00", "20:00", "21:00", "declined"),
    (1, "2025-04-27T12:00:00", "12:00", "13:00", "cancelled"),
]

user_id = 639199607  # telegram_id Жанибек

conn = sqlite3.connect(DB_PATH)
cur = conn.cursor()
for table_id, date, time_start, time_end, status in reservations:
    cur.execute('''INSERT INTO reservations (user_id, table_id, date, time_start, time_end, status)
                  VALUES (?, ?, ?, ?, ?, ?)''',
                (user_id, table_id, date, time_start, time_end, status))
conn.commit()
print("Тестовые брони добавлены.")
conn.close()
