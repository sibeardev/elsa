from .env import EnvSettings

settings = EnvSettings()

LOG_PATH = "/opt/logs/error.log"
LOGGING_CONFIG = {
    "version": 1,
    "disable_existing_loggers": False,
    "formatters": {
        "default": {
            "format": "%(asctime)s:c:%(process)d:%(lineno)d %(levelname)s %(message)s",
            "datefmt": "%Y-%m-%d %H:%M:%S",
        },
        "simple": {
            "format": "%(filename)s:%(lineno)d: - %(message)s",
        },
    },
    "handlers": {
        "logfile": {
            "class": "logging.handlers.RotatingFileHandler",
            "level": "ERROR",
            "filename": LOG_PATH,
            "formatter": "default",
            "backupCount": 2,
        },
        "verbose_output": {
            "class": "logging.StreamHandler",
            "level": "DEBUG",
            "formatter": "simple",
            "stream": "ext://sys.stdout",
        },
    },
    "loggers": {
        "elsa": {
            "level": "INFO",
            "handlers": [
                "verbose_output",
            ],
            "propagate": False,
        },
    },
    "root": {"level": "INFO", "handlers": ["logfile", "verbose_output"]},
}
