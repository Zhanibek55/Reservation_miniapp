# План реализации Telegram Miniapp для бронирования столов в бильярдном зале

---

## Технологии и инструменты
- Python 3.10+ (backend, Telegram Bot)
- [aiogram](https://docs.aiogram.dev/) — асинхронный Telegram Bot API
- [FastAPI](https://fastapi.tiangolo.com/) — backend API для Mini App
- [sqlite3](https://docs.python.org/3/library/sqlite3.html) (или PostgreSQL, при масштабировании)
- [Pillow](https://python-pillow.org/) — генерация и обработка изображений (опционально)
- [python-dotenv](https://pypi.org/project/python-dotenv/) — для работы с .env
- **[React + TypeScript](https://react.dev/)** — фронтенд для Mini App
- [@telegram-apps/sdk](https://www.npmjs.com/package/@telegram-apps/sdk) — интеграция с Telegram WebApp API
- [Vite](https://vitejs.dev/) или [Create React App](https://create-react-app.dev/) — сборка фронтенда
- Docker (опционально, для деплоя)
- Git

---

## Структура проекта (обновлённая)

```
reservation_miniapp/
├── bot/                    # Логика Telegram-бота
│   ├── handlers/           # Обработчики команд и callback'ов
│   ├── keyboards/          # Inline/Reply клавиатуры
│   ├── middlewares/        # Мидлвари (например, логирование, ACL)
│   ├── states.py           # FSM-состояния
│   ├── utils.py            # Утилиты (например, генерация схемы зала)
│   └── main.py             # Точка входа бота
├── db/                     # Работа с БД
│   ├── models.py           # Описания таблиц/ORM моделей
│   ├── crud.py             # CRUD-операции
│   └── database.py         # Инициализация соединения
├── miniapp-frontend/       # Фронтенд Mini App (React + TypeScript)
│   ├── public/             # Статичные файлы (favicon, index.html, и др.)
│   ├── src/                # Исходный код фронтенда
│   │   ├── components/     # UI-компоненты (выбор стола, бронирование и пр.)
│   │   ├── api/            # API-клиенты для общения с backend
│   │   ├── hooks/          # React hooks
│   │   ├── utils/          # Утилиты
│   │   ├── types/          # Типы данных
│   │   └── App.tsx         # Главный компонент
│   ├── package.json        # Зависимости фронтенда
│   └── README.md           # Документация по фронтенду
├── static/
│   └── billiard_hall.svg   # Исходная схема зала
├── migrations/             # Скрипты миграций (alembic, если нужен рост)
├── tests/                  # Юнит-тесты
├── .env                    # Конфиги и секреты
├── requirements.txt        # Зависимости backend
├── README.md               # Документация
└── PROJECT_PLAN.md         # Этот файл (план)
```

---

## Чеклист этапов реализации

- [ ] 1. Анализ требований и проектирование структуры
- [ ] 2. Инициализация репозитория, настройка окружения, зависимостей
- [ ] 3. Реализация моделей данных и схемы БД
- [ ] 4. Реализация backend (бот + API):
    - [ ] Регистрация пользователя
    - [ ] API для бронирования, получения статусов столов, управления бронированиями
    - [ ] Админ-панель (API для управления столами, настройками клуба)
- [ ] 5. Разработка Mini App (frontend):
    - [ ] Инициализация проекта (React + TypeScript, @telegram-apps/sdk)
    - [ ] Вёрстка и UI: выбор стола, отображение схемы зала, статусы (SVG/Canvas)
    - [ ] Интеграция с Telegram WebApp API
    - [ ] Интеграция с backend API
    - [ ] Управление бронированиями, отображение истории
    - [ ] Админ-интерфейс (управление столами, настройками)
- [ ] 6. Генерация и отображение схемы зала (frontend)
- [ ] 7. Тестирование (юнит-тесты backend, ручное и автоматизированное тестирование frontend)
- [ ] 8. Документация (README, примеры)
- [ ] 9. Подготовка к деплою:
    - [ ] Деплой backend (например, PythonAnywhere, VPS)
    - [ ] Деплой frontend Mini App на публичный HTTPS URL (Vercel, Netlify, Render, и др.)
    - [ ] Интеграция Mini App с ботом (через WebApp кнопку)
- [ ] 10. Возможности для расширения:
    - [ ] Поддержка нескольких клубов
    - [ ] Гибкая схема зала (редактируемое количество/расположение столов)
    - [ ] Онлайн-оплата брони
    - [ ] Внешний API для интеграций/аналитики

---

## Описание основных модулей/файлов

- `bot/main.py` — запуск и настройка бота
- `bot/handlers/` — обработчики команд, inline-кнопок, FSM-сценариев
- `bot/keyboards/` — генерация клавиатур (выбор стола, времени, управления)
- `bot/states.py` — состояния FSM для сложных сценариев
- `bot/utils.py` — утилиты, в т.ч. функция генерации изображения зала (опционально)
- `db/models.py` — модели пользователей, столов, бронирований, клубов
- `db/crud.py` — функции для работы с данными (создание, чтение, обновление, удаление)
- `db/database.py` — инициализация и подключение к БД
- `miniapp-frontend/` — фронтенд Mini App (React + TypeScript, @telegram-apps/sdk)
- `static/billiard_hall.svg` — схема зала (исходник)
- `migrations/` — миграции БД (если потребуется)
- `tests/` — тесты

---

## Гибкость и расширяемость
- Вынесение бизнес-логики и структуры данных в отдельные модули
- Возможность добавления новых клубов через отдельную таблицу/модель
- Хранение схемы зала и столов в БД (или конфиге), чтобы можно было менять их без изменений кода
- Расширяемая система ролей (админ, супер-админ, оператор)
- Поддержка онлайн-оплаты через отдельный модуль
- API для интеграции с внешними сервисами
- Возможность изменения/расширения UI Mini App без изменений backend

---

## Безопасность
- Хранение токенов и секретов только в .env
- Проверка прав доступа для админских функций
- Валидация пользовательских данных
- Проверка авторизации пользователей через Telegram WebApp API

---

## Источники и ссылки
- [aiogram docs](https://docs.aiogram.dev/)
- [FastAPI docs](https://fastapi.tiangolo.com/)
- [Pillow docs](https://pillow.readthedocs.io/en/stable/)
- [python-dotenv](https://pypi.org/project/python-dotenv/)
- [Документация Telegram Mini Apps](https://docs.telegram-mini-apps.com/)
- [@telegram-apps/sdk (NPM)](https://www.npmjs.com/package/@telegram-apps/sdk)

---

> После согласования плана начнем поэтапную реализацию. Все пункты плана могут быть детализированы и расширены по мере необходимости.
