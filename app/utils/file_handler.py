import os
import json
import yaml
from pathlib import Path
from typing import Any, Dict, Optional

from app.utils.logger import get_logger


logger = get_logger(__name__)


def _validate_path(path: str | Path) -> Path:
    p = Path(path).expanduser().resolve()
    if not p.is_absolute():
        raise ValueError(f"Path must be absolute: {p}")
    return p


def read_file(path: str | Path, encoding: str = "utf-8") -> str:
    p = _validate_path(path)
    try:
        with p.open("r", encoding=encoding) as f:
            content = f.read()
        logger.debug(f"Read file {p}")
        return content
    except FileNotFoundError as exc:
        logger.error(f"File not found: {p}", exc_info=True)
        raise
    except OSError as exc:
        logger.error(f"I/O error reading {p}: {exc}", exc_info=True)
        raise


def write_file(path: str | Path, data: str, encoding: str = "utf-8") -> None:
    p = _validate_path(path)
    try:
        with p.open("w", encoding=encoding) as f:
            f.write(data)
        logger.debug(f"Wrote file {p}")
    except OSError as exc:
        logger.error(f"I/O error writing {p}: {exc}", exc_info=True)
        raise


def read_json(path: str | Path, encoding: str = "utf-8") -> Dict[str, Any]:
    content = read_file(path, encoding=encoding)
    try:
        return json.loads(content)
    except json.JSONDecodeError as exc:
        logger.error(f"JSON decode error in {path}: {exc}", exc_info=True)
        raise


def write_json(path: str | Path, data: Dict[str, Any], encoding: str = "utf-8") -> None:
    content = json.dumps(data, indent=2, ensure_ascii=False)
    write_file(path, content, encoding=encoding)


def read_yaml(path: str | Path, encoding: str = "utf-8") -> Any:
    content = read_file(path, encoding=encoding)
    try:
        return yaml.safe_load(content)
    except yaml.YAMLError as exc:
        logger.error(f"YAML load error in {path}: {exc}", exc_info=True)
        raise


def write_yaml(path: str | Path, data: Any, encoding: str = "utf-8") -> None:
    content = yaml.safe_dump(data, sort_keys=False, allow_unicode=True)
    write_file(path, content, encoding=encoding)


def get_extension(path: str | Path) -> str:
    p = _validate_path(path)
    return p.suffix.lower().lstrip(".")


def ensure_directory_exists(path: str | Path) -> None:
    p = _validate_path(path).parent
    try:
        p.mkdir(parents=True, exist_ok=True)
    except OSError as exc:
        logger.error(f"Failed to create directory {p}: {exc}", exc_info=True)
        raise


def read_file_as_dict(
    path: str | Path,
    *,
    encoding: str = "utf-8",
    parser: Optional[str] = None,
) -> Dict[str, Any]:
    ext = get_extension(path)
    if parser is None:
        parser = ext
    if parser == "json":
        return read_json(path, encoding=encoding)
    if parser in ("yaml", "yml"):
        return read_yaml(path, encoding=encoding)
    raise ValueError(f"Unsupported parser: {parser}")


def write_dict_as_file(
    path: str | Path,
    data: Dict[str, Any],
    *,
    encoding: str = "utf-8",
    formatter: Optional[str] = None,
) -> None:
    ext = get_extension(path)
    if formatter is None:
        formatter = ext
    ensure_directory_exists(path)
    if formatter == "json":
        write_json(path, data, encoding=encoding)
    elif formatter in ("yaml", "yml"):
        write_yaml(path, data, encoding=encoding)
    else:
        raise ValueError(f"Unsupported formatter: {formatter}")