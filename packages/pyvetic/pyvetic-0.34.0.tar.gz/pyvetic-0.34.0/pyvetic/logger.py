import logging
import os
import sys
from logging.handlers import RotatingFileHandler
from queue import Queue

import logging_loki

from pyvetic.constants import APP_NAME, LOKI_HOST, MONITORING_AUTH_PASS, MONITORING_AUTH_USER

# Shared Loki handler to prevent multiple queues/threads
_shared_loki_handler = None


# --- Colored Formatter ---
class CustomFormatter(logging.Formatter):
    grey = "\x1b[38;21m"
    blue = "\x1b[38;5;39m"
    yellow = "\x1b[38;5;226m"
    red = "\x1b[38;5;196m"
    bold_red = "\x1b[31;1m"
    reset = "\x1b[0m"

    def __init__(self, fmt):
        super().__init__()
        self.fmt = fmt
        self.FORMATS = {
            logging.DEBUG: self.grey + self.fmt + self.reset,
            logging.INFO: self.blue + self.fmt + self.reset,
            logging.WARNING: self.yellow + self.fmt + self.reset,
            logging.ERROR: self.red + self.fmt + self.reset,
            logging.CRITICAL: self.bold_red + self.fmt + self.reset,
        }

    def format(self, record):
        log_fmt = self.FORMATS.get(record.levelno, self.fmt)
        formatter = logging.Formatter(log_fmt)
        return formatter.format(record)


# --- Default Formats ---
LOG_FORMAT = "%(asctime)s - [%(levelname)s] - %(name)s - (%(filename)s).%(funcName)s(L:%(lineno)d) - %(message)s"
LOKI_LOG_FORMAT = "%(name)s - %(message)s"
ACCESS_LOG = "%(asctime)s - %(message)s"

DEFAULT_LOGGING_CONFIG = None
LOKI_ENABLED = False


def enable_loki():
    global LOKI_ENABLED
    LOKI_ENABLED = True


def disable_loki():
    global LOKI_ENABLED
    LOKI_ENABLED = False


# --- Global Config Store ---
def get_logger_config():
    if DEFAULT_LOGGING_CONFIG and isinstance(DEFAULT_LOGGING_CONFIG, dict):
        return DEFAULT_LOGGING_CONFIG

    return {
        "level": "INFO",
        "handlers": {
            "stream": {"log_format": LOG_FORMAT},
            "file": {
                "filename": "logs/app.log",
                "max_bytes": 10 * 1024 * 1024,
                "backup_count": 5,
                "log_format": LOG_FORMAT,
            },
            "loki": {
                "log_format": LOKI_LOG_FORMAT,
                "loki_host": LOKI_HOST,
                "auth": (MONITORING_AUTH_USER, MONITORING_AUTH_PASS),
            },
        },
    }


initialized_loggers = set()


# --- Public API to override default config ---
def set_logging_config(config_dict: dict):
    """
    Replace the default logging config globally.
    All future calls to get_logger() without explicit config will use this.
    """
    global DEFAULT_LOGGING_CONFIG
    DEFAULT_LOGGING_CONFIG = config_dict


# --- Handler Creators ---
def get_stream_handler(config):
    stream_handler = logging.StreamHandler(sys.stdout)
    stream_handler.setLevel(config.get("level", "INFO"))
    stream_handler.setFormatter(CustomFormatter(config.get("log_format", LOG_FORMAT)))
    return stream_handler


def get_file_handler(config):
    filepath = config.get("filename", "logs/app.log")
    os.makedirs(os.path.dirname(filepath), exist_ok=True)
    file_handler = RotatingFileHandler(
        filename=filepath,
        maxBytes=config.get("max_bytes", 10 * 1024 * 1024),
        backupCount=config.get("backup_count", 5),
        encoding="utf-8",
    )
    file_handler.setLevel(config.get("level", "INFO"))
    file_handler.setFormatter(logging.Formatter(config.get("log_format", LOG_FORMAT)))
    return file_handler


def get_loki_handler(config):
    global _shared_loki_handler

    # Create shared handler on first use
    if _shared_loki_handler is None:
        _shared_loki_handler = logging_loki.LokiQueueHandler(
            Queue(-1),  # Only ONE queue for all loggers
            url=f"{config['loki_host'].rstrip('/')}/loki/api/v1/push",
            tags={"app": APP_NAME},
            auth=config.get("auth", (MONITORING_AUTH_USER, MONITORING_AUTH_PASS)),
            version="1",
        )

    # Configure level and formatter based on current config
    _shared_loki_handler.setLevel(config.get("level", "INFO"))
    _shared_loki_handler.setFormatter(logging.Formatter(config.get("log_format", LOKI_LOG_FORMAT)))

    return _shared_loki_handler


# Helper function to check if handler type already exists
def _handler_exists(logger, handler_type):
    """Check if a handler of the given type already exists on the logger."""
    for handler in logger.handlers:
        if (
            handler_type == "stream"
            and isinstance(handler, logging.StreamHandler)
            and not isinstance(handler, RotatingFileHandler)
        ):
            return True
        elif handler_type == "file" and isinstance(handler, RotatingFileHandler):
            return True
        elif handler_type == "loki" and isinstance(handler, logging_loki.LokiQueueHandler):
            return True
    return False


# --- Logger Config Setup ---
def _setup_logger_handlers(logger):
    """Fix 3: Setup handlers for individual logger instead of root logger."""
    config = get_logger_config()
    level = getattr(logging, config.get("level", "INFO").upper())

    logger.setLevel(level)

    handlers = config.get("handlers", {})

    # Auto-add Loki handler if enabled but not in config
    if LOKI_ENABLED and "loki" not in handlers and LOKI_HOST:
        handlers = handlers.copy()
        handlers["loki"] = {
            "log_format": LOKI_LOG_FORMAT,
            "loki_host": LOKI_HOST,
            "auth": (MONITORING_AUTH_USER, MONITORING_AUTH_PASS),
        }

    for name, handler_cfg in handlers.items():
        try:
            # Skip if handler already exists
            if _handler_exists(logger, name):
                continue

            # Add main config level to handler config
            handler_cfg_with_level = handler_cfg.copy()
            handler_cfg_with_level["level"] = config.get("level", "INFO")

            handler = None
            if name == "stream":
                handler = get_stream_handler(handler_cfg_with_level)
            elif name == "file":
                handler = get_file_handler(handler_cfg_with_level)
            elif name == "loki" and LOKI_ENABLED:
                handler = get_loki_handler(handler_cfg_with_level)

            if handler:
                logger.addHandler(handler)

        except Exception as e:
            print(f"Warning: Failed to create {name} handler: {e}", file=sys.stderr)


# --- Logger Accessor ---
def get_logger(name):
    if name in initialized_loggers:
        return logging.getLogger(name)

    logger = logging.getLogger(name)

    if name not in initialized_loggers:
        _setup_logger_handlers(logger)
        # Prevent propagation to avoid duplicate logs from root logger
        logger.propagate = False
        initialized_loggers.add(name)

    return logger


# --- Server Logger Configuration ---

# Server logger name mappings
SERVER_LOGGERS = {
    "uvicorn": ["uvicorn", "uvicorn.access", "uvicorn.error"],
    "django": ["django", "django.request", "django.server", "gunicorn.access", "gunicorn.error"],
}

HANDLER_CREATORS = {"stream": get_stream_handler, "file": get_file_handler, "loki": get_loki_handler}


def _configure_server_loggers(logger_names: list[str]) -> None:
    """
    Internal function to configure server loggers with ACCESS_LOG format.

    Args:
        logger_names: List of logger names to configure
    """
    config = get_logger_config()
    level = getattr(logging, config.get("level", "INFO").upper())
    handlers_config = config.get("handlers", {})

    for logger_name in logger_names:
        logger_instance = logging.getLogger(logger_name)
        logger_instance.handlers.clear()

        for handler_name, handler_cfg in handlers_config.items():
            try:
                # Skip loki if not enabled
                if handler_name == "loki" and not LOKI_ENABLED:
                    continue

                # Skip unknown handler types
                if handler_name not in HANDLER_CREATORS:
                    continue

                # Configure handler with appropriate format
                handler_config = handler_cfg.copy()
                handler_config["level"] = config.get("level", "INFO")

                # Use ACCESS_LOG for stream/file, LOKI_LOG_FORMAT for loki
                if handler_name == "loki":
                    handler_config["log_format"] = LOKI_LOG_FORMAT
                else:
                    handler_config["log_format"] = ACCESS_LOG

                handler = HANDLER_CREATORS[handler_name](handler_config)
                logger_instance.addHandler(handler)

            except Exception as e:
                print(f"Warning: Failed to create {handler_name} handler for {logger_name}: {e}", file=sys.stderr)

        logger_instance.setLevel(level)
        logger_instance.propagate = False


def override_uvicorn_loggers() -> None:
    """Override Uvicorn loggers to use ACCESS_LOG format."""
    _configure_server_loggers(SERVER_LOGGERS["uvicorn"])


def override_django_loggers() -> None:
    """Override Django and Gunicorn loggers to use ACCESS_LOG format."""
    _configure_server_loggers(SERVER_LOGGERS["django"])
