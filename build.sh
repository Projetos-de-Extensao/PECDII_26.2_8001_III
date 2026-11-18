#!/usr/bin/env bash
set -o errexit

uv sync

uv run python src/manage.py collectstatic --noinput
uv run python src/manage.py migrate

DJANGO_SUPERUSER_USERNAME=admin \
DJANGO_SUPERUSER_EMAIL=admin@example.com \
DJANGO_SUPERUSER_PASSWORD="$DJANGO_SUPERUSER_PASSWORD" \
uv run python src/manage.py createsuperuser --noinput