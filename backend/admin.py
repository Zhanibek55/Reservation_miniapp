import asyncio
from fastapi import FastAPI
from fastapi_admin.app import app as admin_app
from fastapi_admin.providers.login import UsernamePasswordProvider
from fastapi_admin.resources import Model
from fastapi_admin.file_upload import FileUpload
from sqlalchemy import Column, Integer, String, Boolean, Date, Time, ForeignKey, create_engine, Text
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker, relationship
from starlette.requests import Request
import databases
import uvicorn
import os

DATABASE_URL = "sqlite+aiosqlite:///./reservation.sqlite3"
SECRET = "supersecretkey"  # замените на свой

Base = declarative_base()

class User(Base):
    __tablename__ = "users"
    telegram_id = Column(Integer, primary_key=True)
    first_name = Column(String)
    last_name = Column(String)
    phone = Column(String)
    is_admin = Column(Boolean, default=False)

class Table(Base):
    __tablename__ = "tables"
    id = Column(Integer, primary_key=True, autoincrement=True)
    number = Column(Integer)
    active = Column(Boolean, default=True)

class Reservation(Base):
    __tablename__ = "reservations"
    id = Column(Integer, primary_key=True, autoincrement=True)
    user_id = Column(Integer, ForeignKey("users.telegram_id"))
    table_id = Column(Integer, ForeignKey("tables.id"))
    date = Column(String)
    time_start = Column(String)
    time_end = Column(String)
    status = Column(String)
    user = relationship("User")
    table = relationship("Table")

# Создание таблиц, если не существуют
engine = create_engine("sqlite:///reservation.sqlite3")
Base.metadata.create_all(engine)

# FastAPI Admin
app = FastAPI()

@app.on_event("startup")
async def startup():
    await admin_app.configure(
        logo_url="https://fastapi-admin.github.io/img/logo.png",
        template_folders=[],
        providers=[
            UsernamePasswordProvider(
                admin_model=User,
                login_logo_url="https://fastapi-admin.github.io/img/logo.png",
                username_field="first_name",
                password_field="phone"  # для MVP: вход по имени и телефону
            )
        ],
        resources=[
            Model(User),
            Model(Table),
            Model(Reservation)
        ],
        database_url=DATABASE_URL,
        secret_key=SECRET,
    )
    app.mount("/admin", admin_app)

if __name__ == "__main__":
    uvicorn.run("admin:app", host="0.0.0.0", port=8001, reload=True)
