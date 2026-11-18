#!/usr/bin/env bash
set -o errexit

uv sync
python src/manage.py migrate
python src/scripts/populate_test_db.py