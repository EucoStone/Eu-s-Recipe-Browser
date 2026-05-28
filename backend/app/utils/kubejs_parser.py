from __future__ import annotations

from collections.abc import Iterator
from contextlib import suppress
from pathlib import Path
from typing import Any
import hashlib
import json

try:
    import ijson  # type: ignore
except Exception:  # pragma: no cover
    ijson = None


def stable_recipe_id(payload: dict[str, Any], fallback: str) -> str:
    raw_key = payload.get("id") or payload.get("name") or payload.get("recipe_id") or fallback
    if raw_key:
        return str(raw_key)
    digest = hashlib.sha1(json.dumps(payload, sort_keys=True, ensure_ascii=False).encode("utf-8")).hexdigest()
    return f"recipe:{digest}"


def load_json(path: Path) -> Any:
    with path.open("r", encoding="utf-8-sig") as fh:
        return json.load(fh)


def iter_recipe_candidates(payload: Any) -> Iterator[tuple[str, dict[str, Any]]]:
    if isinstance(payload, dict):
        if "type" in payload:
            yield stable_recipe_id(payload, "recipe"), payload
            return

        if isinstance(payload.get("recipes"), list):
            for index, item in enumerate(payload["recipes"]):
                if isinstance(item, dict):
                    yield stable_recipe_id(item, f"recipes[{index}]"), item
            return

        for key, value in payload.items():
            if isinstance(value, dict) and "type" in value:
                yield stable_recipe_id(value, str(key)), value
            elif isinstance(value, list):
                for index, item in enumerate(value):
                    if isinstance(item, dict) and "type" in item:
                        yield stable_recipe_id(item, f"{key}[{index}]"), item
        return

    if isinstance(payload, list):
        for index, item in enumerate(payload):
            if isinstance(item, dict) and "type" in item:
                yield stable_recipe_id(item, f"list[{index}]"), item


def iter_recipe_candidates_from_path(path: Path) -> Iterator[tuple[str, dict[str, Any]]]:
    if ijson is not None:
        with path.open("r", encoding="utf-8-sig") as fh:
            yielded = False
            with suppress(Exception):
                for index, item in enumerate(ijson.items(fh, "recipes.item")):
                    if isinstance(item, dict):
                        yielded = True
                        yield stable_recipe_id(item, f"recipes[{index}]"), item
            if yielded:
                return

    payload = load_json(path)
    if isinstance(payload, dict) and "type" in payload:
        yield stable_recipe_id(payload, path.as_posix()), payload
        return

    yield from iter_recipe_candidates(payload)


def extract_output_values(recipe: dict[str, Any]) -> list[tuple[str, float]]:
    outputs: list[tuple[str, float]] = []

    def add_item(value: Any, default_count: float = 1) -> None:
        if isinstance(value, str):
            outputs.append((value, default_count))
            return
        if isinstance(value, dict):
            item = value.get("item") or value.get("id") or value.get("name")
            if item:
                count = value.get("count", value.get("amount", default_count))
                try:
                    outputs.append((str(item), float(count)))
                except (TypeError, ValueError):
                    outputs.append((str(item), default_count))

    for key in ("result", "output", "item"):
        value = recipe.get(key)
        if value:
            add_item(value)

    for key in ("results", "outputs"):
        value = recipe.get(key)
        if isinstance(value, list):
            for entry in value:
                add_item(entry)
        elif isinstance(value, dict):
            add_item(value)

    return outputs


def extract_ingredients(recipe: dict[str, Any]) -> list[dict[str, Any]]:
    ingredients: list[dict[str, Any]] = []

    def normalize(entry: Any) -> None:
        if entry is None:
            return
        if isinstance(entry, str):
            ingredients.append({"item": entry, "count": 1, "raw": entry})
            return
        if isinstance(entry, dict):
            item = entry.get("item") or entry.get("id") or entry.get("name")
            tag = entry.get("tag")
            count = entry.get("count", entry.get("amount", 1))
            if item or tag:
                ingredients.append({"item": item, "tag": tag, "count": count, "raw": entry})

    for key in ("ingredients", "input", "inputs", "ingredient"):
        value = recipe.get(key)
        if isinstance(value, list):
            for entry in value:
                normalize(entry)
        elif isinstance(value, dict):
            normalize(value)
        elif isinstance(value, str):
            normalize(value)

    if isinstance(recipe.get("key"), dict) and isinstance(recipe.get("pattern"), list):
        key_map = recipe["key"]
        pattern = recipe["pattern"]
        seen: set[str] = set()
        for row in pattern:
            if not isinstance(row, str):
                continue
            for symbol in row:
                if symbol == " " or symbol in seen:
                    continue
                seen.add(symbol)
                entry = key_map.get(symbol)
                if isinstance(entry, dict):
                    normalize(entry)
                elif isinstance(entry, list):
                    for sub in entry:
                        normalize(sub)

    return ingredients
