import atexit
import json
import logging
from logging.config import dictConfig
from logging.handlers import QueueHandler, QueueListener

from logery.settings import (
    LogLevel,
    default_logger_level,
    logging_config_json,
    logs_dir,
    setup_logger_level,
    setup_logger_name,
    validate_level,
)

_setup_logging_done: bool = False
_default_queue_listener: QueueListener | None = None

_logger = logging.getLogger(setup_logger_name)
_logger.setLevel(setup_logger_level)


def _create_default_config() -> dict:
    """Cria uma configuração padrão de logging"""
    return {
        "version": 1,
        "disable_existing_loggers": False,
        "formatters": {
            "file": {
                "format": "%(levelname)s|%(name)s|%(asctime)s|%(message)s|%(filename)s|%(lineno)d|%(funcName)s|%(module)s|%(process)d|%(processName)s|%(thread)d|%(threadName)s|%(taskName)s"
            },
            "json": {
                "()": "logery.formatters.JSONLogFormatter",
                "include_keys": [
                    "created",
                    "message",
                    "levelname",
                    "name",
                    "filename",
                    "module",
                    "exc_info",
                    "lineno",
                    "threadName",
                    "processName",
                    "taskName",
                    "args",
                    "contexto"
                ]
            },
            "console_stdout": {
                "format": "%(message)s",
                "datefmt": "[%Y-%m-%d %H:%M:%S]"
            },
            "console_stderr": {
                "format": "%(message)s",
                "datefmt": "[%Y-%m-%d %H:%M:%S]"
            }
        },
        "filters": {
            "max_level_info": {
                "()": "logery.filters.MaxLevelFilter",
                "level": "INFO"
            }
        },
        "handlers": {
            "queue": {
                "class": "logging.handlers.QueueHandler",
                "handlers": ["console_stdout", "console_stderr", "file"],
                "respect_handler_level": True
            },
            "console_stdout": {
                "()": "logery.handlers.MyRichHandler",
                "formatter": "console_stdout",
                "rich_tracebacks": False,
                "tracebacks_show_locals": False,
                "show_time": True,
                "show_level": True,
                "omit_repeated_times": False,
                "markup": False,
                "enable_link_path": True,
                "show_path": True,
                "file": "stdout",
                "level": "DEBUG",
                "filters": ["max_level_info"]
            },
            "console_stderr": {
                "()": "logery.handlers.MyRichHandler",
                "formatter": "console_stderr",
                "rich_tracebacks": False,
                "tracebacks_show_locals": False,
                "show_time": True,
                "show_level": True,
                "omit_repeated_times": False,
                "markup": False,
                "enable_link_path": True,
                "show_path": True,
                "file": "stderr",
                "level": "WARNING"
            },
            "file": {
                "class": "logging.handlers.RotatingFileHandler",
                "formatter": "json",
                "filename": "logs/log.jsonl",
                "maxBytes": 5242880,
                "backupCount": 5,
                "encoding": "utf-8"
            }
        },
        "root": {
            "handlers": ["queue"]
        },
        "loggers": {
            "meuapp": {
                "level": "DEBUG"
            }
        }
    }


def _setup_logging() -> None:
    global _setup_logging_done, _default_queue_listener

    if _setup_logging_done:
        _logger.debug("logging already configured, doing nothing for now")
        return

    # Criar diretório de logs se não existir
    if not logs_dir.is_dir():
        logs_dir.mkdir(parents=True, exist_ok=True)
        _logger.debug("Logs directory created: %s", logs_dir)

    # Criar arquivo de configuração se não existir
    if not logging_config_json.is_file():
        default_config = _create_default_config()
        with logging_config_json.open("w", encoding="utf-8") as file:
            json.dump(default_config, file, indent=4)
        _logger.debug("Default config file created: %s", logging_config_json)

    with logging_config_json.open("r", encoding="utf-8") as file:
        logging_config = json.load(file)
        _logger.debug("JSON config file loaded: %s", logging_config_json)

    dictConfig(logging_config)

    queue_handlers = [
        handler
        for handler in logging.getLogger().handlers
        if isinstance(handler, QueueHandler)
    ]

    queue_handlers_count = len(queue_handlers)
    _logger.debug("QueueHandlers found: %d", queue_handlers_count)

    if queue_handlers_count > 1:
        msg = "This function does not allow more than one QueueHandler"
        raise RuntimeError(msg)

    if queue_handlers_count > 0:
        queue_handler = queue_handlers[0]
        _logger.debug("Found QueueHandler with name: '%s'", queue_handler.name)

        if queue_handler:
            _default_queue_listener = queue_handler.listener

            if _default_queue_listener is not None:
                _default_queue_listener.start()
                atexit.register(_stop_queue_listener)

                _logger.debug(
                    "QueueListener from QueueHandler '%s' started", queue_handler.name
                )

                _logger.debug(
                    "Function '%s' registered with atexit",
                    _stop_queue_listener.__name__,
                )

    _setup_logging_done = True


def _stop_queue_listener() -> None:
    if _default_queue_listener is None:
        return

    _logger.debug("Default listener will stop now, 👋 bye...")
    _default_queue_listener.stop()


def start_log() -> None:
    """
    Configura o sistema de logging automaticamente.
    Cria os diretórios e arquivos de configuração necessários se não existirem.
    """
    _setup_logging()


def get_logger(name: str = "", level: LogLevel | None = None) -> logging.Logger:
    """
    Retorna um logger configurado.
    Se o logging não foi configurado ainda, configura automaticamente.
    """
    if not _setup_logging_done:
        _setup_logging()
        _logger.debug("'_setup_logging' used to configure Python logging.")

    logger = logging.getLogger(name)

    if level is not None:
        validate_level(level)
        _logger.debug(f"Level {level!r} used by 'get_logger' to configure {name!r} logger.")
        logger.setLevel(level)
    else:
        env_level = default_logger_level
        _logger.debug(f"Level {env_level!r} used by 'ENV' to configure {name!r} logger.")
        logger.setLevel(env_level)

    return logger
