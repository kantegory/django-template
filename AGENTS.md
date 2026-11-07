# AGENTS.md

Instructions and operational context for agents working in this repository.

---

## Workflow & Communication Rules

- **Communication Language**: Communicate with the user exclusively in Russian (русский язык).
- **Commit Messages**: Write commit messages in English using Conventional Commits (e.g. `feat: ...`, `fix: ...`, `refactor: ...`) to match the existing repository style.
- **Explicit Commit Approval**: Never commit changes automatically. Commit only after presenting the result for review and receiving explicit confirmation from the user.

---

## Architecture & Layout

- **Template stack**: Python 3.12, Django 5.0.4, Celery 5.3.6, PostgreSQL, Redis, Nginx, Gunicorn.
- **Directory root vs. Django root**: The Django project lives inside `django_core/` (`django_core/manage.py`), not the workspace root.
- **Nginx host port**: Nginx maps container port `80` to host port `3337` (`http://localhost:3337`).
- **Services in Docker Compose**:
  - `backend`: Gunicorn reload on `8000`. Runs `migrate` and `collectstatic` on startup.
  - `celery`: Runs Celery worker + beat scheduler together (`celery -A django_core worker -B -l DEBUG -c 3`).
  - `db`: PostgreSQL with volume mounted to `./dbs/postgres-data`.
  - `redis`: Redis with volume mounted to `./dbs/redis-data`.
  - `nginx`: Reverse proxy with media/static mounts.

---

## Essential Commands

### Docker Compose (Root Directory)
```bash
# Start all services
docker compose up -d

# View service logs
docker compose logs -f backend

# Run Django management commands
docker compose exec backend python manage.py <command>

# Run tests
docker compose exec backend python manage.py test

# Create superuser
docker compose exec backend python manage.py createsuperuser
```

### Local Development (inside `django_core/`)
```bash
cd django_core

# Install local dependencies (includes black, flake8, pylint)
pip install -r requirements/local.txt

# Run migrations & dev server (requires Postgres & Redis running)
python manage.py migrate
python manage.py runserver

# Linting & formatting
black .
flake8 .
```

---

## Configuration & Environment Gotchas

- **Environment File**: Located at `django_core/.env` (copy from `django_core/.env.example`). Loaded via `django-environ` in `settings.py`. Required keys: `SECRET_KEY`, `DB_ENGINE`, `POSTGRES_*`, `REDIS_*`, `S3_*`.
- **URL Prefixes**:
  - URLs are prefixed by `BASE_URL` (default `""`) and `API_PREFIX` (default `"api/"`).
  - Swagger UI: `http://localhost:3337/<BASE_URL><API_PREFIX>docs/swagger/` (e.g. `/api/docs/swagger/`).
  - OpenAPI Schema: `/<BASE_URL><API_PREFIX>docs/`.
  - Auth: `/<BASE_URL><API_PREFIX>auth/` (Djoser + JWT blacklist).
  - Admin: `/<BASE_URL>admin/`.
- **Redis DB Allocations**:
  - `db 0`: Default cache and Celery broker.
  - `db 1`: Blacklisted JWT refresh tokens (`caches["blacklist"]`).
  - `db 2`: Endpoint cache (`caches["endpoints"]`).
  - `db 4`: Constance live settings (`constance.backends.redisd.CachingRedisBackend`).

---

## Known Code Quirks & Warnings

- **Missing `SIMPLE_JWT` setting**: `django_core/users/views.py` (`BlacklistTokenView`) references `settings.SIMPLE_JWT["REFRESH_TOKEN_LIFETIME"]`, but `SIMPLE_JWT` is not defined in `settings.py`. Define `SIMPLE_JWT = {"REFRESH_TOKEN_LIFETIME": ...}` before invoking token blacklist endpoints.
