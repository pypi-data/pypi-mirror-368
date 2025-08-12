import os

from pyvetic.utils import get_repo_name

APP_NAME = os.getenv("APP_NAME", get_repo_name())

if not APP_NAME:
    APP_NAME = "unknown-app"

PUSHGATEWAY_HOST = os.getenv("PUSHGATEWAY_HOST", "http://localhost:9091")
PUSHGATEWAY_JOB_NAME = f"{APP_NAME}_metrics"

LOKI_HOST = os.getenv("LOKI_HOST")

MONITORING_AUTH_USER = os.getenv("MONITORING_AUTH_USER", "admin")
MONITORING_AUTH_PASS = os.getenv("MONITORING_AUTH_PASS", "admin")
