# Django Template

Современный production-ready шаблон бэкенд-приложения на базе Django, Django Modern REST и Dramatiq.

---

## Стек технологий

- **Язык & Фреймворк**: Python 3.12 (`python:3.12-slim`), Django 6.1.3
- **REST API**: [Django Modern REST (DMR)](https://github.com/wemake-services/django-modern-rest) со строгой типизацией на Pydantic и автогенерацией OpenAPI/Swagger
- **Фоновые задачи**: [Dramatiq](https://dramatiq.io/) 2.2.1 + `django-dramatiq` + `periodiq` (брокер Redis)
- **База данных**: PostgreSQL 17 с современным драйвером [Psycopg 3](https://www.psycopg.org/psycopg3/) (`psycopg[binary,pool]`)
- **Кэширование & Сессии**: Redis (`django-redis`)
- **Веб-сервер & Реверс-прокси**: Nginx (`nginx:1.27-alpine`) с динамической настройкой через шаблоны, Gzip-сжатием и кэшированием статики
- **WSGI Сервер**: Gunicorn 26.2.0
- **Динамические настройки**: `django-constance` с персистентным хранением в PostgreSQL (`DatabaseBackend`)
- **Контейнеризация**: Docker Compose с отдельными конфигурациями для разработки и продакшна

---

## Структура проекта

```text
├── django_core/            # Исходный код Django-приложения
│   ├── django_core/        # Конфигурация проекта (settings, wsgi, urls)
│   ├── users/              # Модуль пользователей и аутентификации (DMR API, JWT, задачи)
│   ├── requirements/       # Зависимости (base.txt, production.txt, local.txt)
│   ├── Dockerfile          # Легковесный multi-stage образ на python:3.12-slim
│   ├── entrypoint.sh       # Скрипт инициализации (миграции, collectstatic, graceful shutdown)
│   └── .env.example        # Пример переменных окружения для бэкенда и БД
├── nginx/                  # Конфигурация Nginx
│   ├── Dockerfile          # Образ на nginx:1.27-alpine
│   ├── default.conf.template # Шаблон конфигурации Nginx (динамический envsubst)
│   └── .env.example        # Переменные окружения для Nginx (изолированные от Django)
├── docker-compose.yml      # Окружение для локальной разработки (hot-reload, volume mounts)
├── docker-compose.prod.yml # Production-окружение (иммутабельный образ, ротация логов, named volumes)
└── AGENTS.md               # Инструкции и операционный контекст для AI-агентов
```

---

## Быстрый старт (Локальная разработка)

### 1. Подготовка переменных окружения

Скопируйте примеры файлов конфигурации:

```bash
cp django_core/.env.example django_core/.env
cp nginx/.env.example nginx/.env
```

> **Важно**: В `django_core/.env` задайте надёжный `SECRET_KEY` (длиной не менее 32 символов для безопасной работы JWT).

### 2. Запуск сервисов

```bash
docker compose up -d
```

Docker поднимет сервисы в строгом порядке готовности (`db` → `redis` → `backend` → `nginx` & `dramatiq`):
- `backend` автоматически применит миграции и соберёт статику при первом запуске через `entrypoint.sh`.
- Nginx будет доступен на хостовом порту **1337**.

### 3. Доступные эндпоинты

- **Swagger UI**: [http://localhost:1337/api/docs/swagger/](http://localhost:1337/api/docs/swagger/)
- **OpenAPI Schema**: [http://localhost:1337/api/docs/schema.json](http://localhost:1337/api/docs/schema.json)
- **Django Admin**: [http://localhost:1337/admin/](http://localhost:1337/admin/)
- **API Аутентификации**:
  - `POST /api/auth/register/` — регистрация пользователя
  - `POST /api/auth/login/` — получение пары access/refresh токенов
  - `POST /api/auth/jwt/refresh/` — ротация токенов (старый refresh помещается в блэклист)
  - `POST /api/auth/jwt/verify/` — проверка валидности токена
  - `POST /api/auth/jwt/blacklist/` — отзыв refresh-токена (логаут)
  - `GET /api/auth/me/` — профиль текущего авторизованного пользователя

---

## Основные команды

### Создание суперпользователя
```bash
docker compose exec backend python manage.py createsuperuser
```

### Применение миграций
```bash
docker compose exec backend python manage.py migrate
```

### Запуск тестов
```bash
docker compose exec backend python manage.py test
```

### Просмотр логов
```bash
# Логи бэкенда
docker compose logs -f backend

# Логи воркеров Dramatiq
docker compose logs -f dramatiq
```

### Остановка сервисов
```bash
docker compose down
```
> Данные базы данных и Redis сохраняются в именованных томах `postgres_data` и `redis_data`.

---

## Запуск в Production

Для развёртывания на боевом сервере используется манифест `docker-compose.prod.yml`:

```bash
docker compose -f docker-compose.prod.yml up -d --build
```

**Отличия продакшн-конфигурации:**
- Код не монтируется с хоста — используется автономный иммутабельный Docker-образ.
- Gunicorn запускается в боевом режиме без флага `--reload`.
- Включена автоматическая ротация логов Docker (`max-size: 10m`, `max-file: 3`).
- Настроен `stop_grace_period: 60s` для Dramatiq (безопасное завершение активных задач).
- Статика и медиа изолированы в именованных томах с доступом `read-only` со стороны Nginx.
- Nginx слушает порт `1337` для проксирования через внешний системный веб-сервер с SSL (Certbot / Cloudflare).
