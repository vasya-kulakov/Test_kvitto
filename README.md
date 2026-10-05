# Test_kvitto

Краткая инструкция по запуску проекта и прогону тестов.

Требования
- Docker и docker-compose (или Docker Desktop с включённым compose).
- (Опционально) Python 3.11 и виртуальное окружение, если запускать локально.

Быстрый запуск (Docker Compose)

1. Сборка и запуск контейнера:

```powershell
docker compose up --build
```

2. Приложение будет доступно по адресу:

- http://localhost:8000 — FastAPI
- http://localhost:8000/docs — Swagger / OpenAPI UI

Инициализация / сброс базы

Для сброса и повторной инициализации БД есть endpoint:

GET /admin/reset

Пример:

```bash
curl -X GET http://localhost:8000/admin/reset
```

Запуск тестов

В контейнере (рекомендуется для повторяемой среды):

```powershell
# Открыть шелл в работающем контейнере
docker compose exec web bash

# Внутри контейнера
pytest -v
```

Или выполнить тесты прямо через docker compose (одноразовый контейнер):

```powershell
docker compose run --rm web pytest -v
```

Локальный запуск без Docker

1. Создать и активировать виртуальное окружение

```powershell
python -m venv .venv
.\\.venv\\Scripts\\activate
pip install -r requirements.txt
```

2. Запуск сервера локально:

```powershell
uvicorn src.core.main:app --reload
```

Примеры HTTP-запросов (curl)

1) Создание платежа (без Idempotency-Key — сервер сгенерирует ключ):

```bash
curl -i -X POST http://localhost:8000/payments \
  -H "Content-Type: application/json" \
  -d '{"tariff_id":1, "email":"user@example.com", "method":"card"}'
```

2) Создание платежа с Idempotency-Key (повторный запрос с тем же ключом вернёт тот же платёж):

```bash
curl -i -X POST http://localhost:8000/payments \
  -H "Content-Type: application/json" \
  -H "Idempotency-Key: my-key-123" \
  -d '{"tariff_id":1, "email":"user@example.com", "method":"card"}'
```

3) Проверка созданного платежа по id:

```bash
curl -i http://localhost:8000/payments/1
```

4) Сброс и пересоздание БД (см. выше):

```bash
curl -X GET http://localhost:8000/admin/reset
```

Полезные заметки
- Файлы конфигурации: Dockerfile и docker-compose.yml находятся в корне проекта.
- OpenAPI-документация доступна по /docs после старта сервера.
- Если при установке зависимостей в контейнере возникает ошибка по greenlet, убедитесь, что в requirements.txt присутствует "sqlalchemy[asyncio]" и "greenlet" (и докер пересобран).

Если нужны дополнительные примеры или CI-конфигурация — добавлю по запросу.
