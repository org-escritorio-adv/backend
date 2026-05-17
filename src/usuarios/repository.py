from typing import Any

_db: list[dict[str, Any]] = []


def get_store() -> list[dict[str, Any]]:
    return _db
