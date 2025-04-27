from fastapi import FastAPI
from sqladmin import Admin, ModelView
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from models import User, Table, Reservation  # Используем SQLAlchemy модели из нового файла
import os

DATABASE_URL = "sqlite:///reservation.sqlite3"

app = FastAPI()

# SQLAlchemy engine & session
engine = create_engine(DATABASE_URL)
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

# SQLAdmin
admin = Admin(app, engine)

# Admin Views
class UserAdmin(ModelView, model=User):
    column_list = [User.telegram_id, User.first_name, User.last_name, User.phone, User.is_admin]
    column_searchable_list = [User.first_name, User.last_name, User.phone]

class TableAdmin(ModelView, model=Table):
    column_list = [Table.id, Table.number, Table.active]

class ReservationAdmin(ModelView, model=Reservation):
    column_list = [Reservation.id, Reservation.user_id, Reservation.table_id, Reservation.date, Reservation.time_start, Reservation.time_end, Reservation.status]

admin.add_view(UserAdmin)
admin.add_view(TableAdmin)
admin.add_view(ReservationAdmin)

if __name__ == "__main__":
    import uvicorn
    uvicorn.run("admin_sqladmin:app", host="0.0.0.0", port=8001, reload=True)
