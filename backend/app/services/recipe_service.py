from __future__ import annotations

from itertools import chain
from pathlib import Path
from typing import Any

from app.core.database import get_database
from app.core.translations import resolve_item_labels
from app.schemas.recipe import IngredientItem, RecipeItem, RecipeSearchItem
from app.utils.kubejs_parser import (
    extract_ingredients,
    extract_output_values,
    iter_recipe_candidates,
    iter_recipe_candidates_from_path,
    load_json,
)


async def import_recipes(file_path: Path, source_file: str | None = None) -> dict[str, Any]:
    db = get_database()

    inserted = 0
    updated = 0
    skipped = 0

    try:
        candidate_iter = iter_recipe_candidates_from_path(file_path)
        first_candidate = next(candidate_iter, None)
        if first_candidate is None:
            payload = load_json(file_path)
            candidate_iter = iter_recipe_candidates(payload)
        else:
            candidate_iter = chain([first_candidate], candidate_iter)
    except Exception:
        payload = load_json(file_path)
        candidate_iter = iter_recipe_candidates(payload)

    for recipe_id, raw_recipe in candidate_iter:
        outputs = extract_output_values(raw_recipe)
        if not outputs:
            skipped += 1
            continue

        normalized = RecipeItem(
            recipe_id=recipe_id,
            type=str(raw_recipe.get("type", "unknown")),
            outputs=[item for item, _ in outputs],
            output_count=float(outputs[0][1]) if outputs else 1,
            ingredients=[IngredientItem(**ingredient) for ingredient in extract_ingredients(raw_recipe)],
            raw=raw_recipe,
            source_file=source_file,
        ).model_dump()

        normalized["output_name"] = normalized["outputs"][0] if normalized["outputs"] else None
        normalized["output_labels"] = resolve_item_labels(normalized["outputs"])
        result = await db.recipes.update_one({"recipe_id": recipe_id}, {"$set": normalized}, upsert=True)
        if result.upserted_id is not None:
            inserted += 1
        elif result.modified_count > 0:
            updated += 1
        else:
            updated += 1

    return {
        "inserted": inserted,
        "updated": updated,
        "skipped": skipped,
        "total_seen": inserted + updated + skipped,
    }


async def import_recipe_directory(directory: Path) -> dict[str, Any]:
    summaries: list[dict[str, Any]] = []
    for file_path in directory.rglob("*.json"):
        summaries.append(await import_recipes(file_path, source_file=file_path.relative_to(directory).as_posix()))
    return merge_import_summaries(summaries)


def merge_import_summaries(summaries: list[dict[str, Any]]) -> dict[str, Any]:
    return {
        "inserted": sum(int(summary.get("inserted", 0)) for summary in summaries),
        "updated": sum(int(summary.get("updated", 0)) for summary in summaries),
        "skipped": sum(int(summary.get("skipped", 0)) for summary in summaries),
        "total_seen": sum(int(summary.get("total_seen", 0)) for summary in summaries),
    }


async def search_recipes(query: str, limit: int = 20) -> list[RecipeSearchItem]:
    db = get_database()
    escaped = query.replace("\\", "\\\\")
    cursor = db.recipes.find(
        {
            "$or": [
                {"recipe_id": {"$regex": escaped, "$options": "i"}},
                {"outputs": {"$regex": escaped, "$options": "i"}},
                {"output_name": {"$regex": escaped, "$options": "i"}},
                {"output_labels": {"$regex": escaped, "$options": "i"}},
                {"type": {"$regex": escaped, "$options": "i"}},
            ]
        }
    ).limit(min(max(limit, 1), 50))
    items: list[RecipeSearchItem] = []
    async for document in cursor:
        outputs = document.get("outputs", [])
        items.append(
            RecipeSearchItem(
                recipe_id=document["recipe_id"],
                type=document.get("type", "unknown"),
                outputs=outputs,
                output_labels=document.get("output_labels") or resolve_item_labels(outputs),
                output_count=float(document.get("output_count", 1)),
                source_file=document.get("source_file"),
            )
        )
    return items


async def get_recipe_by_output(item_id: str) -> list[dict[str, Any]]:
    db = get_database()
    cursor = db.recipes.find({"outputs": item_id})
    return [document async for document in cursor]


async def get_recipe_by_id(recipe_id: str) -> dict[str, Any] | None:
    db = get_database()
    return await db.recipes.find_one({"recipe_id": recipe_id})
