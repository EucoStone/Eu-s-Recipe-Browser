from __future__ import annotations

from pathlib import Path
from typing import Any

from pymongo import UpdateOne

from app.core.database import get_database
from app.core.translations import load_translation_file, resolve_item_labels


def import_translation_paths(paths: list[Path]) -> dict[str, Any]:
    entries = 0
    for path in paths:
        summary = load_translation_file(path)
        entries += int(summary.get("entries", 0))
    return {"entries": entries, "files": len(paths)}


async def refresh_recipe_labels() -> dict[str, Any]:
    db = get_database()
    cursor = db.recipes.find({}, {"outputs": 1})
    operations: list[UpdateOne] = []
    updated = 0
    scanned = 0

    async for document in cursor:
        scanned += 1
        labels = resolve_item_labels(document.get("outputs", []))
        operations.append(
            UpdateOne(
                {"_id": document["_id"]},
                {"$set": {"output_labels": labels}},
            )
        )
        if len(operations) >= 500:
            result = await db.recipes.bulk_write(operations, ordered=False)
            updated += result.modified_count
            operations.clear()

    if operations:
        result = await db.recipes.bulk_write(operations, ordered=False)
        updated += result.modified_count

    return {"scanned": scanned, "updated": updated}
