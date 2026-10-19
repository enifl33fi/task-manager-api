# Task Manager API

REST-сервис «Менеджер задач» на **FastAPI + PostgreSQL + SQLAlchemy 2.0 (async)**.

Сервис хранит пользователей и их задачи, предоставляет REST API для CRUD-операций.

## Стек

- **Python** 3.12
- **FastAPI** - веб-фреймворк
- **SQLAlchemy 2.0 (async)** + **asyncpg** - ORM и драйвер PostgreSQL
- **Pydantic v2** + **pydantic-settings** - валидация и конфигурация
- **Alembic** - миграции БД
- **PostgreSQL 16**
- **Docker Compose** - подъём БД
- **Uvicorn** — ASGI-сервер

## Структура проекта

```
task-manager-api/
├── app/
│   ├── __init__.py
│   ├── main.py             # создание FastAPI, подключение роутеров и middleware
│   ├── config.py           # настройки через pydantic-settings
│   ├── db.py               # async engine, фабрика сессий, get_session
│   ├── models.py           # ORM-модели User и Task (SQLAlchemy 2.0)
│   ├── schemas.py          # Pydantic-схемы *Create / *Read / *Update
│   ├── middleware.py       # ProcessTimeMiddleware (X-Process-Time + лог)
│   └── routers/
│       ├── __init__.py
│       ├── users.py
│       └── tasks.py
├── migrations/             # Alembic (env.py, versions/)
├── alembic.ini
├── docker-compose.yml
├── requirements.txt
├── .env.example
├── .gitignore
└── README.md
```

## API

| Метод | Путь             | Описание                              |
|-------|------------------|---------------------------------------|
| POST  | `/users`         | Создать пользователя                  |
| GET   | `/users`         | Список пользователей                  |
| GET   | `/users/{id}`    | Получить пользователя                 |
| PATCH | `/users/{id}`    | Частично обновить пользователя        |
| DELETE| `/users/{id}`    | Удалить пользователя                  |
| POST  | `/tasks`         | Создать задачу (нужен `owner_id`)     |
| GET   | `/tasks`         | Список задач                          |
| GET   | `/tasks/{id}`    | Получить задачу                       |
| PATCH | `/tasks/{id}`    | Частично обновить задачу              |
| DELETE| `/tasks/{id}`    | Удалить задачу                        |
| GET   | `/health`        | Проверка живости                      |

Интерактивная документация: <http://127.0.0.1:8000/docs>

## Запуск

### Предварительные требования

- Python 3.11+ (рекомендуется 3.12)
- PostgreSQL 16
- Docker и Docker Compose
- Git Bash (Windows) или любой POSIX-совместимый терминал

### Клонирование и виртуальное окружение

```bash
git clone https://github.com/<ваш-логин>/task-manager-api.git
cd task-manager-api

python -m venv .venv
source .venv/Scripts/activate      # Windows Git Bash
# source .venv/bin/activate        # Linux / macOS
pip install -r requirements.txt
```

```bash
docker compose up -d db
docker compose exec db psql -U app -d tasks -c "select 1"
```

Пропишите `.env` (см. `.env.example`):

```env
DATABASE_URL=postgresql+asyncpg://app:app@localhost:5432/tasks
```

### Миграции

```bash
alembic upgrade head
```

> ⚠️ Таблицы создаются **только** через Alembic. `create_all()` нигде не вызывается.

### Запуск приложения

```bash
uvicorn app.main:app --reload
```

Приложение: <http://127.0.0.1:8000>
Swagger UI: <http://127.0.0.1:8000/docs>
ReDoc: <http://127.0.0.1:8000/redoc>

## Скриншоты

### Swagger UI — успешные запросы

`POST /users` → 201 и `GET /users` → 200.

![Swagger — успешные запросы](docs/swagger-post-success.png)
![Swagger — успешные запросы](docs/swagger-get-success.png)

### Swagger UI — ответ 404

`GET /users/999` → 404 `{"detail": "User not found"}`.

![Swagger — ответ 404](docs/swagger-404.png)

### Заголовок `X-Process-Time`

`curl -i http://127.0.0.1:8000/health` — в ответе присутствует `x-process-time`.

![X-Process-Time](docs/x-process-time.png)

### Таблицы в БД (`\dt` в psql)

![Таблицы в БД](docs/db-tables.png)

## Middleware

Класс `ProcessTimeMiddleware` (Starlette `BaseHTTPMiddleware`) на каждый запрос:

- замеряет длительность обработки;
- добавляет в ответ заголовок `X-Process-Time`;
- пишет в лог строку `METHOD PATH -> STATUS (duration s)`.

Проверить заголовок:

```bash
curl -i http://127.0.0.1:8000/health
```

Ожидаемо в заголовках ответа: `x-process-time: 0.000xxx`.

## Примеры запросов

### Создать пользователя

```bash
curl -i -X POST http://127.0.0.1:8000/users \
  -H "Content-Type: application/json" \
  -d '{"email":"alice@example.com","name":"Alice"}'
```

Ожидаемо: `201 Created` + тело с `id`, `email`, `name`, `created_at`.

### Создать задачу

```bash
curl -i -X POST http://127.0.0.1:8000/tasks \
  -H "Content-Type: application/json" \
  -d '{"title":"Buy milk","description":"2 liters","owner_id":1}'
```

### Ошибки

```bash
curl -i http://127.0.0.1:8000/users/999
# HTTP/1.1 404 Not Found
# {"detail": "User not found"}

curl -i -X POST http://127.0.0.1:8000/tasks \
  -H "Content-Type: application/json" \
  -d '{"title":"Ghost","owner_id":9999}'
# HTTP/1.1 404 Not Found
# {"detail": "Owner not found"}
```
