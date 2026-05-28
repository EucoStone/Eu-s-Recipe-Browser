from __future__ import annotations

from pathlib import Path
from typing import Any
import json

from app.utils.item_names import format_item_name, unique_ordered

TRANSLATION_MAP: dict[str, str] = {}


def load_translation_file(file_path: Path) -> dict[str, Any]:
    with file_path.open("r", encoding="utf-8-sig") as fh:
        payload = json.load(fh)

    if not isinstance(payload, dict):
        return {"entries": 0}

    added = 0
    for key, value in payload.items():
        if isinstance(value, str) and value.strip():
            TRANSLATION_MAP[key] = value.strip()
            added += 1

    return {"entries": added}


def resolve_item_label(item_id: str | None) -> str:
    if not item_id:
        return ""

    if ":" in item_id:
        namespace, path = item_id.split(":", 1)
    else:
        namespace, path = "", item_id

    candidates = unique_ordered(
        [
            f"block.{namespace}.{path}",
            f"item.{namespace}.{path}",
            f"entity.{namespace}.{path}",
            f"fluid.{namespace}.{path}",
        ]
    )
    for key in candidates:
        value = TRANSLATION_MAP.get(key)
        if value:
            return value

    return format_item_name(item_id)


def resolve_item_labels(item_ids: list[str]) -> list[str]:
    return [resolve_item_label(item_id) for item_id in item_ids]
