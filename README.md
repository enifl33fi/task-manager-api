# Task Manager API

![CI](https://github.com/enifl33fi/task-manager-api/actions/workflows/ci.yml/badge.svg)

REST-сервис «Менеджер задач» на **FastAPI + PostgreSQL + SQLAlchemy 2.0 (async)**.

Сервис хранит пользователей и их задачи, предоставляет REST API для CRUD-операций. Проект включает автоматические тесты на PostgreSQL, контейнеризацию с помощью Docker и CI/CD на GitHub Actions.

## Стек

- **Python** 3.12
- **FastAPI** — веб-фреймворк
- **SQLAlchemy 2.0 (async)** + **asyncpg** — ORM и драйвер PostgreSQL
- **Pydantic v2** + **pydantic-settings** — валидация и конфигурация
- **Alembic** — миграции БД
- **PostgreSQL 16**
- **pytest** + **pytest-asyncio** + **HTTPX** — автоматические тесты
- **Ruff** — проверка и форматирование кода
- **Docker** + **Docker Compose** — контейнеризация
- **GitHub Actions** — CI/CD
- **GitHub Container Registry (GHCR)** и **Docker Hub** — хранение Docker-образов
- **Uvicorn** — ASGI-сервер

## Структура проекта

```text
task-manager-api/
├── app/
│   ├── __init__.py
│   ├── main.py             # создание FastAPI, подключение роутеров и middleware
│   ├── config.py           # настройки через pydantic-settings
│   ├── db.py               # async engine, фабрика сессий, get_session
│   ├── models.py            # ORM-модели User и Task
│   ├── schemas.py           # Pydantic-схемы Create / Read / Update
│   ├── middleware.py        # ProcessTimeMiddleware
│   └── routers/
│       ├── __init__.py
│       ├── users.py
│       └── tasks.py
├── migrations/              # Alembic (env.py, versions/)
├── tests/                   # автоматические тесты
│   ├── conftest.py
│   ├── test_users.py
│   ├── test_tasks.py
│   └── test_middleware.py
├── .github/
│   └── workflows/
│       └── ci.yml           # CI/CD pipeline
├── docs/                    # скриншоты API
├── alembic.ini
├── Dockerfile
├── docker-compose.yml
├── requirements.txt
├── requirements-dev.txt
├── pytest.ini
├── .env.example
├── .dockerignore
├── .gitignore
└── README.md
```

## API

| Метод | Путь | Описание |
|---|---|---|
| POST | `/users` | Создать пользователя |
| GET | `/users` | Список пользователей |
| GET | `/users/{id}` | Получить пользователя |
| PATCH | `/users/{id}` | Частично обновить пользователя |
| DELETE | `/users/{id}` | Удалить пользователя |
| POST | `/tasks` | Создать задачу (нужен `owner_id`) |
| GET | `/tasks` | Список задач с фильтрами и пагинацией |
| GET | `/tasks/{id}` | Получить задачу |
| PATCH | `/tasks/{id}` | Частично обновить задачу |
| DELETE | `/tasks/{id}` | Удалить задачу |
| GET | `/health` | Проверка живости |

Для списка задач поддерживаются фильтрация по `done` и `owner_id`, а также пагинация через `limit` и `offset`.

Интерактивная документация: <http://127.0.0.1:8000/docs>

## Запуск

### Предварительные требования

- Python 3.11+ (рекомендуется 3.12)
- Docker и Docker Compose
- Git Bash (Windows) или любой POSIX-совместимый терминал

### Клонирование и виртуальное окружение

```bash
git clone https://github.com/enifl33fi/task-manager-api.git
cd task-manager-api

python -m venv .venv
source .venv/Scripts/activate      # Windows Git Bash
# source .venv/bin/activate        # Linux / macOS
```

### Установка зависимостей

Для запуска приложения:

```bash
python -m pip install -r requirements.txt
```

Для разработки и тестирования:

```bash
python -m pip install -r requirements-dev.txt
```

### Запуск PostgreSQL

```bash
docker compose up -d db
docker compose exec db psql -U app -d tasks -c "select 1"
```

Пропишите `.env` на основе `.env.example`:

```env
DATABASE_URL=postgresql+asyncpg://app:app@localhost:5432/tasks
```

### Миграции

```bash
alembic upgrade head
```

> Таблицы создаются через Alembic. Схема базы данных обновляется применением миграций.

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

![Swagger — успешное создание пользователя](docs/swagger-post-success.png)

![Swagger — получение списка пользователей](docs/swagger-get-success.png)

### Swagger UI — ответ 404

`GET /users/999` → 404 `{"detail": "User not found"}`.

![Swagger — ответ 404](docs/swagger-404.png)

### Заголовок `X-Process-Time`

`curl -i http://127.0.0.1:8000/health` — в ответе присутствует `x-process-time`.

![X-Process-Time](docs/x-process-time.png)

### Таблицы в БД

![Таблицы в БД](docs/db-tables.png)

### Успешный CI/CD pipeline

![Успешный pipeline](docs/ci-passed.png)

### Неуспешный CI/CD pipeline

Забыл сфоткать :(

## Middleware

Класс `ProcessTimeMiddleware` на каждый запрос:

- замеряет длительность обработки;
- добавляет в ответ заголовок `X-Process-Time`;
- записывает в лог метод, путь, статус ответа и длительность обработки.

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

Ожидаемо: `201 Created` и объект с `id`, `email`, `name`, `created_at`.

### Создать задачу

```bash
curl -i -X POST http://127.0.0.1:8000/tasks \
  -H "Content-Type: application/json" \
  -d '{"title":"Buy milk","description":"2 liters","owner_id":1}'
```

### Получить выполненные задачи

```bash
curl -i "http://127.0.0.1:8000/tasks?done=true&limit=10&offset=0"
```

### Ошибки

```bash
curl -i http://127.0.0.1:8000/users/999
# HTTP 404 Not Found

curl -i -X POST http://127.0.0.1:8000/tasks \
  -H "Content-Type: application/json" \
  -d '{"title":"Ghost","owner_id":9999}'
# HTTP 404 Not Found
```

## Тестирование

Для автоматического тестирования используются `pytest`, `pytest-asyncio` и `HTTPX`. Тесты работают с реальной PostgreSQL и используют отдельную тестовую базу данных `tasks_test`.

### Подготовка тестовой БД

Создайте базу данных `tasks_test` в PostgreSQL. При необходимости укажите пользователя и пароль в `TEST_DATABASE_URL`, используемом тестовой конфигурацией.

Пример строки подключения:

```env
TEST_DATABASE_URL=postgresql+asyncpg://app:app@localhost:5432/tasks_test
```

### Запуск тестов локально

```bash
python -m pytest -v
```

### Проверка кода

```bash
python -m ruff check app tests migrations
python -m ruff format --check app tests migrations
```

### Проверяемые сценарии

Автоматические тесты проверяют:

1. Создание пользователя — HTTP 201.
2. Повторную регистрацию с тем же email — HTTP 409.
3. Некорректный email — HTTP 422.
4. Создание задачи — HTTP 201.
5. Создание задачи с несуществующим владельцем — HTTP 404.
6. Фильтрацию задач по `done` и пагинацию.
7. Частичное обновление задачи через PATCH.
8. Удаление задачи и последующий GET — HTTP 404.
9. Наличие заголовка `X-Process-Time`.

Перед выполнением тестов таблицы очищаются. Зависимость `get_session` переопределяется через `app.dependency_overrides`, чтобы тестовые запросы работали с тестовой базой данных.

## Docker

### Сборка и запуск

```bash
docker compose up --build -d
```

Проверить состояние контейнеров:

```bash
docker compose ps
```

Посмотреть логи приложения:

```bash
docker compose logs -f app
```

Посмотреть логи PostgreSQL:

```bash
docker compose logs -f db
```

Приложение ожидает готовности БД, после чего применяются миграции Alembic и запускается FastAPI.

Swagger UI: <http://localhost:8000/docs>

### Остановка контейнеров

```bash
docker compose down
```

Для удаления контейнеров и данных в томах:

```bash
docker compose down -v
```

> Команда `docker compose down -v` удаляет данные из томов, в том числе данные PostgreSQL.

## CI/CD

Для автоматизации проверок и публикации Docker-образов используется GitHub Actions.

Workflow находится в `.github/workflows/ci.yml`.

### Этапы pipeline

**Lint**

- Проверка кода с помощью Ruff.
- Проверка форматирования.

**Test**

- Запуск PostgreSQL для тестов.
- Выполнение автоматических тестов через pytest.
- Проверка API с использованием тестовой базы данных.

**Build**

- Сборка Docker-образа.
- Публикация образа после успешного выполнения необходимых проверок при push в `main`.

### Условия запуска

- При каждом push запускаются проверки кода и тесты.
- При создании Pull Request запускаются проверки кода и тесты.
- При push в `main` после успешных проверок собирается и публикуется образ в GHCR и Docker Hub.

### Секреты GitHub Actions

Для публикации образа в Docker Hub в настройках репозитория добавляются Actions secrets:

| Имя | Назначение |
|---|---|
| `DOCKERHUB_USERNAME` | Логин Docker Hub |
| `DOCKERHUB_TOKEN` | Токен доступа Docker Hub с правами Read & Write |

Для публикации в GHCR используется автоматически создаваемый `GITHUB_TOKEN` с разрешением `packages: write`.

Секреты настраиваются в разделе:

`Settings → Secrets and variables → Actions`.

Токены не хранятся в исходном коде репозитория.

### Docker-образы

**GitHub Container Registry (GHCR)**

Образ: `ghcr.io/enifl33fi/task-manager-api:latest`

Ссылка на пакет: <https://github.com/enifl33fi/task-manager-api/pkgs/container/task-manager-api>

**Docker Hub**

Образ: `markovka1/task-manager-api:latest`

Ссылка: <https://hub.docker.com/r/markovka1/task-manager-api>

### Загрузка образа

Из GHCR:

```bash
docker pull ghcr.io/enifl33fi/task-manager-api:latest
```

Из Docker Hub:

```bash
docker pull markovka1/task-manager-api:latest
```

Для запуска контейнера требуется настроить подключение к PostgreSQL через `DATABASE_URL`.