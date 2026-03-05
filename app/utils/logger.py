import logging
import logging.handlers
from pathlib import Path
from typing import Optional

from .config import Config


class LoggerFactory:
    _instances: dict[str, logging.Logger] = {}

    @classmethod
    def get_logger(cls, name: str) -> logging.Logger:
        if name in cls._instances:
            return cls._instances[name]
        logger = logging.getLogger(name)
        logger.setLevel(_get_level(Config.LOG_LEVEL))
        if not logger.handlers:
            formatter = _json_formatter()
            file_handler = _file_handler(logger.name, formatter)
            stream_handler = _stream_handler(formatter)
            logger.addHandler(file_handler)
            logger.addHandler(stream_handler)
            logger.propagate = False
        cls._instances[name] = logger
        return logger


def _get_level(level_name: str) -> int:
    try:
        return getattr(logging, level_name.upper())
    except AttributeError as exc:
        raise ValueError(f"Invalid log level: {level_name}") from exc


def _file_handler(name: str, formatter: logging.Formatter) -> logging.Handler:
    log_path = Path(Config.LOG_FILE)
    log_dir = log_path.parent
    log_dir.mkdir(parents=True, exist_ok=True)
    handler = logging.handlers.RotatingFileHandler(
        filename=str(log_path),
        maxBytes=10 * 1024 * 1024,
        backupCount=5,
        encoding="utf-8",
    )
    handler.setLevel(_get_level(Config.LOG_LEVEL))
    handler.setFormatter(formatter)
    return handler


def _stream_handler(formatter: logging.Formatter) -> logging.Handler:
    handler = logging.StreamHandler()
    handler.setLevel(_get_level(Config.LOG_LEVEL))
    handler.setFormatter(formatter)
    return handler


def _json_formatter() -> logging.Formatter:
    class JSONFormatter(logging.Formatter):
        def format(self, record: logging.LogRecord) -> str:
            log_record = {
                "timestamp": self.formatTime(record, "%Y-%m-%dT%H:%M:%S"),
                "level": record.levelname,
                "logger": record.name,
                "message": record.getMessage(),
                "pathname": record.pathname,
                "lineno": record.lineno,
            }
            if record.exc_info:
                log_record["exc_info"] = self.formatException(record.exc_info)
            return str(log_record)

    return JSONFormatter()


get_logger = LoggerFactory.get_logger

def configure_root() -> None:
    root = logging.getLogger()
    root.setLevel(_get_level(Config.LOG_LEVEL))
    if not root.handlers:
        formatter = _json_formatter()
        file_handler = _file_handler("root", formatter)
        stream_handler = _stream_handler(formatter)
        root.addHandler(file_handler)
        root.addHandler(stream_handler)
        root.propagate = False
configure_root()