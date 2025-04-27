# Временный скрипт для удаления всех пользователей из БД
from pathlib import Path
import sqlite3

DB_PATH = Path(__file__).parent.parent / "reservation.db"

conn = sqlite3.connect(DB_PATH)
cur = conn.cursor()
cur.execute("DELETE FROM users")
conn.commit()
print("Все пользователи удалены из таблицы users.")
conn.close()
