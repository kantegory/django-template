# AGENTS.md

Instructions and operational context for agents working in this repository.

---

## Workflow & Communication Rules

- **Communication Language**: Communicate with the user exclusively in Russian (русский язык).
- **Commit Messages**: Write commit messages in English using Conventional Commits (e.g. `feat: ...`, `fix: ...`, `refactor: ...`) to match the existing repository style.
- **Explicit Commit Approval**: Never commit changes automatically. Commit only after presenting the result for review and receiving explicit confirmation from the user.

---

## Architecture & Layout

- **Template stack**: Python 3.12, Django 6.1.3, Django Modern REST (DMR), Dramatiq 2.2.1, Psycopg 3, PostgreSQL, Redis, Nginx, Gunicorn.
- **Directory root vs. Django root**: The Django project lives inside `django_core/` (`django_core/manage.py`), not the workspace root.
- **Nginx host port**: Nginx maps container port `80` to host port `1337` (`http://localhost:1337`).
- **Services in Docker Compose**:
  - `backend`: Gunicorn reload on `8000`. Runs `migrate` and `collectstatic` on startup via entrypoint, with healthcheck.
  - `dramatiq`: Runs Dramatiq worker (`python manage.py rundramatiq`).
  - `db`: PostgreSQL 17 using named volume `postgres_data`.
  - `redis`: Redis using named volume `redis_data`.
  - `nginx`: Reverse proxy with media/static mounts.

---

## Essential Commands

### Docker Compose (Root Directory)
```bash
# Start development environment
docker compose up -d

# Start production environment
docker compose -f docker-compose.prod.yml up -d

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

- **Environment Files**:
  - `django_core/.env` (copy from `django_core/.env.example`): Loaded via `django-environ` in `settings.py` and Docker Compose for `backend`, `dramatiq`, and `db`. Required keys: `SECRET_KEY`, `DB_ENGINE`, `POSTGRES_*`, `REDIS_*`, `S3_*`, `JWT_*`, `CSRF_TRUSTED_ORIGINS`, `CORS_ALLOWED_ORIGINS`.
  - `nginx/.env` (copy from `nginx/.env.example`): Loaded in Docker Compose for `nginx`. Configurable keys: `NGINX_CLIENT_MAX_BODY_SIZE`.
- **Database & Constance**: Uses `psycopg` (v3) driver (`django.db.backends.postgresql`). Constance settings use `DatabaseBackend` (`constance.backends.database`) persisted in PostgreSQL with caching.
- **URL Prefixes**:
  - URLs are prefixed by `BASE_URL` (default `""`) and `API_PREFIX` (default `"api/"`).
  - Auth: `/<BASE_URL><API_PREFIX>auth/` (users app: `register/`, `login/`, `jwt/refresh/`, `jwt/verify/`, `jwt/blacklist/`, `me/`).
  - OpenAPI / Swagger UI: `/<BASE_URL><API_PREFIX>docs/swagger/` and schema at `/<BASE_URL><API_PREFIX>docs/schema.json`.
  - Admin: `/<BASE_URL>admin/`.
- **Redis DB Allocations**:
  - `db 0`: Default cache and Dramatiq broker (`DRAMATIQ_BROKER_URL`).
  - `db 1`: Blacklisted JWT refresh tokens (`caches["blacklist"]`).
  - `db 2`: Endpoint cache (`caches["endpoints"]`).

---

## Known Code Quirks & Warnings

- **CSRF Origin on Host Port 1337**: Requests via Nginx from host must be listed in `CSRF_TRUSTED_ORIGINS` (includes `http://localhost:1337` and `http://127.0.0.1:1337`).
- **Django Modern REST (DMR) Conventions**:
  - DMR skills for AI agents are available in `.agents/skills/` (`dmr`, `dmr-from-drf`, `dmr-from-django-ninja`, `dmr-from-dj-rest-auth`, `dmr-openapi-skeleton`, `dmr-upgrade`).
  - Controller methods expect request body argument named strictly `parsed_body: Body[...]` (not `body`).
  - Do NOT create a module named `jwt.py` in apps (e.g. `users/jwt.py`), as DMR's `dmr.security.jwt` will accidentally perform relative imports from it instead of the system PyJWT package. Use `tokens.py`.
  - `DMR_SETTINGS["exclude_validate_responses"]` requires `HTTPStatus` enum members (from `http import HTTPStatus`), not plain integers.
