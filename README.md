# OrgAtlas API

REST API приложение для справочника Организаций, Зданий и Деятельности.

## Стек технологий

- FastAPI - веб-фреймворк
- Pydantic - валидация данных
- SQLAlchemy - ORM
- Alembic - миграции базы данных
- PostgreSQL - база данных
- Docker & Docker Compose - контейнеризация

## 🐳 Запуск с Docker

### Запуск

```bash
docker-compose up --build
```

### Остановка

```bash
docker-compose down
```

### Доступ к сервисам

- **API**: http://localhost:8000
- **Документация**: http://localhost:8000/docs