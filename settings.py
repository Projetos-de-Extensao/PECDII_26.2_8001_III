import os

SECRET_KEY = os.environ["SECRET_KEY"]

DEBUG = os.environ.get("DEBUG", "False") == "True"

ALLOWED_HOSTS = [
    host for host in os.environ.get("ALLOWED_HOSTS", "").split(",")
    if host
]