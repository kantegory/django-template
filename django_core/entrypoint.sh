#!/usr/bin/env bash
set -e

# Automatically run migrations and collectstatic when starting the web server
if [[ "$*" == *"gunicorn"* ]] || [[ "$*" == *"runserver"* ]]; then
    echo "[Entrypoint] Applying database migrations..."
    python manage.py migrate --noinput

    echo "[Entrypoint] Collecting static files..."
    python manage.py collectstatic --noinput
fi

exec "$@"
