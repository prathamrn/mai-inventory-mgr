import os

import config
from multiprocessing import Queue

LOKI_DISABLED = os.environ.get("MAI_DISABLE_LOKI", "0") == "1"

if LOKI_DISABLED:
    _loki_handler = {
        "class": "logging.NullHandler",
    }
    _loki_in_handlers = False
else:
    _loki_handler = {
        # Use '()' factory rather than 'class' so dictConfig does not route
        # through Python 3.12's QueueHandler special-case, which drops
        # kwargs like url/tags/version before instantiating the handler.
        "()": "logging_loki.LokiQueueHandler",
        "queue": Queue(-1),
        "url": "https://loki.abouhaiba.com/loki/api/v1/push",
        "tags": {"application": "mai-inventory-mgr", "stage": config.STAGE},
        "formatter": "loki",
        "version": "1",
    }
    _loki_in_handlers = True


def _logger_handlers():
    if config.DEBUG and not _loki_in_handlers:
        return ["console"]
    if config.DEBUG:
        return ["console", "loki"]
    return ["loki"] if _loki_in_handlers else ["console"]


LOGGING_CONFIGURATION = {
    "version": 1,
    "disable_existing_loggers": True,
    "formatters": {
        "default": {
            "format": "[%(asctime)s] %(levelname)s in %(module)s: %(message)s",
        },
        "loki": {
            "format": "%(levelname)s in %(module)s: %(message)s",
        },
        "access": {
            "format": "%(message)s",
        }
    },
    "handlers": {
        "console": {
            "level": "INFO",
            "class": "logging.StreamHandler",
            "formatter": "default",
            "stream": "ext://sys.stdout",
        },
        "loki": _loki_handler,
    },
    "loggers": {
        "gunicorn.error": {
            "handlers": _logger_handlers(),
            "level": "INFO",
            "propagate": False,
        },
        "gunicorn.access": {
            "handlers": _logger_handlers(),
            "level": "INFO",
            "propagate": False,
        }
    },
    "root": {
        "level": "DEBUG" if config.DEBUG else "INFO",
        "handlers": _logger_handlers(),
    }
}
