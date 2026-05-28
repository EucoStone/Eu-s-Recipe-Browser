from __future__ import annotations

from collections import defaultdict
from dataclasses import dataclass
from math import ceil
from typing import Any

from app.schemas.calculator import MaterialItem, TreeNode
from app.services.recipe_service import get_recipe_by_id, get_recipe_by_output
from app.core.translations import resolve_item_label


@dataclass
class CalculationContext:
    inventory: dict[str, float]
    memo: dict[str, tuple[dict[str, float], dict[str, Any] | None]]
    cycles: set[str]


def _ingredient_amount(ingredient: dict[str, Any]) -> float:
    try:
        return float(ingredient.get("count", 1) or 1)
    except (TypeError, ValueError):
        return 1.0


def _sum_materials(target: dict[str, float], source: dict[str, float], multiplier: float) -> None:
    for item_id, amount in source.items():
        target[item_id] += amount * multiplier


async def calculate_item(item_id: str, amount: float, inventory: dict[str, float] | None = None, recipe_id: str | None = None) -> dict[str, Any]:
    context = CalculationContext(
        inventory=inventory or {},
        memo={},
        cycles=set(),
    )
    materials: defaultdict[str, float] = defaultdict(float)
    tree = await _expand(item_id=item_id, amount=amount, context=context, materials=materials, recipe_id=recipe_id)
    result_materials: list[MaterialItem] = []
    for material_id, needed in sorted(materials.items()):
        available = float(context.inventory.get(material_id, 0))
        shortage = max(needed - available, 0)
        result_materials.append(
            MaterialItem(
                item_id=material_id,
                item_label=resolve_item_label(material_id),
                amount_needed=round(needed, 4),
                amount_available=round(available, 4),
                amount_shortage=round(shortage, 4),
            )
        )
    return {
        "tree": tree,
        "materials": result_materials,
        "unresolved_cycles": sorted(context.cycles),
        "target_label": resolve_item_label(item_id),
    }


async def _expand(
    item_id: str,
    amount: float,
    context: CalculationContext,
    materials: defaultdict[str, float],
    recipe_id: str | None = None,
) -> TreeNode:
    available = context.inventory.get(item_id, 0)
    if available >= amount:
        context.inventory[item_id] = available - amount
        return TreeNode(item_id=item_id, item_label=resolve_item_label(item_id), amount=amount, is_base=True, craft_count=0, children=[])

    amount = amount - available
    context.inventory[item_id] = 0

    recipe = None
    if recipe_id:
        recipe = await get_recipe_by_id(recipe_id)
    else:
        recipes = await get_recipe_by_output(item_id)
        if recipes:
            recipe = recipes[0]

    if not recipe:
        materials[item_id] += amount
        return TreeNode(item_id=item_id, item_label=resolve_item_label(item_id), amount=amount, is_base=True, craft_count=0, children=[])

    output_count = float(recipe.get("output_count", 1) or 1)
    craft_count = ceil(amount / output_count)
    node = TreeNode(
        item_id=item_id,
        item_label=resolve_item_label(item_id),
        amount=amount,
        recipe_id=recipe.get("recipe_id"),
        craft_count=craft_count,
        children=[],
        is_base=False,
    )

    memo_key = f"{item_id}:{recipe.get('recipe_id')}"
    if memo_key in context.cycles:
        context.cycles.add(memo_key)
        materials[item_id] += amount
        node.is_base = True
        return node

    if memo_key in context.memo:
        cached_materials, _ = context.memo[memo_key]
        _sum_materials(materials, cached_materials, craft_count)
        return node

    context.cycles.add(memo_key)

    total_materials: defaultdict[str, float] = defaultdict(float)
    for ingredient in recipe.get("ingredients", []):
        ingredient_item = ingredient.get("item") or ingredient.get("tag")
        if not ingredient_item:
            continue
        ingredient_amount = _ingredient_amount(ingredient) * craft_count
        child = await _expand(ingredient_item, ingredient_amount, context, total_materials)
        node.children.append(child)

    if not node.children:
        materials[item_id] += amount
        node.is_base = True
        context.cycles.discard(memo_key)
        return node

    context.memo[memo_key] = (dict(total_materials), recipe)
    _sum_materials(materials, total_materials, 1)
    context.cycles.discard(memo_key)
    return node
