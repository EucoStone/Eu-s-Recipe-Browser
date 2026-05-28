from __future__ import annotations

from collections.abc import Iterable


def format_item_name(item_id: str | None) -> str:
    if not item_id:
        return ""

    if ":" in item_id:
        namespace, path = item_id.split(":", 1)
    else:
        namespace, path = "", item_id

    words = path.replace("/", " ").replace("_", " ").replace("-", " ").split()
    label = " ".join(word.capitalize() for word in words)
    if namespace and namespace not in {"minecraft"}:
        return f"{label} ({namespace})"
    return label


def format_item_names(item_ids: list[str]) -> list[str]:
    return [format_item_name(item_id) for item_id in item_ids]


def translation_key_to_item_ids(key: str) -> list[str]:
    parts = key.split(".")
    if len(parts) < 3:
        return []

    prefix = parts[0]
    if prefix not in {"item", "block", "entity", "fluid"}:
        return []

    namespace = parts[1]
    raw_path = ".".join(parts[2:])
    candidates = {
        f"{namespace}:{raw_path}",
        f"{namespace}:{raw_path.replace('.', '_')}",
        f"{namespace}:{raw_path.replace('.', '/')}",
    }
    return [candidate for candidate in candidates if candidate]


def unique_ordered(values: Iterable[str]) -> list[str]:
    seen: set[str] = set()
    ordered: list[str] = []
    for value in values:
        if value in seen:
            continue
        seen.add(value)
        ordered.append(value)
    return ordered
