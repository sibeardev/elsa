# elsa

REST API для приложения справочника с организациями, зданиями и видами деятельности.

> ⚠️ MVP. Проект реализован в рамках тестового задания.

Основная цель — демонстрация:

- проектирование реляционной модели данных
- асинхронную работу с PostgreSQL
- FastAPI + SQLAlchemy 2.0
- Alembic миграции
- документированный API (Swagger / ReDoc)

------------------------------------------------------------------------

## Запуск проекта

### 1. Клонирование

``` bash
git clone https://github.com/sibeardev/elsa.git
cd elsa
```

### 2. Создайте файл окружения `.env`

```plaintext
POSTGRES__USER={user}
POSTGRES__PASSWORD={yourpassword}
POSTGRES__DB={catalog_db}
API_KEY={staticApiKey}
```

### 3. Запуск через Docker

``` bash
docker-compose up --build
```

### 4. Применение миграций

``` bash
docker compose exec api uv run alembic upgrade head
```

После запуска сервисы доступны по следующим адресам:

- Swagger UI: <http://localhost:8000/docs>
- Redoc: <http://localhost:8000/redoc>

### 5. Заполнение тестовыми данными

``` bash
docker compose exec api uv run python -m scripts.seed_db
```

Источник данных: `data/test_data.json`

### 6. Остановить приложение и БД

Ctrl+C или

```bash
docker compose down
```
