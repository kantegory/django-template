FROM python:3.12-slim

# Prevent Python from writing .pyc files to disk and ensure stdout/stderr are unbuffered
ENV PYTHONDONTWRITEBYTECODE=1 \
    PYTHONUNBUFFERED=1

WORKDIR /var/www/apps/django_core

# Install dependencies first to leverage Docker layer caching
RUN pip install --upgrade pip
COPY ./requirements ./requirements
RUN pip install --no-cache-dir -r requirements/production.txt

# Copy project files into container
COPY . .

# Set up entrypoint script
RUN chmod +x /var/www/apps/django_core/entrypoint.sh
ENTRYPOINT ["/var/www/apps/django_core/entrypoint.sh"]

# Default command (overridden in docker-compose.yml for development)
CMD ["gunicorn", "-w", "3", "django_core.wsgi:application", "--bind", "0.0.0.0:8000"]
