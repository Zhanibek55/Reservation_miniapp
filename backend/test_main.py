import pytest
from fastapi.testclient import TestClient
from main import app

client = TestClient(app)

# Примерные данные пользователя (замените на актуальные, если нужно)
TEST_USER = {
    "id": 123456789,
    "first_name": "Test",
    "last_name": "User",
    "username": "testuser",
    "auth_date": 1710000000,
    "hash": "fakehash"  # Для реального теста нужен корректный hash
}

def test_register_and_auth():
    """Тест регистрации/авторизации пользователя через Telegram"""
    response = client.post("/auth/telegram", json=TEST_USER)
    assert response.status_code == 200
    data = response.json()
    assert data["status"] == "ok"
    assert data["telegram_id"] == TEST_USER["id"]

# Добавьте аналогичные тесты для бронирования, получения профиля и т.д.
# Например:
# def test_create_booking():
#     ...
