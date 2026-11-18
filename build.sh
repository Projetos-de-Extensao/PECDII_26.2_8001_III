#!/usr/bin/env bash
set -o errexit

uv sync
python src/manage.py migrate
DJANGO_SUPERUSER_USERNAME=admin 
DJANGO_SUPERUSER_EMAIL=admin@example.com
DJANGO_SUPERUSER_PASSWORD='123' 
python src/manage.py createsuperuser --noinput