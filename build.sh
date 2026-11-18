#!/usr/bin/env bash
set -o errexit

uv sync
python src/manage.py migrate